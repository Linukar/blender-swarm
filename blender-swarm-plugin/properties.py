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

    # bpy.types.Scene.control_objects = bpy.types.CollectionProperty(type=bpy.types.Object)

    bpy.types.Scene.selected_agent = bpy.props.EnumProperty(
        name="Agents",
        items=lambda self, context: findAgents(self, context),
        update=lambda self, context: updateAgent(self, context),
    )

    bpy.types.Scene.current_agent_settings = bpy.props.PointerProperty(type=AgentSettings)



def deinitProperies():
    del bpy.types.Scene.swarm_settings



class AgentSettings(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Preset Name", default="")
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

    name: bpy.props.StringProperty(name="Name", default="")

    # general swarm properties
    swarm_seed: bpy.props.IntProperty(default=random.randint(0, maxPropSize), min=0, max=maxPropSize)
    swarm_agentCount: bpy.props.IntProperty(default=30, min=1, max=10000)
    swarm_swarmCount: bpy.props.IntProperty(default=3, min=1, max=1000)

    swarm_spawnAreaSize: bpy.props.FloatProperty(default=3, min=0, precision=2)
    swarm_maxSimulationSteps: bpy.props.IntProperty(default=10000, min=1)
    swarm_visualizeAgents: bpy.props.BoolProperty(default=True)
    swarm_useSculpting: bpy.props.BoolProperty(default=True)
    swarm_randomStartLocation: bpy.props.BoolProperty(default=True)
    swarm_randomStartXYRotation: bpy.props.BoolProperty(default=True)
    swarm_randomStartZRotation: bpy.props.BoolProperty(default=True)

    # agent properties
    agent_definitions: bpy.props.CollectionProperty(type=AgentSettings)


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
    

def setPresetAsCurrent(preset: "SwarmSettings", context: bpy.types.Context):
    for prop in context.scene.swarm_settings.bl_rna.properties:
        if prop.identifier == "rna_type" or prop.identifier == "agent_definitions":
            continue
        setattr(context.scene.swarm_settings, prop.identifier, getattr(preset, prop.identifier))

    # Update agent_definitions
    context.scene.swarm_settings.agent_definitions.clear()
    for agent_def in preset.agent_definitions:
        new_agent_def = context.scene.swarm_settings.agent_definitions.add()
        for prop in agent_def.bl_rna.properties:
            if prop.identifier == "rna_type":
                continue
            setattr(new_agent_def, prop.identifier, getattr(agent_def, prop.identifier))


    if len(preset.agent_definitions) <= 0:
        return
    
    setAgentAsCurrent(preset.agent_definitions[0], context)


def findAgents(self, context):
    agents = context.scene.swarm_settings.agent_definitions
    items = [(agent.name, agent.name, "") for i, agent in enumerate(agents)]
    return items


def updateAgent(self, context: bpy.types.Context):
    agents = context.scene.swarm_settings.agent_definitions
    i, selected_agent = findInCollection(agents, lambda a: a.name == context.scene.selected_agent)

    if selected_agent is None:
        return

    setAgentAsCurrent(selected_agent, context)

    
def setAgentAsCurrent(agent: "AgentSettings", context: bpy.types.Context):
    for prop in agent.bl_rna.properties:
        if prop.identifier == "rna_type":
            continue
        setattr(context.scene.current_agent_settings, prop.identifier, getattr(agent, prop.identifier))