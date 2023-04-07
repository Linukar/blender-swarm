import math
import random
import bpy
import mathutils
import random
import gpu

from .utils import context_override, clamp
from .DrawPoint import drawPoint, drawLine
from typing import List
from .boidrules import *

from bpy_extras import view3d_utils

from mathutils import Vector
from bpy.types import Camera, Object, Context
from typing import Tuple


class Agent:

    possibleTools = ["DRAW", "CLAY"]
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

        self.sculpt_tool = random.choice(Agent.possibleTools)

        if context.scene.swarm_settings.swarm_visualizeAgents:
            self.handler = bpy.types.SpaceView3D.draw_handler_add(self.onDraw, (), 'WINDOW', 'POST_VIEW')

        self.initial_camera_distance = Agent.get_viewport_camera_location(context).magnitude

    def onDraw(self):
        # do not add drawPoint as handler directly, as it uses references and won't use new values, if they get overwritten
        drawPoint(self.position, self.rotation, self.color)

        # draw steering vector for debugging
        # drawLine(self.position, self.position + self.steering)

    def onStop(self, context: bpy.types.Context):
        if context.scene.swarm_settings.swarm_visualizeAgents:
            bpy.types.SpaceView3D.draw_handler_remove(self.handler, 'WINDOW')


    def get_viewport_camera_location(context: Context) -> Vector:
        area = next(area for area in context.screen.areas if area.type == 'VIEW_3D')
        region = next(region for region in area.regions if region.type == 'WINDOW')
        rv3d = next(space for space in area.spaces if space.type == 'VIEW_3D')
        
        if rv3d.region_3d.view_perspective == 'CAMERA':
            return context.scene.camera.matrix_world.to_translation()
        else:
            depth_location = view3d_utils.region_2d_to_location_3d(region, rv3d.region_3d, (region.width / 2.0, region.height / 2.0), rv3d.region_3d.view_distance * mathutils.Vector((1.0, 1.0, 1.0)))
            return depth_location

    def get_distance_to_object(camera_location: Vector, obj_location: Vector) -> float:
        distance = (camera_location - obj_location).length
        return distance


    def normalize_distance(distance:float , reference_distance: float) -> float:
        return distance / reference_distance

    def calculate_size_value(relative_distance: float, object_dimensions: Vector, size_scale_factor: float) -> float:
        object_size = max(object_dimensions)
        size_value = object_size * relative_distance * size_scale_factor
        return size_value

    def create_visualization_sphere(location, size_value):
        bpy.ops.mesh.primitive_uv_sphere_add(location=location)
        sphere = bpy.context.active_object
        sphere.name = "visualization_sphere"
        sphere.scale = (size_value, size_value, size_value)
        return sphere

    def calculate_screen_space_size_value(relative_size: float, object_camera_distance: float, depth_location: float, screen_width: int) -> float:
        return relative_size * (depth_location / (object_camera_distance ** 2)) * screen_width

    def calculate_compensated_size_value(relative_size: float, object_camera_distance: float, viewport_camera_distance: float) -> float:
        return relative_size * (viewport_camera_distance / object_camera_distance)


    def linear_scaling(relative_size: float, initial_camera_distance: float, current_camera_distance: float) -> float:
        inverse_scaling_factor = initial_camera_distance / current_camera_distance
        return relative_size * inverse_scaling_factor

    def logarithmic_scaling(relative_size: float, initial_camera_distance: float, current_camera_distance: float, base: float = 2) -> float:
        inverse_scaling_factor = math.log(initial_camera_distance, base) / math.log(current_camera_distance, base)
        return relative_size * inverse_scaling_factor

    def quadratic_scaling(relative_size: float, initial_camera_distance: float, current_camera_distance: float) -> float:
        inverse_scaling_factor = (initial_camera_distance ** 2) / (current_camera_distance ** 2)
        return relative_size * inverse_scaling_factor



    def applyBrush(self):
        # Set a reference distance to normalize the camera distance
        reference_distance = 10.0
        # Set a size scale factor to control the size value
        size_scale_factor = 0.001

        # viewport_camera_depth_location, screen_width = Agent.get_viewport_camera_location(self.context)
        # object_location = obj.matrix_world.to_translation()

        # Get the distance between the camera and the object
        # distance = Agent.get_distance_to_object(viewport_camera_depth_location, object_location)
        # Normalize the distance using the reference distance
        # normalized_distance = Agent.normalize_distance(distance, reference_distance)

        # Get the object's dimensions
        # object_dimensions = obj.dimensions

        # Calculate the size value based on the object's dimensions and normalized distance
        # size_value = Agent.calculate_screen_space_size_value(relative_size, normalized_distance, viewport_camera_depth_location.length, screen_width)

        obj = self.context.active_object

        object_location = obj.matrix_world.to_translation()
        viewport_camera_location = Agent.get_viewport_camera_location(self.context)
        camera_distance = (object_location - viewport_camera_location).magnitude

        current_camera_distance = (object_location - viewport_camera_location).magnitude
        inverse_scaling_factor = self.initial_camera_distance / current_camera_distance


        relative_size = 50  # Set the desired relative size in Blender units
        compensated_size_value = relative_size * inverse_scaling_factor
        # Choose the desired scaling method
        compensated_size_value = Agent.linear_scaling(relative_size, self.initial_camera_distance, current_camera_distance)
        # compensated_size_value = Agent.logarithmic_scaling(relative_size, self.initial_camera_distance, current_camera_distance)
        # compensated_size_value = Agent.quadratic_scaling(relative_size, self.initial_camera_distance, current_camera_distance)

        # original_active_object = self.context.active_object
        # visualization_sphere = Agent.create_visualization_sphere(object_location, size_value/100)
        # self.context.view_layer.objects.active = original_active_object

        self.context.scene.tool_settings.sculpt.brush.size = int(compensated_size_value)

        import bpy

        # Create a custom brush
        custom_brush = bpy.data.brushes.new(name="CustomBrush", mode='SCULPT')

        # Assign the custom brush to the sculpt tool
        bpy.context.tool_settings.sculpt.brush = custom_brush

        # Set the custom brush properties
        custom_brush.sculpt_tool = self.sculpt_tool
        custom_brush.size = int(compensated_size_value)

        stroke = [{
                "name": "stroke",
                "is_start": True,
                "location": self.position,
                "mouse": (0, 0),
                "mouse_event": (0.0, 0.0),
                "pen_flip": True,
                "pressure": 1,
                "size": compensated_size_value,
                "time": 1,
                "x_tilt": 0,
                "y_tilt": 0
            }]

        print(compensated_size_value)

        # bpy.ops.paint.brush_select(sculpt_tool = self.sculpt_tool, toggle = False)

        bpy.ops.sculpt.brush_stroke(context_override(self.context), stroke = stroke, mode = "INVERT", ignore_background_click = False)


    def update(self, fixedTimeStep: float, step: int, agents: List["Agent"]):
        self.recalcForward()
        self.boidMovement(fixedTimeStep, agents)

        #debug flying in circles
        # self.steering = self.rotation @ mathutils.Vector((1, 0, 0))
        # self.steering.rotate(mathutils.Euler((0, 0, 45)))
        # quatDiff = self.forward.rotation_difference(self.steering)
        # rot = mathutils.Quaternion().slerp(quatDiff, clamp(fixedTimeStep * self.steeringSpeed, 0, 1))
        # self.rotation = rot @ self.rotation

        # self.position += self.forward * self.maxSpeed * fixedTimeStep

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
