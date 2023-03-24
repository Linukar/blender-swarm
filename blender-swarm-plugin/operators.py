import bpy
import mathutils
from bpy.types import Operator
from .swarmManager import SwarmManager

class Swarm_OT_Sculpt_Test(Operator):
    bl_idname = "swarm.test1"
    bl_label = "Sculpt"
    bl_description = "Test1"

    def update():
        print("op update")

    def execute(self, context):
        SwarmManager.startSwarm(context)
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return not SwarmManager.isRunning()


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
    
class Swarm_OT_Stop_Simulation(Operator):
    bl_idname = "swarm.stop_simulation"
    bl_label = "Stop Simulation"
    bl_description = "Stop Simulation"

    def execute(self, context):    
        SwarmManager.stopSwarm()

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True



class Swarm_OT_Start_Simulation(Operator):
    bl_idname = "swarm.modal_simulation"
    bl_label = "Simple Modal Operator"

    def __init__(self):
        print("Start")

    def __del__(self):
        print("End")

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(4)
        wm.modal_handler_add(self)
        self.isRunning = True
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        print("update - pre check")
        if(self == None): print("self is none")
        print("self is not none")
        print(self)
        print("printed self")
        if(not self.isRunning):
            print("update - not running")
            return {'CANCELLED'}
        print("update - post check")
        if event.type == 'TIMER':  # Apply
            print("update")
        elif event.type == 'ESC':  # Cancel
            self.stop(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def stop(self, context: bpy.types.Context):
        print("1")
        wm = context.window_manager
        print("2")
        wm.event_timer_remove(self._timer)
        print("3")
        self.isRunning = False


    def invoke(self, context, event):
        self.execute(context)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}