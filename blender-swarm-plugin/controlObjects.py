import bpy

from itertools import groupby

from .utils import findInCollection
from .agentSettings import findAgentDefinition


coTypes = ["Spawner", "Attractor", "Repulsor", "Transformer", "Splitter"]
collectionName = "SwarmControlObjects"

materialNameIdentifier = "swarm_m_"
replaceMaterialName = "swarm_rm_"
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


def typeUpdate(self, context: bpy.types.Context):

    # if self.type == "Transformer":
    #     existingMat = bpy.data.materials.get(materialNameIdentifier + agentDef.name)

    setObjectName(self, context)

def agentIdUpdate(self, context: bpy.types.Context):

    i, agentDef = findAgentDefinition(context, self.agentId)

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
    

def setMaterial(self, context):
    i, agentDef = findInCollection(context.scene.swarm_settings.agent_definitions, lambda a: a.name == self.agentId)

    if agentDef is None: return

    color = agentDef.color

    if self.type != "Transformer":

        existingMat = bpy.data.materials.get(materialNameIdentifier + agentDef.name)

        if existingMat is None:
            existingMat = bpy.data.materials.new(name=materialNameIdentifier + agentDef.name)
            existingMat.use_nodes = True
            bsdf_node = existingMat.node_tree.nodes.get("Principled BSDF")
            if bsdf_node:
                bsdf_node.inputs["Base Color"].default_value = [color[0], color[1], color[2], 1]

    # else:
        # replacementResult = 
        # existingMat = bpy.data.materials.get(replaceMaterialName + agentDef.name + self.)

        # if existingMat is None:
        #     existingMat = twoColorMat(replaceMaterialName + agentDef.name)
        #     existingMat.use_nodes = True
        #     bsdf_node = existingMat.node_tree.nodes.get("Principled BSDF")
        #     if bsdf_node:
        #         bsdf_node.inputs["Base Color"].default_value = [color[0], color[1], color[2], 1]


    context.active_object.data.materials.clear()
    context.active_object.data.materials.append(existingMat)

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


def twoColorMat(name, color1, color2):
    # Create a new material
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear all nodes to start clean
    while(nodes): nodes.remove(nodes[0])

    # Create necessary nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    mix_shader = nodes.new(type='ShaderNodeMixShader')
    diffuse1 = nodes.new(type='ShaderNodeBsdfPrincipled')
    diffuse2 = nodes.new(type='ShaderNodeBsdfPrincipled')
    geometry = nodes.new(type='ShaderNodeNewGeometry')
    separate_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    math_node = nodes.new(type='ShaderNodeMath')

    # Set node positions to make it more organized
    output.location = (400,0)
    mix_shader.location = (200,0)
    diffuse1.location = (0,100)
    diffuse2.location = (0,-100)
    geometry.location = (-400,0)
    separate_xyz.location = (-200,0)
    math_node.location = (-100, 0)

    # Set the colors for the diffuse shaders
    diffuse1.inputs['Base Color'].default_value = color1
    diffuse2.inputs['Base Color'].default_value = color2

    # Set the operation of the Math node to "Greater Than"
    math_node.operation = 'GREATER_THAN'
    math_node.inputs[1].default_value = 0.0

    # Link the nodes together
    links.new(geometry.outputs['Position'], separate_xyz.inputs['Vector'])
    links.new(separate_xyz.outputs['X'], math_node.inputs[0])
    links.new(math_node.outputs['Value'], mix_shader.inputs[0])
    links.new(diffuse1.outputs['BSDF'], mix_shader.inputs[1])
    links.new(diffuse2.outputs['BSDF'], mix_shader.inputs[2])
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])

    return mat
