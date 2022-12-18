import bpy
import mathutils

def testPrint():
    print("test")

class Agent():

    def __init__(self):
        bpy.app.handlers.frame_change_pre.append(testPrint)
        self.empty = bpy.data.objects.new("TestAgent", None)
        self.position = mathutils.Vector((0, 0, 0))
        print("init")

    def updateLocation(self):
        # self.position = mathutils.Vector((self.position.x, self.position.y, self.position.z + 0.2))    
        # self.empty.location = self.position
        print("update")