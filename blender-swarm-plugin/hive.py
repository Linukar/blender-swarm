import bpy
import itertools
import random

from typing import List
from .agent import Agent

class Hive:

    deltaTime = 0.033 # 30 fps

    def __init__(self, totalSteps: int):
        possibleTools = ["DRAW", "CLAY", "CREASE"]
        agentCount = 20
        spawnCubeSize = 0.3

        self.agents: List[Agent] = []

        for _ in range (0, agentCount):
            self.agents.append(Agent(random.choice(possibleTools), spawnCubeSize))

        self.totalSteps = totalSteps
        self.step = 0;

        def update():
            for agent in self.agents:
                agent.update(Hive.deltaTime, self.step, self.agents)
                print("Step: " + str(self.step))



            self.step += 1
            if self.step > self.totalSteps:
                for agent in self.agents:
                    agent.onStop()

                bpy.app.timers.unregister(self.updateFunc)

            
            return Hive.deltaTime
        

        self.updateFunc = update

        bpy.app.timers.register(self.updateFunc)


    def isRunning(self):
        return self.step < self.totalSteps
