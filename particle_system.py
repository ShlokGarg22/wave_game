"""
Death Circuit - Particle System
Handles visual effects like muzzle flashes, explosions, and impacts
"""

import pygame
import random
import math
from typing import List, Tuple, Optional
from utils import normalize_vector, vector_from_angle
import config


class Particle:
    """Individual particle with position, velocity, and lifetime"""
    
    def __init__(self, pos: Tuple[float, float], velocity: Tuple[float, float],
                 color: Tuple[int, int, int], lifetime: float, size: int = 2):
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.color = color
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.size = size
        self.alpha = 255
    
    def update(self, dt: float):
        """Update particle position and lifetime"""
        # Update position
        self.pos[0] += self.velocity[0] * dt
        self.pos[1] += self.velocity[1] * dt
        
        # Update lifetime
        self.lifetime -= dt
        
        # Update alpha based on remaining lifetime
        if self.lifetime > 0:
            self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        else:
            self.alpha = 0
    
    def draw(self, screen: pygame.Surface):
        """Draw the particle"""
        if self.alpha <= 0:
            return
        
        # Create surface for particle with alpha
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Calculate color with alpha
        color_with_alpha = (*self.color, self.alpha)
        
        # Draw particle as a circle
        pygame.draw.circle(particle_surface, color_with_alpha, 
                          (self.size, self.size), self.size)
        
        # Draw to screen
        screen.blit(particle_surface, 
                   (int(self.pos[0] - self.size), int(self.pos[1] - self.size)))


class ParticleEmitter:
    """Manages particle effects and emission"""
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.max_particles = config.PARTICLE_MAX_COUNT
    
    def update(self, dt: float):
        """Update all particles"""
        # Update existing particles
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen: pygame.Surface):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)
    
    def create_muzzle_flash(self, pos: Tuple[float, float], 
                          direction: float, color: Tuple[int, int, int]):
        """Create muzzle flash effect"""
        for _ in range(config.MUZZLE_FLASH_PARTICLES):
            # Random angle within cone
            spread = random.uniform(-0.3, 0.3)
            angle = direction + spread
            
            # Random speed
            speed = random.uniform(100, 300)
            velocity = vector_from_angle(angle, speed)
            
            # Add some randomness to starting position
            offset = vector_from_angle(angle, random.uniform(5, 15))
            start_pos = (pos[0] + offset[0], pos[1] + offset[1])
            
            # Random color variation
            color_variation = random.randint(-30, 30)
            particle_color = (
                clamp(color[0] + color_variation, 0, 255),
                clamp(color[1] + color_variation, 0, 255),
                clamp(color[2] + color_variation, 0, 255)
            )
            
            particle = Particle(
                start_pos, velocity, particle_color,
                random.uniform(0.05, config.MUZZLE_FLASH_LIFETIME),
                random.randint(1, 3)
            )
            
            self.particles.append(particle)
            
            # Remove oldest particles if over limit
            self._cleanup_excess_particles()
    
    def create_blood_splatter(self, pos: Tuple[float, float], 
                            hit_direction: Tuple[float, float]):
        """Create blood splatter effect when entity is hit"""
        for _ in range(config.BLOOD_PARTICLES):
            # Random direction away from hit
            base_angle = math.atan2(hit_direction[1], hit_direction[0])
            angle = base_angle + random.uniform(-1.0, 1.0)
            
            # Random speed
            speed = random.uniform(50, 200)
            velocity = vector_from_angle(angle, speed)
            
            # Random color (dark red variations)
            color = (
                random.randint(100, 150),
                0,
                random.randint(0, 50)
            )
            
            particle = Particle(
                pos, velocity, color,
                random.uniform(0.2, config.BLOOD_LIFETIME),
                random.randint(2, 4)
            )
            
            self.particles.append(particle)
            self._cleanup_excess_particles()
    
    def create_death_explosion(self, pos: Tuple[float, float], 
                             color: Tuple[int, int, int]):
        """Create explosion effect when entity dies"""
        for _ in range(config.DEATH_EXPLOSION_PARTICLES):
            # Random direction in all directions
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 400)
            velocity = vector_from_angle(angle, speed)
            
            # Random color variation
            color_variation = random.randint(-50, 50)
            particle_color = (
                clamp(color[0] + color_variation, 0, 255),
                clamp(color[1] + color_variation, 0, 255),
                clamp(color[2] + color_variation, 0, 255)
            )
            
            particle = Particle(
                pos, velocity, particle_color,
                random.uniform(0.5, config.DEATH_EXPLOSION_LIFETIME),
                random.randint(3, 6)
            )
            
            self.particles.append(particle)
            self._cleanup_excess_particles()
    
    def create_impact_sparks(self, pos: Tuple[float, float], 
                           normal: Tuple[float, float]):
        """Create impact sparks when bullet hits wall"""
        for _ in range(config.IMPACT_SPARKS):
            # Random direction away from wall normal
            base_angle = math.atan2(normal[1], normal[0])
            angle = base_angle + random.uniform(-0.5, 0.5)
            speed = random.uniform(100, 300)
            velocity = vector_from_angle(angle, speed)
            
            # Bright yellow/white sparks
            color = (
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(100, 150)
            )
            
            particle = Particle(
                pos, velocity, color,
                random.uniform(0.1, config.IMPACT_LIFETIME),
                random.randint(1, 2)
            )
            
            self.particles.append(particle)
            self._cleanup_excess_particles()
    
    def create_trail_particle(self, pos: Tuple[float, float], 
                            velocity: Tuple[float, float],
                            color: Tuple[int, int, int]):
        """Create a trail particle behind fast-moving objects"""
        # Slower, smaller particles for trails
        trail_velocity = (velocity[0] * 0.3, velocity[1] * 0.3)
        
        particle = Particle(
            pos, trail_velocity, color,
            config.BULLET_TRAIL_DURATION,
            1
        )
        
        self.particles.append(particle)
        self._cleanup_excess_particles()
    
    def _cleanup_excess_particles(self):
        """Remove oldest particles if over the limit"""
        while len(self.particles) > self.max_particles:
            self.particles.pop(0)
    
    def clear_all_particles(self):
        """Remove all particles"""
        self.particles.clear()


def clamp(value: int, min_val: int, max_val: int) -> int:
    """Clamp a value between min and max"""
    return max(min_val, min(value, max_val))