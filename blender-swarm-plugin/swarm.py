import bpy
import time

from typing import List
from .agent import Agent
from .utils import printProgressBar

class Swarm:

    fixedTimeStep = 0.033 # 30 fps

    def __init__(self, context: bpy.types.Context):
        agentCount = context.scene.swarm_settings.swarm_agentCount

        self.agents: List[Agent] = []

        for _ in range (0, agentCount):
            self.agents.append(Agent(context))

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
