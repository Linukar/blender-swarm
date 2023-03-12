import bpy

from .swarm import Swarm


class SwarmManager:
    _swarm: Swarm = None

    @staticmethod
    def startSwarm(context: bpy.types.Context):
        bpy.ops.object.mode_set(mode="SCULPT")
        bpy.context.scene.tool_settings.sculpt.use_symmetry_x = False
        SwarmManager._swarm = Swarm(context)

    @staticmethod
    def stopSwarm():
        SwarmManager._swarm.stop()

    @staticmethod
    def isRunning():
        return SwarmManager._swarm is not None and SwarmManager._swarm.isRunning()