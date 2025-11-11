"""
Death Circuit - Player Class
Handles player movement, shooting, health, and weapon management
"""

import pygame
import math
import random
from typing import Tuple, List, Optional
from weapon import WeaponManager
from bullet import Bullet
from particle_system import ParticleEmitter
from utils import normalize_vector, vector_from_angle, clamp, distance
import config


class Player:
    """Player character class"""
    
    def __init__(self, pos: Tuple[float, float]):
        self.id = 'player'  # Unique identifier for bullet ownership
        self.pos = list(pos)
        self.velocity = [0.0, 0.0]
        self.radius = config.PLAYER_SIZE // 2
        self.max_health = config.PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.speed = config.PLAYER_SPEED
        self.look_direction = 0.0  # radians
        self.color = config.PLAYER_COLOR
        
        # Movement
        self.move_direction = [0.0, 0.0]  # Normalized movement input
        self.acceleration = 2000  # pixels per second squared
        self.friction = 0.85  # Velocity multiplier each frame
        
        # Health system
        self.last_damage_time = 0
        self.regen_timer = 0
        self.invincible = False
        self.invincibility_timer = 0
        self.last_contact_damage_time = 0  # For enemy contact damage cooldown
        
        # Combat
        self.weapon_manager = WeaponManager()
        self.particle_emitter = None
        self.bullets = None  # Will be set by game
        
        # Input
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_pressed = False
        self.last_shot_time = 0
        self.reload_key_was_pressed = False  # Track reload key state to prevent continuous reload
        
        # Statistics
        self.kills = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        self.time_alive = 0
        
        # Visual
        self.screen_shake_timer = 0
        self.screen_shake_intensity = 0
    
    def update(self, dt: float, current_time: float):
        """Update player state"""
        self.time_alive += dt
        
        # Update weapon manager
        self.weapon_manager.update(dt)
        
        # Handle input
        self._handle_input()
        
        # Update movement
        self._update_movement(dt)
        
        # Update health system
        self._update_health_system(dt, current_time)
        
        # Update invincibility
        if self.invincible:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.invincible = False
        
        # Update screen shake
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= dt
        
        # Handle shooting
        self._handle_shooting(current_time)
    
    def _handle_input(self):
        """Handle keyboard and mouse input"""
        # Movement input (supports multiple keys simultaneously)
        self.move_direction = [0.0, 0.0]
        
        if config.KEY_UP in self.keys_pressed:
            self.move_direction[1] -= 1
        if config.KEY_DOWN in self.keys_pressed:
            self.move_direction[1] += 1
        if config.KEY_LEFT in self.keys_pressed:
            self.move_direction[0] -= 1
        if config.KEY_RIGHT in self.keys_pressed:
            self.move_direction[0] += 1
        
        # Normalize movement direction
        if self.move_direction != [0.0, 0.0]:
            length = math.sqrt(self.move_direction[0]**2 + self.move_direction[1]**2)
            self.move_direction[0] /= length
            self.move_direction[1] /= length
        
        # Weapon switching (check all keys, first one found wins)
        if config.KEY_WEAPON_1 in self.keys_pressed:
            self.weapon_manager.switch_weapon(0)
        if config.KEY_WEAPON_2 in self.keys_pressed:
            self.weapon_manager.switch_weapon(1)
        if config.KEY_WEAPON_3 in self.keys_pressed:
            self.weapon_manager.switch_weapon(2)
        if config.KEY_WEAPON_4 in self.keys_pressed:
            self.weapon_manager.switch_weapon(3)
        
        # Reload (trigger once per key press, not continuously)
        if config.KEY_RELOAD in self.keys_pressed:
            if not self.reload_key_was_pressed:
                self.weapon_manager.start_reload()
                self.reload_key_was_pressed = True
        else:
            self.reload_key_was_pressed = False
        
        # Update look direction based on mouse
        mouse_x, mouse_y = self.mouse_pos
        dx = mouse_x - self.pos[0]
        dy = mouse_y - self.pos[1]
        self.look_direction = math.atan2(dy, dx)
    
    def _update_movement(self, dt: float):
        """Update player movement and physics"""
        # Apply acceleration
        if self.move_direction != [0.0, 0.0]:
            self.velocity[0] += self.move_direction[0] * self.acceleration * dt
            self.velocity[1] += self.move_direction[1] * self.acceleration * dt
        
        # Apply friction
        self.velocity[0] *= self.friction
        self.velocity[1] *= self.friction
        
        # Clamp velocity
        current_speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        if current_speed > self.speed:
            factor = self.speed / current_speed
            self.velocity[0] *= factor
            self.velocity[1] *= factor
        
        # Update position
        new_x = self.pos[0] + self.velocity[0] * dt
        new_y = self.pos[1] + self.velocity[1] * dt
        
        # Boundary checking
        new_x = clamp(new_x, self.radius, config.SCREEN_WIDTH - self.radius)
        new_y = clamp(new_y, self.radius, config.SCREEN_HEIGHT - self.radius)
        
        # Wall collision (if collision manager is available)
        if hasattr(self, 'collision_manager') and self.collision_manager:
            test_pos = (new_x, new_y)
            if self.collision_manager.check_entity_wall_collision(test_pos, self.radius):
                new_pos = self.collision_manager.resolve_entity_wall_collision(test_pos, self.radius)
                new_x, new_y = new_pos
                # Reduce velocity after collision
                self.velocity[0] *= 0.5
                self.velocity[1] *= 0.5
        
        self.pos[0] = new_x
        self.pos[1] = new_y
    
    def _update_health_system(self, dt: float, current_time: float):
        """Update health regeneration and timers"""
        # No auto-regeneration during gameplay
        # Health only regenerates between waves
        pass
    
    def _handle_shooting(self, current_time: float):
        """Handle weapon firing"""
        if self.mouse_pressed and self.bullets is not None:
            # Fire current weapon
            fire_pos = (self.pos[0] + math.cos(self.look_direction) * 30,
                       self.pos[1] + math.sin(self.look_direction) * 30)
            
            fired = self.weapon_manager.fire(
                fire_pos, self.look_direction, 'player', 
                self.bullets, self.particle_emitter
            )
            
            if fired:
                self.last_shot_time = current_time
    
    def take_damage(self, amount: int, current_time: float):
        """Apply damage to player"""
        if self.invincible:
            return
        
        self.health -= amount
        self.damage_taken += amount
        self.last_damage_time = current_time
        
        # Apply invincibility
        self.invincible = True
        self.invincibility_timer = config.PLAYER_INVINCIBILITY_DURATION
        
        # Screen shake
        self.screen_shake_timer = config.SCREEN_SHAKE_DURATION
        self.screen_shake_intensity = config.SCREEN_SHAKE_INTENSITY
        
        # Create damage particles
        if self.particle_emitter:
            damage_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
            self.particle_emitter.create_blood_splatter(self.pos, damage_direction)
    
    def heal(self, amount: int):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
    
    def is_dead(self) -> bool:
        """Check if player is dead"""
        return self.health <= 0
    
    def draw(self, screen: pygame.Surface):
        """Draw the player"""
        # Apply screen shake
        shake_x = 0
        shake_y = 0
        if self.screen_shake_timer > 0:
            shake_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
        
        # Draw player body
        player_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        # Main body
        if self.invincible and int(self.invincibility_timer * 10) % 2:
            # Flash when invincible
            color = (255, 255, 255)
        else:
            color = self.color
        
        pygame.draw.circle(player_surface, color, (self.radius, self.radius), self.radius)
        
        # Draw direction indicator
        end_x = self.radius + math.cos(self.look_direction) * self.radius
        end_y = self.radius + math.sin(self.look_direction) * self.radius
        pygame.draw.line(player_surface, (255, 255, 255), 
                        (self.radius, self.radius), (end_x, end_y), 3)
        
        # Draw to screen with shake offset
        screen.blit(player_surface, 
                   (int(self.pos[0] - self.radius + shake_x), 
                    int(self.pos[1] - self.radius + shake_y)))
        
        # Draw glow effect
        if not self.invincible:
            glow_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            glow_alpha = 50
            pygame.draw.circle(glow_surface, (*self.color, glow_alpha), 
                             (self.radius * 2, self.radius * 2), self.radius * 2)
            screen.blit(glow_surface, 
                       (int(self.pos[0] - self.radius * 2 + shake_x), 
                        int(self.pos[1] - self.radius * 2 + shake_y)))
    
    def get_screen_shake_offset(self) -> Tuple[int, int]:
        """Get screen shake offset for camera"""
        if self.screen_shake_timer > 0:
            return (random.randint(-self.screen_shake_intensity, self.screen_shake_intensity),
                   random.randint(-self.screen_shake_intensity, self.screen_shake_intensity))
        return (0, 0)
    
    def get_weapon_info(self) -> dict:
        """Get current weapon information"""
        return self.weapon_manager.get_weapon_info()
    
    def get_accuracy_stats(self) -> dict:
        """Get player accuracy statistics"""
        return self.weapon_manager.get_accuracy_stats()
    
    def add_kill(self):
        """Increment kill counter"""
        self.kills += 1
    
    def add_damage_dealt(self, amount: int):
        """Add to damage dealt counter"""
        self.damage_dealt += amount
    
    def reset(self, pos: Tuple[float, float]):
        """Reset player state"""
        self.pos = list(pos)
        self.velocity = [0.0, 0.0]
        self.health = self.max_health
        self.last_damage_time = 0
        self.regen_timer = 0
        self.invincible = False
        self.invincibility_timer = 0
        self.kills = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        self.time_alive = 0
        self.screen_shake_timer = 0
        self.last_contact_damage_time = 0
        
        # Clear input states
        self.keys_pressed = set()
        self.mouse_pressed = False
        self.move_direction = [0.0, 0.0]
        self.reload_key_was_pressed = False
        
        # Reset weapons
        self.weapon_manager = WeaponManager()
    
    def set_collision_manager(self, collision_manager):
        """Set collision manager for wall collision"""
        self.collision_manager = collision_manager
    
    def set_particle_emitter(self, particle_emitter: ParticleEmitter):
        """Set particle emitter for effects"""
        self.particle_emitter = particle_emitter
    
    def set_bullet_list(self, bullets: List[Bullet]):
        """Set bullet list for shooting"""
        self.bullets = bullets