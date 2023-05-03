import bpy


class ReproductionRule:
    def __init__(self, context: bpy.types.Context):
        self.predecessor = ""
        self.hasContext = False

    def checkContext(self) -> bool:
        return False