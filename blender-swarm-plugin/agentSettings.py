import bpy

from .utils import findInCollection, copyPropertyGroup
from .sculptTools import tools


class AgentSettings(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Preset Name", default="")
    color: bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', default=(1, 1, 1), min=0, max=1)

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


def findAgents(self, context):
    agents = context.scene.swarm_settings.agent_definitions
    items = [(agent.name, agent.name, "") for i, agent in enumerate(agents)]
    return items


def updateAgent(self, context: bpy.types.Context):
    i, selected = findAgentDefinition(context, context.scene.selected_agent)

    if selected is None:
        return

    setAgentAsCurrent(selected, context)

    
def setAgentAsCurrent(agent: "AgentSettings", context: bpy.types.Context):
    copyPropertyGroup(agent, context.scene.current_agent_settings)


def findAgentDefinition(context: bpy.types.Context, name: str) -> tuple[int, AgentSettings]:
    return findInCollection(context.scene.swarm_settings.agent_definitions, lambda a: a.name == name)