import bpy
import mathutils

from .utils import context_override

def testPrint():
    print("test")

class Agent():

    def __init__(self):
        self.position = mathutils.Vector((0, 0, 0))

    def update(self):
        self.position = mathutils.Vector((self.position.x, self.position.y + 0.04, self.position.z))    

        stroke = []

        for i in range (2):
            stroke.append({
                "name": "stroke",
                "is_start": i == 0,
                "location": (self.position.x, self.position.y + i * 0.2, self.position.z),
                "mouse": (0,0),
                "mouse_event": (0.0, 0.0),
                "pen_flip" : True,
                "pressure": 1,
                "size": 2,
                "time": 1,
                "x_tilt": 0,
                "y_tilt": 0
            })

        bpy.ops.paint.brush_select(sculpt_tool="DRAW", toggle=False)

        bpy.ops.sculpt.brush_stroke(context_override(), stroke=stroke)
