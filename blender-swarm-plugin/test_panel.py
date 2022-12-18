import bpy

from bpy.types import Panel

class SWARM_PT_Panel(Panel):
    bl_idname = "SWARM_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Swarm Generator"
    bl_category = "Swarm Generator"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.operator("object.cancel_all_mods", text = "Button1")
        col.operator("object.place_agent", text = "Button2")