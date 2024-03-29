import bpy

from .utils import copyPropertyGroup, findInCollection, findAgentDefinition
from .sculptTools import tools
from .materials import updateControlObjectMaterial
from .controlObjects import collectControlObjects

toolModes = [("NORMAL", "Normal", ""), ("INVERT", "Inverted", "")]

def getBrushes(self, context):
    items = []
    if hasattr(bpy.data, 'brushes'):
        for b in bpy.data.brushes:
            if b.use_paint_sculpt:
                items.append((b.name, b.name, ""))
    return items

class AgentSettings(bpy.types.PropertyGroup):

    #general
    name: bpy.props.StringProperty(name="Preset Name", default="Default")
    color: bpy.props.FloatVectorProperty(name="Color", subtype='COLOR_GAMMA', size=4, default=(1, 1, 1, 1), min=0, max=1)

    energy: bpy.props.FloatProperty(name="Energy", default=30, min=0, precision=1)
    minimumLifetime: bpy.props.FloatProperty(name="Min Lifetime", default=0.5, min=0, precision=2)

    # boid
    snapToSurface: bpy.props.BoolProperty(name="Snap to Surface", default=False)
    seeThroughWalls: bpy.props.BoolProperty(name="See through walls", default=False)
    viewAngle: bpy.props.IntProperty(default=180, min=0, max=360)

    noClumpRadius: bpy.props.FloatProperty(default=3, min=0, step=0.01, precision=2)
    localAreaRadius: bpy.props.FloatProperty(default=10, min=0, precision=3)
    speed: bpy.props.FloatProperty(default=2, min=0, precision=3)
    steeringSpeed: bpy.props.FloatProperty(default=1, min=0, precision=3)

    separationWeight: bpy.props.FloatProperty(default=0.5, min=0, max = 1, precision=2)
    alignementWeight: bpy.props.FloatProperty(default=0.35, min=0, max = 1, precision=2)
    cohesionWeight: bpy.props.FloatProperty(default=0.16, min=0, max = 1, precision=2)
    centerUrgeWeight: bpy.props.FloatProperty(default=0.2, min=0, max = 1, precision=2)
    centerMaxDistance: bpy.props.FloatProperty(default=12, min=0, precision=1)
    surfaceWeight: bpy.props.FloatProperty(default=0.2, min=0, max = 1, precision=2)
    randomWeight: bpy.props.FloatProperty(default=0.05, min=0, max = 1, precision=3)
    controlObjectWeight: bpy.props.FloatProperty(default=0.2, min= 0, max=1, precision=2)

    #sculpt
    applyAtEnd: bpy.props.BoolProperty(name="Apply at end", default=False)
    tool: bpy.props.EnumProperty(
        name="Sculpting Brushes",
        description="Available sculpting brushes",
        items=getBrushes
    )
    toolRadius: bpy.props.FloatProperty(name="Tool Radius", default=1, min=0.001, precision=1)
    toolCooldown: bpy.props.FloatProperty(name="Tool Cooldown", default=0, min=0)
    toolStrength: bpy.props.FloatProperty(name="Tool Strength", default=0.5, min=0, max=1, precision=3)
    toolMode: bpy.props.EnumProperty(items=toolModes)
    toolIgnoreBackground: bpy.props.BoolProperty(name="Ignore Background", default=False)
    refreshTopology: bpy.props.BoolProperty(name="Refres Topo", default=False)


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
    for obj in collectControlObjects(context):
        updateControlObjectMaterial(obj, context)


def saveAgentChanges(context: bpy.types.Context):
    _, agent = findAgentDefinition(context, context.scene.selected_agent)
    if agent is None:
        agent = context.scene.swarm_settings.agent_definitions.add()
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


def cloneCurrentAgent(context: bpy.types.Context) -> None:
    agents = context.scene.swarm_settings.agent_definitions
    current_agent_settings = context.scene.current_agent_settings

    new_agent = agents.add()
    copyPropertyGroup(current_agent_settings, new_agent)

    new_agent.name = current_agent_settings.name + "-copy"
