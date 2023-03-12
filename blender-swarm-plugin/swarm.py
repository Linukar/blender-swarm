import bpy
import itertools
import random

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

        def update():
            for agent in self.agents:
                agent.update(Swarm.deltaTime, self.step, self.agents)
                print("Step: " + str(self.step))



            self.step += 1
            if self.step > self.totalSteps:
                for agent in self.agents:
                    agent.onStop()

                bpy.app.timers.unregister(self.updateFunc)

            
            return Swarm.deltaTime
        

        self.updateFunc = update

        bpy.app.timers.register(self.updateFunc)


    def isRunning(self):
        return self.step < self.totalSteps
