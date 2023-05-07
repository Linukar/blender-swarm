import bpy

from .utils import findInCollection


coTypes = ["Spawner", "Attractor", "Repulsor", "Transformer", "Splitter"]


def addControlObject(context: bpy.types.Context):
    # Add a cube to the scene at the origin
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cube = context.active_object

    # Add custom properties
    cube["controlType"] = coTypes[0]
    cube["agentId"] = coTypes[0]

    item = context.scene.control_objects.add()
    item.object = cube


def propertyUpdate(context: bpy.types.Context, propName: str, propValue):
    if not pollControlObject(context):
        return

    context.active_object[propName] = propValue

    i, agentDef = findInCollection(context.scene.swarm_settings.agent_definitions, lambda a: a.name == context.active_object["agentId"])

    if agentDef is None: return

    color = agentDef.color

    # Create a new material and set its base color
    material = bpy.data.materials.new(name="ControlObjectMaterial")
    material.use_nodes = True
    bsdf_node = material.node_tree.nodes.get("Principled BSDF")
    if bsdf_node:
        bsdf_node.inputs["Base Color"].default_value = [color[0], color[1], color[2], 1]

    # Assign the material to the cube
    context.active_object.data.materials.append(material)
    


def pollControlObject(context: bpy.types.Context):
    return context.active_object is not None and "controlType" in context.active_object