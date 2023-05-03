import bpy

from .swarm import Swarm


_swarm: Swarm = None

def startSwarm(context: bpy.types.Context):
    bpy.ops.object.mode_set(mode="SCULPT")
    bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False
    # bpy.context.tool_settings.sculpt.use_dynamic_topology_sculpting = True

    global _swarm 
    _swarm = Swarm(context)


def stopSwarm(context: bpy.types.Context):
    global _swarm
    _swarm.stop()


def isRunning(context: bpy.types.Context):
    global _swarm
    return _swarm is not None and _swarm.isRunning()

