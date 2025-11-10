"""
Death Circuit - Map Generation
Handles procedural arena generation and wall placement
"""

import pygame
import random
from typing import List, Tuple, Optional
from utils import line_of_sight
import config


class MapGenerator:
    """Generates procedural arena layouts"""
    
    def __init__(self):
        self.walls: List[pygame.Rect] = []
        self.spawn_zones: List[Tuple[int, int]] = []
        self.player_spawn = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        self._generate_spawn_zones()
    
    def _generate_spawn_zones(self):
        """Generate enemy spawn zones around the edges"""
        zones = []
        
        # Divide edges into zones
        edge_zones = 8
        
        # Top edge
        for i in range(edge_zones // 2):
            x = (config.SCREEN_WIDTH * i) // (edge_zones // 2 - 1)
            zones.append((x, 50))
        
        # Right edge
        for i in range(edge_zones // 2):
            y = (config.SCREEN_HEIGHT * i) // (edge_zones // 2 - 1)
            zones.append((config.SCREEN_WIDTH - 50, y))
        
        # Bottom edge
        for i in range(edge_zones // 2):
            x = config.SCREEN_WIDTH - ((config.SCREEN_WIDTH * i) // (edge_zones // 2 - 1)) - 50
            zones.append((x, config.SCREEN_HEIGHT - 50))
        
        # Left edge
        for i in range(edge_zones // 2):
            y = config.SCREEN_HEIGHT - ((config.SCREEN_HEIGHT * i) // (edge_zones // 2 - 1)) - 50
            zones.append((50, y))
        
        self.spawn_zones = zones
    
    def generate_arena(self, wave_number: int) -> List[pygame.Rect]:
        """Generate a new arena layout for the given wave"""
        self.walls.clear()
        
        # Determine number of walls based on wave
        # More walls in higher waves for more complex gameplay
        wall_count = random.randint(config.WALL_COUNT_MIN, config.WALL_COUNT_MAX)
        wall_count += wave_number // 3  # Add more walls in higher waves
        wall_count = min(wall_count, config.WALL_COUNT_MAX + 5)
        
        attempts = 0
        max_attempts = 100
        
        while len(self.walls) < wall_count and attempts < max_attempts:
            wall = self._generate_wall()
            if wall and self._is_wall_valid(wall):
                self.walls.append(wall)
            attempts += 1
        
        return self.walls
    
    def _generate_wall(self) -> Optional[pygame.Rect]:
        """Generate a single wall rectangle"""
        # Random dimensions
        width = random.randint(config.WALL_MIN_WIDTH, config.WALL_MAX_WIDTH) * config.TILE_SIZE
        height = random.randint(config.WALL_MIN_HEIGHT, config.WALL_MAX_HEIGHT) * config.TILE_SIZE
        
        # Try to find a valid position
        attempts = 0
        max_attempts = 50
        
        while attempts < max_attempts:
            # Random position
            x = random.randint(config.TILE_SIZE, config.SCREEN_WIDTH - width - config.TILE_SIZE)
            y = random.randint(config.TILE_SIZE, config.SCREEN_HEIGHT - height - config.TILE_SIZE)
            
            wall = pygame.Rect(x, y, width, height)
            
            if self._is_wall_position_valid(wall):
                return wall
            
            attempts += 1
        
        return None
    
    def _is_wall_position_valid(self, wall: pygame.Rect) -> bool:
        """Check if a wall position is valid"""
        # Check distance from center (player spawn)
        center_x = config.SCREEN_WIDTH // 2
        center_y = config.SCREEN_HEIGHT // 2
        wall_center_x = wall.centerx
        wall_center_y = wall.centery
        
        distance_to_center = ((wall_center_x - center_x)**2 + (wall_center_y - center_y)**2)**0.5
        
        if distance_to_center < config.WALL_CLEARANCE_CENTER:
            return False
        
        # Check distance from edges
        if (wall.left < config.WALL_CLEARANCE_EDGES or
            wall.right > config.SCREEN_WIDTH - config.WALL_CLEARANCE_EDGES or
            wall.top < config.WALL_CLEARANCE_EDGES or
            wall.bottom > config.SCREEN_HEIGHT - config.WALL_CLEARANCE_EDGES):
            return False
        
        return True
    
    def _is_wall_valid(self, new_wall: pygame.Rect) -> bool:
        """Check if a new wall is valid (doesn't block all paths)"""
        # Check overlap with existing walls
        for existing_wall in self.walls:
            if new_wall.colliderect(existing_wall):
                return False
        
        # Check if it creates isolated areas (simplified check)
        # This prevents walls from completely blocking off sections
        player_pos = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
        
        # Check if wall blocks too much of the arena
        temp_walls = self.walls + [new_wall]
        
        # Check if we can still reach some spawn zones
        reachable_zones = 0
        for zone in self.spawn_zones:
            if line_of_sight(player_pos, zone, temp_walls):
                reachable_zones += 1
        
        # Need to be able to reach at least some spawn zones
        return reachable_zones >= len(self.spawn_zones) // 2
    
    def get_spawn_position(self, entity_type: str, index: int, total_entities: int) -> Tuple[int, int]:
        """Get a spawn position for an entity"""
        if entity_type == 'player':
            return self.player_spawn
        
        # For enemies, distribute them among spawn zones
        if total_entities <= len(self.spawn_zones):
            zone_index = index % len(self.spawn_zones)
        else:
            # Distribute evenly if more enemies than zones
            zone_index = (index * len(self.spawn_zones)) // total_entities
        
        base_pos = self.spawn_zones[zone_index]
        
        # Add some randomness to prevent stacking
        offset_x = random.randint(-30, 30)
        offset_y = random.randint(-30, 30)
        
        return (base_pos[0] + offset_x, base_pos[1] + offset_y)
    
    def draw(self, screen: pygame.Surface):
        """Draw the map (walls and grid)"""
        # Draw background grid
        self._draw_grid(screen)
        
        # Draw walls
        for wall in self.walls:
            # Main wall color
            pygame.draw.rect(screen, config.WALL_COLOR, wall)
            
            # Add beveled edge effect
            self._draw_wall_bevel(screen, wall)
    
    def _draw_grid(self, screen: pygame.Surface):
        """Draw the background grid"""
        # Draw vertical lines
        for x in range(0, config.SCREEN_WIDTH, config.TILE_SIZE):
            pygame.draw.line(screen, config.GRID_COLOR, 
                           (x, 0), (x, config.SCREEN_HEIGHT), 1)
        
        # Draw horizontal lines
        for y in range(0, config.SCREEN_HEIGHT, config.TILE_SIZE):
            pygame.draw.line(screen, config.GRID_COLOR, 
                           (0, y), (config.SCREEN_WIDTH, y), 1)
    
    def _draw_wall_bevel(self, screen: pygame.Surface, wall: pygame.Rect):
        """Draw beveled edges on walls for 3D effect"""
        # Light edge (top and left)
        light_color = self._lighten_color(config.WALL_COLOR, 0.3)
        pygame.draw.line(screen, light_color, 
                        (wall.left, wall.top), (wall.right - 1, wall.top), 2)
        pygame.draw.line(screen, light_color, 
                        (wall.left, wall.top), (wall.left, wall.bottom - 1), 2)
        
        # Dark edge (bottom and right)
        dark_color = self._darken_color(config.WALL_COLOR, 0.3)
        pygame.draw.line(screen, dark_color, 
                        (wall.left + 1, wall.bottom - 1), 
                        (wall.right, wall.bottom - 1), 2)
        pygame.draw.line(screen, dark_color, 
                        (wall.right - 1, wall.top + 1), 
                        (wall.right - 1, wall.bottom), 2)
    
    def _lighten_color(self, color: Tuple[int, int, int], amount: float) -> Tuple[int, int, int]:
        """Lighten a color by given amount"""
        return (
            min(255, int(color[0] * (1 + amount))),
            min(255, int(color[1] * (1 + amount))),
            min(255, int(color[2] * (1 + amount)))
        )
    
    def _darken_color(self, color: Tuple[int, int, int], amount: float) -> Tuple[int, int, int]:
        """Darken a color by given amount"""
        return (
            max(0, int(color[0] * (1 - amount))),
            max(0, int(color[1] * (1 - amount))),
            max(0, int(color[2] * (1 - amount)))
        )
    
    def get_walls(self) -> List[pygame.Rect]:
        """Get list of wall rectangles"""
        return self.walls
    
    def is_position_in_wall(self, pos: Tuple[float, float], radius: float = 0) -> bool:
        """Check if a position is inside a wall"""
        point_rect = pygame.Rect(pos[0] - radius, pos[1] - radius, radius * 2, radius * 2)
        
        for wall in self.walls:
            if wall.colliderect(point_rect):
                return True
        
        return False
    
    def get_nearest_wall_distance(self, pos: Tuple[float, float]) -> float:
        """Get distance to nearest wall"""
        min_distance = float('inf')
        
        for wall in self.walls:
            # Calculate closest point on wall
            closest_x = max(wall.left, min(pos[0], wall.right))
            closest_y = max(wall.top, min(pos[1], wall.bottom))
            
            # Calculate distance
            distance = ((pos[0] - closest_x)**2 + (pos[1] - closest_y)**2)**0.5
            min_distance = min(min_distance, distance)
        
        return min_distance if min_distance != float('inf') else 1000
    
    def clear_walls(self):
        """Clear all walls"""
        self.walls.clear()