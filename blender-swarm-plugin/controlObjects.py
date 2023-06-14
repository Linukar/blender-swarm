import bpy

from itertools import groupby

from .materials import updateControlObjectMaterial


coTypes = ["None", "Spawner", "Attractor", "Deflector", "Replicator"]
collectionName = "SwarmControlObjects"

controlObjectNameIdentifier = "swarm_co_"

class ControlObjectSettings(bpy.types.PropertyGroup):
    useAsControl: bpy.props.BoolProperty(name="Use as Control", default=False)

    type: bpy.props.EnumProperty(
        items=lambda s, c: map(lambda t: (t, t, ""), coTypes),
        update=lambda s, c: updateControlObjectName(s, c)
    )

    agentId: bpy.props.EnumProperty(name="Agent", 
        items=lambda self, context: collectAgentIds(context),
        update=lambda s, c: onAgentUpdate(s, c)
    )

    strength: bpy.props.FloatProperty(name="Strength", default=0.5, min=0)
    
    attractionRange: bpy.props.FloatProperty(name="Radius", default=30, min=0)

    replacementResult: bpy.props.EnumProperty(name="Replacement Result", 
        items=lambda self, context: collectAgentIds(context),
        update=lambda s, c: onReplacementUpdate(s, c)
    )

    replacementRange: bpy.props.FloatProperty(name="Replacement Range", default=5, min=0)
    replacementChance: bpy.props.FloatProperty(name="Replacement Chance", default=1, min=0, precision=2)

    replacementCount: bpy.props.IntProperty(name="Replacement Count", default=1, min=1)

    spawnerRepeat: bpy.props.BoolProperty(name="Spawner Repeat", default=True)
    spawnerFrequency: bpy.props.FloatProperty(name="Spawner Frequency", default=1, min=0, precision=1)
    spawnerAmount: bpy.props.IntProperty(name="Spawner Amount", default=5, min=1)
    spawnerLimit: bpy.props.IntProperty(name="Spawner Limit", default=1000, min=1)
    spawnOnStart: bpy.props.BoolProperty(name="Spawner Start", default=True)
    spawnerOffset: bpy.props.FloatProperty(name="Spawner Offset", default=0, min = 0, precision=1)

    spawnerTimer: bpy.props.FloatProperty(name="Spawner Timer", default=0, min=0)
    spawnerHasSpawned: bpy.props.BoolProperty(name="Spawner Has Spawned", default=False)



def collectAgentIds(context: bpy.types.Context):
    return map(lambda d: (d.name, d.name, ""), context.scene.swarm_settings.agent_definitions)


def addControlObject(context: bpy.types.Context):
    # Add a cube to the scene at the origin
    bpy.ops.mesh.primitive_cube_add(size=0.2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cube = context.active_object
    cube.control_settings.useAsControl = True

    collection = bpy.data.collections.get(collectionName)
    if collection is None:
        collection = bpy.data.collections.new(collectionName)
        context.scene.collection.children.link(collection)

    collection.objects.link(cube)
    context.view_layer.active_layer_collection.collection.objects.unlink(cube)

    cube.name = controlObjectNameIdentifier + cube.control_settings.type + "_" + cube.control_settings.agentId


def updateControlObjectName(self, context: bpy.types.Context):
    context.active_object.name = controlObjectNameIdentifier + self.type + "_" + self.agentId


def onTypeUpdate(self, context: bpy.types.Context):
    updateControlObjectName(self, context)
    updateControlObjectMaterial(context.active_object, context)


def onAgentUpdate(self, context: bpy.types.Context):
    updateControlObjectName(self, context)
    updateControlObjectMaterial(context.active_object, context)
    

def onReplacementUpdate(self, context: bpy.types.Context):
    updateControlObjectName(self, context)
    updateControlObjectMaterial(context.active_object, context)


def isControlObject(object):
    return object is not None and object.control_settings.useAsControl


def collectControlObjects(context: bpy.types.Context) -> list[bpy.types.Object]:
    collection = bpy.data.collections.get(collectionName)
    if collection is not None:
        allObjects = collection.objects
    else:
        allObjects = context.scene.objects
    
    controlObjects = list(filter(lambda o: isControlObject(o), allObjects))

    return controlObjects
