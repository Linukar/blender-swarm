import math
import random
import bpy
import mathutils

from .utils import context_override, clamp
from .DrawPoint import drawPoint
from typing import List


class Agent:

    def __init__(self, sculptTool: str, spawnCubeSize: float, context: bpy.types.Context):

        self.context = context
        
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
        
        self.rotation = eul.to_quaternion()
        self.forward.rotate(self.rotation)

        self.sculpt_tool = sculptTool
        if context.scene.swarm_settings.swarm_visualizeAgents:
            self.handler = bpy.types.SpaceView3D.draw_handler_add(self.onDraw, (), 'WINDOW', 'POST_VIEW')


    def onDraw(self):
        # do not add drawPoint as handler directly, as it uses references and won't use new values, if they get overwritten
        drawPoint(self.position, self.rotation, (0.99, 0.05, 0.29))

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


    def update(self, fixedTimeStep: float, step: int, agents: List["Agent"]):
    
        self.recalcForward()
        self.boidMovement(fixedTimeStep, agents)

        self.position += self.forward * self.speed * fixedTimeStep

        if self.context.scene.swarm_settings.swarm_useSculpting: self.applyBrush()


    def recalcForward(self):
        self.forward = mathutils.Vector((1, 0, 0))
        self.forward.rotate(self.rotation)

    
    def boidMovement(self, fixedTimeStep: float, agents: List["Agent"]):
        
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
            steering += separationDirection * self.context.scene.swarm_settings.agent_general_separationWeight

        if(alignmentCount > 0):
            alignmentDirection /= alignmentCount
            alignmentDirection.normalize()
            steering += alignmentDirection * self.context.scene.swarm_settings.agent_general_alignementWeight

        if(cohesionCount > 0):
            cohesionDirection /= cohesionCount
            cohesionDirection.normalize()
            steering += cohesionDirection * self.context.scene.swarm_settings.agent_general_cohesionWeight

        directionToCenter = -self.position
        steering += directionToCenter * self.context.scene.swarm_settings.agent_general_centerUrgeWeight

        if(steering.length != 0):
            steering.normalize()
            quatDiff = self.forward.rotation_difference(steering)
            self.rotation = self.rotation.slerp(quatDiff, clamp(fixedTimeStep * self.steeringSpeed, 0, 1))

