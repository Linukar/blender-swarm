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
        col.operator("swarm.remove_selected", text = "Remove selected Object")
        col.operator("swarm.spawn_plane", text = "Spawn Plane")
        col.operator("swarm.test1", text = "Begin Simulation")
        col.operator("swarm.stop_simulation", text = "Stop Simulation")

        col.label(text="General Swarm Settings")
        swarmSettings = col.box()
        swarmSettings.prop(context.scene.swarm_settings, "swarm_agentCount", text="Agent Count")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_spawnAreaSize", text="Spawn Area")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_maxSimulationSteps", text="Simulation Steps")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_visualizeAgents", text="Visualize Agents")
        
        col.label(text="Agent Behaviour Settings")
        agentSettings = col.box()
        agentSettings.prop(context.scene.swarm_settings, "agent_general_noClumpRadius", text="Separation Radius")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_localAreaRadius", text="Neighbour Radius")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_speed", text="Agent Speed")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_steeringSpeed", text="Agent Steering Speed")
