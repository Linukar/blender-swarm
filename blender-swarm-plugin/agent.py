import math
import random
import bpy
import mathutils

from .utils import context_override
from .DrawPoint import drawPoint
from typing import List


class Agent:

    def __init__(self, sculptTool: str, spawnCubeSize: float, context: bpy.types.Context):
        # boid
        self.noClumpRadius = context.scene.swarm_settings.agent_general_noClumpRadius
        self.localAreaRadius = context.scene.swarm_settings.agent_general_localAreaRadius

        self.speed = context.scene.swarm_settings.agent_general_speed
        self.steeringSpeed = context.scene.swarm_settings.agent_general_steeringSpeed

        self.position = mathutils.Vector((
            random.uniform(-spawnCubeSize, spawnCubeSize), 
            random.uniform(-spawnCubeSize, spawnCubeSize), 
            random.uniform(-spawnCubeSize, spawnCubeSize)
            ))
        
        self.forward = mathutils.Vector((1, 0, 0))
        eul = mathutils.Euler((
            math.radians(random.uniform(0, 360)), 
            math.radians(random.uniform(0, 360)), 
            math.radians(random.uniform(0, 360))
            ))
        self.forward.rotate(eul)

        self.sculpt_tool = sculptTool
        args = (self.position, (0.99, 0.05, 0.29))

        if context.scene.swarm_settings.swarm_visualizeAgents:
            self.handler = bpy.types.SpaceView3D.draw_handler_add(drawPoint, args, 'WINDOW', 'POST_VIEW')


    def onStop(self, context: bpy.types.Context):
        if context.scene.swarm_settings.swarm_visualizeAgents:
            bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')


    def applyBrush(self):
        stroke = [{
                "name": "stroke",
                "is_start": True,
                "location": self.position,
                "mouse": (0, 0),
                "mouse_event": (0.0, 0.0),
                "pen_flip": True,
                "pressure": 1,
                "size": 2,
                "time": 1,
                "x_tilt": 0,
                "y_tilt": 0
            }]

        bpy.ops.paint.brush_select(sculpt_tool = self.sculpt_tool, toggle = False)

        bpy.ops.sculpt.brush_stroke(context_override(), stroke = stroke, mode = "INVERT", ignore_background_click = False)


    def update(self, deltaTime: float, step: int, agents: List["Agent"]):

        steering = mathutils.Vector()

        separationDirection = mathutils.Vector()
        separationCount = 0

        alignmentDirection = mathutils.Vector()
        alignmentCount = 0

        cohesionDirection = mathutils.Vector()
        cohesionCount = 0

        for other in agents:
            if(other == self): continue

            distance = math.dist(self.position, other.position)

            if(distance < self.noClumpRadius):
                separationDirection += other.position - self.position
                separationCount += 1

            if(distance < self.localAreaRadius):
                alignmentDirection += other.forward
                alignmentCount += 1

                cohesionDirection += other.position - self.position
                cohesionCount += 1

        if(separationCount > 0):
            separationDirection /= separationCount
            separationDirection.normalize()
            separationDirection.negate()
            steering = separationDirection

        if(alignmentCount > 0):
            alignmentDirection /= alignmentCount
            alignmentDirection.normalize()
            steering += alignmentDirection

        if(cohesionCount > 0):
            cohesionDirection /= cohesionCount
            cohesionDirection.normalize()
            cohesionDirection.negate()
            steering += cohesionDirection

        if(steering.length_squared != 0):
            self.forward = self.forward.slerp(steering, deltaTime * self.steeringSpeed).normalized()

        self.position += self.forward * self.speed * deltaTime


        self.applyBrush()
