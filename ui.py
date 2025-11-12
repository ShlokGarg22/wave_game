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
             wave_info=None, enemies_remaining=0, fps=0, entity_counts=None):
        """Draw UI elements"""
        if game_state == 'PLAYING':
            self._draw_hud(screen, player, wave_info, enemies_remaining, fps, entity_counts)
            self._draw_crosshair(screen)
        
        elif game_state == 'MENU':
            self._draw_main_menu(screen)
        
        elif game_state == 'SETTINGS':
            self._draw_settings_menu(screen)
        
        elif game_state == 'GAME_OVER':
            self._draw_game_over(screen, player)
        
        elif game_state == 'PAUSED':
            self._draw_pause_menu(screen)
    
    def _draw_hud(self, screen: pygame.Surface, player, wave_info, enemies_remaining, fps=0, entity_counts=None):
        """Draw in-game HUD"""
        if not player:
            return
        
        # Health bar (top-left)
        self._draw_health_bar(screen, player)
        
        # Ammo counter (bottom-right)
        self._draw_ammo_counter(screen, player)
        
        # Dash cooldown indicator (bottom-left)
        if config.DASH_ENABLED:
            self._draw_dash_cooldown(screen, player)
        
        # Wave info (top-center)
        self._draw_wave_info(screen, wave_info, enemies_remaining)
        
        # FPS counter and performance stats (top-right)
        self._draw_performance_stats(screen, fps, entity_counts)
        
        # Low health warning
        if config.LOW_HEALTH_WARNING_ENABLED and player.health < player.max_health * 0.3:
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
    
    def _draw_dash_cooldown(self, screen: pygame.Surface, player):
        """Draw dash ability cooldown indicator"""
        x, y = 20, config.SCREEN_HEIGHT - 80
        size = 60
        
        # Background circle
        pygame.draw.circle(screen, (40, 40, 40), (x + size // 2, y + size // 2), size // 2)
        pygame.draw.circle(screen, (100, 100, 100), (x + size // 2, y + size // 2), size // 2, 2)
        
        # Dash icon (lightning bolt style)
        icon_color = (100, 200, 255) if player.dash_cooldown <= 0 else (60, 60, 60)
        center_x = x + size // 2
        center_y = y + size // 2
        
        # Draw lightning bolt icon
        points = [
            (center_x, center_y - 15),
            (center_x - 5, center_y),
            (center_x + 2, center_y),
            (center_x - 8, center_y + 15),
            (center_x + 5, center_y - 2),
            (center_x - 2, center_y - 2)
        ]
        pygame.draw.polygon(screen, icon_color, points)
        
        # Cooldown overlay (arc that fills up)
        if player.dash_cooldown > 0:
            cooldown_ratio = player.dash_cooldown / config.DASH_COOLDOWN
            # Draw dark arc for cooldown progress
            angle_start = -90  # Top of circle
            angle_sweep = int(360 * cooldown_ratio)
            
            # Draw pie slice for cooldown
            points = [(center_x, center_y)]
            for angle in range(angle_start, angle_start + angle_sweep + 1, 5):
                rad = math.radians(angle)
                point_x = center_x + math.cos(rad) * (size // 2 - 2)
                point_y = center_y + math.sin(rad) * (size // 2 - 2)
                points.append((int(point_x), int(point_y)))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, (20, 20, 20, 180), points)
        
        # Dash text
        dash_text = "DASH"
        text_surface = self.font_small.render(dash_text, True, self.text_color)
        text_x = x + size // 2 - text_surface.get_width() // 2
        screen.blit(text_surface, (text_x, y + size + 5))
        
        # Cooldown text
        if player.dash_cooldown > 0:
            cooldown_text = f"{player.dash_cooldown:.1f}s"
            text_surface = self.font_small.render(cooldown_text, True, (255, 100, 100))
            text_x = x + size // 2 - text_surface.get_width() // 2
            screen.blit(text_surface, (text_x, y + size + 25))
    
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
    
    def _draw_performance_stats(self, screen: pygame.Surface, fps=0, entity_counts=None):
        """Draw FPS counter and entity counts"""
        x = config.SCREEN_WIDTH - 150
        y = 20
        
        # FPS
        fps_color = (0, 255, 0) if fps >= 50 else (255, 255, 0) if fps >= 30 else (255, 0, 0)
        fps_text = f"FPS: {int(fps)}"
        text_surface = self.font_small.render(fps_text, True, fps_color)
        screen.blit(text_surface, (x, y))
        
        # Entity counts if provided
        if entity_counts:
            y += 25
            bullets_text = f"Bullets: {entity_counts.get('bullets', 0)}"
            text_surface = self.font_small.render(bullets_text, True, self.text_color)
            screen.blit(text_surface, (x, y))
            
            y += 20
            particles_text = f"Particles: {entity_counts.get('particles', 0)}"
            text_surface = self.font_small.render(particles_text, True, self.text_color)
            screen.blit(text_surface, (x, y))
            
            y += 20
            enemies_text = f"Enemies: {entity_counts.get('enemies', 0)}"
            text_surface = self.font_small.render(enemies_text, True, self.text_color)
            screen.blit(text_surface, (x, y))
    
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
            ("START GAME", config.SCREEN_HEIGHT // 2 - 80),
            ("DIFFICULTY: " + config.get_difficulty_name().upper(), config.SCREEN_HEIGHT // 2 - 10),
            ("SETTINGS", config.SCREEN_HEIGHT // 2 + 60),
            ("CONTROLS", config.SCREEN_HEIGHT // 2 + 130),
            ("QUIT", config.SCREEN_HEIGHT // 2 + 200)
        ]
        
        for text, y_pos in buttons:
            # Button background
            button_width = 300 if "DIFFICULTY" in text else 200
            button_height = 50
            button_x = config.SCREEN_WIDTH // 2 - button_width // 2
            button_rect = pygame.Rect(button_x, y_pos - button_height // 2, button_width, button_height)
            
            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            # Color based on difficulty if it's the difficulty button
            if "DIFFICULTY" in text:
                if "EASY" in text:
                    base_color = (50, 80, 50)
                elif "NORMAL" in text:
                    base_color = (50, 50, 80)
                elif "HARD" in text:
                    base_color = (80, 50, 50)
                elif "NIGHTMARE" in text:
                    base_color = (80, 20, 20)
                else:
                    base_color = (30, 30, 50)
                color = tuple(min(c + 20, 255) for c in base_color) if is_hovered else base_color
            else:
                color = (50, 50, 80) if is_hovered else (30, 30, 50)
            
            pygame.draw.rect(screen, color, button_rect)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)
            
            # Button text
            text_surface = self.font_medium.render(text, True, self.text_color)
            text_x = button_x + button_width // 2 - text_surface.get_width() // 2
            text_y = y_pos - text_surface.get_height() // 2
            screen.blit(text_surface, (text_x, text_y))
        
        # Difficulty description
        diff_desc = config.DIFFICULTY_SETTINGS[config.CURRENT_DIFFICULTY]['description']
        desc_surface = self.font_small.render(diff_desc, True, (150, 150, 150))
        desc_x = config.SCREEN_WIDTH // 2 - desc_surface.get_width() // 2
        desc_y = config.SCREEN_HEIGHT // 2 + 20
        screen.blit(desc_surface, (desc_x, desc_y))
    
    def _draw_settings_menu(self, screen: pygame.Surface):
        """Draw settings menu"""
        # Background
        screen.fill((0, 0, 0))
        
        # Title
        title_text = "SETTINGS"
        title_surface = self.font_large.render(title_text, True, self.text_color)
        title_x = config.SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        title_y = 100
        screen.blit(title_surface, (title_x, title_y))
        
        # Screen Effects Section
        section_text = "Screen Effects"
        section_surface = self.font_medium.render(section_text, True, (150, 150, 150))
        section_x = config.SCREEN_WIDTH // 2 - section_surface.get_width() // 2
        section_y = 200
        screen.blit(section_surface, (section_x, section_y))
        
        # Checkboxes for screen effects
        checkbox_size = 30
        checkbox_x = config.SCREEN_WIDTH // 2 - 200
        start_y = 260
        spacing = 60
        
        settings_list = [
            ("Screen Shake", config.SCREEN_SHAKE_ENABLED, "Shake screen on hit"),
            ("Screen Flash", config.SCREEN_FLASH_ENABLED, "Flash effects on damage"),
            ("Hit Stop", config.HIT_STOP_ENABLED, "Brief freeze on impact"),
            ("Low Health Warning", config.LOW_HEALTH_WARNING_ENABLED, "Red vignette at low HP")
        ]
        
        for i, (label, enabled, description) in enumerate(settings_list):
            y_pos = start_y + i * spacing
            
            # Checkbox background
            checkbox_rect = pygame.Rect(checkbox_x, y_pos, checkbox_size, checkbox_size)
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = checkbox_rect.collidepoint(mouse_pos)
            
            # Draw checkbox
            color = (60, 60, 80) if is_hovered else (40, 40, 60)
            pygame.draw.rect(screen, color, checkbox_rect)
            pygame.draw.rect(screen, (255, 255, 255), checkbox_rect, 2)
            
            # Draw checkmark if enabled
            if enabled:
                check_points = [
                    (checkbox_x + 5, y_pos + checkbox_size // 2),
                    (checkbox_x + checkbox_size // 3, y_pos + checkbox_size - 8),
                    (checkbox_x + checkbox_size - 5, y_pos + 5)
                ]
                pygame.draw.lines(screen, (0, 255, 0), False, check_points, 3)
            
            # Label text
            label_surface = self.font_medium.render(label, True, self.text_color)
            label_x = checkbox_x + checkbox_size + 15
            label_y = y_pos + checkbox_size // 2 - label_surface.get_height() // 2
            screen.blit(label_surface, (label_x, label_y))
            
            # Description text
            desc_surface = self.font_small.render(description, True, (120, 120, 120))
            desc_x = label_x
            desc_y = label_y + 25
            screen.blit(desc_surface, (desc_x, desc_y))
        
        # Back button
        back_button_width = 200
        back_button_height = 50
        back_button_x = config.SCREEN_WIDTH // 2 - back_button_width // 2
        back_button_y = config.SCREEN_HEIGHT - 100
        back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = back_button_rect.collidepoint(mouse_pos)
        color = (50, 50, 80) if is_hovered else (30, 30, 50)
        
        pygame.draw.rect(screen, color, back_button_rect)
        pygame.draw.rect(screen, (255, 255, 255), back_button_rect, 2)
        
        back_text = "BACK"
        back_surface = self.font_medium.render(back_text, True, self.text_color)
        back_x = back_button_x + back_button_width // 2 - back_surface.get_width() // 2
        back_y = back_button_y + back_button_height // 2 - back_surface.get_height() // 2
        screen.blit(back_surface, (back_x, back_y))
    
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
        elif game_state == 'SETTINGS':
            return self._handle_settings_click(mouse_pos)
        elif game_state == 'GAME_OVER':
            return self._handle_game_over_click(mouse_pos)
        elif game_state == 'PAUSED':
            return self._handle_pause_click(mouse_pos)
        
        return game_state
    
    def _handle_menu_click(self, mouse_pos: Tuple[int, int]) -> str:
        """Handle main menu clicks"""
        buttons = [
            ("START GAME", config.SCREEN_HEIGHT // 2 - 80, 200, 'PLAYING'),
            ("DIFFICULTY: " + config.get_difficulty_name().upper(), config.SCREEN_HEIGHT // 2 - 10, 300, 'DIFFICULTY'),
            ("SETTINGS", config.SCREEN_HEIGHT // 2 + 60, 200, 'SETTINGS'),
            ("CONTROLS", config.SCREEN_HEIGHT // 2 + 130, 200, 'CONTROLS'),
            ("QUIT", config.SCREEN_HEIGHT // 2 + 200, 200, 'QUIT')
        ]
        
        for text, y_pos, width, next_state in buttons:
            button_width = width
            button_height = 50
            button_x = config.SCREEN_WIDTH // 2 - button_width // 2
            button_rect = pygame.Rect(button_x, y_pos - button_height // 2, button_width, button_height)
            
            if button_rect.collidepoint(mouse_pos):
                return next_state
        
        return 'MENU'
    
    def _handle_settings_click(self, mouse_pos: Tuple[int, int]) -> str:
        """Handle settings menu clicks"""
        # Checkbox parameters
        checkbox_size = 30
        checkbox_x = config.SCREEN_WIDTH // 2 - 200
        start_y = 260
        spacing = 60
        
        settings_list = [
            ("SCREEN_SHAKE_ENABLED", config.SCREEN_SHAKE_ENABLED),
            ("SCREEN_FLASH_ENABLED", config.SCREEN_FLASH_ENABLED),
            ("HIT_STOP_ENABLED", config.HIT_STOP_ENABLED),
            ("LOW_HEALTH_WARNING_ENABLED", config.LOW_HEALTH_WARNING_ENABLED)
        ]
        
        # Check checkbox clicks
        for i, (setting_name, _) in enumerate(settings_list):
            y_pos = start_y + i * spacing
            checkbox_rect = pygame.Rect(checkbox_x, y_pos, checkbox_size, checkbox_size)
            
            if checkbox_rect.collidepoint(mouse_pos):
                # Toggle setting in config
                current_value = getattr(config, setting_name)
                setattr(config, setting_name, not current_value)
                return 'SETTINGS'
        
        # Check back button
        back_button_width = 200
        back_button_height = 50
        back_button_x = config.SCREEN_WIDTH // 2 - back_button_width // 2
        back_button_y = config.SCREEN_HEIGHT - 100
        back_button_rect = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
        
        if back_button_rect.collidepoint(mouse_pos):
            return 'MENU'
        
        return 'SETTINGS'
    
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