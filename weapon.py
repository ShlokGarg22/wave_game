"""
Death Circuit - Weapon System
Handles different weapon types, firing mechanics, and ammo management
"""

import pygame
import math
import random
from typing import List, Tuple, Optional
from bullet import Bullet
from particle_system import ParticleEmitter
from utils import vector_from_angle, clamp
import config


class Weapon:
    """Base weapon class with common functionality"""
    
    def __init__(self, name: str, damage: int, fire_rate: float, bullet_speed: float,
                 spread: float, magazine_size: int, reload_time: float,
                 color: Tuple[int, int, int], auto_fire: bool = False):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate  # shots per second
        self.bullet_speed = bullet_speed
        self.spread = spread  # radians
        self.magazine_size = magazine_size
        self.reload_time = reload_time
        self.color = color
        self.auto_fire = auto_fire
        
        # Current state
        self.ammo = magazine_size
        self.is_reloading = False
        self.reload_timer = 0.0
        self.fire_timer = 0.0
        self.fire_cooldown = 1.0 / fire_rate
        
        # Statistics
        self.shots_fired = 0
        self.total_shots_fired = 0
    
    def can_fire(self) -> bool:
        """Check if weapon can fire"""
        return (not self.is_reloading and 
                self.ammo > 0 and 
                self.fire_timer <= 0)
    
    def is_empty(self) -> bool:
        """Check if magazine is empty"""
        return self.ammo <= 0
    
    def needs_reload(self) -> bool:
        """Check if weapon needs reloading"""
        return self.ammo <= 0 and not self.is_reloading
    
    def start_reload(self):
        """Start reloading"""
        if not self.is_reloading and self.ammo < self.magazine_size:
            self.is_reloading = True
            self.reload_timer = self.reload_time
    
    def update(self, dt: float):
        """Update weapon timers"""
        # Update fire cooldown
        if self.fire_timer > 0:
            self.fire_timer -= dt
        
        # Update reload timer
        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.finish_reload()
    
    def finish_reload(self):
        """Complete reload"""
        self.ammo = self.magazine_size
        self.is_reloading = False
        self.reload_timer = 0.0
    
    def fire(self, pos: Tuple[float, float], direction: float, 
             owner_id: str, bullets: List[Bullet], 
             particle_emitter: Optional[ParticleEmitter] = None) -> bool:
        """Fire the weapon"""
        if not self.can_fire():
            return False
        
        # Create bullet with spread
        spread_angle = direction + random.uniform(-self.spread/2, self.spread/2)
        velocity = vector_from_angle(spread_angle, self.bullet_speed)
        
        bullet = Bullet(pos, velocity, self.damage, owner_id, self.color)
        bullets.append(bullet)
        
        # Update ammo and timers
        self.ammo -= 1
        self.fire_timer = self.fire_cooldown
        self.shots_fired += 1
        self.total_shots_fired += 1
        
        # Create muzzle flash
        if particle_emitter:
            particle_emitter.create_muzzle_flash(pos, direction, self.color)
        
        return True
    
    def get_ammo_ratio(self) -> float:
        """Get ammo ratio (0.0 to 1.0)"""
        return self.ammo / self.magazine_size
    
    def get_reload_progress(self) -> float:
        """Get reload progress (0.0 to 1.0)"""
        if not self.is_reloading:
            return 0.0
        return 1.0 - (self.reload_timer / self.reload_time)


class Pistol(Weapon):
    """Pistol - Balanced weapon"""
    
    def __init__(self):
        super().__init__(
            name="Pistol",
            damage=config.PISTOL_DAMAGE,
            fire_rate=config.PISTOL_FIRE_RATE,
            bullet_speed=config.PISTOL_BULLET_SPEED,
            spread=config.PISTOL_SPREAD,
            magazine_size=config.PISTOL_MAGAZINE_SIZE,
            reload_time=config.PISTOL_RELOAD_TIME,
            color=config.BULLET_COLOR
        )


class SMG(Weapon):
    """SMG - High fire rate automatic weapon"""
    
    def __init__(self):
        super().__init__(
            name="SMG",
            damage=config.SMG_DAMAGE,
            fire_rate=config.SMG_FIRE_RATE,
            bullet_speed=config.SMG_BULLET_SPEED,
            spread=config.SMG_SPREAD,
            magazine_size=config.SMG_MAGAZINE_SIZE,
            reload_time=config.SMG_RELOAD_TIME,
            color=config.BULLET_COLOR,
            auto_fire=True
        )


