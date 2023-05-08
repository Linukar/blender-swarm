import mathutils
import bpy
import bmesh

from mathutils.bvhtree import BVHTree
from .properties import AgentSettings

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import Agent

class BoidRule:

    def __init__(self, context: bpy.types.Context, agentSettings: AgentSettings, agent: "Agent"):
        self.count = 0
        self.direction = mathutils.Vector()
        self.context = context
        self.agentSettings = agentSettings
        self.agent = agent

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        pass

    def calcDirection(self, swarm, agent: "Agent"):
        return mathutils.Vector()


class Separation(BoidRule):
    def __init__(self, context, agentSettings: AgentSettings, agent: "Agent"):
        super().__init__(context, agentSettings, agent)
        self.noClumpRadius = agentSettings.noClumpRadius

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.noClumpRadius):
            self.direction += other.position - agent.position
            self.count += 1

    def calcDirection(self, swarm, agent):
        if(self.count <= 0):
            return mathutils.Vector()
        
        self.direction /= self.count
        self.direction.normalize()
        self.direction.negate()
        self.direction *= self.agentSettings.separationWeight
            
        return self.direction


class Alignement(BoidRule):
    def __init__(self, context, agentSettings: AgentSettings, agent: "Agent"):
        super().__init__(context, agentSettings, agent)
        self.localAreaRadius = self.agentSettings.localAreaRadius

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.localAreaRadius):
            self.direction += other.forward
            self.count += 1

    def calcDirection(self, swarm, agent: "Agent"):
        if(self.count <= 0):
            return mathutils.Vector()
        
        self.direction /= self.count
        self.direction.normalize()
        self.direction *= self.agentSettings.alignementWeight
            
        return self.direction


class Cohesion(BoidRule):
    def __init__(self, context, agentSettings: AgentSettings, agent: "Agent"):
        super().__init__(context, agentSettings, agent)
        self.localAreaRadius = self.agentSettings.localAreaRadius

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.localAreaRadius):
            self.direction += other.position - agent.position
            self.count += 1

    def calcDirection(self, swarm, agent: "Agent"):
        if(self.count <= 0):
            return mathutils.Vector()
        
        self.direction /= self.count
        self.direction.normalize()
        self.direction *= self.agentSettings.cohesionWeight
            
        return self.direction


class CenterUrge(BoidRule):
    def __init__(self, context: bpy.types.Context, agentSettings: AgentSettings, agent: "Agent"):
        self.center = context.active_object.location
        super().__init__(context, agentSettings, agent)

    def calcDirection(self, swarm, agent: "Agent"):
        directionToCenter = self.center - agent.position
        if(directionToCenter.magnitude > self.agentSettings.centerMaxDistance):
            directionToCenter.normalize()
            return directionToCenter * self.agentSettings.centerUrgeWeight
        return mathutils.Vector()
    

class Leadership(BoidRule):
    def __init__(self, context: bpy.types.Context, agentSettings: AgentSettings, agent: "Agent"):
        self.leaderAgent = None
        super().__init__(context, agentSettings, agent)

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.localAreaRadius):
            if(angle < self.leaderAngle and angle < 90):
                self.leaderAgent = other;
                self.leaderAngle = angle;

    def calcDirection(self, swarm, agent: "Agent"):
        if (self.leaderAgent is None):
            return mathutils.Vector()

        vecToLeader = self.leaderAgent.position - agent.position
        vecToLeader.normalize()
        return vecToLeader * self.agentSettings.leaderWeight;


class Surface(BoidRule):
    def __init__(self, context: bpy.types.Context, agentSettings: AgentSettings, agent: "Agent"):
        self.object = context.active_object
        super().__init__(context, agentSettings, agent)

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        pass

    def calcDirection(self, swarm, agent: "Agent"):
        closestPoint = self.findClosestPoint(swarm.bvhTree, swarm.bmesh, agent.position)

        if closestPoint is None:
            return mathutils.Vector()

        dirToClosest = closestPoint - agent.position
        return dirToClosest * self.agentSettings.surfaceWeight
    
    def findClosestPoint(self, bvhTree: BVHTree, bmesh: bmesh.types.BMesh , point: mathutils.Vector):
        closestPoint, _, __, ___ = bvhTree.find_nearest(point)

        # If no nearest point is found, return None
        if closestPoint is None:
            bmesh.free()
            return None

        # Return the closest point
        bmesh.free()
        return closestPoint


class ControlObjectAttraction(BoidRule):
    def __init__(self, context: bpy.types.Context, agentSettings: AgentSettings, agent: "Agent"):
        super().__init__(context, agentSettings, agent)
        self.relevantObjects = [obj for obj in agent.controlObjects if obj.control_settings.type in ("Attractor", "Transformer")]


    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        pass

    def calcDirection(self, swarm, agent: "Agent"):
        dir = mathutils.Vector()
        for obj in self.relevantObjects:
            dir += obj.location - agent.position

        dir /= max(len(self.relevantObjects), 1)

        return dir