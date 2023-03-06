import bpy
import itertools
import random

from typing import List
from .agent import Agent

class Hive:

    deltaTime = 0.033 # 30 fps

    def __init__(self, totalSteps: int):
        possibleTools = ["DRAW", "CLAY", "CREASE"]

        self.agents: List[Agent] = []

        for _ in range (0, 20):
            self.agents.append(Agent(random.choice(possibleTools)))

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
