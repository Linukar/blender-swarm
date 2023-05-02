import bpy
import mathutils
import random
import sys
import bpy_extras

from bpy.types import Operator
from .swarmManager import SwarmManager
from .constants import maxPropSize
from .presets import importPresets, exportPresets, addPreset, removePreset, savePresetChanges

class Swarm_OT_Start_Simulation(Operator):
    bl_idname = "swarm.start_simulation"
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

        bpy.ops.mesh.primitive_plane_add(size = 100)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=10000)
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



class Swarm_OT_Start_Modal_Simulation(Operator):
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



class Swarm_OT_DeleteAll(bpy.types.Operator):
    """Delete all objects"""
    bl_idname = "object.delete_all"
    bl_label = "Delete All Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        return {'FINISHED'}


class Swarm_OT_NewSeed(bpy.types.Operator):
    bl_idname = "swarm.new_seed"
    bl_label = "Set Random Swarm Seed"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        random.seed(None)
        context.scene.swarm_settings.swarm_seed = random.randint(0, maxPropSize)
        return {'FINISHED'}
    

class SWARM_OT_ExportPresets(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "swarm.export_presets"
    bl_label = "Export Presets"
    bl_options = {'REGISTER'}

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        addonPrefs = context.preferences.addons[__package__].preferences
        exportPresets(self.filepath, addonPrefs, context)
        return {'FINISHED'}



class SWARM_OT_ImportPresets(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "swarm.import_presets"
    bl_label = "Import Presets"
    bl_options = {'REGISTER'}

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        addonPrefs = context.preferences.addons[__package__].preferences
        importPresets(self.filepath, addonPrefs)
        return {'FINISHED'}


class SWARM_OT_AddPreset(bpy.types.Operator):
    bl_idname = "swarm.add_preset"
    bl_label = "Add Preset"
    bl_options = {'REGISTER'}

    def execute(self, context):
        addPreset(context)
        return {'FINISHED'}
    

class SWARM_OT_RemovePreset(bpy.types.Operator):
    bl_idname = "swarm.remove_preset"
    bl_label = "Remove Preset"
    bl_options = {'REGISTER'}

    def execute(self, context):
        removePreset(context)
        return {'FINISHED'}
    

class SWARM_OT_SavePreset(bpy.types.Operator):
    bl_idname = "swarm.save_preset"
    bl_label = "Save Preset"
    bl_options = {'REGISTER'}

    def execute(self, context):
        savePresetChanges(context)
        return {'FINISHED'}