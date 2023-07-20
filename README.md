# blender.swarm

# A Blender Plugin for Sculpting with Swarm Grammars

# Installation

- pack the blender-swarm-plugin folder into a .zip
- in Blender go to Preferences->Addons->Install and select .zip


# How-To-Use
There is a new Panel on the right side of the viewport called Swarm Generator, all the settings are here

On the top there are general utilities and settings of the entire swarm. Most stuff is not explained, so good luck.
In the agent behaviour settings section agent types can be defined. The parameters below the agent dropdown belong to the selected agent. Agent types can be added, removed and cloned by the buttons below the dropdown. In the agents settings, the agents boid urges and sculpting tools can be defined.

On the bottom there are the control object settings. Press the button "add control object" to add a control object to the scene. It can be moved rotated and scaled like any other blender object, but doing anything else to it could result in unexpected behaviour. Selected the added control object to edit its internal parameters. To start the swarm there has to be at least one "Spawner" type control object. 

To start the simulation, select a mesh object, that is not a control object and press "Begin Simulation"
