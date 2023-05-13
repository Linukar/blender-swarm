import bpy

from itertools import groupby

from .utils import findInCollection


coTypes = ["Spawner", "Attractor", "Repulsor", "Transformer", "Splitter"]
collectionName = "SwarmControlObjects"

materialNameIdentifier = "swarm_m_"
controlObjectNameIdentifier = "swarm_co_"

class ControlObjectSettings(bpy.types.PropertyGroup):
    useAsControl: bpy.props.BoolProperty(name="Use as Control", default=False)

    type: bpy.props.EnumProperty(
        items=lambda s, c: map(lambda t: (t, t, ""), coTypes),
        update=lambda s, c: setObjectName(s, c)
    )

    agentId: bpy.props.EnumProperty(name="Agent", 
        items=lambda self, context: collectAgentIds(context),
        update=lambda s, c: agentIdUpdate(s, c)
    )

    strength: bpy.props.FloatProperty(name="Strength", default=0.5, min=0)
    
    attractionRange: bpy.props.FloatProperty(name="Radius", default=30, min=0)

    replacementResult: bpy.props.EnumProperty(name="Replacement Result", 
        items=lambda self, context: collectAgentIds(context)
    )

    replacementRange: bpy.props.FloatProperty(name="Replacement Range", default=5, min=0)



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


def setObjectName(self, context: bpy.types.Context):
    context.active_object.name = controlObjectNameIdentifier + self.type + "_" + self.agentId


def agentIdUpdate(self, context: bpy.types.Context):

    i, agentDef = findInCollection(context.scene.swarm_settings.agent_definitions, lambda a: a.name == self.agentId)

    if agentDef is None: return

    color = agentDef.color

    existingMat = bpy.data.materials.get(materialNameIdentifier + agentDef.name)

    if existingMat is None:
        existingMat = bpy.data.materials.new(name=materialNameIdentifier + agentDef.name)
        existingMat.use_nodes = True
        bsdf_node = existingMat.node_tree.nodes.get("Principled BSDF")
        if bsdf_node:
            bsdf_node.inputs["Base Color"].default_value = [color[0], color[1], color[2], 1]


    context.active_object.data.materials.clear()
    context.active_object.data.materials.append(existingMat)

    setObjectName(self, context)
    

def isControlObject(object):
    return object is not None and object.control_settings.useAsControl


def collectControlObjects(context: bpy.types.Context) -> dict[str, list[bpy.types.Object]]:
    collection = bpy.data.collections.get(collectionName)
    if collection is not None:
        allObjects = collection.objects
    else:
        allObjects = context.scene.objects
    
    controlObjects = list(filter(lambda o: isControlObject(o), allObjects))
    sortedObjects = sorted(controlObjects, key=lambda o: o.control_settings.agentId)
    grouped = groupby(sortedObjects, lambda o: o.control_settings.agentId)

    return {key: list(group) for key, group in grouped}
