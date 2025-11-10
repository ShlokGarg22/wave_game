"""
Death Circuit - Collision Detection
Handles all collision detection between game objects
"""

import pygame
from typing import List, Tuple, Optional
from utils import circle_rect_collision, distance
import config


class CollisionManager:
    """Manages collision detection between all game objects"""
    
    def __init__(self):
        self.walls: List[pygame.Rect] = []
        self.spatial_grid = {}
        self.grid_size = 64  # pixels per grid cell
    
    def set_walls(self, walls: List[pygame.Rect]):
        """Update the list of wall rectangles"""
        self.walls = walls
    
    def clear_spatial_grid(self):
        """Clear the spatial partitioning grid"""
        self.spatial_grid = {}
    
    def add_to_spatial_grid(self, obj, pos: Tuple[float, float], radius: float):
        """Add an object to the spatial grid for efficient collision detection"""
        grid_x = int(pos[0] // self.grid_size)
        grid_y = int(pos[1] // self.grid_size)
        
        # Add to multiple grid cells if object spans multiple cells
        cells_to_check = self._get_grid_cells_for_circle(pos, radius)
        
        for cell in cells_to_check:
            if cell not in self.spatial_grid:
                self.spatial_grid[cell] = []
            self.spatial_grid[cell].append(obj)
    
    def _get_grid_cells_for_circle(self, pos: Tuple[float, float], radius: float) -> List[Tuple[int, int]]:
        """Get all grid cells that a circle might occupy"""
        cells = []
        
        # Calculate bounding box in grid coordinates
        min_x = int((pos[0] - radius) // self.grid_size)
        max_x = int((pos[0] + radius) // self.grid_size)
        min_y = int((pos[1] - radius) // self.grid_size)
        max_y = int((pos[1] + radius) // self.grid_size)
        
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                cells.append((x, y))
        
        return cells
    
    def check_entity_wall_collision(self, entity_pos: Tuple[float, float], 
                                  entity_radius: float) -> bool:
        """Check if an entity (circle) collides with any wall"""
        for wall in self.walls:
            if circle_rect_collision(entity_pos, entity_radius, wall):
                return True
        return False
    
    def resolve_entity_wall_collision(self, entity_pos: Tuple[float, float],
                                    entity_radius: float) -> Tuple[float, float]:
        """Resolve collision between entity and wall by pushing entity out"""
        new_pos = list(entity_pos)
        
        for wall in self.walls:
            if circle_rect_collision(entity_pos, entity_radius, wall):
                # Calculate closest point on rectangle to circle center
                closest_x = max(wall.left, min(entity_pos[0], wall.right))
                closest_y = max(wall.top, min(entity_pos[1], wall.bottom))
                
                # Calculate direction to push
                dx = entity_pos[0] - closest_x
                dy = entity_pos[1] - closest_y
                
                if dx == 0 and dy == 0:
                    # Circle center is exactly at rectangle center
                    dx = entity_pos[0] - (wall.left + wall.right) / 2
                    dy = entity_pos[1] - (wall.top + wall.bottom) / 2
                
                # Normalize and push out
                dist = (dx * dx + dy * dy) ** 0.5
                if dist > 0:
                    push_distance = entity_radius - dist + config.COLLISION_EPSILON
                    new_pos[0] += (dx / dist) * push_distance
                    new_pos[1] += (dy / dist) * push_distance
        
        return tuple(new_pos)
    
    def check_bullet_entity_collision(self, bullet_pos: Tuple[float, float],
                                    bullet_radius: float,
                                    entities: List) -> List:
        """Check which entities a bullet collides with using spatial grid"""
        hit_entities = []
        
        # Get potential colliders from spatial grid
        grid_cells = self._get_grid_cells_for_circle(bullet_pos, bullet_radius)
        potential_colliders = set()
        
        for cell in grid_cells:
            if cell in self.spatial_grid:
                potential_colliders.update(self.spatial_grid[cell])
        
        # Check collision with each potential collider
        for entity in potential_colliders:
            if hasattr(entity, 'pos') and hasattr(entity, 'radius'):
                dist = distance(bullet_pos, entity.pos)
                if dist < bullet_radius + entity.radius:
                    hit_entities.append(entity)
        
        return hit_entities
    
    def check_entity_entity_collision(self, entity1_pos: Tuple[float, float],
                                    entity1_radius: float,
                                    entity2_pos: Tuple[float, float],
                                    entity2_radius: float) -> bool:
        """Check collision between two entities (circles)"""
        dist = distance(entity1_pos, entity2_pos)
        return dist < entity1_radius + entity2_radius
    
    def resolve_entity_entity_collision(self, entity1_pos: Tuple[float, float],
                                      entity1_radius: float,
                                      entity2_pos: Tuple[float, float],
                                      entity2_radius: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Resolve collision between two entities by pushing them apart"""
        dist = distance(entity1_pos, entity2_pos)
        min_dist = entity1_radius + entity2_radius
        
        if dist < min_dist and dist > 0:
            # Calculate push direction
            dx = entity1_pos[0] - entity2_pos[0]
            dy = entity1_pos[1] - entity2_pos[1]
            
            # Normalize
            dx /= dist
            dy /= dist
            
            # Calculate overlap
            overlap = min_dist - dist
            
            # Push entities apart equally
            push_distance = overlap / 2
            
            new_pos1 = (
                entity1_pos[0] + dx * push_distance,
                entity1_pos[1] + dy * push_distance
            )
            new_pos2 = (
                entity2_pos[0] - dx * push_distance,
                entity2_pos[1] - dy * push_distance
            )
            
            return new_pos1, new_pos2
        
        return entity1_pos, entity2_pos
    
    def check_bullet_wall_collision(self, bullet_pos: Tuple[float, float],
                                  bullet_radius: float) -> bool:
        """Check if a bullet collides with any wall"""
        for wall in self.walls:
            if circle_rect_collision(bullet_pos, bullet_radius, wall):
                return True
        return False
    
    def get_nearest_wall_distance(self, pos: Tuple[float, float]) -> float:
        """Get distance to nearest wall (for AI cover seeking)"""
        min_distance = float('inf')
        
        for wall in self.walls:
            # Calculate closest point on wall to position
            closest_x = max(wall.left, min(pos[0], wall.right))
            closest_y = max(wall.top, min(pos[1], wall.bottom))
            
            dist = distance(pos, (closest_x, closest_y))
            min_distance = min(min_distance, dist)
        
        return min_distance if min_distance != float('inf') else 1000
    
    def get_wall_normal(self, pos: Tuple[float, float], wall: pygame.Rect) -> Tuple[float, float]:
        """Get the normal vector of a wall at a given position"""
        # Find closest point on wall
        closest_x = max(wall.left, min(pos[0], wall.right))
        closest_y = max(wall.top, min(pos[1], wall.bottom))
        
        # Calculate normal vector
        dx = pos[0] - closest_x
        dy = pos[1] - closest_y
        
        # Normalize
        length = (dx * dx + dy * dy) ** 0.5
        if length > 0:
            return (dx / length, dy / length)
        else:
            return (1.0, 0.0)  # Default normal
    
    def is_position_valid(self, pos: Tuple[float, float], radius: float) -> bool:
        """Check if a position is valid (not inside walls and within bounds)"""
        # Check screen bounds
        if (pos[0] - radius < 0 or pos[0] + radius > config.SCREEN_WIDTH or
            pos[1] - radius < 0 or pos[1] + radius > config.SCREEN_HEIGHT):
            return False
        
        # Check wall collision
        if self.check_entity_wall_collision(pos, radius):
            return False
        
        return True
    
    def find_valid_spawn_position(self, preferred_pos: Tuple[float, float], 
                                radius: float, max_attempts: int = 10) -> Tuple[float, float]:
        """Find a valid spawn position near the preferred position"""
        if self.is_position_valid(preferred_pos, radius):
            return preferred_pos
        
        for attempt in range(max_attempts):
            # Try positions in expanding circles
            angle = (attempt / max_attempts) * 2 * math.pi
            distance = radius * 2 + attempt * radius
            
            test_pos = (
                preferred_pos[0] + math.cos(angle) * distance,
                preferred_pos[1] + math.sin(angle) * distance
            )
            
            if self.is_position_valid(test_pos, radius):
                return test_pos
        
        # Fallback: try random positions
        import random
        for _ in range(max_attempts):
            test_pos = (
                random.randint(radius, config.SCREEN_WIDTH - radius),
                random.randint(radius, config.SCREEN_HEIGHT - radius)
            )
            if self.is_position_valid(test_pos, radius):
                return test_pos
        
        # Last resort: return center of screen
        return (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)