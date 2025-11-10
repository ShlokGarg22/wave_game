"""
Death Circuit - AI Behavior System
Handles intelligent enemy decision-making, pathfinding, and combat tactics
"""

import pygame
import math
import random
from typing import List, Tuple, Optional, Dict, Any
from utils import distance, angle_to, normalize_vector, vector_from_angle, predict_intercept, wrap_angle, line_of_sight
from collision import CollisionManager
import config


class AIState:
    """AI state enumeration"""
    PATROL = 0
    CHASE = 1
    ATTACK = 2
    RETREAT = 3
    DODGE = 4
    DEAD = 5


class AIDecision:
    """AI decision structure"""
    def __init__(self):
        self.state = AIState.PATROL
        self.target_pos = None
        self.should_fire = False
        self.move_direction = (0.0, 0.0)
        self.look_direction = 0.0
        self.priority = 0


class AIBehavior:
    """Base AI behavior class"""
    
    def __init__(self, entity, collision_manager: CollisionManager):
        self.entity = entity
        self.collision_manager = collision_manager
        self.state = AIState.PATROL
        self.target_player = None
        self.last_seen_player_pos = None
        self.last_seen_time = 0
        self.state_timer = 0
        self.decision_cooldown = 0
        self.pathfinding_target = None
        self.pathfinding_path = []
        self.dodge_cooldown = 0
        self.aggro_cooldown = 0
        
        # Memory for player movement prediction
        self.player_velocity_memory = []
        self.memory_duration = 2.0  # seconds
    
    def update(self, dt: float, player, all_entities: List):
        """Update AI behavior"""
        self.target_player = player
        self.decision_cooldown -= dt
        self.state_timer -= dt
        self.dodge_cooldown -= dt
        self.aggro_cooldown -= dt
        
        # Update player memory
        self._update_player_memory(player, dt)
        
        # Make decisions at AI update rate
        if self.decision_cooldown <= 0:
            decision = self._make_decision(all_entities)
            self._execute_decision(decision, dt)
            self.decision_cooldown = 1.0 / config.AI_UPDATE_RATE
    
    def _update_player_memory(self, player, dt: float):
        """Update memory of player movement for prediction"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Add current player state to memory
        if hasattr(player, 'velocity'):
            self.player_velocity_memory.append({
                'time': current_time,
                'pos': player.pos,
                'velocity': player.velocity
            })
        
        # Remove old memory
        self.player_velocity_memory = [
            mem for mem in self.player_velocity_memory
            if current_time - mem['time'] < self.memory_duration
        ]
    
    def _make_decision(self, all_entities: List) -> AIDecision:
        """Make AI decision - to be overridden by subclasses"""
        decision = AIDecision()
        decision.state = self.state
        return decision
    
    def _execute_decision(self, decision: AIDecision, dt: float):
        """Execute the AI decision"""
        self.state = decision.state
        
        if decision.target_pos:
            self.pathfinding_target = decision.target_pos
        
        if decision.should_fire and self._can_see_player():
            self.entity.fire_weapon()
        
        # Set movement direction
        if decision.move_direction != (0.0, 0.0):
            self.entity.move_direction = decision.move_direction
        
        # Set look direction
        self.entity.look_direction = decision.look_direction
    
    def _can_see_player(self) -> bool:
        """Check if AI can see the player"""
        if not self.target_player:
            return False
        
        dist = distance(self.entity.pos, self.target_player.pos)
        if dist > self.entity.detection_range:
            return False
        
        # Check line of sight
        return line_of_sight(self.entity.pos, self.target_player.pos, 
                           self.collision_manager.walls)
    
    def _get_predicted_player_position(self, prediction_time: float) -> Tuple[float, float]:
        """Predict where player will be in the future"""
        if not self.target_player:
            return self.last_seen_player_pos or self.entity.pos
        
        # Use recent player velocity for prediction
        if self.player_velocity_memory:
            avg_velocity = [0.0, 0.0]
            for mem in self.player_velocity_memory[-5:]:  # Last 5 entries
                avg_velocity[0] += mem['velocity'][0]
                avg_velocity[1] += mem['velocity'][1]
            
            count = min(len(self.player_velocity_memory), 5)
            avg_velocity[0] /= count
            avg_velocity[1] /= count
            
            # Predict position
            predicted_x = self.target_player.pos[0] + avg_velocity[0] * prediction_time
            predicted_y = self.target_player.pos[1] + avg_velocity[1] * prediction_time
            
            return (predicted_x, predicted_y)
        
        return self.target_player.pos
    
    def _detect_incoming_bullets(self) -> List[Tuple[float, float]]:
        """Detect bullets heading towards this entity"""
        incoming_bullets = []
        
        if hasattr(self.entity, 'game'):
            for bullet in self.entity.game.bullet_manager.bullets:
                if bullet.owner_id != self.entity.id and bullet.alive:
                    # Check if bullet is heading towards entity
                    bullet_to_entity = (
                        self.entity.pos[0] - bullet.pos[0],
                        self.entity.pos[1] - bullet.pos[1]
                    )
                    bullet_direction = normalize_vector(bullet.velocity)
                    entity_direction = normalize_vector(bullet_to_entity)
                    
                    # Check if bullet is moving towards entity
                    dot_product = (bullet_direction[0] * entity_direction[0] + 
                                 bullet_direction[1] * entity_direction[1])
                    
                    if dot_product > 0.7:  # Bullet is heading towards entity
                        dist = distance(bullet.pos, self.entity.pos)
                        if dist < config.DODGER_BULLET_DODGE_RADIUS:
                            incoming_bullets.append(bullet.velocity)
        
        return incoming_bullets


class RusherAI(AIBehavior):
    """Rusher AI - Charges directly at player"""
    
    def __init__(self, entity, collision_manager: CollisionManager):
        super().__init__(entity, collision_manager)
        self.entity.detection_range = 400
        self.charge_speed = config.RUSHER_SPEED
    
    def _make_decision(self, all_entities: List) -> AIDecision:
        decision = AIDecision()
        
        if not self.target_player:
            decision.state = AIState.PATROL
            return decision
        
        player_distance = distance(self.entity.pos, self.target_player.pos)
        can_see_player = self._can_see_player()
        
        if can_see_player:
            self.last_seen_player_pos = self.target_player.pos
            self.last_seen_time = pygame.time.get_ticks() / 1000.0
        
        # State transitions
        if player_distance < config.RUSHER_ATTACK_RANGE and can_see_player:
            decision.state = AIState.ATTACK
        elif can_see_player or player_distance < self.entity.detection_range:
            decision.state = AIState.CHASE
        else:
            decision.state = AIState.PATROL
        
        # Behavior based on state
        if decision.state == AIState.CHASE or decision.state == AIState.ATTACK:
            # Move directly towards player
            if self.last_seen_player_pos:
                direction = normalize_vector((
                    self.last_seen_player_pos[0] - self.entity.pos[0],
                    self.last_seen_player_pos[1] - self.entity.pos[1]
                ))
                decision.move_direction = direction
                decision.look_direction = math.atan2(direction[1], direction[0])
                decision.target_pos = self.last_seen_player_pos
        
        # Fire when in attack range
        if decision.state == AIState.ATTACK and can_see_player:
            decision.should_fire = True
        
        return decision


class SniperAI(AIBehavior):
    """Sniper AI - Maintains distance and fires accurately"""
    
    def __init__(self, entity, collision_manager: CollisionManager):
        super().__init__(entity, collision_manager)
        self.entity.detection_range = 600
        self.preferred_range = config.SNIPER_PREFERRED_RANGE
        self.retreat_range = config.SNIPER_RETREAT_RANGE
        self.shot_prepare_timer = 0
    
    def _make_decision(self, all_entities: List) -> AIDecision:
        decision = AIDecision()
        
        if not self.target_player:
            decision.state = AIState.PATROL
            return decision
        
        player_distance = distance(self.entity.pos, self.target_player.pos)
        can_see_player = self._can_see_player()
        
        if can_see_player:
            self.last_seen_player_pos = self.target_player.pos
            self.last_seen_time = pygame.time.get_ticks() / 1000.0
        
        # State transitions
        if player_distance < self.retreat_range and can_see_player:
            decision.state = AIState.RETREAT
        elif (player_distance > self.preferred_range - 50 and 
              player_distance < self.preferred_range + 50 and can_see_player):
            decision.state = AIState.ATTACK
        elif can_see_player:
            decision.state = AIState.CHASE
        else:
            decision.state = AIState.PATROL
        
        # Behavior based on state
        if decision.state == AIState.RETREAT:
            # Move away from player
            if self.last_seen_player_pos:
                direction = normalize_vector((
                    self.entity.pos[0] - self.last_seen_player_pos[0],
                    self.entity.pos[1] - self.last_seen_player_pos[1]
                ))
                decision.move_direction = direction
                decision.look_direction = math.atan2(-direction[1], -direction[0])
        
        elif decision.state == AIState.CHASE:
            # Move to preferred range
            if self.last_seen_player_pos:
                direction_to_player = normalize_vector((
                    self.last_seen_player_pos[0] - self.entity.pos[0],
                    self.last_seen_player_pos[1] - self.entity.pos[1]
                ))
                
                # Move towards player but stop at preferred range
                if player_distance > self.preferred_range:
                    decision.move_direction = direction_to_player
                
                decision.look_direction = math.atan2(direction_to_player[1], direction_to_player[0])
        
        elif decision.state == AIState.ATTACK:
            # Stay still and aim
            if self.last_seen_player_pos:
                # Predict player movement for leading shots
                predicted_pos = self._get_predicted_player_position(0.5)  # 0.5s prediction
                direction_to_predicted = normalize_vector((
                    predicted_pos[0] - self.entity.pos[0],
                    predicted_pos[1] - self.entity.pos[1]
                ))
                
                decision.look_direction = math.atan2(direction_to_predicted[1], direction_to_predicted[0])
                decision.should_fire = True
        
        return decision


class DodgerAI(AIBehavior):
    """Dodger AI - Strafes and dodges bullets"""
    
    def __init__(self, entity, collision_manager: CollisionManager):
        super().__init__(entity, collision_manager)
        self.entity.detection_range = 350
        self.strafe_direction = 1  # 1 for right, -1 for left
        self.strafe_timer = 0
        self.dash_cooldown = 0
    
    def _make_decision(self, all_entities: List) -> AIDecision:
        decision = AIDecision()
        
        if not self.target_player:
            decision.state = AIState.PATROL
            return decision
        
        player_distance = distance(self.entity.pos, self.target_player.pos)
        can_see_player = self._can_see_player()
        incoming_bullets = self._detect_incoming_bullets()
        
        if can_see_player:
            self.last_seen_player_pos = self.target_player.pos
            self.last_seen_time = pygame.time.get_ticks() / 1000.0
        
        # Check for dodge
        if incoming_bullets and self.dodge_cooldown <= 0:
            decision.state = AIState.DODGE
        elif player_distance < 200 and can_see_player:
            decision.state = AIState.ATTACK
        elif can_see_player:
            decision.state = AIState.CHASE
        else:
            decision.state = AIState.PATROL
        
        # Behavior based on state
        if decision.state == AIState.DODGE:
            # Dodge incoming bullets
            bullet_velocity = incoming_bullets[0]  # Dodge first detected bullet
            
            # Move perpendicular to bullet trajectory
            dodge_direction = normalize_vector((-bullet_velocity[1], bullet_velocity[0]))
            
            # Randomly choose left or right dodge
            if random.random() < 0.5:
                dodge_direction = (-dodge_direction[0], -dodge_direction[1])
            
            decision.move_direction = dodge_direction
            decision.look_direction = math.atan2(-bullet_velocity[1], -bullet_velocity[0])
            
            # Dash if available
            if self.dash_cooldown <= 0:
                decision.move_direction = (dodge_direction[0] * 2, dodge_direction[1] * 2)
                self.dash_cooldown = config.DODGER_DASH_COOLDOWN
        
        elif decision.state == AIState.CHASE or decision.state == AIState.ATTACK:
            if self.last_seen_player_pos:
                # Move towards player but strafe
                direction_to_player = normalize_vector((
                    self.last_seen_player_pos[0] - self.entity.pos[0],
                    self.last_seen_player_pos[1] - self.entity.pos[1]
                ))
                
                # Update strafe direction periodically
                self.strafe_timer -= 1/60.0  # Assuming 60 FPS
                if self.strafe_timer <= 0:
                    self.strafe_direction *= -1
                    self.strafe_timer = random.uniform(1.0, 3.0)
                
                # Calculate strafe direction (perpendicular to player direction)
                strafe_direction = normalize_vector((-direction_to_player[1] * self.strafe_direction,
                                                   direction_to_player[0] * self.strafe_direction))
                
                # Combine forward and strafe movement
                combined_direction = normalize_vector((
                    direction_to_player[0] * 0.7 + strafe_direction[0] * 0.3,
                    direction_to_player[1] * 0.7 + strafe_direction[1] * 0.3
                ))
                
                decision.move_direction = combined_direction
                decision.look_direction = math.atan2(direction_to_player[1], direction_to_player[0])
        
        # Fire when in attack range
        if decision.state == AIState.ATTACK and can_see_player:
            decision.should_fire = True
        
        return decision


class FlankerAI(AIBehavior):
    """Flanker AI - Tries to attack from sides/back"""
    
    def __init__(self, entity, collision_manager: CollisionManager):
        super().__init__(entity, collision_manager)
        self.entity.detection_range = 500
        self.flank_angle = math.radians(config.FLANKER_FLANK_ANGLE)
        self.flank_position = None
        self.path_update_timer = 0
    
    def _make_decision(self, all_entities: List) -> AIDecision:
        decision = AIDecision()
        
        if not self.target_player:
            decision.state = AIState.PATROL
            return decision
        
        player_distance = distance(self.entity.pos, self.target_player.pos)
        can_see_player = self._can_see_player()
        
        if can_see_player:
            self.last_seen_player_pos = self.target_player.pos
            self.last_seen_time = pygame.time.get_ticks() / 1000.0
        
        # Update flank position periodically
        self.path_update_timer -= 1/60.0
        if self.path_update_timer <= 0 and self.last_seen_player_pos:
            self.flank_position = self._calculate_flank_position()
            self.path_update_timer = 2.0
        
        # State transitions
        if self.flank_position and player_distance < 300:
            # Check if we're in good flanking position
            if self._is_good_flanking_position():
                decision.state = AIState.ATTACK
            else:
                decision.state = AIState.CHASE
        elif can_see_player:
            decision.state = AIState.CHASE
        else:
            decision.state = AIState.PATROL
        
        # Behavior based on state
        if decision.state == AIState.CHASE and self.flank_position:
            # Move to flank position
            direction = normalize_vector((
                self.flank_position[0] - self.entity.pos[0],
                self.flank_position[1] - self.entity.pos[1]
            ))
            decision.move_direction = direction
            decision.look_direction = math.atan2(direction[1], direction[0])
            decision.target_pos = self.flank_position
        
        elif decision.state == AIState.ATTACK and self.last_seen_player_pos:
            # Aim at player from flanking position
            direction_to_player = normalize_vector((
                self.last_seen_player_pos[0] - self.entity.pos[0],
                self.last_seen_player_pos[1] - self.entity.pos[1]
            ))
            
            decision.look_direction = math.atan2(direction_to_player[1], direction_to_player[0])
            decision.should_fire = True
        
        return decision
    
    def _calculate_flank_position(self) -> Tuple[float, float]:
        """Calculate a good flanking position"""
        if not self.last_seen_player_pos or not self.target_player:
            return self.entity.pos
        
        # Get player facing direction
        player_facing = self.target_player.look_direction
        
        # Calculate positions to the sides of player
        flank_distance = 250  # Distance from player for flanking
        
        # Left flank
        left_angle = player_facing + math.pi / 2
        left_pos = (
            self.last_seen_player_pos[0] + math.cos(left_angle) * flank_distance,
            self.last_seen_player_pos[1] + math.sin(left_angle) * flank_distance
        )
        
        # Right flank
        right_angle = player_facing - math.pi / 2
        right_pos = (
            self.last_seen_player_pos[0] + math.cos(right_angle) * flank_distance,
            self.last_seen_player_pos[1] + math.sin(right_angle) * flank_distance
        )
        
        # Choose the flank position that's further from current position
        # (to encourage movement around the player)
        left_dist = distance(self.entity.pos, left_pos)
        right_dist = distance(self.entity.pos, right_pos)
        
        chosen_pos = left_pos if left_dist > right_dist else right_pos
        
        # Validate position
        if not self.collision_manager.is_position_valid(chosen_pos, self.entity.radius):
            # If invalid, choose the other position
            chosen_pos = left_pos if chosen_pos == right_pos else right_pos
            
            # If still invalid, use current position
            if not self.collision_manager.is_position_valid(chosen_pos, self.entity.radius):
                chosen_pos = self.entity.pos
        
        return chosen_pos
    
    def _is_good_flanking_position(self) -> bool:
        """Check if current position is good for flanking"""
        if not self.last_seen_player_pos or not self.target_player:
            return False
        
        # Check if we're roughly 90 degrees to the side of player's facing direction
        player_to_ai = normalize_vector((
            self.entity.pos[0] - self.last_seen_player_pos[0],
            self.entity.pos[1] - self.last_seen_player_pos[1]
        ))
        
        player_facing = vector_from_angle(self.target_player.look_direction, 1.0)
        
        # Calculate angle between player facing and direction to AI
        dot_product = player_facing[0] * player_to_ai[0] + player_facing[1] * player_to_ai[1]
        angle = math.acos(clamp(dot_product, -1, 1))
        
        # Good flanking position is roughly 90 degrees to the side
        return math.pi / 3 < angle < 2 * math.pi / 3


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(value, max_val))