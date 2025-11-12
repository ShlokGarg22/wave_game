"""
Death Circuit - Game Configuration
Contains all constants, colors, and game parameters
"""

import pygame

# Screen and Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Colors (RGB)
BACKGROUND_COLOR = (10, 10, 10)
GRID_COLOR = (26, 26, 46)
PLAYER_COLOR = (0, 255, 255)
ENEMY_RUSHER_COLOR = (255, 68, 68)
ENEMY_SNIPER_COLOR = (255, 170, 0)
ENEMY_DODGER_COLOR = (170, 0, 255)
ENEMY_FLANKER_COLOR = (0, 255, 136)
BULLET_COLOR = (255, 255, 255)
WALL_COLOR = (51, 68, 85)
UI_TEXT_COLOR = (255, 255, 255)
UI_SHADOW_COLOR = (0, 0, 0)
HEALTH_BAR_BG = (50, 50, 50)
AMMO_BAR_BG = (50, 50, 50)

# Player Settings
PLAYER_SIZE = 24
PLAYER_SPEED = 200  # pixels per second
PLAYER_MAX_HEALTH = 100
PLAYER_REGEN_DELAY = 5.0  # seconds
PLAYER_REGEN_RATE = 10  # health per second
PLAYER_INVINCIBILITY_DURATION = 0.1  # seconds

# Dash Ability Settings
DASH_ENABLED = True
DASH_DISTANCE = 150  # pixels
DASH_DURATION = 0.15  # seconds
DASH_COOLDOWN = 2.0  # seconds between dashes
DASH_INVINCIBILITY = True  # Player is invincible during dash
DASH_TRAIL_PARTICLES = 8  # Number of afterimage particles
DASH_SPEED_MULTIPLIER = 10.0  # How fast the dash is

# Screen Effects Settings (User Preferences)
SCREEN_SHAKE_ENABLED = True  # Toggle screen shake
SCREEN_FLASH_ENABLED = True  # Toggle screen flash effects
HIT_STOP_ENABLED = True  # Toggle hit freeze frames
LOW_HEALTH_WARNING_ENABLED = True  # Toggle low health vignette

# Enemy Settings
ENEMY_BASE_HEALTH = 40
ENEMY_HEALTH_SCALING = 0.1  # 10% increase per wave
ENEMY_MAX_HEALTH_BONUS = 1.0  # 100% max bonus
ENEMY_BASE_ACCURACY = 0.7
ENEMY_ACCURACY_SCALING = 0.05  # 5% increase per wave
ENEMY_MAX_ACCURACY = 0.95
ENEMY_SPAWN_INVINCIBILITY = 1.0  # seconds
ENEMY_CONTACT_DAMAGE = 5  # Damage per contact with player
ENEMY_CONTACT_COOLDOWN = 0.5  # Seconds between contact damage

# AI Behavior Parameters
AI_UPDATE_RATE = 6  # frames (10 FPS)
AI_PREDICTION_ENABLED = True  # Enable predictive aiming
AI_PREDICTION_ACCURACY = 0.85  # 0.0 to 1.0, higher = more accurate predictions
RUSHER_SPEED = 150
RUSHER_ATTACK_RANGE = 200
RUSHER_PREDICTION_TIME = 0.3  # seconds ahead to predict
SNIPER_SPEED = 100
SNIPER_PREFERRED_RANGE = 400
SNIPER_RETREAT_RANGE = 300
SNIPER_SHOT_PREPARE_TIME = 1.0
SNIPER_PREDICTION_TIME = 0.5  # seconds ahead to predict
DODGER_SPEED = 120
DODGER_DASH_SPEED = 250
DODGER_DASH_DURATION = 0.3
DODGER_DASH_COOLDOWN = 2.0
DODGER_BULLET_DODGE_RADIUS = 100
DODGER_PREDICTION_TIME = 0.4  # seconds ahead to predict
FLANKER_SPEED = 130
FLANKER_FLANK_ANGLE = 90  # degrees
FLANKER_RETREAT_DISTANCE = 200
FLANKER_PREDICTION_TIME = 0.35  # seconds ahead to predict

# Weapon Settings
WEAPON_SWITCH_TIME = 0.0  # instant
PISTOL_DAMAGE = 20
PISTOL_FIRE_RATE = 3.0  # shots per second
PISTOL_BULLET_SPEED = 500
PISTOL_SPREAD = 0.05  # radians
PISTOL_MAGAZINE_SIZE = 12
PISTOL_RELOAD_TIME = 1.5

SMG_DAMAGE = 10
SMG_FIRE_RATE = 10.0
SMG_BULLET_SPEED = 600
SMG_SPREAD = 0.1
SMG_MAGAZINE_SIZE = 30
SMG_RELOAD_TIME = 2.0

