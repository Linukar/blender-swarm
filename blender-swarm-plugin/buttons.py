import bpy
import mathutils
import bmesh
from bpy.types import Operator

from .agent import Agent


def context_override():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return {'window': window, 'screen': screen, 'area': area, 'region': region, 'scene': bpy.context.scene} 


class Swarm_OT_Sculpt_Test(Operator):
    bl_idname = "swarm.test1"
    bl_label = "Sculpt"
    bl_description = "Test1"

    def update():
        print("op update")

    def execute(self, context):

        bpy.ops.object.mode_set(mode="SCULPT")

        bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False

        stroke = [{
                "name": "stroke",
                "is_start": True,
                "location": (0, 0, 0),
                "mouse": (0,0),
                "mouse_event": (0.0, 0.0),
                "pen_flip" : True,
                "pressure": 1,
                "size": 50,
                "time": 1,
                "x_tilt": 0,
                "y_tilt": 0
            }]

        bpy.ops.paint.brush_select(sculpt_tool="DRAW", toggle=False)
        bpy.ops.sculpt.brush_stroke(context_override(), stroke=stroke)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True


class Swarm_OT_Spawn_Plane(Operator):
    bl_idname = "swarm.spawn_plane"
    bl_label = "Spawn Plane"
    bl_description = "Spawns plane with subdivisions"

    def __init__(self):
        self.agents = []

    def execute(self, context):    

        bpy.ops.mesh.primitive_plane_add(size = 2)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=100)
        bpy.ops.object.mode_set(mode="OBJECT")

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True

class Swarm_OT_Remove_Selected(Operator):
    bl_idname = "swarm.remove_selected"
    bl_label = "Remove Selected"
    bl_description = "Remove Selected"

    def __init__(self):
        self.agents = []

    def execute(self, context):    

        if context.mode == "SCULPT":
            bpy.data.objects.remove(bpy.context.active_object)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True