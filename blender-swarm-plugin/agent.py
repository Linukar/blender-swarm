from __future__ import annotations

import math
import random
import bpy
import mathutils
import random
import gpu

import sys

from .utils import context_override, clamp, findAgentDefinition
from .visualization import drawTriangle, drawLine, drawPyramid
from typing import List
from .boidrules import *

from bpy_extras import view3d_utils

from mathutils import Vector
from bpy.types import Camera, Object, Context
from typing import Tuple

from .rewritingRules import *

from .agentSettings import AgentSettings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .swarm import Swarm

class Agent:

    colors = [
        (0.41, 0.22, 0.36), #violet
        (0.86, 0.19, 0.41), #red pink
        (0.37, 0.71, 0.61), #green
        (1, 0.95, 0.46), #yellow
        (0.42, 0.5, 0.86), #blue
        (0.96, 0.58, 0.76), #pink
        (0.02, 0.84, 0.63), 
        (0.36, 0.09, 0.31), 
        (0.15, 0.33, 0.49), 
        (0.5, 1, 0.93), 
        (0.22, 0.18, 0.35), 
        (0.2, 0.62, 0.36),
        (0.93, 0.81, 0.56), 
        (0.89, 0.52, 0.07)]


    def __init__(
            self,
            context: bpy.types.Context, 
            swarm: Swarm, 
            swarmIndex: int, 
            agentSettings: AgentSettings, 
            controlObjects: list[bpy.types.Object],
            spawnPosition: mathutils.Vector = None,
            inheritTransformFrom: Agent = None):

        self.context = context
        self.swarm = swarm
        
        self.agentSettings = agentSettings

        self.swarmIndex = swarmIndex
        self.controlObjects = controlObjects
        self.setFilteredControlObjects()

        self.energy = 200
        self.lifetime = 0

        spawnCubeSize = context.scene.swarm_settings.swarm_spawnAreaSize

        if inheritTransformFrom is not None:
            # they cannt be on the exact same location; boid functions require a direction vector between agents
            # if they are on the same location there is no direction, no distance and the boid cannot calculate its desired direction
            eps = sys.float_info.epsilon
            self.position = inheritTransformFrom.position + mathutils.Vector((eps, eps, eps)) 
            self.rotation = inheritTransformFrom.rotation
        else:

            if spawnPosition is not None:
                self.position = spawnPosition.copy()

            else:
                if context.scene.swarm_settings.swarm_randomStartLocation:
                    self.position = mathutils.Vector((
                        random.uniform(-spawnCubeSize, spawnCubeSize), 
                        random.uniform(-spawnCubeSize, spawnCubeSize), 
                        random.uniform(-spawnCubeSize, spawnCubeSize)
                        ))
                else:
                    self.position = context.active_object.location.copy()

            eul = mathutils.Euler((
                math.radians(random.uniform(0, 360)) if context.scene.swarm_settings.swarm_randomStartXYRotation else 0, 
                math.radians(random.uniform(0, 360)) if context.scene.swarm_settings.swarm_randomStartXYRotation else 0, 
                math.radians(random.uniform(0, 360)) if context.scene.swarm_settings.swarm_randomStartZRotation else 0,
                ))
            self.rotation = eul.to_quaternion()

        self.recalcForward()

        self.steering = self.forward

        self.boidRules = [Separation(context, self), Alignement(context, self), 
                          Cohesion(context, self), CenterUrge(context, self), 
                          Surface(context, self), ControlObjectAttraction(context, self)]
        self.rewritingRules = []

        if context.scene.swarm_settings.swarm_visualizeAgents:
            self.handler = bpy.types.SpaceView3D.draw_handler_add(self.onDraw, (), 'WINDOW', 'POST_VIEW')


    def onDraw(self):
        # do not add drawPoint as handler directly, as it uses references and won't use new values, if they get overwritten
        drawPyramid(self.position, self.rotation, self.agentSettings.color)

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


        bpy.ops.paint.brush_select(sculpt_tool = self.agentSettings.tool, toggle = False)

        bpy.ops.sculpt.brush_stroke(context_override(self.context), stroke = stroke, mode = "NORMAL", ignore_background_click = False)


    def update(self,fixedTimeStep: float, step: int, agents: List["Agent"]):
        self.lifetime += fixedTimeStep
        self.recalcForward()

        self.replacement(fixedTimeStep)

        self.boidMovement(fixedTimeStep, agents)

        #debug flying in circles
        # self.steering = self.rotation @ mathutils.Vector((1, 0, 0))
        # self.steering.rotate(mathutils.Euler((0, 0, 45)))
        # quatDiff = self.forward.rotation_difference(self.steering)
        # rot = mathutils.Quaternion().slerp(quatDiff, clamp(fixedTimeStep * self.steeringSpeed, 0, 1))
        # self.rotation = rot @ self.rotation

        self.position += self.forward * self.agentSettings.speed * fixedTimeStep

        if self.context.scene.swarm_settings.swarm_useSculpting: self.applyBrush()


    def recalcForward(self):
        self.forward = self.rotation @ mathutils.Vector((1, 0, 0))

    
    def boidMovement(self, fixedTimeStep: float, agents: List["Agent"]):
        
        self.steering = mathutils.Vector()

        for other in agents:
            if(other == self or other.swarmIndex is not self.swarmIndex): continue

            vec = other.position - self.position
            distance = vec.magnitude

            angle = vec.angle(self.forward) if distance > 0 else 0 

            for rule in self.boidRules:
                rule.compareWithOther(distance=distance, angle=angle, agent=self, other=other)


        for rule in self.boidRules:
            self.steering += rule.calcDirection(self)

        if(self.steering.length != 0):
            self.steering.normalize()
            quatDiff = self.forward.rotation_difference(self.steering)
            rot = mathutils.Quaternion().slerp(quatDiff, clamp(fixedTimeStep * self.agentSettings.steeringSpeed, 0, 1))
            self.rotation = rot @ self.rotation


    def replacement(self, timeStep):
        chance = 0.0
        closestTransformer = None
        closestDistance = float("inf")

        for t in self.transformer:
            vec = t.location - self.position
            mag = vec.magnitude
            replacementRange = t.control_settings.replacementRange
            chance += 1 - (clamp(mag, 0, replacementRange) / replacementRange)

            if closestDistance > mag:
                closestDistance = mag
                closestTransformer = t

        chance /= 10
        doNotReplace = random.random() > chance
        # try to slow down exponential explosion if agents are replaced by multiples of themself
        tooYoungToDie = self.lifetime < timeStep * 10 

        if closestTransformer is None or doNotReplace or tooYoungToDie:
            return
                
        i, agentDef = findAgentDefinition(self.context, closestTransformer.control_settings.replacementResult)

        self.agentSettings = agentDef
        self.setFilteredControlObjects()

        replacementCount = closestTransformer.control_settings.replacementCount

        if replacementCount > 1:
            for i in range(replacementCount - 1):
                self.swarm.addAgent(
                    Agent(self.context, self.swarm, self.swarmIndex, self.agentSettings, self.controlObjects, inheritTransformFrom=self)
                )
        

    def setFilteredControlObjects(self):
        self.controlObjectsOfAgentType = list(filter(lambda o: o.control_settings.agentId == self.agentSettings.name, self.controlObjects))
        self.attractors = list(filter(lambda o: o.control_settings.type in ["Attractor", "Transformer"], self.controlObjectsOfAgentType))
        self.transformer = list(filter(lambda o: o.control_settings.type == "Transformer", self.controlObjectsOfAgentType))
        