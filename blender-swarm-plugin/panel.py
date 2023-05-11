import bpy

from bpy.types import Panel
from .controlObjects import isControlObject

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


        col.label(text="General")
        general = col.box()
        general.operator("swarm.start_simulation", text = "Begin Simulation")
        # col.operator("swarm.modal_simulation", text = "Modal Simulation")
        general.operator("swarm.stop_simulation", text = "Stop Simulation")


        col.label(text="Presets")
        presetBox = col.box()
        presetIOBox = presetBox.box()
        importRow = presetIOBox.row()
        importRow.operator("swarm.import_presets", text="Import")
        importRow.operator("swarm.export_presets", text="Export")

        presetBox.prop(context.scene, "selected_preset")
        presetRow = presetBox.row()
        presetRow.operator("swarm.add_preset", text="+")
        presetRow.operator("swarm.remove_preset", text="-")
        presetBox.operator("swarm.save_preset", text="Save")

        presetBox.separator()

        presetBox.label(text="General Swarm Settings")
        swarmSettings = presetBox.box()
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

        presetBox.separator()

        presetBox.label(text="Agent Behaviour Settings")
        agentSettings = presetBox.box()
        agentSettings.prop(context.scene, "selected_agent")
        agentRow = agentSettings.row()
        agentRow.operator("swarm.add_agent_type", text="+")
        agentRow.operator("swarm.remove_agent_type", text="-")
        agentSettings.operator("swarm.save_agent", text="Save")

        agentSettings.prop(context.scene.current_agent_settings, "name", text="Name")
        agentSettings.prop(context.scene.current_agent_settings, "color", text="Color")
        agentSettings.prop(context.scene.current_agent_settings, "tool", text="Tool to use")
        agentSettings.prop(context.scene.current_agent_settings, "noClumpRadius", text="Separation Radius")
        agentSettings.prop(context.scene.current_agent_settings, "localAreaRadius", text="Neighbour Radius")
        agentSettings.prop(context.scene.current_agent_settings, "speed", text="Agent Speed")
        agentSettings.prop(context.scene.current_agent_settings, "steeringSpeed", text="Agent Steering Speed")
        agentSettings.prop(context.scene.current_agent_settings, "separationWeight", text="Separation Weight")
        agentSettings.prop(context.scene.current_agent_settings, "alignementWeight", text="Alignement Weight")
        agentSettings.prop(context.scene.current_agent_settings, "cohesionWeight", text="Cohesion Weight")
        agentSettings.prop(context.scene.current_agent_settings, "leaderWeight", text="Leader Weight")
        agentSettings.prop(context.scene.current_agent_settings, "centerUrgeWeight", text="Center Weight")
        agentSettings.prop(context.scene.current_agent_settings, "centerMaxDistance", text="Max Distance to Center")
        agentSettings.prop(context.scene.current_agent_settings, "surfaceWeight", text="Surface Urge")

        col.separator()

        controlObjectBox = col.box()

        controlObjectBox.label(text="Control Object Settings")
        controlObjectBox.operator("swarm.add_control_object", text="Add Control Object")

        if isControlObject(context.active_object):
            controlObjectBox.prop(context.active_object.control_settings, "type", text="Type")
            controlObjectBox.prop(context.active_object.control_settings, "agentId", text="Agent")
            controlObjectBox.prop(context.active_object.control_settings, "radius", text="Radius")

            if context.active_object.control_settings.type in ["Transformer", "Attractor", "Repulsor", "Splitter"]:
                controlObjectBox.prop(context.active_object.control_settings, "strength", text="Strength")


            if context.active_object.control_settings.type == "Transformer":
                controlObjectBox.prop(context.active_object.control_settings, "transformerResult", text="Result")
                



