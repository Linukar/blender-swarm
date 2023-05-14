import bpy

from .utils import copyPropertyGroup, findInCollection, findAgentDefinition
from .sculptTools import tools
from .materials import updateControlObjectMaterial
from .controlObjects import collectControlObjects


class AgentSettings(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Preset Name", default="")
    color: bpy.props.FloatVectorProperty(name="Color", subtype='COLOR_GAMMA', size=4, default=(1, 1, 1, 1), min=0, max=1)

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

    
def setAgentAsCurrent(agent: AgentSettings, context: bpy.types.Context):
    copyPropertyGroup(agent, context.scene.current_agent_settings)


def updateControlObjectColor(context):
    for key, list in collectControlObjects(context).items():
        for obj in list:
            updateControlObjectMaterial(obj.control_settings, context)


def saveAgentChanges(context: bpy.types.Context):
    _, agent = findAgentDefinition(context, context.scene.selected_agent)
    copyPropertyGroup(context.scene.current_agent_settings, agent)
    updateControlObjectColor(context)

            
def addAgent(context: bpy.types.Context) -> None:
    swarm_settings = context.scene.swarm_settings
    newAgent = swarm_settings.agent_definitions.add()
    newAgent.name = "Unnamed Agent"

    # Set the new agent as the selected agent
    context.scene.selected_agent = newAgent.name
    

def removeAgent(context: bpy.types.Context) -> None:
    agents = context.scene.swarm_settings.agent_definitions

    i, _ = findInCollection(agents, lambda p: p.name == context.scene.selected_agent)

    if i is not None and len(agents) > 1:
        agents.remove(i)
        setAgentAsCurrent(agents[i-1], context)