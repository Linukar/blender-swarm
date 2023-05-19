import bpy
import random
import sys

from .constants import maxPropSize
from .utils import findInCollection, copyPropertyGroup
from .controlObjects import ControlObjectSettings
from .agentSettings import findAgents, updateAgent, AgentSettings, setAgentAsCurrent


def initProperties():

    bpy.types.Scene.swarm_settings = bpy.props.PointerProperty(type=SwarmSettings)

    bpy.types.Scene.selected_preset = bpy.props.EnumProperty(
        name="Presets",
        items=lambda self, context: findPresets(context),
        update=lambda self, context: updatePreset(self, context),
    )

    bpy.types.Scene.selected_agent = bpy.props.EnumProperty(
        name="Agents",
        items=lambda self, context: findAgents(self, context),
        update=lambda self, context: updateAgent(self, context),
    )

    bpy.types.Scene.current_agent_settings = bpy.props.PointerProperty(type=AgentSettings)

    bpy.types.Object.control_settings = bpy.props.PointerProperty(type=ControlObjectSettings)


def deinitProperies():
    del bpy.types.Scene.swarm_settings
    del bpy.types.Scene.selected_preset
    del bpy.types.Scene.selected_agent
    del bpy.types.Scene.current_agent_settings
    del bpy.types.Object.control_settings


class SwarmSettings(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")

    # general swarm properties
    seed: bpy.props.IntProperty(default=random.randint(0, maxPropSize), min=0, max=maxPropSize)
    agentCount: bpy.props.IntProperty(default=42, min=1, max=10000)
    swarmCount: bpy.props.IntProperty(default=1, min=1, max=1000)

    spawnAreaSize: bpy.props.FloatProperty(default=3, min=0, precision=2)
    maxSimulationSteps: bpy.props.IntProperty(default=10000, min=1)
    visualizeAgents: bpy.props.BoolProperty(default=True)
    useSculpting: bpy.props.BoolProperty(default=True)
    randomStartLocation: bpy.props.BoolProperty(default=True)
    randomStartXYRotation: bpy.props.BoolProperty(default=True)
    randomStartZRotation: bpy.props.BoolProperty(default=True)
    useDyntypo: bpy.props.BoolProperty(default=True)
    dyntypoResolution: bpy.props.FloatProperty(default=2, min=0.001)

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
    copyPropertyGroup(preset, context.scene.swarm_settings, ["agent_definitions"])

    # Update agent_definitions
    context.scene.swarm_settings.agent_definitions.clear()
    for agent_def in preset.agent_definitions:
        new_agent_def = context.scene.swarm_settings.agent_definitions.add()
        copyPropertyGroup(agent_def, new_agent_def)

    if len(preset.agent_definitions) <= 0:
        return
    
    setAgentAsCurrent(preset.agent_definitions[0], context)
