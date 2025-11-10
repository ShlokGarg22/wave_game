"""
Death Circuit - User Interface
Handles HUD, menus, and game state displays
"""

import pygame
import math
from typing import Tuple, List, Optional
from utils import clamp
import config


class UI:
    """Main UI manager"""
    
    def __init__(self):
        pygame.font.init()
        
        # Fonts
        self.font_small = pygame.font.Font(None, config.UI_FONT_SIZE_SMALL)
        self.font_medium = pygame.font.Font(None, config.UI_FONT_SIZE_MEDIUM)
        self.font_large = pygame.font.Font(None, config.UI_FONT_SIZE_LARGE)
        
        # Colors
        self.text_color = config.UI_TEXT_COLOR
        self.shadow_color = config.UI_SHADOW_COLOR
        
        # Crosshair
        self.crosshair_surface = self._create_crosshair()
        
        # Menu states
        self.current_menu = None
        self.button_hover = None
        
        # Statistics display
        self.stats_surface = None
        self.stats_timer = 0
    
    def _create_crosshair(self) -> pygame.Surface:
        """Create crosshair surface"""
        size = config.CROSSHAIR_SIZE
        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Draw crosshair
        center_x, center_y = size, size
        
        # Horizontal line
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x - size//2, center_y), 
                        (center_x + size//2, center_y), 2)
        
        # Vertical line
        pygame.draw.line(surface, (255, 255, 255), 
                        (center_x, center_y - size//2), 
                        (center_x, center_y + size//2), 2)
        
        # Center dot
        pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), 2)
        
        return surface
    
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """Update UI elements"""
        self.stats_timer += dt
        
        # Update button hover states
        self.button_hover = None
        if self.current_menu:
            for button in self.current_menu.buttons:
                if button.is_hovered(mouse_pos):
                    self.button_hover = button
                    break
    
    def draw(self, screen: pygame.Surface, game_state: str, player=None, 
             wave_info=None, enemies_remaining=0):
        """Draw UI elements"""
        if game_state == 'PLAYING':
            self._draw_hud(screen, player, wave_info, enemies_remaining)
            self._draw_crosshair(screen)
        
        elif game_state == 'MENU':
            self._draw_main_menu(screen)
        
        elif game_state == 'GAME_OVER':
            self._draw_game_over(screen, player)
        
        elif game_state == 'PAUSED':
            self._draw_pause_menu(screen)
    
    def _draw_hud(self, screen: pygame.Surface, player, wave_info, enemies_remaining):
        """Draw in-game HUD"""
        if not player:
            return
        
        # Health bar (top-left)
        self._draw_health_bar(screen, player)
        
        # Ammo counter (bottom-right)
        self._draw_ammo_counter(screen, player)
        
        # Wave info (top-center)
        self._draw_wave_info(screen, wave_info, enemies_remaining)
        
        # Low health warning
        if player.health < player.max_health * 0.3:
            self._draw_low_health_warning(screen)
    
    def _draw_health_bar(self, screen: pygame.Surface, player):
        """Draw player health bar"""
        x, y = 20, 20
        width = config.HEALTH_BAR_WIDTH
        height = config.HEALTH_BAR_HEIGHT
        
        # Background
        pygame.draw.rect(screen, config.HEALTH_BAR_BG, (x, y, width, height))
        
        # Health bar
        health_ratio = player.health / player.max_health
        health_width = int(width * health_ratio)
        
        # Gradient color
        if health_ratio > 0.6:
            color = (0, 255, 0)  # Green
        elif health_ratio > 0.3:
            color = (255, 255, 0)  # Yellow
        else:
            color = (255, 0, 0)  # Red
        
        pygame.draw.rect(screen, color, (x, y, health_width, height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)
        
        # Health text
        health_text = f"{int(player.health)}/{int(player.max_health)}"
        text_surface = self.font_small.render(health_text, True, self.text_color)
        text_x = x + width // 2 - text_surface.get_width() // 2
        text_y = y + height + 5
        screen.blit(text_surface, (text_x, text_y))
    
    def _draw_ammo_counter(self, screen: pygame.Surface, player):
        """Draw weapon and ammo counter"""
        weapon_info = player.get_weapon_info()
        
        x = config.SCREEN_WIDTH - 170
        y = config.SCREEN_HEIGHT - 60
        
        # Weapon name
        weapon_text = weapon_info['name']
        text_surface = self.font_medium.render(weapon_text, True, self.text_color)
        screen.blit(text_surface, (x, y))
        
        # Ammo bar
        ammo_y = y + 25
        ammo_width = config.AMMO_BAR_WIDTH
        ammo_height = config.AMMO_BAR_HEIGHT
        
        # Background
        pygame.draw.rect(screen, config.AMMO_BAR_BG, (x, ammo_y, ammo_width, ammo_height))
        
        # Ammo bar
        ammo_ratio = weapon_info['ammo_ratio']
        ammo_bar_width = int(ammo_width * ammo_ratio)
        
        # Color based on ammo
        if ammo_ratio > 0.5:
            color = (0, 200, 255)  # Cyan
        elif ammo_ratio > 0.2:
            color = (255, 200, 0)  # Orange
        else:
            color = (255, 0, 0)  # Red
        
        pygame.draw.rect(screen, color, (x, ammo_y, ammo_bar_width, ammo_height))
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (x, ammo_y, ammo_width, ammo_height), 2)
        
        # Ammo text
        ammo_text = f"{weapon_info['ammo']}/{weapon_info['magazine_size']}"
        text_surface = self.font_small.render(ammo_text, True, self.text_color)
        text_x = x + ammo_width // 2 - text_surface.get_width() // 2
        text_y = ammo_y + ammo_height + 5
        screen.blit(text_surface, (text_x, text_y))
        
        # Reload indicator
        if weapon_info['is_reloading']:
            reload_text = "RELOADING..."
            text_surface = self.font_small.render(reload_text, True, (255, 100, 100))
            text_x = x + ammo_width // 2 - text_surface.get_width() // 2
            screen.blit(text_surface, (text_x, text_y + 20))
    
    def _draw_wave_info(self, screen: pygame.Surface, wave_info, enemies_remaining):
        """Draw wave information"""
        if not wave_info:
            return
        
        x = config.SCREEN_WIDTH // 2
        y = 20
        
        # Check if this is a boss wave
        is_boss_wave = (wave_info['number'] % config.BOSS_WAVE_INTERVAL == 0)
        
        # Wave number
        wave_text = f"WAVE {wave_info['number']}"
        if is_boss_wave:
            wave_text = f"⚔ BOSS WAVE {wave_info['number']} ⚔"
            wave_color = (255, 215, 0)  # Gold color for boss waves
        else:
            wave_color = self.text_color
            
        text_surface = self.font_large.render(wave_text, True, wave_color)
        text_rect = text_surface.get_rect(centerx=x, y=y)
        screen.blit(text_surface, text_rect)
        
        # Enemies remaining
        enemies_text = f"{enemies_remaining} ENEMIES REMAINING"
        text_surface = self.font_small.render(enemies_text, True, self.text_color)
        text_rect = text_surface.get_rect(centerx=x, y=y + 40)
        screen.blit(text_surface, text_rect)
    
    def _draw_crosshair(self, screen: pygame.Surface):
        """Draw mouse crosshair"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x = mouse_x - self.crosshair_surface.get_width() // 2
        y = mouse_y - self.crosshair_surface.get_height() // 2
        screen.blit(self.crosshair_surface, (x, y))
    
    def _draw_low_health_warning(self, screen: pygame.Surface):
        """Draw low health warning overlay"""
        alpha = int(100 * (1 + math.sin(self.stats_timer * 5)) / 2)
        warning_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        warning_surface.fill((255, 0, 0, alpha))
        
        # Vignette effect
        center_x = config.SCREEN_WIDTH // 2
        center_y = config.SCREEN_HEIGHT // 2
        
        for radius in range(100, 300, 50):
            pygame.draw.circle(warning_surface, (255, 0, 0, alpha // 2), 
                             (center_x, center_y), radius, 10)
        
        screen.blit(warning_surface, (0, 0))
    
    def _draw_main_menu(self, screen: pygame.Surface):
        """Draw main menu"""
        # Background
        screen.fill((0, 0, 0))
        
        # Title
        title_text = "DEATH CIRCUIT"
        title_surface = self.font_large.render(title_text, True, self.text_color)
        title_x = config.SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        title_y = config.SCREEN_HEIGHT // 3
        screen.blit(title_surface, (title_x, title_y))
        
        # Subtitle
        subtitle_text = "2D Combat Arena"
        subtitle_surface = self.font_medium.render(subtitle_text, True, (100, 100, 100))
        subtitle_x = config.SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2
        subtitle_y = title_y + 60
        screen.blit(subtitle_surface, (subtitle_x, subtitle_y))
        
        # Menu buttons
        buttons = [
            ("START GAME", config.SCREEN_HEIGHT // 2),
            ("CONTROLS", config.SCREEN_HEIGHT // 2 + 80),
            ("QUIT", config.SCREEN_HEIGHT // 2 + 160)
        ]
        
        for text, y_pos in buttons:
            # Button background
            button_width = 200
            button_height = 50
            button_x = config.SCREEN_WIDTH // 2 - button_width // 2
            button_rect = pygame.Rect(button_x, y_pos - button_height // 2, button_width, button_height)
            
            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            color = (50, 50, 80) if is_hovered else (30, 30, 50)
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
            
            # Button text
            text_surface = self.font_medium.render(text, True, self.text_color)
            text_x = button_x + button_width // 2 - text_surface.get_width() // 2
            text_y = y_pos - text_surface.get_height() // 2
            screen.blit(text_surface, (text_x, text_y))
    
    def _draw_game_over(self, screen: pygame.Surface, player):
        """Draw game over screen"""
        # Background overlay
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = "GAME OVER"
        text_surface = self.font_large.render(game_over_text, True, (255, 0, 0))
        text_x = config.SCREEN_WIDTH // 2 - text_surface.get_width() // 2
        text_y = config.SCREEN_HEIGHT // 4
        screen.blit(text_surface, (text_x, text_y))
        
        # Statistics
        if player:
            stats_y = config.SCREEN_HEIGHT // 2 - 100
            stats = [
                f"Waves Survived: {player.game.wave_number - 1}",
                f"Enemies Killed: {player.kills}",
                f"Damage Dealt: {player.damage_dealt}",
                f"Time Alive: {int(player.time_alive // 60)}:{int(player.time_alive % 60):02d}"
            ]
            
            for i, stat in enumerate(stats):
                text_surface = self.font_medium.render(stat, True, self.text_color)
                text_x = config.SCREEN_WIDTH // 2 - text_surface.get_width() // 2
                text_y = stats_y + i * 40
                screen.blit(text_surface, (text_x, text_y))
        
        # Restart button
        button_width = 200
        button_height = 50
        button_x = config.SCREEN_WIDTH // 2 - button_width // 2
        button_y = config.SCREEN_HEIGHT * 3 // 4
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Check hover
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_pos)
        
        color = (50, 50, 80) if is_hovered else (30, 30, 50)
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
        
        # Button text
        restart_text = "RESTART"
        text_surface = self.font_medium.render(restart_text, True, self.text_color)
        text_x = button_x + button_width // 2 - text_surface.get_width() // 2
        text_y = button_y + button_height // 2 - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def _draw_pause_menu(self, screen: pygame.Surface):
        """Draw pause menu"""
        # Background overlay
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = "PAUSED"
        text_surface = self.font_large.render(pause_text, True, self.text_color)
        text_x = config.SCREEN_WIDTH // 2 - text_surface.get_width() // 2
        text_y = config.SCREEN_HEIGHT // 3
        screen.blit(text_surface, (text_x, text_y))
        
        # Resume button
        button_width = 200
        button_height = 50
        button_x = config.SCREEN_WIDTH // 2 - button_width // 2
        button_y = config.SCREEN_HEIGHT // 2
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Check hover
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_pos)
        
        color = (50, 50, 80) if is_hovered else (30, 30, 50)
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
        
        # Button text
        resume_text = "RESUME"
        text_surface = self.font_medium.render(resume_text, True, self.text_color)
        text_x = button_x + button_width // 2 - text_surface.get_width() // 2
        text_y = button_y + button_height // 2 - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def handle_click(self, mouse_pos: Tuple[int, int], game_state: str) -> str:
        """Handle mouse clicks on UI elements"""
        if game_state == 'MENU':
            return self._handle_menu_click(mouse_pos)
        elif game_state == 'GAME_OVER':
            return self._handle_game_over_click(mouse_pos)
        elif game_state == 'PAUSED':
            return self._handle_pause_click(mouse_pos)
        
        return game_state
    
    def _handle_menu_click(self, mouse_pos: Tuple[int, int]) -> str:
        """Handle main menu clicks"""
        buttons = [
            ("START GAME", config.SCREEN_HEIGHT // 2, 'PLAYING'),
            ("CONTROLS", config.SCREEN_HEIGHT // 2 + 80, 'CONTROLS'),
            ("QUIT", config.SCREEN_HEIGHT // 2 + 160, 'QUIT')
        ]
        
        for text, y_pos, next_state in buttons:
            button_width = 200
            button_height = 50
            button_x = config.SCREEN_WIDTH // 2 - button_width // 2
            button_rect = pygame.Rect(button_x, y_pos - button_height // 2, button_width, button_height)
            
            if button_rect.collidepoint(mouse_pos):
                return next_state
        
        return 'MENU'
    
    def _handle_game_over_click(self, mouse_pos: Tuple[int, int]) -> str:
        """Handle game over clicks"""
        button_width = 200
        button_height = 50
        button_x = config.SCREEN_WIDTH // 2 - button_width // 2
        button_y = config.SCREEN_HEIGHT * 3 // 4
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mouse_pos):
            return 'RESTART'
        
        return 'GAME_OVER'
    
    def _handle_pause_click(self, mouse_pos: Tuple[int, int]) -> str:
        """Handle pause menu clicks"""
        button_width = 200
        button_height = 50
        button_x = config.SCREEN_WIDTH // 2 - button_width // 2
        button_y = config.SCREEN_HEIGHT // 2
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        if button_rect.collidepoint(mouse_pos):
            return 'PLAYING'
        
        return 'PAUSED'
    
    def draw_controls_screen(self, screen: pygame.Surface):
        """Draw controls screen"""
        screen.fill((0, 0, 0))
        
        # Title
        title_text = "CONTROLS"
        title_surface = self.font_large.render(title_text, True, self.text_color)
        title_x = config.SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        title_y = 50
        screen.blit(title_surface, (title_x, title_y))
        
        # Controls list
        controls = [
            ("Movement", "WASD"),
            ("Aim", "Mouse"),
            ("Shoot", "Left Click"),
            ("Reload", "R"),
            ("Weapon 1", "1"),
            ("Weapon 2", "2"),
            ("Weapon 3", "3"),
            ("Weapon 4", "4"),
            ("Pause", "ESC")
        ]
        
        y_pos = 150
        for action, key in controls:
            # Action text
            action_surface = self.font_medium.render(action, True, self.text_color)
            screen.blit(action_surface, (100, y_pos))
            
            # Key text
            key_surface = self.font_medium.render(key, True, (100, 200, 255))
            key_x = config.SCREEN_WIDTH - 200 - key_surface.get_width()
            screen.blit(key_surface, (key_x, y_pos))
            
            y_pos += 50
        
        # Back button
        back_text = "BACK"
        back_surface = self.font_medium.render(back_text, True, self.text_color)
        back_x = config.SCREEN_WIDTH // 2 - back_surface.get_width() // 2
        back_y = config.SCREEN_HEIGHT - 100
        screen.blit(back_surface, (back_x, back_y))
        
        # Back button rect for click detection
        self.back_button_rect = pygame.Rect(back_x - 20, back_y - 10, 
                                          back_surface.get_width() + 40, 
                                          back_surface.get_height() + 20)