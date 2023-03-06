import math
from random import randrange
import bpy
import mathutils

from .utils import context_override
from .DrawPoint import drawPoint


def testPrint():
    print("test")


class Agent():

    def __init__(self, sculptTool):
        self.position = mathutils.Vector((0, 0, 0.2))
        self.forward = mathutils.Vector((1, 0, 0))
        eul = mathutils.Euler((0, 0, math.radians(randrange(0, 360))))
        self.forward.rotate(eul)
        self.sculpt_tool = sculptTool
        args = (self.position, (0.99, 0.05, 0.29))
        self.handler = bpy.types.SpaceView3D.draw_handler_add(drawPoint, args, 'WINDOW', 'POST_VIEW')

    def update(self, step: int):

        self.position += self.forward * step * 0.001

        stroke = [{
                "name": "stroke",
                "is_start": True,
                "location": self.position,
                "mouse": (0, 0),
                "mouse_event": (0.0, 0.0),
                "pen_flip": True,
                "pressure": 1,
                "size": 2,
                "time": 1,
                "x_tilt": 0,
                "y_tilt": 0
            }]

        bpy.ops.paint.brush_select(sculpt_tool = self.sculpt_tool, toggle = False)

        bpy.ops.sculpt.brush_stroke(context_override(), stroke = stroke, mode = "INVERT", ignore_background_click = False)

    def onStop(self):
        bpy.types.SpaceView3D.draw_handler_remove(self.handler)
