import bpy
import time
import random

from typing import List

import mathutils
from .agent import Agent
from .utils import printProgressBar, createBVH, findAgentDefinition
from .controlObjects import collectControlObjects
from .agentSettings import AgentSettings


class Swarm:

    fixedTimeStep = 0.033 # 30 fps

    def __init__(self, context: bpy.types.Context):
        agentCount = context.scene.swarm_settings.agentCount
        random.seed(context.scene.swarm_settings.seed)

        self.agents: List[Agent] = []
        self.isPaused = False

        self.controlObjects = collectControlObjects(context)
        self.spawner = list(filter(lambda o: o.control_settings.type == "Spawner", self.controlObjects))

        self.totalSteps = context.scene.swarm_settings.maxSimulationSteps
        self.step = 0;
        self.shouldStop = False
        self.context = context
        self.startTime = time.time()

        agentDefinitions = context.scene.swarm_settings.agent_definitions
        if len(agentDefinitions) < 1: return

        # i = 0
        # for _ in range (0, context.scene.swarm_settings.swarmCount):
        #     i += 1
        #     for _ in range (0, agentCount):
        #         i, selectedAgent = findAgentDefinition(context, context.scene.current_agent_settings.name)
        #         self.createNewAgent(context, i, selectedAgent)

        for spawner in self.spawner:
            if spawner.control_settings.spawnOnStart:
                self.spawnFromSpawner(spawner)

        bpy.app.timers.register(self.update)


    def isRunning(self):
        return self.step < self.totalSteps and not self.shouldStop
    

    def stop(self):
        self.shouldStop = True


    def onStop(self):
        for agent in self.agents:
            agent.onStop(self.context)

        print("Finished in: " + str(time.time() - self.startTime))


    def pause(self):
        self.isPaused = not self.isPaused


    def update(self):
        if self.isPaused:
            return 0

        # printProgressBar(self.step, self.totalSteps, "Simulating...", printEnd="\r")
        self.updateStartTime = time.time()
        timeSinceStart = time.time() - self.startTime

        for spawner in self.spawner:
            spawner.control_settings.spawnerTimer += Swarm.fixedTimeStep
            if (spawner.control_settings.spawnerTimer > spawner.control_settings.spawnerFrequency 
                and timeSinceStart > spawner.control_settings.spawnerOffset):
                    self.spawnFromSpawner(spawner)

        self.bvhTree, self.bmesh = createBVH(self.context.active_object)

        for agent in self.agents:
            agent.update(Swarm.fixedTimeStep, self.step, self.agents)

        self.step += 1

        if self.step > self.totalSteps:
            self.shouldStop = True

        if self.shouldStop:
           self.onStop()
           return None

        # update with 30 fps or slower
        # never faster, to allow the user to be able to understand whats happening
        if self.context.scene.swarm_settings.visualizeAgents:
            timeDiff = (time.time() - self.updateStartTime)
            return max(Swarm.fixedTimeStep - timeDiff, 0)
        else:
            return 0


    def createNewAgent(self, context: bpy.types.Context, swarmIndex: int, agentSettings: AgentSettings, spawnPosition: mathutils.Vector = None):
        self.agents.append(
            Agent(context,
                self,
                swarmIndex=swarmIndex, 
                agentSettings=agentSettings, 
                controlObjects=self.controlObjects,
                spawnPosition=spawnPosition
            ))
        
    
    def addAgent(self, agent: Agent):
        self.agents.append(agent)

    def spawnFromSpawner(self, spawner):
        i, agentDef = findAgentDefinition(self.context, spawner.control_settings.agentId)
        if agentDef is not None:
            for i in range(spawner.control_settings.spawnerAmount):
                self.createNewAgent(self.context, 0, agentDef, spawnPosition=spawner.location)
            spawner.control_settings.spawnerTimer = 0