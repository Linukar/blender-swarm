import bpy

from .swarm import Swarm


_swarm: Swarm = None

def startSwarm(context: bpy.types.Context):
    bpy.ops.object.mode_set(mode="SCULPT")
    bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False

    if context.scene.swarm_settings.useDyntypo:
        if not context.active_object.use_dynamic_topology_sculpting:
            bpy.ops.sculpt.dynamic_topology_toggle()
        bpy.context.scene.tool_settings.sculpt.detail_size = context.scene.swarm_settings.dyntypoResolution

    global _swarm 
    _swarm = Swarm(context)


def stopSwarm(context: bpy.types.Context):
    global _swarm
    _swarm.stop()

def pauseSwarm(context: bpy.types.Context):
    global _swarm
    _swarm.pause()


def isRunning(context: bpy.types.Context):
    global _swarm
    return _swarm is not None and _swarm.isRunning()

