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
        # utils.operator("swarm.remove_selected", text = "Remove selected Object")
        # utils.operator("object.delete_all")
        utils.operator("swarm.spawn_plane", text = "Spawn Plane")


        col.label(text="General")
        general = col.box()
        general.operator("swarm.start_simulation", text = "Begin Simulation")
        # col.operator("swarm.modal_simulation", text = "Modal Simulation")
        general.operator("swarm.pause_simulation", text = "Pause/Resume Simulation")
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

        if context.scene.selected_preset != "":

            presetBox.operator("swarm.save_preset", text="Save")

            presetBox.separator()

            presetBox.label(text="General Swarm Settings")
            swarmSettings = presetBox.box()
            swarmSettings.prop(context.scene.swarm_settings, "name")
            seedRow = swarmSettings.row()
            seedRow.prop(context.scene.swarm_settings, "seed", text="Seed")
            seedRow.operator("swarm.new_seed", text="New Seed")

            # swarmSettings.prop(context.scene.swarm_settings, "agentCount", text="Agent Count")
            # swarmSettings.prop(context.scene.swarm_settings, "swarmCount", text="Swarm Count")
            # swarmSettings.prop(context.scene.swarm_settings, "spawnAreaSize", text="Spawn Area")
            swarmSettings.prop(context.scene.swarm_settings, "maxSimulationSteps", text="Simulation Steps")
            swarmSettings.prop(context.scene.swarm_settings, "visualizeAgents", text="Visualize Agents")
            swarmSettings.prop(context.scene.swarm_settings, "useSculpting", text="use Sculpting")
            swarmSettings.prop(context.scene.swarm_settings, "randomStartLocation", text="Random Start Location")
            swarmSettings.prop(context.scene.swarm_settings, "randomStartXYRotation", text="Random Start XY Rotation")
            swarmSettings.prop(context.scene.swarm_settings, "randomStartZRotation", text="Random Start Z Rotation")

            dyntypoBox = swarmSettings.box()
            dyntypoBox.prop(context.scene.swarm_settings, "useDyntypo", text="Use Dyntypo")
            if context.scene.swarm_settings.useDyntypo:
                dyntypoBox.prop(context.scene.swarm_settings, "dyntypoResolution", text="Resolution")

            swarmSettings.prop(context.scene.swarm_settings, "enableSurfaceAwareness", text="Enable Surface Awareness")


            presetBox.separator()

            presetBox.label(text="Agent Behaviour Settings")
            agentSettings = presetBox.box()
            agentSettings.prop(context.scene, "selected_agent")

            agentRow = agentSettings.row()
            agentRow.operator("swarm.add_agent_type", text="+")
            agentRow.operator("swarm.remove_agent_type", text="-")

            if context.scene.selected_agent != "":
                agentSettings.operator("swarm.save_agent", text="Save")
                agentSettings.prop(context.scene.current_agent_settings, "name", text="Name")
                agentSettings.prop(context.scene.current_agent_settings, "color", text="Color")
                agentSettings.prop(context.scene.current_agent_settings, "energy", text="Energy")
                agentSettings.prop(context.scene.current_agent_settings, "applyAtEnd", text="Apply at End")

                toolBox = agentSettings.box()
                toolBox.label(text="Tool Settings")
                toolBox.prop(context.scene.current_agent_settings, "tool", text="Tool")
                toolBox.prop(context.scene.current_agent_settings, "toolRadius", text="Radius")
                toolBox.prop(context.scene.current_agent_settings, "toolStrength", text="Strength")
                toolBox.prop(context.scene.current_agent_settings, "toolMode", text="Mode")
                toolBox.prop(context.scene.current_agent_settings, "toolIgnoreBackground", text="Ignore Non-Surface")

                boidBox = agentSettings.box()
                boidBox.label(text="Boid Settings")
                boidBox.prop(context.scene.current_agent_settings, "speed", text="Agent Speed")
                boidBox.prop(context.scene.current_agent_settings, "steeringSpeed", text="Agent Steering Speed")
                boidBox.prop(context.scene.current_agent_settings, "localAreaRadius", text="Neighbour Radius")
                boidBox.prop(context.scene.current_agent_settings, "cohesionWeight", text="Cohesion Weight")
                boidBox.prop(context.scene.current_agent_settings, "alignementWeight", text="Alignement Weight")
                boidBox.prop(context.scene.current_agent_settings, "noClumpRadius", text="Separation Radius")
                boidBox.prop(context.scene.current_agent_settings, "separationWeight", text="Separation Weight")
                # agentSettings.prop(context.scene.current_agent_settings, "leaderWeight", text="Leader Weight")
                boidBox.prop(context.scene.current_agent_settings, "centerUrgeWeight", text="Center Weight")
                boidBox.prop(context.scene.current_agent_settings, "centerMaxDistance", text="Max Distance to Center")
                if context.scene.swarm_settings.enableSurfaceAwareness:
                    boidBox.prop(context.scene.current_agent_settings, "surfaceWeight", text="Surface Urge")
                    boidBox.prop(context.scene.current_agent_settings, "snapToSurface", text="Snap to Surface")

        col.separator()

        controlObjectBox = col.box()

        controlObjectBox.label(text="Control Object Settings")
        controlObjectBox.operator("swarm.add_control_object", text="Add Control Object")

        if isControlObject(context.active_object):
            controlObjectBox.prop(context.active_object.control_settings, "type", text="Type")
            controlObjectBox.prop(context.active_object.control_settings, "agentId", text="Agent")

            if context.active_object.control_settings.type in ["Replicator", "Attractor", "Deflector", "Splitter"]:
                controlObjectBox.prop(context.active_object.control_settings, "strength", text="Strength")
                controlObjectBox.prop(context.active_object.control_settings, "attractionRange", text="Attraction Range")


            if context.active_object.control_settings.type == "Replicator":
                resultRow = controlObjectBox.row()
                resultRow.prop(context.active_object.control_settings, "replacementCount", text="Num")
                resultRow.prop(context.active_object.control_settings, "replacementResult", text="Result")
                controlObjectBox.prop(context.active_object.control_settings, "replacementRange", text="Replacement Range")

            if context.active_object.control_settings.type == "Spawner":
                controlObjectBox.prop(context.active_object.control_settings, "spawnOnStart", text="Spawn on Start")
                controlObjectBox.prop(context.active_object.control_settings, "spawnerOffset", text="Offset")
                controlObjectBox.prop(context.active_object.control_settings, "spawnerFrequency", text="Frequency")
                controlObjectBox.prop(context.active_object.control_settings, "spawnerAmount", text="Amount")
                controlObjectBox.prop(context.active_object.control_settings, "spawnerLimit", text="Limit")
