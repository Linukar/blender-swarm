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

        col.label(text="Utils")
        utils = col.box()
        utils.operator("swarm.remove_selected", text = "Remove selected Object")
        utils.operator("object.delete_all")
        utils.operator("swarm.spawn_plane", text = "Spawn Plane")

        col.label(text="Presets")
        presetBox = col.box()
        importRow = presetBox.row()
        importRow.operator("swarm.import_presets", text="Import")
        importRow.operator("swarm.export_presets", text="Export")

        presetBox.prop(context.scene, "selected_preset")
        presetRow = presetBox.row()
        presetRow.operator("swarm.add_preset", text="+")
        presetRow.operator("swarm.remove_preset", text="-")
        presetBox.operator("swarm.save_preset", text="Save")



        col.label(text="General")
        general = col.box()
        general.operator("swarm.start_simulation", text = "Begin Simulation")
        # col.operator("swarm.modal_simulation", text = "Modal Simulation")
        general.operator("swarm.stop_simulation", text = "Stop Simulation")

        col.label(text="General Swarm Settings")
        swarmSettings = col.box()
        swarmSettings.prop(context.scene.swarm_settings, "name")
        seedRow = swarmSettings.row()
        seedRow.prop(context.scene.swarm_settings, "swarm_seed", text="Seed")
        seedRow.operator("swarm.new_seed", text="New Seed")

        swarmSettings.prop(context.scene.swarm_settings, "swarm_agentCount", text="Agent Count")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_swarmCount", text="Swarm Count")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_spawnAreaSize", text="Spawn Area")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_maxSimulationSteps", text="Simulation Steps")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_visualizeAgents", text="Visualize Agents")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_useSculpting", text="use Sculpting")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_randomStartLocation", text="Random Start Location")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_randomStartXYRotation", text="Random Start XY Rotation")
        swarmSettings.prop(context.scene.swarm_settings, "swarm_randomStartZRotation", text="Random Start Z Rotation")


        
        col.label(text="Agent Behaviour Settings")
        agentSettings = col.box()
        agentSettings.prop(context.scene.swarm_settings, "agent_general_tool", text="Tool to use")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_noClumpRadius", text="Separation Radius")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_localAreaRadius", text="Neighbour Radius")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_speed", text="Agent Speed")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_steeringSpeed", text="Agent Steering Speed")

        agentSettings.prop(context.scene.swarm_settings, "agent_general_separationWeight", text="Separation Weight")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_alignementWeight", text="Alignement Weight")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_cohesionWeight", text="Cohesion Weight")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_leaderWeight", text="Leader Weight")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_centerUrgeWeight", text="Center Weight")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_centerMaxDistance", text="Max Distance to Center")
        agentSettings.prop(context.scene.swarm_settings, "agent_general_surfaceWeight", text="Surface Urge")


