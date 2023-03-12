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
    "name" : "SwarmTest",
    "author" : "Me",
    "description" : "",
    "blender" : (3, 3, 2),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Object"
}

import bpy
from .buttons import Swarm_OT_Sculpt_Test, Swarm_OT_Spawn_Plane, Swarm_OT_Remove_Selected, Swarm_OT_Stop_Simulation
from .panel import SWARM_PT_Panel
from .properties import SwarmSettings, registerProperties, unregisterProperies

classes = (Swarm_OT_Sculpt_Test, Swarm_OT_Spawn_Plane, Swarm_OT_Remove_Selected, Swarm_OT_Stop_Simulation,
            SWARM_PT_Panel, SwarmSettings)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    
    registerProperties()

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    
    unregisterProperies()
