import bpy
import time
import random

from typing import List
from .agent import Agent
from .utils import printProgressBar, createBVH

from .agentTypes import *

class Swarm:

    fixedTimeStep = 0.033 # 30 fps

    def __init__(self, context: bpy.types.Context):
        agentCount = context.scene.swarm_settings.swarm_agentCount
        random.seed(context.scene.swarm_settings.swarm_seed)

        self.agents: List[Agent] = []

        i = 0
        for _ in range (0, context.scene.swarm_settings.swarm_swarmCount):
            i += 1
            for _ in range (0, agentCount):
                agentDefinitions = context.scene.swarm_settings.agent_definitions
                currentAgent = agentDefinitions[i % (len(agentDefinitions))]

                self.agents.append(Agent(context, swarmIndex=i, agentSettings=currentAgent))

        self.totalSteps = context.scene.swarm_settings.swarm_maxSimulationSteps
        self.step = 0;
        self.shouldStop = False
        self.context = context
        self.startTime = time.time()

        bpy.app.timers.register(self.update)


    def isRunning(self):
        return self.step < self.totalSteps and not self.shouldStop
    

    def stop(self):
        self.shouldStop = True


    def onStop(self):
        for agent in self.agents:
            agent.onStop(self.context)

        print("Finished in: " + str(time.time() - self.startTime))


    def update(self):
        printProgressBar(self.step, self.totalSteps, "Simulating...", printEnd="\r")
        self.updateStartTime = time.time()

        self.bvhTree, self.bmesh = createBVH(self.context.active_object)

        for agent in self.agents:
            agent.update(self, Swarm.fixedTimeStep, self.step, self.agents)

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
