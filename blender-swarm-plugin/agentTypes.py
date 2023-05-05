import bpy

from .agent import Agent

class Fast(Agent):
    def __init__(self, context: bpy.types.Context, swarmIndex: int):
        super().__init__(context, swarmIndex)
        self.maxSpeed = self.maxSpeed * 10
        self.steeringSpeed = self.steeringSpeed * 10
        self.typeName = "Fast"


class Slow(Agent):
    def __init__(self, context: bpy.types.Context, swarmIndex: int):
        super().__init__(context, swarmIndex)
        self.maxSpeed = self.maxSpeed / 5
        self.steeringSpeed = self.steeringSpeed / 5
        self.typeName = "Slow"