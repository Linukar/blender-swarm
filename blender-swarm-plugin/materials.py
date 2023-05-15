import bpy

from .utils import findAgentDefinition

materialNameIdentifier = "swarm_m_"
replaceMaterialName = "swarm_rm_"

def updateControlObjectMaterial(obj: bpy.types.Object, context: bpy.types.Context):
    coSettings = obj.control_settings
    i, agentDef = findAgentDefinition(context, coSettings.agentId)

    if agentDef is None: return

    color = agentDef.color

    if coSettings.type != "Transformer":

        existingMat = bpy.data.materials.get(materialNameIdentifier + agentDef.name)

        if existingMat is None:
            existingMat = bpy.data.materials.new(name=materialNameIdentifier + agentDef.name)
            existingMat.use_nodes = True
            bsdf_node = existingMat.node_tree.nodes.get("Principled BSDF")
            if bsdf_node:
                bsdf_node.inputs["Base Color"].default_value = [color[0], color[1], color[2], 1]

    else:
        i, agentReplacement = findAgentDefinition(context, coSettings.replacementResult)
        matName = replaceMaterialName + agentDef.name + "_" + agentReplacement.name
        existingMat = bpy.data.materials.get(matName)

        if existingMat is None:
            existingMat = createTwoColorMat(matName, agentDef.color, agentReplacement.color)

        setColorsOfTwoColorMat(existingMat, agentDef.color, agentReplacement.color)


    obj.data.materials.clear()
    obj.data.materials.append(existingMat)


color1BSDFName = "Diffuse1"
color2BSDFName = "Diffuse2"

def createTwoColorMat(name, color1, color2):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    while(nodes): nodes.remove(nodes[0])

    output = nodes.new(type='ShaderNodeOutputMaterial')
    mix_shader = nodes.new(type='ShaderNodeMixShader')
    diffuse1 = nodes.new(type='ShaderNodeBsdfPrincipled')
    diffuse1.name = color1BSDFName
    diffuse2 = nodes.new(type='ShaderNodeBsdfPrincipled')
    diffuse2.name = color2BSDFName
    texture_coord = nodes.new(type='ShaderNodeTexCoord')
    separate_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
    math_node = nodes.new(type='ShaderNodeMath')

    output.location = (400,0)
    mix_shader.location = (200,0)
    diffuse1.location = (0,100)
    diffuse2.location = (0,-100)
    texture_coord.location = (-400,0)
    separate_xyz.location = (-200,0)
    math_node.location = (-100, 0)

    diffuse1.inputs['Base Color'].default_value = color1
    diffuse2.inputs['Base Color'].default_value = color2

    math_node.operation = 'GREATER_THAN'
    math_node.inputs[1].default_value = 0.0

    links.new(texture_coord.outputs['Object'], separate_xyz.inputs['Vector'])
    links.new(separate_xyz.outputs['X'], math_node.inputs[0])
    links.new(math_node.outputs['Value'], mix_shader.inputs[0])
    links.new(diffuse1.outputs['BSDF'], mix_shader.inputs[1])
    links.new(diffuse2.outputs['BSDF'], mix_shader.inputs[2])
    links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])

    return mat


def setColorsOfTwoColorMat(mat, color1, color2):

    if mat is not None and mat.use_nodes:
        nodes = mat.node_tree.nodes

        # Get the Principled BSDF nodes
        diffuse1 = nodes.get(color1BSDFName)
        diffuse2 = nodes.get(color2BSDFName)

        if diffuse1 and diffuse2:
            diffuse1.inputs['Base Color'].default_value = color1
            diffuse2.inputs['Base Color'].default_value = color2