import bpy

from typing import List
from .agent import Agent

class Hive:

    def __init__(self, totalSteps: int):
        self.agents: List[Agent] = []
        self.agents.append(Agent("DRAW"))
        self.agents.append(Agent("CLAY"))
        self.agents.append(Agent("CREASE"))


        self.totalSteps = totalSteps
        self.step = 0;

        def update():
            for agent in self.agents:
                agent.update(self.step)
                print("Step: " + str(self.step))

            self.step += 1
            if self.step > self.totalSteps:
                for agent in self.agents:
                    agent.onStop()

                bpy.app.timers.unregister(self.updateFunc)
            
            return 0.2

        self.updateFunc = update

        bpy.app.timers.register(self.updateFunc)

    def isRunning(self):
        return self.step < self.totalSteps
