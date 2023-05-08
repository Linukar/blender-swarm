import bpy
import bmesh
import mathutils

from mathutils.bvhtree import BVHTree


def context_override(context: bpy.types.Context):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return {'window': window, 'screen': screen, 'area': area, 'region': region, 'scene': context.scene, "object": context.active_object} 

    return context.copy()


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


def clamp(value, lower, upper):
    return lower if value < lower else upper if value > upper else value


def createBVH(obj: bpy.types.Object) -> tuple[BVHTree, bmesh.types.BMesh]:
    # Ensure object has a mesh
    if not isinstance(obj.data, bpy.types.Mesh):
        raise ValueError("Object must have a mesh")

    # Create a bmesh from the object's mesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(obj.matrix_world)
    bm.faces.ensure_lookup_table()

    # Build a BVH tree from the bmesh
    bvhTree = BVHTree.FromBMesh(bm)
    return bvhTree, bm


def findInCollection(prop, when):
    for i, elem in enumerate(prop):
        if when(elem):
            return (i, elem)
    return None


def copyPropertyGroup(src, target, ignore=[]):
    for prop in src.bl_rna.properties:
        if prop.identifier == "rna_type" or prop.identifier in ignore:
            continue
        setattr(target, prop.identifier, getattr(src, prop.identifier))