import bpy
import time
import random

from typing import List
from .agent import Agent
from .utils import printProgressBar, createBVH, findAgentDefinition
from .controlObjects import collectControlObjects
from .agentSettings import AgentSettings


class Swarm:

    fixedTimeStep = 0.033 # 30 fps

    def __init__(self, context: bpy.types.Context):
        agentCount = context.scene.swarm_settings.swarm_agentCount
        random.seed(context.scene.swarm_settings.swarm_seed)

        self.agents: List[Agent] = []
        self.isPaused = False

        self.controlObjects = collectControlObjects(context)

        self.totalSteps = context.scene.swarm_settings.swarm_maxSimulationSteps
        self.step = 0;
        self.shouldStop = False
        self.context = context
        self.startTime = time.time()

        agentDefinitions = context.scene.swarm_settings.agent_definitions
        if len(agentDefinitions) < 1: return

        i = 0
        for _ in range (0, context.scene.swarm_settings.swarm_swarmCount):
            i += 1
            for _ in range (0, agentCount):
                i, selectedAgent = findAgentDefinition(context, context.scene.current_agent_settings.name)
                self.createNewAgent(context, i, selectedAgent)

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

        self.bvhTree, self.bmesh = createBVH(self.context.active_object)

        for agent in self.agents:
            agent.update(Swarm.fixedTimeStep, self.step, self.agents)

        self.step += 1

        if self.step > self.totalSteps:
            self.shouldStop = True

        if self.shouldStop:
           self.onStop()
           return None

        if self.context.scene.swarm_settings.swarm_visualizeAgents:
            timeDiff = (time.time() - self.updateStartTime)
            return max(Swarm.fixedTimeStep - timeDiff, 0)
        else:
            return 0


    def createNewAgent(self, context: bpy.types.Context, swarmIndex: int, agentSettings: AgentSettings):
        self.agents.append(
            Agent(context,
                self,
                swarmIndex=swarmIndex, 
                agentSettings=agentSettings, 
                controlObjects=self.controlObjects
            ))
        
    
    def addAgent(self, agent: Agent):
        self.agents.append(agent)