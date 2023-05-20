# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Swarm",
    "author" : "Me",
    "description" : "",
    "blender" : (3, 3, 2),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Object"
}

__package__ = "blender-swarm-plugin"

import bpy
from bpy.app.handlers import persistent
from .operators import *
from .panel import SWARM_PT_Panel
from .properties import SwarmSettings, AgentSettings, initProperties, deinitProperies, setPresetAsCurrent
from .controlObjects import ControlObjectSettings
from .presets import SwarmPresets

classes = (Swarm_OT_Start_Simulation, 
           Swarm_OT_Spawn_Plane, 
           Swarm_OT_Remove_Selected, 
           Swarm_OT_DeleteAll, 
           Swarm_OT_Stop_Simulation, 
           Swarm_OT_Pause_Simulation,
           Swarm_OT_Start_Modal_Simulation, 
           Swarm_OT_NewSeed, 
           SWARM_OT_ExportPresets,
           SWARM_OT_ImportPresets,
           SWARM_OT_AddPreset,
           SWARM_OT_RemovePreset,
           SWARM_OT_SavePreset,
           SWARM_OT_AddControlObject,
           SWARM_OT_AddAgentType,
           SWARM_OT_RemoveAgentType,
           SWARM_OT_SaveAgent,

           SWARM_PT_Panel, 
           AgentSettings, SwarmSettings, ControlObjectSettings,
           SwarmPresets)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    initProperties()
    bpy.app.handlers.load_post.append(init)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    
    deinitProperies()

@persistent
def init(dummy):
    presets = bpy.context.scene.swarm_presets
    if not presets.presets:
        new = presets.presets.add()
        new.agent_definitions.add()
        setPresetAsCurrent(new, bpy.context)
