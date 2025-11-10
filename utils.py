"""
Death Circuit - Utility Functions
Mathematical helpers and common calculations
"""

import math
import pygame
from typing import Tuple, List, Optional


def distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate distance between two points"""
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return math.sqrt(dx * dx + dy * dy)


def angle_to(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate angle from pos1 to pos2 in radians"""
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return math.atan2(dy, dx)


def normalize_vector(vec: Tuple[float, float]) -> Tuple[float, float]:
    """Normalize a 2D vector to unit length"""
    length = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
    if length == 0:
        return (0.0, 0.0)
    return (vec[0] / length, vec[1] / length)


def rotate_point(point: Tuple[float, float], angle: float, 
                 origin: Tuple[float, float] = (0, 0)) -> Tuple[float, float]:
    """Rotate a point around an origin by given angle"""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Translate point to origin
    x = point[0] - origin[0]
    y = point[1] - origin[1]
    
    # Rotate
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    
    # Translate back
    return (new_x + origin[0], new_y + origin[1])


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(value, max_val))


def line_of_sight(start: Tuple[float, float], end: Tuple[float, float], 
                  walls: List[pygame.Rect]) -> bool:
    """Check if there's a clear line of sight between two points"""
    if not walls:
        return True
    
    # Create a line segment from start to end
    line_start = pygame.math.Vector2(start)
    line_end = pygame.math.Vector2(end)
    
    for wall in walls:
        # Check if line intersects with wall rectangle
        if line_intersects_rect(line_start, line_end, wall):
            return False
    
    return True


def line_intersects_rect(line_start: pygame.math.Vector2, 
                        line_end: pygame.math.Vector2, 
                        rect: pygame.Rect) -> bool:
    """Check if a line segment intersects with a rectangle"""
    # Check if either endpoint is inside the rectangle
    if rect.collidepoint(line_start.x, line_start.y) or rect.collidepoint(line_end.x, line_end.y):
        return True
    
    # Check intersection with each edge of the rectangle
    edges = [
        (pygame.math.Vector2(rect.left, rect.top), pygame.math.Vector2(rect.right, rect.top)),
        (pygame.math.Vector2(rect.right, rect.top), pygame.math.Vector2(rect.right, rect.bottom)),
        (pygame.math.Vector2(rect.right, rect.bottom), pygame.math.Vector2(rect.left, rect.bottom)),
        (pygame.math.Vector2(rect.left, rect.bottom), pygame.math.Vector2(rect.left, rect.top))
    ]
    
    for edge_start, edge_end in edges:
        if line_intersects_line(line_start, line_end, edge_start, edge_end):
            return True
    
    return False


def line_intersects_line(p1: pygame.math.Vector2, p2: pygame.math.Vector2,
                        p3: pygame.math.Vector2, p4: pygame.math.Vector2) -> bool:
    """Check if two line segments intersect"""
    # Calculate determinants
    det = (p2.x - p1.x) * (p4.y - p3.y) - (p2.y - p1.y) * (p4.x - p3.x)
    
    if det == 0:
        return False  # Lines are parallel
    
    # Calculate parameters
    t = ((p3.x - p1.x) * (p4.y - p3.y) - (p3.y - p1.y) * (p4.x - p3.x)) / det
    u = ((p3.x - p1.x) * (p2.y - p1.y) - (p3.y - p1.y) * (p2.x - p1.x)) / det
    
    # Check if intersection is within both line segments
    return 0 <= t <= 1 and 0 <= u <= 1


def circle_rect_collision(circle_pos: Tuple[float, float], circle_radius: float,
                         rect: pygame.Rect) -> bool:
    """Check if a circle collides with a rectangle"""
    # Find the closest point on the rectangle to the circle center
    closest_x = clamp(circle_pos[0], rect.left, rect.right)
    closest_y = clamp(circle_pos[1], rect.top, rect.bottom)
    
    # Calculate distance from circle center to closest point
    dist = distance(circle_pos, (closest_x, closest_y))
    
    return dist <= circle_radius


def predict_intercept(shooter_pos: Tuple[float, float], 
                     target_pos: Tuple[float, float],
                     target_velocity: Tuple[float, float],
                     bullet_speed: float) -> Optional[Tuple[float, float]]:
    """Predict where to aim to hit a moving target"""
    # Calculate relative position and velocity
    rel_x = target_pos[0] - shooter_pos[0]
    rel_y = target_pos[1] - shooter_pos[1]
    
    # Quadratic equation coefficients for interception
    a = target_velocity[0]**2 + target_velocity[1]**2 - bullet_speed**2
    b = 2 * (rel_x * target_velocity[0] + rel_y * target_velocity[1])
    c = rel_x**2 + rel_y**2
    
    # Solve quadratic equation
    discriminant = b**2 - 4 * a * c
    
    if discriminant < 0:
        return None  # No solution
    
    # Find the smallest positive time
    t1 = (-b + math.sqrt(discriminant)) / (2 * a)
    t2 = (-b - math.sqrt(discriminant)) / (2 * a)
    
    t = None
    if t1 > 0 and t2 > 0:
        t = min(t1, t2)
    elif t1 > 0:
        t = t1
    elif t2 > 0:
        t = t2
    else:
        return None
    
    # Calculate intercept position
    intercept_x = target_pos[0] + target_velocity[0] * t
    intercept_y = target_pos[1] + target_velocity[1] * t
    
    return (intercept_x, intercept_y)


def wrap_angle(angle: float) -> float:
    """Wrap an angle to [-π, π] range"""
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values"""
    return start + (end - start) * clamp(t, 0.0, 1.0)


def vector_from_angle(angle: float, length: float = 1.0) -> Tuple[float, float]:
    """Create a vector from an angle and length"""
    return (math.cos(angle) * length, math.sin(angle) * length)