class Shotgun(Weapon):
    """Shotgun - Fires multiple pellets with spread"""
    
    def __init__(self):
        super().__init__(
            name="Shotgun",
            damage=config.SHOTGUN_DAMAGE,
            fire_rate=config.SHOTGUN_FIRE_RATE,
            bullet_speed=config.SHOTGUN_BULLET_SPEED,
            spread=config.SHOTGUN_SPREAD,
            magazine_size=config.SHOTGUN_MAGAZINE_SIZE,
            reload_time=config.SHOTGUN_RELOAD_TIME,
            color=config.BULLET_COLOR
        )
        self.pellets = config.SHOTGUN_PELLETS
    
    def fire(self, pos: Tuple[float, float], direction: float, 
             owner_id: str, bullets: List[Bullet], 
             particle_emitter: Optional[ParticleEmitter] = None) -> bool:
        """Fire shotgun pellets"""
        if not self.can_fire():
            return False
        
        # Create multiple pellets
        for i in range(self.pellets):
            # Calculate spread for this pellet
            pellet_spread = (i - self.pellets // 2) * (self.spread / self.pellets)
            spread_angle = direction + pellet_spread + random.uniform(-0.05, 0.05)
            
            velocity = vector_from_angle(spread_angle, self.bullet_speed)
            bullet = Bullet(pos, velocity, self.damage, owner_id, self.color)
            bullets.append(bullet)
        
        # Update ammo and timers
        self.ammo -= 1
        self.fire_timer = self.fire_cooldown
        self.shots_fired += 1
        self.total_shots_fired += 1
        
        # Create muzzle flash
        if particle_emitter:
            particle_emitter.create_muzzle_flash(pos, direction, self.color)
        
        return True


class Rifle(Weapon):
    """Rifle - High damage, accurate, long-range"""
    
    def __init__(self):
        super().__init__(
            name="Rifle",
            damage=config.RIFLE_DAMAGE,
            fire_rate=config.RIFLE_FIRE_RATE,
            bullet_speed=config.RIFLE_BULLET_SPEED,
            spread=config.RIFLE_SPREAD,
            magazine_size=config.RIFLE_MAGAZINE_SIZE,
            reload_time=config.RIFLE_RELOAD_TIME,
            color=config.BULLET_COLOR
        )


class WeaponManager:
    """Manages weapon switching and inventory"""
    
    def __init__(self):
        self.weapons = {
            0: Pistol(),
            1: SMG(),
            2: Shotgun(),
            3: Rifle()
        }
        self.current_weapon_index = 0
        self.current_weapon = self.weapons[0]
        self.switch_timer = 0.0
    
    def switch_weapon(self, index: int) -> bool:
        """Switch to a different weapon"""
        if index not in self.weapons or index == self.current_weapon_index:
            return False
        
        if self.switch_timer <= 0:
            self.current_weapon_index = index
            self.current_weapon = self.weapons[index]
            self.switch_timer = config.WEAPON_SWITCH_TIME
            return True
        
        return False
    
    def next_weapon(self) -> bool:
        """Switch to next weapon"""
        next_index = (self.current_weapon_index + 1) % len(self.weapons)
        return self.switch_weapon(next_index)
    
    def previous_weapon(self) -> bool:
        """Switch to previous weapon"""
        prev_index = (self.current_weapon_index - 1) % len(self.weapons)
        return self.switch_weapon(prev_index)
    
    def update(self, dt: float):
        """Update current weapon and switch timer"""
        self.current_weapon.update(dt)
        
        if self.switch_timer > 0:
            self.switch_timer -= dt
    
    def fire(self, pos: Tuple[float, float], direction: float, 
             owner_id: str, bullets: List[Bullet], 
             particle_emitter: Optional[ParticleEmitter] = None) -> bool:
        """Fire current weapon"""
        return self.current_weapon.fire(pos, direction, owner_id, 
                                       bullets, particle_emitter)
    
    def start_reload(self):
        """Start reloading current weapon"""
        self.current_weapon.start_reload()
    
    def get_weapon_info(self) -> dict:
        """Get info about current weapon"""
        return {
            'name': self.current_weapon.name,
            'ammo': self.current_weapon.ammo,
            'magazine_size': self.current_weapon.magazine_size,
            'is_reloading': self.current_weapon.is_reloading,
            'reload_progress': self.current_weapon.get_reload_progress(),
            'ammo_ratio': self.current_weapon.get_ammo_ratio()
        }
    
    def get_total_shots_fired(self) -> int:
        """Get total shots fired across all weapons"""
        return sum(weapon.total_shots_fired for weapon in self.weapons.values())
    
    def get_accuracy_stats(self) -> dict:
        """Get accuracy statistics"""
        total_shots = self.get_total_shots_fired()
        return {
            'total_shots': total_shots,
            'shots_by_weapon': {
                weapon.name: weapon.total_shots_fired 
                for weapon in self.weapons.values()
            }
        }