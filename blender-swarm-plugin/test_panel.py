import bpy

from bpy.types import Panel

class Test_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Test Panel"
    bl_category = "Test Util"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.operator("object.cancel_all_mods", text = "Cancel All")
        col.operator("object.place_agent", text = "Place Agent")