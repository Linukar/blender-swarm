import bpy
import json
import os
import bpy_extras

from typing import Dict, Any, List

from .properties import SwarmSettings

class SwarmPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    presets: bpy.props.CollectionProperty(type=SwarmSettings)

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
        else:
            result[prop.identifier] = value
    return result


def setPropertyGroupValuesFromDict(dataDict: Dict[str, Any], propGroup: bpy.types.PropertyGroup) -> None:
    for key, value in dataDict.items():
        if key not in propGroup.bl_rna.properties:
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
        else:
            setattr(propGroup, key, value)


def exportPresets(filepath: str, addonPrefs: SwarmPreferences, context) -> None:
    propGroupDicts = [propertyGroupToDict(preset) for preset in addonPrefs.presets]

    currentGroup = context.scene.swarm_settings
    currentDict = propertyGroupToDict(currentGroup)

    found = False
    for i, preset in enumerate(propGroupDicts):
        if preset["name"] == currentDict["name"]:
            propGroupDicts[i] = currentDict
            found = True
            break

    if not found and currentGroup.name != "":
        propGroupDicts.append(currentDict)

    with open(filepath, "w") as f:
        json.dump(propGroupDicts, f, indent=4)


def importPresets(filepath: str, addonPrefs: SwarmPreferences) -> None:
    with open(filepath, "r") as f:
        presetDataList = json.load(f)

    addonPrefs.presets.clear()

    for presetData in presetDataList:
        newPreset = addonPrefs.presets.add()
        newPreset.name = presetData.get("name", "Unnamed")
        setPropertyGroupValuesFromDict(presetData, newPreset)
        continue

