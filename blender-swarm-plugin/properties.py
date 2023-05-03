import bpy
import random
import sys

from .sculptTools import tools
from .constants import maxPropSize
from .utils import findInCollection

def initProperties():

    bpy.types.Scene.swarm_settings = bpy.props.PointerProperty(type=SwarmSettings)

    bpy.types.Scene.selected_preset = bpy.props.EnumProperty(
        name="Presets",
        items=lambda self, context: findPresets(context),
        update=lambda self, context: updatePreset(self, context),
    )


def deinitProperies():
    del bpy.types.Scene.swarm_settings



class AgentSettings(bpy.types.PropertyGroup):
    noClumpRadius: bpy.props.FloatProperty(default=3, min=0, max=10, step=0.01, precision=3)
    localAreaRadius: bpy.props.FloatProperty(default=10, min=0, precision=3)
    speed: bpy.props.FloatProperty(default=2, min=0, precision=3)
    steeringSpeed: bpy.props.FloatProperty(default=1, min=0, precision=3)

    separationWeight: bpy.props.FloatProperty(default=0.5, min=0, max = 1, precision=2)
    alignementWeight: bpy.props.FloatProperty(default=0.35, min=0, max = 1, precision=2)
    cohesionWeight: bpy.props.FloatProperty(default=0.16, min=0, max = 1, precision=2)
    leaderWeight: bpy.props.FloatProperty(default=0.5, min=0, max=1, precision=2)    
    centerUrgeWeight: bpy.props.FloatProperty(default=0.2, min=0, max = 1, precision=2)
    centerMaxDistance: bpy.props.FloatProperty(default=12, min=0, precision=1)
    surfaceWeight: bpy.props.FloatProperty(default=0.2, min=0, max = 1, precision=2)

    tool: bpy.props.EnumProperty(items=tools)



class SwarmSettings(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Preset Name", default="")

    # general swarm properties
    swarm_seed: bpy.props.IntProperty(default=random.randint(0, maxPropSize), min=0, max=maxPropSize)
    swarm_agentCount: bpy.props.IntProperty(default=30, min=1, max=10000)
    swarm_swarmCount: bpy.props.IntProperty(default=3, min=1, max=1000)

    swarm_spawnAreaSize: bpy.props.FloatProperty(default=3, min=0, precision=2)
    swarm_maxSimulationSteps: bpy.props.IntProperty(default=10000, min=1)
    swarm_visualizeAgents: bpy.props.BoolProperty(default=True)
    swarm_useSculpting: bpy.props.BoolProperty(default=True)


    # agent properties
    agent_general_noClumpRadius: bpy.props.FloatProperty(default=3, min=0, max=10, step=0.01, precision=3)
    agent_general_localAreaRadius: bpy.props.FloatProperty(default=10, min=0, precision=3)
    agent_general_speed: bpy.props.FloatProperty(default=2, min=0, precision=3)
    agent_general_steeringSpeed: bpy.props.FloatProperty(default=1, min=0, precision=3)

    agent_general_separationWeight: bpy.props.FloatProperty(default=0.5, min=0, max = 1, precision=2)
    agent_general_alignementWeight: bpy.props.FloatProperty(default=0.35, min=0, max = 1, precision=2)
    agent_general_cohesionWeight: bpy.props.FloatProperty(default=0.16, min=0, max = 1, precision=2)
    agent_general_leaderWeight: bpy.props.FloatProperty(default=0.5, min=0, max=1, precision=2)    
    agent_general_centerUrgeWeight: bpy.props.FloatProperty(default=0.2, min=0, max = 1, precision=2)
    agent_general_centerMaxDistance: bpy.props.FloatProperty(default=12, min=0, precision=1)
    agent_general_surfaceWeight: bpy.props.FloatProperty(default=0.2, min=0, max = 1, precision=2)

    agent_general_tool: bpy.props.EnumProperty(items=tools)



def findPresets(context):
    addonPrefs = context.preferences.addons[__package__].preferences
    items = [(preset.name, preset.name, "") for i, preset in enumerate(addonPrefs.presets)]
    return items


def updatePreset(self, context: bpy.types.Context):
    selectedPreset = self.selected_preset
    addonPrefs = context.preferences.addons[__package__].preferences
    i, selectedPreset = findInCollection(addonPrefs.presets, lambda p: p.name == selectedPreset)

    if selectedPreset is None:
        return

    setPresetAsCurrent(selectedPreset, context)
    

def setPresetAsCurrent(preset: "SwarmSettings", context : bpy.types.Context):
    for prop in context.scene.swarm_settings.bl_rna.properties:
        if prop.identifier == "rna_type":
            continue
        setattr(context.scene.swarm_settings, prop.identifier, getattr(preset, prop.identifier))

def resetCurrentSettingsToDefault(context: bpy.types.Context):
    context.scene.swarm_settings = SwarmSettings()