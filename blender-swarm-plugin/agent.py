import math
import random
import bpy
import mathutils
import random
import gpu

from .utils import context_override, clamp
from .visualization import drawTriangle, drawLine
from typing import List
from .boidrules import *

from bpy_extras import view3d_utils

from mathutils import Vector
from bpy.types import Camera, Object, Context
from typing import Tuple


class Agent:

    possibleTools = ["DRAW"]


    colors = [(0.13, 0.1, 0.17), (0.54, 0.2, 0.31), (0.88, 0.43, 0.32), (1, 0.82, 0.4), (0.02, 0.84, 0.63), (0.36, 0.09, 0.31), (0.15, 0.33, 0.49), (0.5, 1, 0.93), 
              (0.22, 0.18, 0.35), (0.2, 0.62, 0.36), (0.93, 0.81, 0.56), (0.89, 0.52, 0.07)]


    def __init__(self, context: bpy.types.Context, swarmIndex: int):

        self.context = context
        
        self.swarmIndex = swarmIndex
        self.color = Agent.colors[swarmIndex % len(Agent.colors)]

        self.maxSpeed = context.scene.swarm_settings.agent_general_speed
        self.steeringSpeed = context.scene.swarm_settings.agent_general_steeringSpeed

        spawnCubeSize = context.scene.swarm_settings.swarm_spawnAreaSize

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

        self.sculpt_tool = context.scene.swarm_settings.agent_general_tool

        if context.scene.swarm_settings.swarm_visualizeAgents:
            self.handler = bpy.types.SpaceView3D.draw_handler_add(self.onDraw, (), 'WINDOW', 'POST_VIEW')


    def onDraw(self):
        # do not add drawPoint as handler directly, as it uses references and won't use new values, if they get overwritten
        drawTriangle(self.position, self.rotation, self.color)

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
                "size": 0.5,
                "time": 1,
                "x_tilt": 0,
                "y_tilt": 0
            }]


        bpy.ops.paint.brush_select(sculpt_tool = self.sculpt_tool, toggle = False)

        bpy.ops.sculpt.brush_stroke(context_override(self.context), stroke = stroke, mode = "NORMAL", ignore_background_click = False)


    def update(self, fixedTimeStep: float, step: int, agents: List["Agent"]):
        self.recalcForward()
        self.boidMovement(fixedTimeStep, agents)

        #debug flying in circles
        # self.steering = self.rotation @ mathutils.Vector((1, 0, 0))
        # self.steering.rotate(mathutils.Euler((0, 0, 45)))
        # quatDiff = self.forward.rotation_difference(self.steering)
        # rot = mathutils.Quaternion().slerp(quatDiff, clamp(fixedTimeStep * self.steeringSpeed, 0, 1))
        # self.rotation = rot @ self.rotation

        self.position += self.forward * self.maxSpeed * fixedTimeStep

        if self.context.scene.swarm_settings.swarm_useSculpting: self.applyBrush()


    def recalcForward(self):
        self.forward = self.rotation @ mathutils.Vector((1, 0, 0))

    
    def boidMovement(self, fixedTimeStep: float, agents: List["Agent"]):
        
        self.steering = mathutils.Vector()

        for other in agents:
            if(other == self or other.swarmIndex is not self.swarmIndex): continue

            vec = other.position - self.position
            distance = vec.magnitude
            angle = vec.angle(self.forward)

            for rule in self.boidRules:
                rule.compareWithOther(distance=distance, angle=angle, agent=self, other=other)


        for rule in self.boidRules:
            self.steering += rule.calcDirection(self)

        if(self.steering.length != 0):
            self.steering.normalize()
            quatDiff = self.forward.rotation_difference(self.steering)
            rot = mathutils.Quaternion().slerp(quatDiff, clamp(fixedTimeStep * self.steeringSpeed, 0, 1))
            self.rotation = rot @ self.rotation
