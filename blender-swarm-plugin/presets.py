import bpy
import json
import os
import bpy_extras

from typing import Dict, Any, List

from .properties import SwarmPresets, setPresetAsCurrent
from .agentSettings import saveAgentChanges

from .utils import findInCollection, copyPropertyGroup, findAgentDefinition


def propertyGroupToDict(propGroup: bpy.types.PropertyGroup) -> Dict[str, Any]:
    result = {}
    for prop in propGroup.bl_rna.properties:
        if prop.identifier == "rna_type":
            continue
        value = getattr(propGroup, prop.identifier)
        if isinstance(value, bpy.types.PropertyGroup):
            result[prop.identifier] = propertyGroupToDict(value)
        elif isinstance(value, bpy.types.bpy_prop_collection):
            result[prop.identifier] = [propertyGroupToDict(item) for item in value]
        elif isinstance(value, bpy.types.bpy_prop_array):
            result[prop.identifier] = list(value)  
        else:
            result[prop.identifier] = value
    return result


def setPropertyGroupValuesFromDict(dataDict: Dict[str, Any], propGroup: bpy.types.PropertyGroup) -> None:
    for key, value in dataDict.items():
        if key not in propGroup.bl_rna.properties or key == "agent_definitions":
            continue

        if isinstance(value, dict) and isinstance(propGroup, bpy.types.PropertyGroup):
            sub_propGroup = getattr(propGroup, key)
            setPropertyGroupValuesFromDict(value, sub_propGroup)
        elif isinstance(value, list) and isinstance(propGroup, bpy.types.bpy_prop_collection):
            propCollection = getattr(propGroup, key)
            propCollection.clear()
            for item_data in value:
                item = propCollection.add()
                setPropertyGroupValuesFromDict(item_data, item)
        elif isinstance(value, list) and isinstance(getattr(propGroup, key), bpy.types.bpy_prop_array):
            propArray = getattr(propGroup, key)
            for i, v in enumerate(value):
                if i < len(propArray):  # Ensure not to exceed the length of the bpy_prop_array
                    propArray[i] = v
        else:
            setattr(propGroup, key, value)


def exportPresets(filepath: str, presets: SwarmPresets, context: bpy.types.Context) -> None:
    propGroupDicts = [propertyGroupToDict(preset) for preset in presets.presets]

    for preset, presetDict in zip(presets.presets, propGroupDicts):
        presetDict['agent_definitions'] = [propertyGroupToDict(agent) for agent in preset.agent_definitions]

    with open(filepath, "w") as f:
        json.dump(propGroupDicts, f, indent=4)


def importPresets(filepath: str, presets: SwarmPresets) -> None:
    with open(filepath, "r") as f:
        presetDataList = json.load(f)

    presets.presets.clear()

    for presetData in presetDataList:
        newPreset = presets.presets.add()
        newPreset.agent_definitions.add()

        setPropertyGroupValuesFromDict(presetData, newPreset)

        newPreset.agent_definitions.clear()
        for agentData in presetData['agent_definitions']:
            newAgent = newPreset.agent_definitions.add()
            setPropertyGroupValuesFromDict(agentData, newAgent)



def addPreset(context: bpy.types.Context) -> None:
    presets = context.scene.swarm_presets.presets
    newPreset = presets.add()
    newPreset.name = "Unnamed"
    newPreset.agent_definitions.add()
    setPresetAsCurrent(newPreset, context)


def cloneCurrentPreset(context: bpy.types.Context) -> None:
    presets = context.scene.swarm_presets.presets
    swarm_settings = context.scene.swarm_settings

    newPreset = presets.add()
    copyPropertyGroup(swarm_settings, newPreset, ["agent_definitions"])

    for agent_def in swarm_settings.agent_definitions:
        new_agent_def = newPreset.agent_definitions.add()
        copyPropertyGroup(agent_def, new_agent_def)

    # Set the name of the new preset
    newPreset.name += "-copy"
    setPresetAsCurrent(newPreset, context)


def removePreset(context: bpy.types.Context) -> None:
    presets = context.scene.swarm_presets.presets
    i, _ = findInCollection(presets, lambda p: p.name == context.scene.selected_preset)

    if i is not None and len(presets) > 1:
        presets.remove(i)
        setPresetAsCurrent(presets[i-1], context)


    
def savePresetChanges(context: bpy.types.Context):
    presets = context.scene.swarm_presets.presets

    _, preset = findInCollection(presets, lambda p: p.name == context.scene.selected_preset)

    if preset is None:
        preset = presets.add()

    copyPropertyGroup(context.scene.swarm_settings, preset, ["agent_definitions"])

    saveAgentChanges(context)

    # Update agent_definitions in the preset
    preset.agent_definitions.clear()
    for agent_def in context.scene.swarm_settings.agent_definitions:
        new_agent_def = preset.agent_definitions.add()
        copyPropertyGroup(agent_def, new_agent_def)

    # Update the preset list
    context.scene.swarm_settings.selected_preset = preset.name
