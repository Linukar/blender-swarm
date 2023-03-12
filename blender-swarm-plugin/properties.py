import bpy

def registerProperties():
    bpy.types.Scene.swarm_settings = bpy.props.PointerProperty(type=SwarmSettings)

def unregisterProperies():
    del bpy.types.Scene.swarm_settings

class SwarmSettings(bpy.types.PropertyGroup):
    agent_count: bpy.props.IntProperty(min=1, max=10000)