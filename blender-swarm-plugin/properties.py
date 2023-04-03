import bpy

def registerProperties():
    bpy.types.Scene.swarm_settings = bpy.props.PointerProperty(type=SwarmSettings)

def unregisterProperies():
    del bpy.types.Scene.swarm_settings

class SwarmSettings(bpy.types.PropertyGroup):

    # general swarm properties
    swarm_agentCount: bpy.props.IntProperty(default=30, min=1, max=10000)
    swarm_swarmCount: bpy.props.IntProperty(default=3, min=1, max=10)

    swarm_spawnAreaSize: bpy.props.FloatProperty(default=0.3, min=0, precision=3)
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

