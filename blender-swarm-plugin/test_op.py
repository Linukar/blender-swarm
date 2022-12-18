import bpy

from bpy.types import Operator
from .agent import Agent

class Test_OT_Cancel_All(Operator):
    bl_idname = "object.cancel_all_mods"
    bl_label = "Cancel All"
    bl_description = "Cancel all operators of the active object"

    def execute(self, context):
        active_obj = context.view_layer.objects.active
        active_obj.modifiers.clear()
        print("button1")

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj is not None:
            if obj.mode == "OBJECT":
                return True

        return False


class Test_OT_Place_Agent(Operator):
    bl_idname = "object.place_agent"
    bl_label = "Place Agent"
    bl_description = "Place an agent"

    def __init__(self):
        self.agents = []

    def execute(self, context):    
        print("button2")
        self.agents.append(Agent())

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True