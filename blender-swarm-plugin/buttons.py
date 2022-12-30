import bpy
import mathutils
from bpy.types import Operator
from .hive import Hive


class Swarm_OT_Sculpt_Test(Operator):
    bl_idname = "swarm.test1"
    bl_label = "Sculpt"
    bl_description = "Test1"
    hive = None

    def update():
        print("op update")

    def execute(self, context):

        bpy.ops.object.mode_set(mode="SCULPT")

        bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False
        Swarm_OT_Sculpt_Test.hive = Hive(50)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return Swarm_OT_Sculpt_Test.hive == None or not Swarm_OT_Sculpt_Test.hive.isRunning()


class Swarm_OT_Spawn_Plane(Operator):
    bl_idname = "swarm.spawn_plane"
    bl_label = "Spawn Plane"
    bl_description = "Spawns plane with subdivisions"

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

    def execute(self, context):    
        bpy.data.objects.remove(bpy.context.active_object)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True