# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BACKGROUND_COLOR = (235, 245, 255)  # Light blue for winter theme
UI_COLOR = (200, 220, 255)
TEXT_COLOR = (50, 50, 70)

# Game settings
STARTING_MONEY = 300
STARTING_LIVES = 25
ENEMY_REWARD = 25

# Tower types and costs
TOWER_TYPES = ["SNOWMAN", "IGLOO", "ICE", "HOPE", "BRYCE", "RIVERS", "ANDRII"]
TOWER_COSTS = {
    "SNOWMAN": 50,
    "IGLOO": 100,
    "ICE": 75,
    "HOPE": 500,
    "BRYCE": 500,
    "RIVERS": 150,
    "ANDRII": 1000
}

# Tower upgrade multipliers
UPGRADE_COST_MULTIPLIER = 1.5
MAX_UPGRADE_LEVEL = 4

# Tower properties with upgrade levels
TOWER_PROPERTIES = {
    "SNOWMAN": {
        "range": [150, 170, 190, 210],  # Increases by 20 each level
        "fire_rate": [1.0, 1.2, 1.4, 1.6],  # Increases by 0.2 each level
        "damage": [20, 25, 30, 35],  # Increases by 5 each level
        "projectile_type": "snowball",
        "projectile_size": [6, 8, 10, 12]  # Increases by 2 each level
    },
    "IGLOO": {
        "range": [120, 140, 160, 180],
        "fire_rate": [0.5, 0.6, 0.7, 0.8],
        "damage": [40, 50, 60, 70],
        "projectile_type": "ice_block",
        "projectile_size": [8, 10, 12, 14]
    },
    "ICE": {
        "range": [180, 200, 220, 240],
        "fire_rate": [2.0, 2.4, 2.8, 3.2],
        "damage": [10, 15, 20, 25],
        "projectile_type": "ice_shard",
        "projectile_size": [4, 6, 8, 10]
    },
    "HOPE": {
        "range": [200, 225, 250, 275],
        "fire_rate": [0.5, 0.6, 0.7, 0.8],
        "damage": [500, 600, 700, 800],
        "projectile_type": "hope_beam",
        "projectile_size": [10, 12, 14, 16]
    },
    "BRYCE": {
        "range": [150, 170, 190, 210],
        "fire_rate": [20.0, 22.0, 24.0, 26.0],
        "damage": [5, 7, 9, 11],
        "projectile_type": "lightning_bolt",
        "projectile_size": [3, 4, 5, 6]
    },
    "RIVERS": {
        "range": [180, 200, 220, 240],
        "fire_rate": [1.0, 1.2, 1.4, 1.6],
        "damage": [0, 0, 0, 0],  # No damage, only slowing
        "projectile_type": "mud_blob",
        "projectile_size": [8, 10, 12, 14],
        "slow_duration": [10, 12, 14, 16],  # Increases by 2 seconds each level
        "slow_factor": [0.3, 0.25, 0.2, 0.15]  # Decreases by 0.05 each level (stronger slow)
    },
    "ANDRII": {
        "range": [250, 275, 300, 325],  # Long range
        "fire_rate": [0.5, 0.6, 0.7, 0.8],  # Slow but powerful
        "damage": [100, 125, 150, 175],  # High damage
        "projectile_type": "missile",
        "projectile_size": [8, 10, 12, 14]
    }
}

# Enemy properties
ENEMY_TYPES = ["BASIC", "TREASURE", "SNOW_DRAGON"]
ENEMY_PROPERTIES = {
    "BASIC": {
        "speed": 1.5,
        "health": 30,
        "reward": ENEMY_REWARD
    },
    "TREASURE": {
        "speed": 0.8,
        "health": 150,
        "reward": 1000
    },
    "SNOW_DRAGON": {
        "speed": 2,
        "health": 60,
        "reward": 50,
        "freeze_duration": 0.5,
        "freeze_range": 80
    }
}

# Power-up properties
POWERUP_TYPES = ["FREEZE_RAY", "BLIZZARD"]
POWERUP_COSTS = {
    "FREEZE_RAY": 150,
    "BLIZZARD": 300
}
POWERUP_PROPERTIES = {
    "FREEZE_RAY": {
        "duration": 5,
        "cooldown": 15,
        "freeze_time": 3
    },
    "BLIZZARD": {
        "duration": 8,
        "cooldown": 30,
        "slow_factor": 0.5,
        "radius": 150
    }
}

# Path settings
TILE_SIZE = 40
PATH_COLOR = (200, 200, 220)

# Difficulty settings
DIFFICULTY_LEVELS = ["EASY", "NORMAL", "HARD", "EXTRA_HARD", "IMPOSSIBLE"]
DIFFICULTY_SETTINGS = {
    "EASY": {
        "starting_money": 500,
        "starting_lives": 35,
        "enemy_health_multiplier": 0.5,
        "enemy_speed_multiplier": 0.7,
        "spawn_delay": 6.0,
        "enemies_per_wave_multiplier": 0.6,
        "reward_multiplier": 1.5
    },
    "NORMAL": {
        "starting_money": 300,
        "starting_lives": 25,
        "enemy_health_multiplier": 1.0,
        "enemy_speed_multiplier": 1.0,
        "spawn_delay": 4.0,
        "enemies_per_wave_multiplier": 1.0,
        "reward_multiplier": 1.0
    },
    "HARD": {
        "starting_money": 250,
        "starting_lives": 20,
        "enemy_health_multiplier": 1.4,
        "enemy_speed_multiplier": 1.15,
        "spawn_delay": 3.0,
        "enemies_per_wave_multiplier": 1.2,
        "reward_multiplier": 0.9
    },
    "EXTRA_HARD": {
        "starting_money": 200,
        "starting_lives": 15,
        "enemy_health_multiplier": 1.8,
        "enemy_speed_multiplier": 1.3,
        "spawn_delay": 2.5,
        "enemies_per_wave_multiplier": 1.5,
        "reward_multiplier": 0.8
    },
    "IMPOSSIBLE": {
        "starting_money": 150,
        "starting_lives": 10,
        "enemy_health_multiplier": 2.5,
        "enemy_speed_multiplier": 1.5,
        "spawn_delay": 2.0,
        "enemies_per_wave_multiplier": 2.0,
        "reward_multiplier": 0.7
    }
}

# Victory condition
MAX_WAVE = 10