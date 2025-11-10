"""
Death Circuit - Bullet Class
Handles bullet physics, collision, and rendering
"""

import pygame
import math
from typing import Tuple, Optional, List
from utils import normalize_vector, distance
import config


class Bullet:
    """Represents a single bullet projectile"""
    
    def __init__(self, pos: Tuple[float, float], velocity: Tuple[float, float],
                 damage: int, owner_id: str, color: Tuple[int, int, int] = config.BULLET_COLOR):
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.damage = damage
        self.owner_id = owner_id  # 'player' or enemy ID
        self.color = color
        self.radius = config.BULLET_SIZE
        self.lifetime = config.BULLET_LIFETIME
        self.max_lifetime = config.BULLET_LIFETIME
        self.trail_positions = []  # For bullet trail effect
        self.alive = True
        
        # Calculate max range based on lifetime and speed
        speed = math.sqrt(velocity[0]**2 + velocity[1]**2)
        self.max_range = speed * config.BULLET_LIFETIME
    
    def update(self, dt: float):
        """Update bullet position and lifetime"""
        if not self.alive:
            return
        
        # Store trail position
        self.trail_positions.append(tuple(self.pos))
        if len(self.trail_positions) > config.BULLET_TRAIL_LENGTH:
            self.trail_positions.pop(0)
        
        # Update position
        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt
        
        # Update lifetime
        self.lifetime -= dt
        
        # Check if bullet should be removed
        if self.lifetime <= 0:
            self.alive = False
        
        # Check if bullet is out of bounds
        if (self.pos[0] < -self.radius or self.pos[0] > config.SCREEN_WIDTH + self.radius or
            self.pos[1] < -self.radius or self.pos[1] > config.SCREEN_HEIGHT + self.radius):
            self.alive = False
    
    def draw(self, screen: pygame.Surface):
        """Draw bullet and trail"""
        if not self.alive:
            return
        
        # Draw trail
        if len(self.trail_positions) > 1:
            trail_alpha = int(255 * (self.lifetime / self.max_lifetime))
            trail_color = (*self.color, trail_alpha // 2)
            
            for i in range(len(self.trail_positions) - 1):
                start_pos = self.trail_positions[i]
                end_pos = self.trail_positions[i + 1]
                
                # Create trail surface with alpha
                trail_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(trail_surface, trail_color, 
                               (int(start_pos[0]), int(start_pos[1])),
                               (int(end_pos[0]), int(end_pos[1])), 2)
                screen.blit(trail_surface, (0, 0))
        
        # Draw bullet
        pygame.draw.circle(screen, self.color, 
                         (int(self.pos[0]), int(self.pos[1])), 
                         self.radius)
        
        # Add glow effect
        glow_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        glow_alpha = int(100 * (self.lifetime / self.max_lifetime))
        glow_color = (*self.color, glow_alpha)
        pygame.draw.circle(glow_surface, glow_color, 
                         (self.radius * 2, self.radius * 2), self.radius * 2)
        screen.blit(glow_surface, 
                   (int(self.pos[0] - self.radius * 2), 
                    int(self.pos[1] - self.radius * 2)))
    
    def check_collision_with_entity(self, entity_pos: Tuple[float, float], 
                                  entity_radius: float) -> bool:
        """Check collision with an entity (circle)"""
        dist = distance(self.pos, entity_pos)
        return dist < self.radius + entity_radius
    
    def check_collision_with_rect(self, rect: pygame.Rect) -> bool:
        """Check collision with a rectangle (wall)"""
        # Find closest point on rectangle to bullet
        closest_x = max(rect.left, min(self.pos[0], rect.right))
        closest_y = max(rect.top, min(self.pos[1], rect.bottom))
        
        # Calculate distance
        dist = distance(self.pos, (closest_x, closest_y))
        return dist < self.radius
    
    def get_impact_position(self) -> Tuple[float, float]:
        """Get the bullet's current position for impact effects"""
        return tuple(self.pos)
    
    def get_travel_distance(self) -> float:
        """Get total distance traveled by bullet"""
        if len(self.trail_positions) < 2:
            return 0
        
        total_distance = 0
        for i in range(len(self.trail_positions) - 1):
            total_distance += distance(self.trail_positions[i], self.trail_positions[i + 1])
        
        return total_distance
    
    def predict_position(self, time_ahead: float) -> Tuple[float, float]:
        """Predict bullet position in the future"""
        future_x = self.pos[0] + self.velocity[0] * time_ahead
        future_y = self.pos[1] + self.velocity[1] * time_ahead
        return (future_x, future_y)


class BulletManager:
    """Manages all bullets in the game"""
    
    def __init__(self):
        self.bullets: List[Bullet] = []
        self.bullet_count = 0
    
    def add_bullet(self, bullet: Bullet):
        """Add a bullet to the manager"""
        self.bullets.append(bullet)
        self.bullet_count += 1
    
    def update(self, dt: float):
        """Update all bullets"""
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.alive:
                self.bullets.remove(bullet)
    
    def draw(self, screen: pygame.Surface):
        """Draw all bullets"""
        for bullet in self.bullets:
            bullet.draw(screen)
    
    def clear_bullets(self):
        """Remove all bullets"""
        self.bullets.clear()
        self.bullet_count = 0
    
    def get_bullets_by_owner(self, owner_id: str) -> List[Bullet]:
        """Get all bullets owned by a specific entity"""
        return [bullet for bullet in self.bullets if bullet.owner_id == owner_id]
    
    def get_live_bullets(self) -> List[Bullet]:
        """Get all active bullets"""
        return [bullet for bullet in self.bullets if bullet.alive]
    
    def count_bullets_in_radius(self, pos: Tuple[float, float], 
                              radius: float, owner_filter: Optional[str] = None) -> int:
        """Count bullets within a radius, optionally filtering by owner"""
        count = 0
        for bullet in self.bullets:
            if not bullet.alive:
                continue
            
            if owner_filter and bullet.owner_id != owner_filter:
                continue
            
            if distance(bullet.pos, pos) <= radius:
                count += 1
        
        return count