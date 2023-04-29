import bpy
import random
import sys

from .sculptTools import tools
from .constants import maxPropSize

def registerProperties():
    bpy.types.Scene.swarm_settings = bpy.props.PointerProperty(type=SwarmSettings)

def unregisterProperies():
    del bpy.types.Scene.swarm_settings


def updatePreset(propGroup: bpy.types.PropertyGroup, context: bpy.types.Context):
    addonPrefs = context.preferences.addons[__package__].preferences
    selected_preset = addonPrefs.presets[int(propGroup.presetEnum)]

    for prop in propGroup.bl_rna.properties:
        if prop.identifier == "rna_type" or prop.identifier == "presetEnum":
            continue
        setattr(propGroup, prop.identifier, getattr(selected_preset, prop.identifier))

    

class SwarmSettings(bpy.types.PropertyGroup):

    presetEnum: bpy.props.EnumProperty(
        name="Presets",
        items=lambda self, context: [(str(i), preset.name, "") for i, preset in enumerate(context.preferences.addons[__package__].preferences.presets)],
        update=lambda self, context: updatePreset(self, context),
    )

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


