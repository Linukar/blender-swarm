from __future__ import annotations

import math
import random
import bpy
import mathutils
import random
import bpy_extras

import sys
import time

from .utils import clamp, findAgentDefinition, findClosestPointInBVH, find3dViewportContext, randomVector
from .visualization import drawTriangle, drawLine, drawPyramid
from typing import List
from .boidrules import *

from bpy_extras import view3d_utils

from mathutils import Vector
from bpy.types import Camera, Object, Context
from typing import Tuple

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

        self.swarmIndex = swarmIndex
        self.controlObjects = controlObjects

        self.lifetime = 0
        self.strokes = []
        self.flightPath = []

        area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        self.region = next(region for region in area.regions if region.type == 'WINDOW')
        self.spaceData = next(space for space in area.spaces if space.type == 'VIEW_3D')

        spawnCubeSize = context.scene.swarm_settings.spawnAreaSize

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
                if context.scene.swarm_settings.randomStartLocation:
                    self.position = randomVector(-spawnCubeSize, spawnCubeSize)
                else:
                    self.position = context.active_object.location.copy()

            rndAngles = randomVector(0, 360)
            eul = mathutils.Euler((
                math.radians(rndAngles.x) if context.scene.swarm_settings.randomStartXYRotation else 0, 
                math.radians(rndAngles.y) if context.scene.swarm_settings.randomStartXYRotation else 0, 
                math.radians(rndAngles.z) if context.scene.swarm_settings.randomStartZRotation else 0,
                ))
            self.rotation = eul.to_quaternion()

        self.recalcForward()

        self.steering = self.forward

        self.resetAgent(agentSettings)

        self.depsgraph = context.evaluated_depsgraph_get()

        self.boidRules = [Separation(context, self),
                          Alignement(context, self), 
                          Cohesion(context, self), 
                          CenterUrge(context, self), 
                          Surface(context, self), 
                          ControlObjectAttraction(context, self),
                          TrueRandom(context, self)
                          ]

        if context.scene.swarm_settings.visualizeAgents:
            self.handler = bpy.types.SpaceView3D.draw_handler_add(self.onDraw, (), 'WINDOW', 'POST_VIEW')


    def onDraw(self):
        # do not add drawPoint as handler directly, as it uses references and won't use new values, if they get overwritten
        drawPyramid(self.position, self.rotation, self.agentSettings.color)

        if self.context.scene.swarm_settings.showFlightPaths:
            drawLine(self.flightPath, self.agentSettings.color)

        elif self.agentSettings.applyAtEnd:
            drawLine([s["location"] for s in self.strokes], self.agentSettings.color)

        # draw steering vector for debugging
        # drawLine([self.position, self.position + self.steering*10], [1, 1, 1, 1])


    def onStop(self):
        self.endStroke()
        if self.context.scene.swarm_settings.visualizeAgents:
            bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')

    
    def endStroke(self):
        if self.agentSettings.applyAtEnd:
            self.applyBrush(self.strokes)
            self.strokes.clear()


    def createStrokeAtCurrent(self, isStart: bool):
        location = self.position.copy()
        mouse = bpy_extras.view3d_utils.location_3d_to_region_2d(self.region, self.spaceData.region_3d, location)

        return {
                "name": "stroke",
                "is_start": isStart,
                "location": location,
                "mouse": mouse,
                "mouse_event": mouse,
                "pen_flip": False,
                "pressure": 1,
                "size": 1,
                "time": time.time(),
                "x_tilt": 0,
                "y_tilt": 0 
            }


    def sculptUpdate(self, timeStep: float):
        self.toolCooldown -= timeStep

        if self.toolCooldown > 0:
            return

        self.toolCooldown = self.agentSettings.toolCooldown

        if self.agentSettings.applyAtEnd:
            self.strokes.append(self.createStrokeAtCurrent(isStart=False))
        
        else:
            stroke = [self.createStrokeAtCurrent(isStart=True)]
            self.applyBrush(stroke)


    def applyBrush(self, stroke):
        bpy.ops.paint.brush_select(sculpt_tool = self.agentSettings.tool, toggle = False)

        brush = self.context.tool_settings.unified_paint_settings
        brush.unprojected_radius = self.agentSettings.toolRadius
        brush.use_unified_strength = True
        brush.strength = self.agentSettings.toolStrength
        brush.use_locked_size = "SCENE"

        window, area, region = find3dViewportContext(self.context)

        if window and area and region:
            with self.context.temp_override(
                window=window,
                area=area,
                region=region, 
                scene=self.context.scene, 
                object=self.context.active_object):
                    bpy.ops.sculpt.brush_stroke(
                        stroke=stroke, 
                        mode=self.agentSettings.toolMode, 
                        ignore_background_click=self.agentSettings.toolIgnoreBackground)
                    pass


    def update(self,fixedTimeStep: float, step: int, agents: List["Agent"]):
        self.lifetime += fixedTimeStep
        self.energy -= fixedTimeStep
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

        if self.agentSettings.snapToSurface and self.context.scene.swarm_settings.enableSurfaceAwareness:
            self.position = findClosestPointInBVH(self.swarm.bvhTree, self.position)

        if self.context.scene.swarm_settings.useSculpting: self.sculptUpdate(fixedTimeStep)

        if self.energy < 0:
            self.swarm.removeAgent(self)

        if self.context.scene.swarm_settings.showFlightPaths:
            self.flightPath.append(self.position.copy())


    def recalcForward(self):
        self.forward = self.rotation @ mathutils.Vector((1, 0, 0))

    
    def boidMovement(self, fixedTimeStep: float, agents: List["Agent"]):
        
        self.steering = mathutils.Vector()

        for other in agents:
            if(other == self or other.swarmIndex is not self.swarmIndex): continue

            vec = other.position - self.position
            distance = vec.magnitude

            angle = vec.angle(self.forward) if distance > 0 else 0 

            if degrees(angle) > self.agentSettings.viewAngle / 2:
                continue

            for rule in self.boidRules:
                rule.compareWithOther(distance=distance, angle=angle, agent=self, other=other)


        for rule in self.boidRules:
            self.steering += rule.calcDirection(self)

        if(self.steering.length != 0):
            self.steering.normalize()
            quatDiff = self.forward.rotation_difference(self.steering)
            rot = mathutils.Quaternion().slerp(quatDiff, clamp(self.agentSettings.steeringSpeed, 0, 1))
            self.rotation = rot @ self.rotation


    def replacement(self, timeStep):
        chanceToReplace = 0.0
        closestReplicator = None
        closestDistance = float("inf")

        for rep in self.replicator:
            vecToRepCenter = rep.location - self.position

            if vecToRepCenter.magnitude > rep.control_settings.replacementRange:
                continue

            hit, hitLocation, n, i, o, m  = self.context.scene.ray_cast(
                depsgraph= self.depsgraph, 
                origin= self.position, 
                direction=vecToRepCenter)

            if hit:
                vecToRep = hitLocation - self.position
            else:
                vecToRep = vecToRepCenter

            magnitude = vecToRep.magnitude
            replacementRange = rep.control_settings.replacementRange
            chanceToReplace += 1 - (clamp(magnitude, 0, replacementRange) / replacementRange)

            if closestDistance > magnitude:
                closestDistance = magnitude
                closestReplicator = rep

        if closestReplicator is None:
            return

        chanceToReplace *= closestReplicator.control_settings.replacementChance
        doNotReplace = random.random() > chanceToReplace
        # try to slow down exponential explosion if agents are replaced by multiples of themself
        tooYoungToDie = self.lifetime < timeStep * 10 

        if doNotReplace or tooYoungToDie:
            return
                
        i, agentDef = findAgentDefinition(self.context, closestReplicator.control_settings.replacementResult)

        self.resetAgent(agentDef)

        replacementCount = closestReplicator.control_settings.replacementCount

        if replacementCount > 1:
            for i in range(replacementCount - 1):
                self.swarm.addAgent(
                    Agent(self.context, self.swarm, self.swarmIndex, self.agentSettings, self.controlObjects, inheritTransformFrom=self)
                )
        

    def setFilteredControlObjects(self):
        self.controlObjectsOfAgentType = [o for o in self.controlObjects if o.control_settings.agentId == self.agentSettings.name]
        self.attractors = [o for o in self.controlObjectsOfAgentType if o.control_settings.type in ["Attractor", "Replicator", "Deflector"]]
        self.replicator = [o for o in self.controlObjectsOfAgentType if o.control_settings.type == "Replicator"]
        

    def setAgentSettings(self, agentSettings: AgentSettings):
        self.agentSettings = agentSettings
        self.energy = agentSettings.energy


    def resetAgent(self, agentSettings: AgentSettings):
        self.setAgentSettings(agentSettings)
        self.setFilteredControlObjects()
        self.strokes.clear()
        self.strokes.append(self.createStrokeAtCurrent(isStart=True))
        self.toolCooldown = agentSettings.toolCooldown