SHOTGUN_DAMAGE = 8
SHOTGUN_PELLETS = 8
SHOTGUN_FIRE_RATE = 1.0
SHOTGUN_BULLET_SPEED = 400
SHOTGUN_SPREAD = 0.3
SHOTGUN_MAGAZINE_SIZE = 6
SHOTGUN_RELOAD_TIME = 2.5

RIFLE_DAMAGE = 35
RIFLE_FIRE_RATE = 1.5
RIFLE_BULLET_SPEED = 800
RIFLE_SPREAD = 0.02
RIFLE_MAGAZINE_SIZE = 10
RIFLE_RELOAD_TIME = 2.0

# Bullet Settings
BULLET_SIZE = 4
BULLET_LIFETIME = 3.0  # seconds
BULLET_TRAIL_LENGTH = 5
BULLET_TRAIL_DURATION = 0.2

# Map Generation
WALL_COUNT_MIN = 5
WALL_COUNT_MAX = 10
WALL_MIN_WIDTH = 2  # tiles
WALL_MAX_WIDTH = 8  # tiles
WALL_MIN_HEIGHT = 1  # tiles
WALL_MAX_HEIGHT = 3  # tiles
WALL_CLEARANCE_CENTER = 200  # pixels
WALL_CLEARANCE_EDGES = 50  # pixels

# Wave System
WAVE_BREAK_TIME = 5.0  # seconds
WAVE_BASE_ENEMIES = 3
WAVE_ENEMY_INCREMENT = 2
BOSS_WAVE_INTERVAL = 5  # Boss appears every 5 waves
BOSS_HEALTH_MULTIPLIER = 3.0  # Boss has 3x health
BOSS_SIZE_MULTIPLIER = 1.5  # Boss is 1.5x larger
BOSS_SPEED_MULTIPLIER = 0.8  # Boss is slightly slower
BOSS_DAMAGE_MULTIPLIER = 1.5  # Boss deals 1.5x damage
BOSS_FIRE_RATE_MULTIPLIER = 1.3  # Boss shoots 30% faster

# Particle System
PARTICLE_MAX_COUNT = 500
MUZZLE_FLASH_PARTICLES = 8
MUZZLE_FLASH_LIFETIME = 0.1
BLOOD_PARTICLES = 15
BLOOD_LIFETIME = 0.5
DEATH_EXPLOSION_PARTICLES = 40
DEATH_EXPLOSION_LIFETIME = 1.0
IMPACT_SPARKS = 5
IMPACT_LIFETIME = 0.2

# UI Settings
UI_FONT_SIZE_SMALL = 16
UI_FONT_SIZE_MEDIUM = 24
UI_FONT_SIZE_LARGE = 32
CROSSHAIR_SIZE = 20
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
AMMO_BAR_WIDTH = 150
AMMO_BAR_HEIGHT = 15
SCREEN_SHAKE_INTENSITY = 2
SCREEN_SHAKE_DURATION = 0.2

# Collision
COLLISION_EPSILON = 0.1
ENTITY_SPACING = 50  # minimum distance between enemies

# Performance Optimization
MAX_BULLETS_ON_SCREEN = 500  # Hard cap for all bullets
MAX_BULLETS_PER_ENTITY = 30  # Max bullets per player/enemy
MAX_PARTICLES_ON_SCREEN = 250  # Hard cap for particles
BULLET_CULL_DISTANCE = 150  # Pixels off-screen before deletion
BULLET_MAX_LIFETIME = 5.0  # Seconds before auto-deletion
PARTICLE_CULL_DISTANCE = 100  # Pixels off-screen before deletion
OFF_SCREEN_UPDATE_RATE = 5  # Update off-screen enemies every N frames
ENABLE_OBJECT_POOLING = True  # Use object pooling for bullets
ADAPTIVE_QUALITY = True  # Lower quality when FPS drops

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_GAME_OVER = 3

# Difficulty System
DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2
DIFFICULTY_NIGHTMARE = 3
CURRENT_DIFFICULTY = DIFFICULTY_NORMAL  # Default difficulty

