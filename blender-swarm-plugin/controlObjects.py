import bpy

from itertools import groupby

from .utils import findInCollection


coTypes = ["Spawner", "Attractor", "Repulsor", "Transformer", "Splitter"]
collectionName = "SwarmControlObjects"
controlTypePropertyName = "controlType"
agentIdPropertyName = "agentId"


class ControlObjectSettings(bpy.types.PropertyGroup):
    useAsControl: bpy.props.BoolProperty(name="Use as Control", default=False)

    type: bpy.props.EnumProperty(
        items=lambda s, c: map(lambda t: (t, t, ""), coTypes)
    )

    agentId: bpy.props.EnumProperty(name="Agent", 
        items=lambda self, context: map(lambda d: (d.name, d.name, ""), context.scene.swarm_settings.agent_definitions),
        update=lambda s, c: agentIdUpdate(s, c)
    )

def addControlObject(context: bpy.types.Context):
    # Add a cube to the scene at the origin
    bpy.ops.mesh.primitive_cube_add(size=0.2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cube = context.active_object
    cube.control_settings.useAsControl = True

    item = context.scene.control_objects.add()
    item.object = cube

    collection = bpy.data.collections.get(collectionName)
    if collection is None:
        collection = bpy.data.collections.new(collectionName)
        context.scene.collection.children.link(collection)

    collection.objects.link(cube)
    context.view_layer.active_layer_collection.collection.objects.unlink(cube)


def agentIdUpdate(self, context: bpy.types.Context):

    i, agentDef = findInCollection(context.scene.swarm_settings.agent_definitions, lambda a: a.name == self.agentId)

    if agentDef is None: return

    color = agentDef.color

    # Create a new material and set its base color
    material = bpy.data.materials.new(name=agentDef.name)
    material.use_nodes = True
    bsdf_node = material.node_tree.nodes.get("Principled BSDF")
    if bsdf_node:
        bsdf_node.inputs["Base Color"].default_value = [color[0], color[1], color[2], 1]

    # Assign the material to the cube
    context.active_object.data.materials.append(material)
    
    

def isControlObject(object):
    return object is not None and object.control_settings.useAsControl


def collectControlObjects(context: bpy.types.Context):
    collection = bpy.data.collections.get(collectionName)
    if collection is not None:
        allObjects = collection.objects
    else:
        allObjects = context.scene.objects
    
    controlObjects = filter(lambda o: isControlObject(o), allObjects)

    return groupby(controlObjects, lambda o: o[agentIdPropertyName])
