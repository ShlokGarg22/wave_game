"""
Death Circuit - Main Game File
Entry point and game loop management
"""

import pygame
import sys
import random
import time
from typing import List, Optional

# Import game modules
import config
from player import Player
from enemy import EnemySpawner
from bullet import BulletManager
from map import MapGenerator
from ui import UI
from collision import CollisionManager
from particle_system import ParticleEmitter
from utils import distance, vector_from_angle, normalize_vector


class Game:
    """Main game class"""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            # Audio not available, continue without sound
            print("Warning: Audio system not available, running without sound")
        
        # Set up display
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Death Circuit - 2D Combat Arena")
        
        # Clock for frame rate control
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_state = config.STATE_MENU
        self.running = True
        self.paused = False
        
        # Game objects
        self.player = None
        self.enemy_spawner = EnemySpawner()
        self.bullet_manager = BulletManager()
        self.map_generator = MapGenerator()
        self.collision_manager = CollisionManager()
        self.particle_emitter = ParticleEmitter()
        self.ui = UI()
        
        # Game timing
        self.current_time = 0
        self.last_time = pygame.time.get_ticks() / 1000.0
        self.wave_number = 1
        self.wave_break_timer = 0
        self.enemies_remaining = 0
        
        # Statistics
        self.total_kills = 0
        self.highest_wave = 0
        
        # Initialize game
        self._initialize_game()
    
    def _initialize_game(self):
        """Initialize game objects"""
        # Create player
        player_spawn = self.map_generator.get_spawn_position('player', 0, 1)
        self.player = Player(player_spawn)
        
        # Set up player references
        self.player.set_collision_manager(self.collision_manager)
        self.player.set_particle_emitter(self.particle_emitter)
        self.player.set_bullet_list(self.bullet_manager)
        self.player.game = self  # Reference back to game
        
        # Generate initial map
        self._generate_new_map()
    
    def _generate_new_map(self):
        """Generate a new map for the current wave"""
        walls = self.map_generator.generate_arena(self.wave_number)
        self.collision_manager.set_walls(walls)
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Calculate delta time
            current_ticks = pygame.time.get_ticks() / 1000.0
            dt = current_ticks - self.last_time
            self.last_time = current_ticks
            self.current_time = current_ticks
            
            # Limit frame rate
            dt = min(dt, 1/30)  # Prevent large time steps
            
            # Handle events
            self._handle_events()
            
            # Update game state
            if self.game_state == config.STATE_PLAYING and not self.paused:
                self._update_game(dt)
            
            # Draw everything
            self._draw()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(config.FPS)
        
        # Quit
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event.key)
            
            elif event.type == pygame.KEYUP:
                self._handle_key_up(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event.button, event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event.button, event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
    
    def _handle_key_down(self, key):
        """Handle key press"""
        if self.game_state == config.STATE_MENU:
            if key == pygame.K_RETURN:
                self.start_game()
            elif key == pygame.K_ESCAPE:
                self.running = False
        
        elif self.game_state == config.STATE_PLAYING:
            if key == config.KEY_PAUSE:
                self.paused = not self.paused
            else:
                self.player.keys_pressed.add(key)
        
        elif self.game_state == config.STATE_GAME_OVER:
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.restart_game()
            elif key == pygame.K_ESCAPE:
                self.game_state = config.STATE_MENU
        
        elif self.game_state == 'CONTROLS':
            if key == pygame.K_ESCAPE or key == pygame.K_RETURN:
                self.game_state = config.STATE_MENU
    
    def _handle_key_up(self, key):
        """Handle key release"""
        if self.game_state == config.STATE_PLAYING:
            self.player.keys_pressed.discard(key)
    
    def _handle_mouse_down(self, button, pos):
        """Handle mouse button press"""
        if self.game_state == config.STATE_PLAYING:
            if button == pygame.BUTTON_LEFT:
                self.player.mouse_pressed = True
        
        elif self.game_state in [config.STATE_MENU, config.STATE_GAME_OVER, config.STATE_PAUSED]:
            new_state = self.ui.handle_click(pos, self._get_ui_game_state())
            self._handle_ui_state_change(new_state)
    
    def _handle_mouse_up(self, button, pos):
        """Handle mouse button release"""
        if self.game_state == config.STATE_PLAYING:
            if button == pygame.BUTTON_LEFT:
                self.player.mouse_pressed = False
    
    def _handle_mouse_motion(self, pos):
        """Handle mouse movement"""
        if self.game_state == config.STATE_PLAYING:
            self.player.mouse_pos = pos
    
    def _get_ui_game_state(self):
        """Get current game state for UI"""
        if self.game_state == config.STATE_MENU:
            return 'MENU'
        elif self.game_state == config.STATE_GAME_OVER:
            return 'GAME_OVER'
        elif self.paused:
            return 'PAUSED'
        else:
            return 'PLAYING'
    
    def _handle_ui_state_change(self, new_state):
        """Handle UI state changes"""
        if new_state == 'PLAYING':
            if self.game_state == config.STATE_MENU:
                self.start_game()
            elif self.paused:
                self.paused = False
        
        elif new_state == 'RESTART':
            self.restart_game()
        
        elif new_state == 'QUIT':
            self.running = False
        
        elif new_state == 'CONTROLS':
            self.game_state = 'CONTROLS'
        
        elif new_state == 'SETTINGS':
            self.game_state = 'SETTINGS'
        
        elif new_state == 'MENU':
            self.game_state = config.STATE_MENU
        
        elif new_state == 'DIFFICULTY':
            # Cycle through difficulties
            difficulties = [config.DIFFICULTY_EASY, config.DIFFICULTY_NORMAL, 
                          config.DIFFICULTY_HARD, config.DIFFICULTY_NIGHTMARE]
            current_index = difficulties.index(config.CURRENT_DIFFICULTY)
            next_index = (current_index + 1) % len(difficulties)
            config.set_difficulty(difficulties[next_index])
    
    def _update_game(self, dt):
        """Update game logic"""
        # Update player
        self.player.update(dt, self.current_time)
        
        # Check if player is dead
        if self.player.is_dead():
            self.game_over()
            return
        
        # Update wave system
        self._update_wave_system(dt)
        
        # Update enemies
        all_entities = [self.player] + self.enemy_spawner.get_active_enemies()
        self.enemy_spawner.update(dt, self.player, all_entities, self.current_time,
                                self.collision_manager, self.particle_emitter,
                                self.bullet_manager, self)
        
        # Update bullets
        self.bullet_manager.update(dt)
        
        # Update particles
        self.particle_emitter.update(dt)
        
        # Update collision detection
        self._update_collision_detection()
        
        # Update UI
        mouse_pos = pygame.mouse.get_pos()
        self.ui.update(dt, mouse_pos)
        
        # Update enemy count
        self.enemies_remaining = self.enemy_spawner.get_enemy_count()
    
    def _update_wave_system(self, dt):
        """Update wave progression"""
        if self.enemy_spawner.is_wave_complete() and self.wave_break_timer <= 0:
            # Start next wave
            self.wave_number += 1
            self.highest_wave = max(self.highest_wave, self.wave_number)
            self._generate_new_map()
            self.enemy_spawner.start_wave(self.wave_number, self.map_generator)
            self.wave_break_timer = config.WAVE_BREAK_TIME
        
        elif self.wave_break_timer > 0:
            self.wave_break_timer -= dt
            
            # Heal player during wave break
            if self.wave_break_timer > 0:
                self.player.heal(config.PLAYER_REGEN_RATE * dt)
    
    def _update_collision_detection(self):
        """Update collision detection between game objects"""
        # Clear spatial grid
        self.collision_manager.clear_spatial_grid()
        
        # Add entities to spatial grid
        self.collision_manager.add_to_spatial_grid(self.player, self.player.pos, self.player.radius)
        
        for enemy in self.enemy_spawner.get_active_enemies():
            self.collision_manager.add_to_spatial_grid(enemy, enemy.pos, enemy.radius)
        
        # Bullet-entity collisions
        for bullet in self.bullet_manager.bullets[:]:
            if not bullet.alive:
                continue
            
            # Check collision with walls
            if self.collision_manager.check_bullet_wall_collision(bullet.pos, bullet.radius):
                # Create impact effect
                if self.particle_emitter:
                    wall_normal = (1, 0)  # Simplified normal
                    self.particle_emitter.create_impact_sparks(bullet.pos, wall_normal)
                bullet.alive = False
                continue
            
            # Check collision with entities
            hit_entities = self.collision_manager.check_bullet_entity_collision(
                bullet.pos, bullet.radius, self.enemy_spawner.get_active_enemies() + [self.player]
            )
            
            for entity in hit_entities:
                # Check if entity is alive (handle both Player and Enemy)
                entity_alive = not entity.is_dead() if isinstance(entity, Player) else entity.alive
                if entity_alive and bullet.owner_id != entity.id:
                    # Handle different take_damage signatures
                    if isinstance(entity, Player):
                        entity.take_damage(bullet.damage, self.current_time)
                        entity.damage_taken += bullet.damage
                    else:
                        entity.take_damage(bullet.damage, bullet.owner_id)
                    
                    # Mark bullet as hit
                    bullet.alive = False
                    
                    # Create hit effect
                    if self.particle_emitter:
                        hit_direction = normalize_vector((
                            bullet.velocity[0], bullet.velocity[1]
                        ))
                        self.particle_emitter.create_blood_splatter(bullet.pos, hit_direction)
                    
                    break  # Bullet can only hit one entity
        
        # Entity-entity collisions
        enemies = self.enemy_spawner.get_active_enemies()
        for i, enemy1 in enumerate(enemies):
            for enemy2 in enemies[i+1:]:
                if (self.collision_manager.check_entity_entity_collision(
                    enemy1.pos, enemy1.radius, enemy2.pos, enemy2.radius)):
                    
                    # Resolve collision
                    new_pos1, new_pos2 = self.collision_manager.resolve_entity_entity_collision(
                        enemy1.pos, enemy1.radius, enemy2.pos, enemy2.radius
                    )
                    enemy1.pos = list(new_pos1)
                    enemy2.pos = list(new_pos2)
        
        # Player-enemy collisions (contact damage)
        for enemy in enemies:
            if not enemy.alive:
                continue
            
            if self.collision_manager.check_entity_entity_collision(
                self.player.pos, self.player.radius, enemy.pos, enemy.radius):
                
                # Apply contact damage to player (with cooldown)
                time_since_last_contact = self.current_time - self.player.last_contact_damage_time
                if (not self.player.invincible and not enemy.invincible and 
                    time_since_last_contact >= config.ENEMY_CONTACT_COOLDOWN):
                    self.player.take_damage(config.ENEMY_CONTACT_DAMAGE, self.current_time)
                    self.player.last_contact_damage_time = self.current_time
                
                # Push player away from enemy
                new_player_pos, new_enemy_pos = self.collision_manager.resolve_entity_entity_collision(
                    self.player.pos, self.player.radius, enemy.pos, enemy.radius
                )
                self.player.pos = list(new_player_pos)
                enemy.pos = list(new_enemy_pos)
    
    def _draw(self):
        """Draw everything"""
        # Clear screen
        self.screen.fill(config.BACKGROUND_COLOR)
        
        if self.game_state == config.STATE_MENU:
            self.ui._draw_main_menu(self.screen)
        
        elif self.game_state == 'CONTROLS':
            self.ui.draw_controls_screen(self.screen)
        
        elif self.game_state in [config.STATE_PLAYING, config.STATE_PAUSED, config.STATE_GAME_OVER]:
            # Apply screen shake if needed
            shake_offset = self.player.get_screen_shake_offset()
            if shake_offset != (0, 0):
                # Create temporary surface for screen shake effect
                temp_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
                self._draw_game_world(temp_surface)
                self.screen.blit(temp_surface, shake_offset)
            else:
                self._draw_game_world(self.screen)
            
            # Draw UI overlay
            wave_info = {'number': self.wave_number} if self.wave_number > 0 else None
            fps = self.clock.get_fps()
            entity_counts = {
                'bullets': len(self.bullet_manager.bullets),
                'particles': len(self.particle_emitter.particles),
                'enemies': len(self.enemy_spawner.enemies)
            }
            self.ui.draw(self.screen, self._get_ui_game_state(), 
                        self.player, wave_info, self.enemies_remaining, fps, entity_counts)
    
    def _draw_game_world(self, screen):
        """Draw the game world (map, entities, bullets, particles)"""
        # Draw map
        self.map_generator.draw(screen)
        
        # Draw particles (background effects)
        self.particle_emitter.draw(screen)
        
        # Draw bullets
        self.bullet_manager.draw(screen)
        
        # Draw enemies
        self.enemy_spawner.draw(screen)
        
        # Draw player
        if self.player:
            self.player.draw(screen)
    
    def start_game(self):
        """Start a new game"""
        self.game_state = config.STATE_PLAYING
        self.paused = False
        self.wave_number = 1
        self.total_kills = 0
        
        # Reset player
        player_spawn = self.map_generator.get_spawn_position('player', 0, 1)
        self.player.reset(player_spawn)
        
        # Clear everything
        self.bullet_manager.clear_bullets()
        self.particle_emitter.clear_all_particles()
        self.enemy_spawner.clear_all_enemies()
        
        # Generate map and start first wave
        self._generate_new_map()
        self.enemy_spawner.start_wave(self.wave_number, self.map_generator)
    
    def restart_game(self):
        """Restart the game"""
        self.start_game()
    
    def on_enemy_killed(self, enemy, killer_id):
        """Handle enemy death"""
        self.total_kills += 1
        
        if killer_id == 'player':
            self.player.add_kill()
            self.player.add_damage_dealt(enemy.max_health)
    
    def game_over(self):
        """Handle game over"""
        self.game_state = config.STATE_GAME_OVER
        self.highest_wave = max(self.highest_wave, self.wave_number - 1)


def main():
    """Main entry point"""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()