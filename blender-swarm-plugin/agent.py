import math
import random
import bpy
import mathutils

from .utils import context_override, clamp
from .DrawPoint import drawPoint, drawLine
from typing import List
from .boidrules import *

class Agent:

    def __init__(self, sculptTool: str, spawnCubeSize: float, context: bpy.types.Context):

        self.context = context
        
        self.speed = context.scene.swarm_settings.agent_general_speed
        self.steeringSpeed = context.scene.swarm_settings.agent_general_steeringSpeed

        self.position = mathutils.Vector((
            random.uniform(-spawnCubeSize, spawnCubeSize), 
            random.uniform(-spawnCubeSize, spawnCubeSize), 
            random.uniform(-spawnCubeSize, spawnCubeSize)
            ))
        
        eul = mathutils.Euler((
            math.radians(random.uniform(0, 360)), 
            math.radians(random.uniform(0, 360)), 
            math.radians(random.uniform(0, 360))
            ))
        
        self.rotation = eul.to_quaternion()

        self.forward = mathutils.Vector((1, 0, 0))
        self.forward.rotate(self.rotation)

        self.steering = self.forward

        self.boidRules = [Separation(context), Alignement(context), Cohesion(context), CenterUrge(context)]

        self.sculpt_tool = sculptTool
        if context.scene.swarm_settings.swarm_visualizeAgents:
            self.handler = bpy.types.SpaceView3D.draw_handler_add(self.onDraw, (), 'WINDOW', 'POST_VIEW')


    def onDraw(self):
        # do not add drawPoint as handler directly, as it uses references and won't use new values, if they get overwritten
        drawPoint(self.position, self.rotation, (0.99, 0.05, 0.29))

        # draw steering vector for debugging
        # drawLine(self.position, self.position + self.steering)

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

        #debug flying in circles
        # self.steering = self.rotation @ mathutils.Vector((1, 0, 0))
        # self.steering.rotate(mathutils.Euler((0, 0, 45)))
        # quatDiff = self.forward.rotation_difference(self.steering)
        # rot = mathutils.Quaternion().slerp(quatDiff, clamp(fixedTimeStep * self.steeringSpeed, 0, 1))
        # self.rotation = rot @ self.rotation

        self.position += self.forward * self.speed * fixedTimeStep

        if self.context.scene.swarm_settings.swarm_useSculpting: self.applyBrush()


    def recalcForward(self):
        self.forward = self.rotation @ mathutils.Vector((1, 0, 0))

    
    def boidMovement(self, fixedTimeStep: float, agents: List["Agent"]):
        
        self.steering = mathutils.Vector()

        for other in agents:
            if(other == self): continue

            distance = math.dist(self.position, other.position)

            for rule in self.boidRules:
                rule.compareWithOther(distance, agent=self, other=other)


        for rule in self.boidRules:
            self.steering += rule.calcDirection(self)

        if(self.steering.length != 0):
            self.steering.normalize()
            quatDiff = self.forward.rotation_difference(self.steering)
            rot = mathutils.Quaternion().slerp(quatDiff, clamp(fixedTimeStep * self.steeringSpeed, 0, 1))
            self.rotation = rot @ self.rotation
