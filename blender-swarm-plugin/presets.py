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


def dictToPropertyGroup(dataDict: Dict[str, Any], propGroup: bpy.types.PropertyGroup) -> None:
    for propName, propValue in dataDict.items():
        if propName in propGroup:
            propGroup[propName] = propValue

def exportPresets(filepath: str, addonPrefs: SwarmPreferences, context) -> None:
    propGroupDicts = [propertyGroupToDict(preset) for preset in addonPrefs.presets]

    current = propertyGroupToDict(context.scene.swarm_settings)
    propGroupDicts.append(current)

    with open(filepath, "w") as f:
        json.dump(propGroupDicts, f, indent=4)


def importPresets(filepath: str, addonPrefs: SwarmPreferences) -> None:
    with open(filepath, "r") as f:
        presetDataList = json.load(f)

    addonPrefs.presets.clear()

    for presetData in presetDataList:
        newPreset = addonPrefs.presets.add()
        newPreset.name = presetData.get("name", "Unnamed")
        dictToPropertyGroup(presetData, newPreset)





