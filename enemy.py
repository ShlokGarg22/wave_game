"""
Death Circuit - Enemy Classes
Base enemy class and specific AI personality types
"""

import pygame
import math
import random
from typing import Tuple, List, Optional
from ai_behaviors import RusherAI, SniperAI, DodgerAI, FlankerAI, AIState
from weapon import Pistol, SMG, Shotgun, Rifle
from bullet import Bullet
from particle_system import ParticleEmitter
from utils import normalize_vector, vector_from_angle, distance
import config


class Enemy:
    """Base enemy class"""
    
    def __init__(self, pos: Tuple[float, float], enemy_type: str):
        self.pos = list(pos)
        self.velocity = [0.0, 0.0]
        self.radius = config.PLAYER_SIZE // 2
        self.enemy_type = enemy_type
        self.id = f"enemy_{random.randint(1000, 9999)}"
        self.is_boss = False  # Will be set to True for boss enemies
        
        # Health and combat
        self.max_health = config.ENEMY_BASE_HEALTH
        self.health = self.max_health
        self.detection_range = 700  # Increased from 300 for more aggressive enemies
        self.damage = 10
        
        # Movement
        self.speed = 100
        self.move_direction = (0.0, 0.0)
        self.look_direction = 0.0
        self.ai_behavior = None
        
        # Weapon
        self.weapon = None
        self.bullets = None
        self.particle_emitter = None
        
        # State
        self.state = AIState.PATROL
        self.alive = True
        self.spawn_time = pygame.time.get_ticks() / 1000.0
        self.invincible = True
        self.invincibility_timer = config.ENEMY_SPAWN_INVINCIBILITY
        
        # Statistics
        self.damage_dealt = 0
        self.shots_fired = 0
        
        # Visual
        self.color = (255, 0, 0)  # Default red
        self.collision_manager = None
    
    def update(self, dt: float, player, all_entities: List, current_time: float):
        """Update enemy state"""
        if not self.alive:
            return
        
        # Update spawn invincibility
        if self.invincible:
            self.invincibility_timer -= dt
            if self.invincibility_timer <= 0:
                self.invincible = False
        
        # Update AI behavior
        if self.ai_behavior:
            self.ai_behavior.update(dt, player, all_entities)
            self.state = self.ai_behavior.state
        
        # Update movement
        self._update_movement(dt)
        
        # Update weapon
        if self.weapon:
            self.weapon.update(dt)
    
    def _update_movement(self, dt: float):
        """Update enemy movement"""
        # Calculate velocity from move direction
        if self.move_direction != (0.0, 0.0):
            self.velocity[0] = self.move_direction[0] * self.speed
            self.velocity[1] = self.move_direction[1] * self.speed
        else:
            self.velocity[0] = 0
            self.velocity[1] = 0
        
        # Update position
        new_x = self.pos[0] + self.velocity[0] * dt
        new_y = self.pos[1] + self.velocity[1] * dt
        
        # Boundary checking
        new_x = max(self.radius, min(new_x, config.SCREEN_WIDTH - self.radius))
        new_y = max(self.radius, min(new_y, config.SCREEN_HEIGHT - self.radius))
        
        # Wall collision
        if self.collision_manager:
            test_pos = (new_x, new_y)
            if self.collision_manager.check_entity_wall_collision(test_pos, self.radius):
                new_pos = self.collision_manager.resolve_entity_wall_collision(test_pos, self.radius)
                new_x, new_y = new_pos
        
        self.pos[0] = new_x
        self.pos[1] = new_y
    
    def take_damage(self, amount: int, attacker_id: str = None):
        """Apply damage to enemy"""
        if not self.alive or self.invincible:
            return
        
        self.health -= amount
        
        # Create damage particles
        if self.particle_emitter:
            damage_direction = (random.uniform(-1, 1), random.uniform(-1, 1))
            self.particle_emitter.create_blood_splatter(self.pos, damage_direction)
        
        if self.health <= 0:
            self.die(attacker_id)
    
    def die(self, killer_id: str = None):
        """Handle enemy death"""
        self.alive = False
        
        # Create death explosion
        if self.particle_emitter:
            self.particle_emitter.create_death_explosion(self.pos, self.color)
        
        # Notify game of death
        if hasattr(self, 'game') and self.game:
            self.game.on_enemy_killed(self, killer_id)
    
    def fire_weapon(self):
        """Fire enemy weapon"""
        if not self.weapon or not self.bullets:
            return
        
        # Calculate fire position
        fire_pos = (self.pos[0] + math.cos(self.look_direction) * 30,
                   self.pos[1] + math.sin(self.look_direction) * 30)
        
        # Fire weapon
        fired = self.weapon.fire(fire_pos, self.look_direction, self.id,
                                self.bullets, self.particle_emitter)
        
        if fired:
            self.shots_fired += 1
    
    def make_boss(self):
        """Convert this enemy into a boss"""
        self.is_boss = True
        self.id = f"BOSS_{random.randint(1000, 9999)}"
        
        # Apply boss multipliers
        self.max_health = int(self.max_health * config.BOSS_HEALTH_MULTIPLIER)
        self.health = self.max_health
        self.radius = int(self.radius * config.BOSS_SIZE_MULTIPLIER)
        self.speed = int(self.speed * config.BOSS_SPEED_MULTIPLIER)
        self.damage = int(self.damage * config.BOSS_DAMAGE_MULTIPLIER)
        self.detection_range = int(self.detection_range * 1.5)  # Bosses detect from further
        
        # Visual distinction - make boss darker/more menacing
        r, g, b = self.color
        self.color = (min(255, r + 50), max(0, g - 50), max(0, b - 50))
        
        # Boost weapon if available
        if self.weapon:
            self.weapon.fire_cooldown /= config.BOSS_FIRE_RATE_MULTIPLIER
            self.weapon.damage = int(self.weapon.damage * config.BOSS_DAMAGE_MULTIPLIER)
    
    def draw(self, screen: pygame.Surface):
        """Draw the enemy"""
        if not self.alive:
            return
        
        # Draw enemy body
        enemy_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
        # Flash when invincible
        if self.invincible and int(self.invincibility_timer * 5) % 2:
            color = (255, 255, 255)
        else:
            color = self.color
        
        pygame.draw.circle(enemy_surface, color, (self.radius, self.radius), self.radius)
        
        # Draw direction indicator
        end_x = self.radius + math.cos(self.look_direction) * self.radius * 0.7
        end_y = self.radius + math.sin(self.look_direction) * self.radius * 0.7
        pygame.draw.line(enemy_surface, (255, 255, 255), 
                        (self.radius, self.radius), (end_x, end_y), 2)
        
        # Draw type indicator
        self._draw_type_indicator(enemy_surface)
        
        # Draw boss crown if this is a boss
        if self.is_boss:
            self._draw_boss_crown(enemy_surface)
        
        # Draw to screen
        screen.blit(enemy_surface, 
                   (int(self.pos[0] - self.radius), 
                    int(self.pos[1] - self.radius)))
        
        # Draw health bar (bigger for bosses)
        self._draw_health_bar(screen)
    
    def _draw_type_indicator(self, surface: pygame.Surface):
        """Draw indicator showing enemy type"""
        # Different shapes for different types
        if self.enemy_type == 'rusher':
            # Triangle pointing forward
            points = [
                (self.radius, self.radius - 5),
                (self.radius - 3, self.radius - 10),
                (self.radius + 3, self.radius - 10)
            ]
            pygame.draw.polygon(surface, (255, 255, 255), points)
        
        elif self.enemy_type == 'sniper':
            # Crosshair
            pygame.draw.circle(surface, (255, 255, 255), (self.radius, self.radius - 8), 3, 1)
            pygame.draw.line(surface, (255, 255, 255), 
                           (self.radius - 5, self.radius - 8), 
                           (self.radius + 5, self.radius - 8), 1)
            pygame.draw.line(surface, (255, 255, 255), 
                           (self.radius, self.radius - 13), 
                           (self.radius, self.radius - 3), 1)
        
        elif self.enemy_type == 'dodger':
            # Lightning bolt shape
            points = [
                (self.radius - 2, self.radius - 12),
                (self.radius + 1, self.radius - 8),
                (self.radius - 1, self.radius - 6),
                (self.radius + 2, self.radius - 2),
                (self.radius, self.radius - 2),
                (self.radius - 2, self.radius - 12)
            ]
            pygame.draw.polygon(surface, (255, 255, 255), points)
        
        elif self.enemy_type == 'flanker':
            # Curved arrow
            center_x, center_y = self.radius, self.radius - 8
            pygame.draw.arc(surface, (255, 255, 255), 
                          (center_x - 5, center_y - 5, 10, 10), 
                          0, math.pi, 2)
            # Arrow head
            pygame.draw.line(surface, (255, 255, 255), 
                           (center_x + 5, center_y), 
                           (center_x + 3, center_y - 2), 2)
            pygame.draw.line(surface, (255, 255, 255), 
                           (center_x + 5, center_y), 
                           (center_x + 3, center_y + 2), 2)
    
    def _draw_boss_crown(self, surface: pygame.Surface):
        """Draw a crown above the boss"""
        crown_color = (255, 215, 0)  # Gold
        center_x, center_y = self.radius, int(self.radius * 0.3)
        
        # Crown base
        crown_width = int(self.radius * 0.6)
        crown_height = int(self.radius * 0.3)
        
        # Draw crown with three points
        points = [
            (center_x - crown_width//2, center_y + crown_height//2),  # Bottom left
            (center_x - crown_width//3, center_y - crown_height//2),  # Left peak
            (center_x - crown_width//6, center_y),                     # Left valley
            (center_x, center_y - crown_height),                       # Center peak
            (center_x + crown_width//6, center_y),                     # Right valley
            (center_x + crown_width//3, center_y - crown_height//2),  # Right peak
            (center_x + crown_width//2, center_y + crown_height//2),  # Bottom right
        ]
        pygame.draw.polygon(surface, crown_color, points)
        pygame.draw.polygon(surface, (200, 180, 0), points, 2)  # Border
    
    def _draw_health_bar(self, screen: pygame.Surface):
        """Draw enemy health bar"""
        bar_width = 40 if self.is_boss else 30  # Bigger health bar for bosses
        bar_height = 6 if self.is_boss else 4
        bar_x = self.pos[0] - bar_width // 2
        bar_y = self.pos[1] - self.radius - (15 if self.is_boss else 10)
        
        # Background
        pygame.draw.rect(screen, (50, 50, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health bar
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        
        # Color based on health
        if health_ratio > 0.6:
            color = (0, 255, 0)  # Green
        elif health_ratio > 0.3:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
        
        pygame.draw.rect(screen, color, 
                        (bar_x, bar_y, health_width, bar_height))
    
    def is_dead(self) -> bool:
        """Check if enemy is dead"""
        return not self.alive
    
    def set_collision_manager(self, collision_manager):
        """Set collision manager"""
        self.collision_manager = collision_manager
    
    def set_particle_emitter(self, particle_emitter: ParticleEmitter):
        """Set particle emitter"""
        self.particle_emitter = particle_emitter
    
    def set_bullet_list(self, bullets: List[Bullet]):
        """Set bullet list"""
        self.bullets = bullets
    
    def set_game_reference(self, game):
        """Set reference to main game"""
        self.game = game


class Rusher(Enemy):
    """Rusher enemy - Charges directly at player"""
    
    def __init__(self, pos: Tuple[float, float]):
        super().__init__(pos, 'rusher')
        self.color = config.ENEMY_RUSHER_COLOR
        self.speed = config.RUSHER_SPEED
        self.max_health = config.ENEMY_BASE_HEALTH
        self.health = self.max_health
        self.weapon = SMG()
        self.ai_behavior = None  # Will be set after collision manager is available


class Sniper(Enemy):
    """Sniper enemy - Maintains distance and fires accurately"""
    
    def __init__(self, pos: Tuple[float, float]):
        super().__init__(pos, 'sniper')
        self.color = config.ENEMY_SNIPER_COLOR
        self.speed = config.SNIPER_SPEED
        self.max_health = config.ENEMY_BASE_HEALTH + 10
        self.health = self.max_health
        self.weapon = Rifle()
        self.ai_behavior = None


class Dodger(Enemy):
    """Dodger enemy - Strafes and dodges bullets"""
    
    def __init__(self, pos: Tuple[float, float]):
        super().__init__(pos, 'dodger')
        self.color = config.ENEMY_DODGER_COLOR
        self.speed = config.DODGER_SPEED
        self.max_health = config.ENEMY_BASE_HEALTH + 20
        self.health = self.max_health
        self.weapon = Shotgun()
        self.ai_behavior = None


class Flanker(Enemy):
    """Flanker enemy - Tries to attack from sides/back"""
    
    def __init__(self, pos: Tuple[float, float]):
        super().__init__(pos, 'flanker')
        self.color = config.ENEMY_FLANKER_COLOR
        self.speed = config.FLANKER_SPEED
        self.max_health = config.ENEMY_BASE_HEALTH + 15
        self.health = self.max_health
        self.weapon = Rifle()
        self.ai_behavior = None


class EnemySpawner:
    """Handles enemy spawning and management"""
    
    def __init__(self):
        self.enemies: List[Enemy] = []
        self.spawn_queue: List[Dict] = []
        self.spawn_timer = 0
        self.wave_number = 0
    
    def start_wave(self, wave_number: int, map_generator):
        """Start a new wave of enemies"""
        self.wave_number = wave_number
        self.enemies.clear()
        self.spawn_queue.clear()
        
        # Check if this is a boss wave
        is_boss_wave = (wave_number % config.BOSS_WAVE_INTERVAL == 0)
        
        if is_boss_wave:
            # Boss wave - spawn 1 boss + some regular enemies
            enemy_count = max(3, config.WAVE_BASE_ENEMIES + (wave_number - 1) // 2)
            enemy_types = self._get_enemy_mix_for_wave(wave_number, enemy_count)
            
            # Make the first enemy a boss
            boss_pos = map_generator.get_spawn_position('enemy', 0, enemy_count)
            self.spawn_queue.append({
                'type': enemy_types[0],
                'pos': boss_pos,
                'spawn_delay': 1.0,
                'is_boss': True
            })
            
            # Add remaining regular enemies
            for i, enemy_type in enumerate(enemy_types[1:], start=1):
                spawn_pos = map_generator.get_spawn_position('enemy', i, enemy_count)
                self.spawn_queue.append({
                    'type': enemy_type,
                    'pos': spawn_pos,
                    'spawn_delay': random.uniform(1.5, 3.0),
                    'is_boss': False
                })
        else:
            # Regular wave
            enemy_count = config.WAVE_BASE_ENEMIES + (wave_number - 1) * config.WAVE_ENEMY_INCREMENT
            enemy_types = self._get_enemy_mix_for_wave(wave_number, enemy_count)
            
            # Queue enemies for spawning
            for i, enemy_type in enumerate(enemy_types):
                spawn_pos = map_generator.get_spawn_position('enemy', i, enemy_count)
                self.spawn_queue.append({
                    'type': enemy_type,
                    'pos': spawn_pos,
                    'spawn_delay': random.uniform(0.5, 2.0),
                    'is_boss': False
                })
        
        self.spawn_timer = config.WAVE_BREAK_TIME
    
    def _get_enemy_mix_for_wave(self, wave_number: int, enemy_count: int) -> List[str]:
        """Determine enemy types for a wave"""
        enemy_types = []
        
        if wave_number == 1:
            # First wave - only rushers
            enemy_types = ['rusher'] * enemy_count
        
        elif wave_number == 2:
            # Second wave - rushers and snipers
            rushers = enemy_count // 2
            snipers = enemy_count - rushers
            enemy_types = ['rusher'] * rushers + ['sniper'] * snipers
        
        elif wave_number == 3:
            # Third wave - mixed types
            rushers = max(1, enemy_count // 3)
            snipers = max(1, enemy_count // 3)
            dodgers = max(1, enemy_count - rushers - snipers)
            enemy_types = (['rusher'] * rushers + 
                         ['sniper'] * snipers + 
                         ['dodger'] * dodgers)
        
        else:
            # Higher waves - all types with increasing difficulty
            types = ['rusher', 'sniper', 'dodger', 'flanker']
            weights = [0.3, 0.3, 0.25, 0.15]  # Adjust weights as needed
            
            for i in range(enemy_count):
                enemy_type = random.choices(types, weights)[0]
                enemy_types.append(enemy_type)
        
        # Shuffle to randomize spawn order
        random.shuffle(enemy_types)
        return enemy_types
    
    def update(self, dt: float, player, all_entities: List, current_time: float,
               collision_manager, particle_emitter, bullets, game):
        """Update enemy spawner and enemies"""
        # Handle spawning
        if self.spawn_timer > 0:
            self.spawn_timer -= dt
        
        elif self.spawn_queue:
            # Spawn next enemy
            spawn_data = self.spawn_queue.pop(0)
            enemy = self._create_enemy(spawn_data['type'], spawn_data['pos'])
            
            # Make this enemy a boss if specified
            if spawn_data.get('is_boss', False):
                enemy.make_boss()
            
            # Set up enemy
            enemy.set_collision_manager(collision_manager)
            enemy.set_particle_emitter(particle_emitter)
            enemy.set_bullet_list(bullets)
            enemy.set_game_reference(game)
            
            # Set up AI behavior
            if enemy.enemy_type == 'rusher':
                enemy.ai_behavior = RusherAI(enemy, collision_manager)
            elif enemy.enemy_type == 'sniper':
                enemy.ai_behavior = SniperAI(enemy, collision_manager)
            elif enemy.enemy_type == 'dodger':
                enemy.ai_behavior = DodgerAI(enemy, collision_manager)
            elif enemy.enemy_type == 'flanker':
                enemy.ai_behavior = FlankerAI(enemy, collision_manager)
            
            self.enemies.append(enemy)
            
            # Set timer for next spawn
            if self.spawn_queue:
                self.spawn_timer = self.spawn_queue[0]['spawn_delay']
        
        # Update existing enemies
        for enemy in self.enemies[:]:
            enemy.update(dt, player, all_entities, current_time)
            
            # Remove dead enemies
            if enemy.is_dead():
                self.enemies.remove(enemy)
    
    def _create_enemy(self, enemy_type: str, pos: Tuple[float, float]) -> Enemy:
        """Create an enemy of the specified type"""
        if enemy_type == 'rusher':
            return Rusher(pos)
        elif enemy_type == 'sniper':
            return Sniper(pos)
        elif enemy_type == 'dodger':
            return Dodger(pos)
        elif enemy_type == 'flanker':
            return Flanker(pos)
        else:
            return Rusher(pos)  # Default fallback
    
    def draw(self, screen: pygame.Surface):
        """Draw all enemies"""
        for enemy in self.enemies:
            enemy.draw(screen)
    
    def get_active_enemies(self) -> List[Enemy]:
        """Get list of active enemies"""
        return self.enemies
    
    def get_enemy_count(self) -> int:
        """Get number of active enemies"""
        return len(self.enemies)
    
    def is_wave_complete(self) -> bool:
        """Check if current wave is complete"""
        return len(self.spawn_queue) == 0 and len(self.enemies) == 0
    
    def clear_all_enemies(self):
        """Clear all enemies"""
        self.enemies.clear()
        self.spawn_queue.clear()