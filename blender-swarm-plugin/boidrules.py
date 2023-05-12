import mathutils
import bpy
import bmesh

from mathutils.bvhtree import BVHTree
from .properties import AgentSettings

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent import Agent

class BoidRule:

    def __init__(self, context: bpy.types.Context, agent: "Agent"):
        self.count = 0
        self.direction = mathutils.Vector()
        self.context = context
        self.agent = agent

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        pass

    def calcDirection(self, agent: "Agent"):
        return mathutils.Vector()


class Separation(BoidRule):
    def __init__(self, context, agent: "Agent"):
        super().__init__(context, agent)

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < agent.agentSettings.noClumpRadius):
            self.direction += other.position - agent.position
            self.count += 1

    def calcDirection(self, agent):
        if(self.count <= 0):
            return mathutils.Vector()
        
        self.direction /= self.count
        self.direction.normalize()
        self.direction.negate()
        self.direction *= agent.agentSettings.separationWeight
            
        return self.direction


class Alignement(BoidRule):
    def __init__(self, context, agent: "Agent"):
        super().__init__(context, agent)
        self.localAreaRadius = agent.agentSettings.localAreaRadius

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.localAreaRadius):
            self.direction += other.forward
            self.count += 1

    def calcDirection(self, agent: "Agent"):
        if(self.count <= 0):
            return mathutils.Vector()
        
        self.direction /= self.count
        self.direction.normalize()
        self.direction *= agent.agentSettings.alignementWeight
            
        return self.direction


class Cohesion(BoidRule):
    def __init__(self, context, agent: "Agent"):
        super().__init__(context, agent)
        self.localAreaRadius = agent.agentSettings.localAreaRadius

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.localAreaRadius):
            self.direction += other.position - agent.position
            self.count += 1

    def calcDirection(self, agent: "Agent"):
        if(self.count <= 0):
            return mathutils.Vector()
        
        self.direction /= self.count
        self.direction.normalize()
        self.direction *= agent.agentSettings.cohesionWeight
            
        return self.direction


class CenterUrge(BoidRule):
    def __init__(self, context: bpy.types.Context, agent: "Agent"):
        self.center = context.active_object.location
        super().__init__(context, agent)

    def calcDirection(self, agent: "Agent"):
        directionToCenter = self.center - agent.position
        if(directionToCenter.magnitude > agent.agentSettings.centerMaxDistance):
            directionToCenter.normalize()
            return directionToCenter * agent.agentSettings.centerUrgeWeight
        return mathutils.Vector()
    

class Leadership(BoidRule):
    def __init__(self, context: bpy.types.Context, agent: "Agent"):
        self.leaderAgent = None
        super().__init__(context, agent)

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.localAreaRadius):
            if(angle < self.leaderAngle and angle < 90):
                self.leaderAgent = other;
                self.leaderAngle = angle;

    def calcDirection(self, agent: "Agent"):
        if (self.leaderAgent is None):
            return mathutils.Vector()

        vecToLeader = self.leaderAgent.position - agent.position
        vecToLeader.normalize()
        return vecToLeader * agent.agentSettings.leaderWeight;


class Surface(BoidRule):
    def __init__(self, context: bpy.types.Context, agent: "Agent"):
        self.object = context.active_object
        super().__init__(context, agent)

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        pass

    def calcDirection(self, agent: "Agent"):
        closestPoint = self.findClosestPoint(agent.swarm.bvhTree, agent.swarm.bmesh, agent.position)

        if closestPoint is None:
            return mathutils.Vector()

        dirToClosest = closestPoint - agent.position
        return dirToClosest * agent.agentSettings.surfaceWeight
    
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
    def __init__(self, context: bpy.types.Context, agent: "Agent"):
        super().__init__(context, agent)


    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        pass


    def calcDirection(self, agent: "Agent"):
        dirSum = mathutils.Vector()
        strengthSum = 0
        attractorsInRangeCounter = 0

        for obj in agent.attractors:
            vec = obj.location - agent.position
            dist = vec.magnitude

            if dist < obj.control_settings.attractionRange:
                norm = vec.normalized()

                # only attract if target is in front of agent
                if agent.forward.dot(norm) > 0:
                    dirSum += vec
                    strengthSum += obj.control_settings.strength
                    attractorsInRangeCounter += 1

        count = max(attractorsInRangeCounter, 1)
        dirSum /= count

        strengthSum /= count #average strength
        dirSum *= strengthSum

        return dirSum