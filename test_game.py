#!/usr/bin/env python3
"""
Simple test to verify the game can be instantiated without errors
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import Game
    print("✓ Successfully imported Game class")
    
    # Test basic initialization
    game = Game()
    print("✓ Game instance created successfully")
    
    # Test that all components are properly initialized
    assert game.player is not None, "Player not initialized"
    print("✓ Player initialized")
    
    assert game.enemy_spawner is not None, "Enemy spawner not initialized"
    print("✓ Enemy spawner initialized")
    
    assert game.bullet_manager is not None, "Bullet manager not initialized"
    print("✓ Bullet manager initialized")
    
    assert game.collision_manager is not None, "Collision manager not initialized"
    print("✓ Collision manager initialized")
    
    assert game.particle_emitter is not None, "Particle emitter not initialized"
    print("✓ Particle emitter initialized")
    
    assert game.ui is not None, "UI not initialized"
    print("✓ UI initialized")
    
    print("\n🎮 All systems initialized successfully!")
    print("\nTo play the game, run:")
    print("python main.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)