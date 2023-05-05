import bpy


coTypes = ["Spawner", "Attractor", "Repulsor", "Transformer"]
agentIds = ["All", "A", "B", "C", "D", "E"]

def addControlObject(context: bpy.types.Context):
    # Add a cube to the scene at the origin
    bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cube = context.active_object

    # Add custom properties
    cube["controlType"] = coTypes[0]
    cube["agentId"] = coTypes[0]
    cube["color"] = "FFFFFF"

    # Create a new material and set its base color
    material = bpy.data.materials.new(name="ControlObjectMaterial")
    material.use_nodes = True
    bsdf_node = material.node_tree.nodes.get("Principled BSDF")
    if bsdf_node:
        bsdf_node.inputs["Base Color"].default_value = tuple(int(cube["color"][i:i+2], 16) / 255 for i in (0, 2, 4)) + (1,)

    # Assign the material to the cube
    cube.data.materials.append(material)

    context.scene.control_objects.add().id_data = cube