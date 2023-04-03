import mathutils
import bpy

class BoidRule:

    def __init__(self, context: bpy.types.Context):
        self.count = 0
        self.direction = mathutils.Vector()
        self.context = context

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        pass

    def calcDirection(self, agent):
        return self.direction


class Separation(BoidRule):
    def __init__(self, context):
        super().__init__(context)
        self.noClumpRadius = self.context.scene.swarm_settings.agent_general_noClumpRadius

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.noClumpRadius):
            self.direction += other.position - agent.position
            self.count += 1

    def calcDirection(self, agent):
        if(self.count > 0):
            self.direction /= self.count
            self.direction.normalize()
            self.direction.negate()
            self.direction *= self.context.scene.swarm_settings.agent_general_separationWeight
            
        return self.direction


class Alignement(BoidRule):
    def __init__(self, context):
        super().__init__(context)
        self.localAreaRadius = context.scene.swarm_settings.agent_general_localAreaRadius

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.localAreaRadius):
            self.direction += other.forward
            self.count += 1

    def calcDirection(self, agent):
        if(self.count > 0):
            self.direction /= self.count
            self.direction.normalize()
            self.direction *= self.context.scene.swarm_settings.agent_general_alignementWeight
            
        return self.direction


class Cohesion(BoidRule):
    def __init__(self, context):
        super().__init__(context)
        self.localAreaRadius = context.scene.swarm_settings.agent_general_localAreaRadius

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.localAreaRadius):
            self.direction += other.position - agent.position
            self.count += 1

    def calcDirection(self, agent):
        if(self.count > 0):
            self.direction /= self.count
            self.direction.normalize()
            self.direction *= self.context.scene.swarm_settings.agent_general_cohesionWeight
            
        return self.direction


class CenterUrge(BoidRule):
    def __init__(self, context: bpy.types.Context):
        self.center = context.active_object.location
        super().__init__(context)

    def calcDirection(self, agent):
        directionToCenter = self.center - agent.position
        if(directionToCenter.magnitude > self.context.scene.swarm_settings.agent_general_centerMaxDistance):
            directionToCenter.normalize()
            return directionToCenter * self.context.scene.swarm_settings.agent_general_centerUrgeWeight
        return mathutils.Vector()
    

class Leadership(BoidRule):
    def __init__(self, context: bpy.types.Context):
        self.leaderAgent = None
        super().__init__(context)

    def compareWithOther(self, distance: float, angle: float, agent: "Agent", other: "Agent"):
        if(distance < self.localAreaRadius):
            if(angle < self.leaderAngle and angle < 90):
                self.leaderAgent = other;
                self.leaderAngle = angle;

    def calcDirection(self, agent):
        if (self.leaderAgent is not None):
            vecToLeader = self.leaderAgent.position - agent.position
            vecToLeader.normalize()
            return vecToLeader * self.context.scene.swarm_settings.agent_general_leaderWeight;
    
            