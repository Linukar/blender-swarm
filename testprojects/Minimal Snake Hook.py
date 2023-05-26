import bpy
import mathutils
import time
import bpy_extras


def find3dViewportContext(context: bpy.types.Context):
    for window in context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return window, area, region
    return None, None, None


area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
region = next(region for region in area.regions if region.type == 'WINDOW')
space_data = next(space for space in area.spaces if space.type == 'VIEW_3D')

stroke = []

for i in range(100):
    pos = mathutils.Vector((0, 0, i/10))
    mouse = bpy_extras.view3d_utils.location_3d_to_region_2d(region, space_data.region_3d, pos)
    strokeElem = {
        "name": "stroke",
        "is_start": True if i == 0 else False,
        "location": pos,
        "mouse": mouse,
        "mouse_event": mouse,
        "pen_flip": False,
        "pressure": 1,
        "size": 1,
        "time": time.time(),
        "x_tilt": 0,
        "y_tilt": 0 
    }
    stroke.append(strokeElem)


bpy.ops.paint.brush_select(sculpt_tool = "DRAW", toggle = False)

window, area, region = find3dViewportContext(bpy.context)

if window and area and region:
    with bpy.context.temp_override(
        window=window,
        area=area,
        region=region, 
        scene=bpy.context.scene, 
        object=bpy.context.active_object):
            bpy.ops.sculpt.brush_stroke(
                stroke=stroke, 
                mode="NORMAL", 
                ignore_background_click=False)
            pass
        