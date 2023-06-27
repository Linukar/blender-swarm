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

        if context.scene.swarm_settings.enableSurfaceAwareness:
            self.bvhTree = createBVH(self.context.active_object)

        agentDefinitions = context.scene.swarm_settings.agent_definitions
        if len(agentDefinitions) < 1: return

        for spawner in self.spawner:
            spawner.control_settings.spawnerHasSpawned = False
            spawner.control_settings.spawnerTimer = 0
            if spawner.control_settings.spawnOnStart:
                self.spawnFromSpawner(spawner)

        bpy.app.timers.register(self.update)


    def isRunning(self):
        return self.step < self.totalSteps and not self.shouldStop
    

    def setShouldStop(self):
        self.shouldStop = True


    def onStop(self):
        for agent in self.agents:
            agent.onStop()

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

            if spawner.control_settings.spawnerRepeat:
                if (spawner.control_settings.spawnerTimer > spawner.control_settings.spawnerFrequency 
                    and timeSinceStart > spawner.control_settings.spawnerOffset
                    and spawner.control_settings.spawnerLimit > len([a for a in self.agents if a.agentSettings.name == spawner.control_settings.agentId])):
                        self.spawnFromSpawner(spawner)
            elif not spawner.control_settings.spawnerHasSpawned and timeSinceStart > spawner.control_settings.spawnerOffset:
                self.spawnFromSpawner(spawner)
                

        if self.context.scene.swarm_settings.enableSurfaceAwareness and self.context.scene.swarm_settings.enablePreciseSurfaceMode:
            if self.context.scene.swarm_settings.useDyntypo and self.context.active_object.use_dynamic_topology_sculpting:
                bpy.ops.sculpt.dynamic_topology_toggle()

            self.bvhTree = createBVH(self.context.active_object)

            if self.context.scene.swarm_settings.useDyntypo and not self.context.active_object.use_dynamic_topology_sculpting:
                bpy.ops.sculpt.dynamic_topology_toggle()


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

        spawner.control_settings.spawnerHasSpawned = True

    
    def removeAgent(self, agent):
        agent.onStop()
        self.agents.remove(agent)