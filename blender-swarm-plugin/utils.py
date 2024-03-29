from __future__ import annotations

from typing import Optional

import bpy
import bmesh
import mathutils
import random

from mathutils.bvhtree import BVHTree

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .agentSettings import AgentSettings


def context_override(context: bpy.types.Context):
    for window in context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return {'window': window, 'screen': screen, 'area': area, 'region': region, 'scene': context.scene, "object": context.active_object} 

    return context.copy()

def find3dViewportContext(context: bpy.types.Context):
    for window in context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return window, area, region
    return None, None, None  # Could not find a 3D Viewport context

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


def createBVH(obj: bpy.types.Object) -> BVHTree:
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

    # delete the bmesh, it creates c++ data, that python wont clean up
    bm.free()
    return bvhTree


def findInCollection(prop, when):
    for i, elem in enumerate(prop):
        if when(elem):
            return (i, elem)
    return (None, None)


def copyPropertyGroup(src, target, ignore=[]):
    for prop in src.bl_rna.properties:
        if prop.identifier == "rna_type" or prop.identifier in ignore:
            continue
        setattr(target, prop.identifier, getattr(src, prop.identifier))


def compareAndCopyPropertyGroup(src, target, ignore=[]):
    for prop in src.bl_rna.properties:
        if prop.identifier == "rna_type" or prop.identifier in ignore:
            continue

        if getattr(target, prop.identifier) == getattr(src, prop.identifier):
            continue

        setattr(target, prop.identifier, getattr(src, prop.identifier))


def findAgentDefinition(context: bpy.types.Context, name: str) -> tuple[int, AgentSettings]:
    return findInCollection(context.scene.swarm_settings.agent_definitions, lambda a: a.name == name)


def findClosestPointInBVH(bvhTree: BVHTree, point: mathutils.Vector):
    return tryfindClosestPoint(bvhTree, point)[0]


def tryfindClosestPoint(bvhTree: BVHTree, point: mathutils.Vector) -> tuple[mathutils.Vector, mathutils.Vector, int, float]:
    closestPoint, normal, index, distance = bvhTree.find_nearest(point)

    if closestPoint is None:
        return None

    return (closestPoint, normal, index, distance)


def randomVector(min: float, max: float) -> mathutils.Vector:
    return mathutils.Vector((
        random.uniform(min, max), 
        random.uniform(min, max), 
        random.uniform(min, max)
        ))


def multiRaycast(depsgraph: bpy.types.Depsgraph, origin: mathutils.Vector, target: bpy.types.Object, direction: mathutils.Vector, maxAttempts: int = 1000, distance: float = 1.70141e+38) -> tuple[bool, mathutils.Vector, mathutils.Vector, int, bpy.types.Object, mathutils.Matrix]:

    # Start and end points of the ray in world coordinates
    attempts = 0
    while attempts < maxAttempts:
        result, location, normal, index, hitObj, matrix = bpy.context.scene.ray_cast(
            depsgraph= depsgraph, origin=origin, direction=direction, distance=distance)
        if result:
            if hitObj == target:
                return (result, location, normal, index, hitObj, matrix)
            else:
                hitDistance = (location - origin).length
                distance -= hitDistance
                # Start next raycast from the hit location plus a small offset
                origin = location + direction * 0.0001
        else:
            break  # No hit, exit the loop
        attempts += 1

    return (None, None, None, None, None, None)