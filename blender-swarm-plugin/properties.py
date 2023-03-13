import bpy

def registerProperties():
    bpy.types.Scene.swarm_settings = bpy.props.PointerProperty(type=SwarmSettings)

def unregisterProperies():
    del bpy.types.Scene.swarm_settings

class SwarmSettings(bpy.types.PropertyGroup):

    # general swarm properties
    swarm_agentCount: bpy.props.IntProperty(default=20, min=1, max=10000)
    swarm_spawnAreaSize: bpy.props.FloatProperty(default=0.3, min=0, precision=3)
    swarm_maxSimulationSteps: bpy.props.IntProperty(default=200, min=1)
    swarm_visualizeAgents: bpy.props.BoolProperty(default=True)
    swarm_useSculpting: bpy.props.BoolProperty(default=True)


    # agent properties
    agent_general_noClumpRadius: bpy.props.FloatProperty(default=0.1, min=0, max=10, step=0.01, precision=3)
    agent_general_localAreaRadius: bpy.props.FloatProperty(default=10, min=0, precision=3)
    agent_general_speed: bpy.props.FloatProperty(default=0.3, min=0, precision=3)
    agent_general_steeringSpeed: bpy.props.FloatProperty(default=5, min=0, precision=3)
