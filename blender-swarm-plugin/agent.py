import bpy
import mathutils

from .utils import context_override

def testPrint():
    print("test")

class Agent():

    def __init__(self):
        self.position = mathutils.Vector((0, 0, 0))

    def update(self):
        self.position = mathutils.Vector((self.position.x, self.position.y, self.position.z + 0.2))    

        stroke = [{
                "name": "stroke",
                "is_start": True,
                "location": self.position,
                "mouse": (0,0),
                "mouse_event": (0.0, 0.0),
                "pen_flip" : True,
                "pressure": 1,
                "size": 5,
                "time": 1,
                "x_tilt": 0,
                "y_tilt": 0
            }]

        print(str(self.position))

        bpy.ops.paint.brush_select(sculpt_tool="DRAW", toggle=False)
        bpy.ops.sculpt.brush_stroke(context_override(), stroke=stroke)
