import bpy
import itertools
import random
import time

from typing import List
from .agent import Agent

class Swarm:

    deltaTime = 0.033 # 30 fps

    def __init__(self, context: bpy.types.Context):
        possibleTools = ["DRAW", "CLAY", "CREASE"]
        agentCount = context.scene.swarm_settings.swarm_agentCount
        spawnCubeSize = context.scene.swarm_settings.swarm_spawnAreaSize

        self.agents: List[Agent] = []

        for _ in range (0, agentCount):
            self.agents.append(Agent(random.choice(possibleTools), spawnCubeSize, context))

        self.totalSteps = context.scene.swarm_settings.swarm_maxSimulationSteps
        self.step = 0;
        self.shouldStop = False

        def update():
            startTime = time.time()
            for agent in self.agents:
                agent.update(Swarm.deltaTime, self.step, self.agents)

            endTime = time.time()

            self.step += 1

            if self.step > self.totalSteps:
                self.shouldStop = True

            if self.shouldStop:
                for agent in self.agents:
                    agent.onStop(context)

                bpy.app.timers.unregister(self.updateFunc)

            
            if context.scene.swarm_settings.swarm_visualizeAgents:
                return min(Swarm.deltaTime - (endTime - startTime), 0)
            else:
                return 0 
        

        self.updateFunc = update

        bpy.app.timers.register(self.updateFunc)


    def isRunning(self):
        return self.step < self.totalSteps and not self.shouldStop
    
    def stop(self):
        self.shouldStop = True

