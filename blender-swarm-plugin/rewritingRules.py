import bpy

#currently unused
class RewritingRule:
    def __init__(self, context: bpy.types.Context):
        self.predecessor = ""
        self.successors = []
        self.hasContext = False

    def checkContext(self) -> bool:
        return False
    
    def isPossible(self) -> bool:
        return False
    