# Difficulty Modifiers (applied based on CURRENT_DIFFICULTY)
DIFFICULTY_SETTINGS = {
    DIFFICULTY_EASY: {
        'name': 'Easy',
        'player_health_multiplier': 1.5,
        'player_damage_multiplier': 1.3,
        'player_regen_rate_multiplier': 1.5,
        'enemy_health_multiplier': 0.7,
        'enemy_damage_multiplier': 0.7,
        'enemy_speed_multiplier': 0.8,
        'enemy_accuracy_multiplier': 0.7,
        'enemy_fire_rate_multiplier': 0.8,
        'wave_enemy_count_multiplier': 0.7,
        'contact_damage_multiplier': 0.5,
        'boss_wave_interval': 6,  # Boss every 6 waves
        'description': 'Relaxed pace, more forgiving'
    },
    DIFFICULTY_NORMAL: {
        'name': 'Normal',
        'player_health_multiplier': 1.0,
        'player_damage_multiplier': 1.0,
        'player_regen_rate_multiplier': 1.0,
        'enemy_health_multiplier': 1.0,
        'enemy_damage_multiplier': 1.0,
        'enemy_speed_multiplier': 1.0,
        'enemy_accuracy_multiplier': 1.0,
        'enemy_fire_rate_multiplier': 1.0,
        'wave_enemy_count_multiplier': 1.0,
        'contact_damage_multiplier': 1.0,
        'boss_wave_interval': 5,  # Boss every 5 waves
        'description': 'Balanced challenge'
    },
    DIFFICULTY_HARD: {
        'name': 'Hard',
        'player_health_multiplier': 0.8,
        'player_damage_multiplier': 0.9,
        'player_regen_rate_multiplier': 0.7,
        'enemy_health_multiplier': 1.3,
        'enemy_damage_multiplier': 1.3,
        'enemy_speed_multiplier': 1.15,
        'enemy_accuracy_multiplier': 1.2,
        'enemy_fire_rate_multiplier': 1.2,
        'wave_enemy_count_multiplier': 1.3,
        'contact_damage_multiplier': 1.5,
        'boss_wave_interval': 4,  # Boss every 4 waves
        'description': 'Intense combat, faster enemies'
    },
    DIFFICULTY_NIGHTMARE: {
        'name': 'Nightmare',
        'player_health_multiplier': 0.6,
        'player_damage_multiplier': 0.8,
        'player_regen_rate_multiplier': 0.5,
        'enemy_health_multiplier': 1.8,
        'enemy_damage_multiplier': 1.6,
        'enemy_speed_multiplier': 1.3,
        'enemy_accuracy_multiplier': 1.5,
        'enemy_fire_rate_multiplier': 1.5,
        'wave_enemy_count_multiplier': 1.5,
        'contact_damage_multiplier': 2.0,
        'boss_wave_interval': 3,  # Boss every 3 waves
        'description': 'Brutal challenge, overwhelming odds'
    }
}

# Controls
KEY_UP = pygame.K_w
KEY_DOWN = pygame.K_s
KEY_LEFT = pygame.K_a
KEY_RIGHT = pygame.K_d
KEY_RELOAD = pygame.K_r
KEY_PAUSE = pygame.K_ESCAPE
KEY_WEAPON_1 = pygame.K_1
KEY_WEAPON_2 = pygame.K_2
KEY_WEAPON_3 = pygame.K_3
KEY_WEAPON_4 = pygame.K_4

# Mouse
MOUSE_LEFT = 1
MOUSE_RIGHT = 3

# Difficulty Helper Functions
def get_difficulty_setting(key):
    """Get a difficulty setting value for current difficulty"""
    return DIFFICULTY_SETTINGS[CURRENT_DIFFICULTY].get(key, 1.0)

def apply_difficulty_to_player_health(base_health):
    """Apply difficulty multiplier to player health"""
    return int(base_health * get_difficulty_setting('player_health_multiplier'))

def apply_difficulty_to_player_damage(base_damage):
    """Apply difficulty multiplier to player damage"""
    return int(base_damage * get_difficulty_setting('player_damage_multiplier'))

def apply_difficulty_to_enemy_health(base_health):
    """Apply difficulty multiplier to enemy health"""
    return int(base_health * get_difficulty_setting('enemy_health_multiplier'))

def apply_difficulty_to_enemy_damage(base_damage):
    """Apply difficulty multiplier to enemy damage"""
    return int(base_damage * get_difficulty_setting('enemy_damage_multiplier'))

def apply_difficulty_to_enemy_speed(base_speed):
    """Apply difficulty multiplier to enemy speed"""
    return base_speed * get_difficulty_setting('enemy_speed_multiplier')

def get_boss_wave_interval():
    """Get boss wave interval based on difficulty"""
    return get_difficulty_setting('boss_wave_interval')

def get_difficulty_name():
    """Get current difficulty name"""
    return DIFFICULTY_SETTINGS[CURRENT_DIFFICULTY]['name']

def set_difficulty(difficulty_level):
    """Set the game difficulty"""
    global CURRENT_DIFFICULTY
    if difficulty_level in DIFFICULTY_SETTINGS:
        CURRENT_DIFFICULTY = difficulty_level
        return True
    return False