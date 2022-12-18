import bpy
import mathutils
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


class Test_OT_Cancel_All(Operator):
    bl_idname = "object.cancel_all_mods"
    bl_label = "Test1"
    bl_description = "Test1"

    def update():
        print("op update")

    def execute(self, context):
        print("button1")

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
        obj = context.object
        if obj is not None:
            if obj.mode == "SCULPT":
                return True

        return False


class Test_OT_Place_Agent(Operator):
    bl_idname = "object.place_agent"
    bl_label = "Test2"
    bl_description = "Test2"

    def __init__(self):
        self.agents = []

    def execute(self, context):    
        print("button2")
        self.agents.append(Agent())

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True