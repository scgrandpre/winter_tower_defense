import pygame
import math
import random
import io
try:
    from cairosvg import svg2png
    HAS_CAIROSVG = True
except (ImportError, OSError):
    HAS_CAIROSVG = False
from .constants import *

class Enemy:
    def __init__(self, path, enemy_type, difficulty_multipliers=None):
        self.type = enemy_type
        self.properties = ENEMY_PROPERTIES[enemy_type].copy()

        # Apply difficulty multipliers if provided
        if difficulty_multipliers:
            self.properties["health"] = int(self.properties["health"] * difficulty_multipliers.get("health", 1.0))
            self.properties["speed"] = self.properties["speed"] * difficulty_multipliers.get("speed", 1.0)

        self.health = self.properties["health"]
        self.speed = self.properties["speed"]
        self.base_speed = self.properties["speed"]  # Store original speed
        self.path = path
        self.path_index = 0
        self.pos = list(path.points[0])
        self.reached_end = False
        self.frozen_until = 0  # Time until frozen effect wears off
        self.slowed_until = 0  # Time until slow effect wears off
        self.slow_factor = 1.0  # Current speed multiplier
        self.last_frost_breath = 0  # For snow dragon's ability

        # Load correct sprite based on enemy type
        if HAS_CAIROSVG:
            sprite_name = {
                "BASIC": "monster",
                "TREASURE": "treasure_chest",
                "SNOW_DRAGON": "snow_dragon"
            }.get(enemy_type, "monster")

            try:
                with open(f"assets/{sprite_name}.svg", "rb") as svg_file:
                    svg_data = svg_file.read()
                png_data = svg2png(bytestring=svg_data, output_width=30, output_height=30)
                png_file = io.BytesIO(png_data)
                self.sprite = pygame.image.load(png_file)
                print(f"Loaded sprite for {enemy_type}")
            except Exception as e:
                print(f"Error loading {enemy_type} sprite: {e}")
                self.sprite = None
        else:
            self.sprite = None

    def use_frost_breath(self, towers):
        if self.type != "SNOW_DRAGON":
            return

        current_time = pygame.time.get_ticks() / 1000
        if current_time - self.last_frost_breath < 3:  # Use ability every 3 seconds
            return

        freeze_range = self.properties["freeze_range"]
        freeze_duration = self.properties["freeze_duration"]

        for tower in towers:
            distance = math.sqrt((tower.pos[0] - self.pos[0])**2 + 
                               (tower.pos[1] - self.pos[1])**2)
            if distance <= freeze_range:
                tower.frozen_until = current_time + freeze_duration
                print(f"Snow Dragon froze a tower at {tower.pos}")

        self.last_frost_breath = current_time

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        print(f"Enemy took {damage} damage. Health remaining: {self.health}")

    def apply_freeze(self, duration):
        current_time = pygame.time.get_ticks() / 1000
        self.frozen_until = current_time + duration
        print(f"Enemy frozen for {duration} seconds")

    def apply_slow(self, duration, slow_factor):
        current_time = pygame.time.get_ticks() / 1000
        self.slowed_until = current_time + duration
        self.slow_factor = slow_factor
        print(f"Enemy slowed to {slow_factor*100}% speed for {duration} seconds")

    def update(self):
        current_time = pygame.time.get_ticks() / 1000

        # Check status effects
        if current_time < self.frozen_until:
            return  # Skip movement if frozen

        # Update speed based on slow effect
        if current_time < self.slowed_until:
            current_speed = self.base_speed * self.slow_factor
        else:
            current_speed = self.base_speed
            self.slow_factor = 1.0

        # Movement logic
        if self.path_index < len(self.path.points) - 1:
            target = self.path.points[self.path_index + 1]
            dx = target[0] - self.pos[0]
            dy = target[1] - self.pos[1]
            distance = math.sqrt(dx**2 + dy**2)

            if distance < current_speed:
                self.path_index += 1
            else:
                self.pos[0] += (dx/distance) * current_speed
                self.pos[1] += (dy/distance) * current_speed
        else:
            self.reached_end = True

    def draw(self, screen):
        try:
            if self.sprite:
                screen.blit(self.sprite, 
                          (self.pos[0] - self.sprite.get_width()//2,
                           self.pos[1] - self.sprite.get_height()//2))
            else:
                # Fallback rendering
                colors = {
                    "BASIC": (255, 150, 150),
                    "TREASURE": (255, 215, 0),
                    "SNOW_DRAGON": (200, 255, 255)
                }
                color = colors.get(self.type, (255, 150, 150))
                pygame.draw.circle(screen, color, 
                                (int(self.pos[0]), int(self.pos[1])), 15)

            # Draw health bar
            health_width = 30 * (self.health / self.properties["health"])
            pygame.draw.rect(screen, (255, 0, 0),
                           (self.pos[0] - 15, self.pos[1] - 20, 30, 4))
            pygame.draw.rect(screen, (0, 255, 0),
                           (self.pos[0] - 15, self.pos[1] - 20, health_width, 4))

            # Draw status effect indicators
            current_time = pygame.time.get_ticks() / 1000
            if current_time < self.frozen_until:
                pygame.draw.circle(screen, (100, 200, 255),
                                (int(self.pos[0]), int(self.pos[1])), 18, 2)
            elif current_time < self.slowed_until:
                pygame.draw.circle(screen, (180, 220, 255),
                                (int(self.pos[0]), int(self.pos[1])), 18, 2)

        except pygame.error as e:
            print(f"Error drawing enemy: {e}")

class EnemyManager:
    def __init__(self, path, difficulty="NORMAL"):
        self.path = path
        self.enemies = []
        self.wave_number = 0
        self.spawn_timer = 0
        self.wave_complete = True  # Start with True so first wave doesn't auto-complete
        self.first_wave_started = False  # Track if first wave has been spawned
        self.enemies_to_spawn = 0  # Counter for remaining enemies to spawn
        self.last_spawn_time = 0   # Timer for individual enemy spawns
        self.difficulty = difficulty
        self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
        self.spawn_delay = self.difficulty_settings["spawn_delay"]
        self.current_reward = ENEMY_REWARD  # Track current wave's reward amount

    def calculate_wave_reward(self):
        # Calculate reward with 20% increase per wave, rounded up to nearest 5
        if self.wave_number == 0:
            return int(ENEMY_REWARD * self.difficulty_settings["reward_multiplier"])
        base_increase = ENEMY_REWARD * (1 + (0.2 * self.wave_number))
        # Apply difficulty multiplier
        base_increase *= self.difficulty_settings["reward_multiplier"]
        # Round up to nearest 5
        return 5 * math.ceil(base_increase / 5)

    def spawn_wave(self):
        self.wave_number += 1
        # Calculate total enemies for this wave with difficulty scaling
        base_enemies = min(self.wave_number * 2, 8)
        bonus_enemies = (self.wave_number // 5)
        total_enemies = base_enemies + bonus_enemies
        # Apply difficulty multiplier
        self.enemies_to_spawn = int(total_enemies * self.difficulty_settings["enemies_per_wave_multiplier"])

        # Update reward for this wave
        self.current_reward = self.calculate_wave_reward()
        print(f"Starting Wave {self.wave_number} with {self.enemies_to_spawn} enemies! Reward per kill: ${self.current_reward}")

        self.wave_complete = False
        self.last_spawn_time = pygame.time.get_ticks() / 1000

    def spawn_single_enemy(self):
        # Determine enemy type based on wave number
        if self.wave_number == 1:
            enemy_type = "BASIC"  # Wave 1 only has basic enemies
        else:
            # After wave 1, introduce other enemy types
            roll = random.random()
            if roll < 0.1 and self.wave_number >= 3:  # 10% chance for treasure chest after wave 3
                enemy_type = "TREASURE"
            elif roll < 0.3 and self.wave_number >= 2:  # 20% chance for snow dragon after wave 2
                enemy_type = "SNOW_DRAGON"
            else:
                enemy_type = "BASIC"

        # Create difficulty multipliers
        difficulty_multipliers = {
            "health": self.difficulty_settings["enemy_health_multiplier"],
            "speed": self.difficulty_settings["enemy_speed_multiplier"]
        }

        # Create enemy with difficulty scaling
        enemy = Enemy(self.path, enemy_type, difficulty_multipliers)
        if enemy_type != "TREASURE":  # Don't scale treasure chest health
            # Add 3 health points per wave
            health_increase = 3 * (self.wave_number - 1)  # Wave 1 has normal health
            enemy.health = enemy.health + health_increase
        enemy.properties["health"] = enemy.health  # Update max health for health bar

        self.enemies.append(enemy)
        print(f"Spawned {enemy_type} enemy with {enemy.health} health! Remaining: {self.enemies_to_spawn-1}")
        self.enemies_to_spawn -= 1
        self.last_spawn_time = pygame.time.get_ticks() / 1000

    def update(self):
        current_time = pygame.time.get_ticks() / 1000

        # Start first wave immediately after game starts
        if not self.first_wave_started and self.wave_number == 0:
            self.spawn_wave()
            self.first_wave_started = True

        # Handle wave completion and new wave spawning
        if not self.enemies and self.enemies_to_spawn <= 0:
            if not self.wave_complete and self.wave_number > 0:
                print(f"Wave {self.wave_number} complete!")
                self.wave_complete = True
                self.spawn_timer = current_time
            elif self.wave_complete and self.wave_number > 0 and current_time - self.spawn_timer >= 10:  # Longer break between waves
                self.spawn_wave()

        # Spawn individual enemies with delay
        if self.enemies_to_spawn > 0 and current_time - self.last_spawn_time >= self.spawn_delay:
            self.spawn_single_enemy()

        # Update existing enemies and their abilities
        for enemy in self.enemies[:]:
            enemy.update()
            if isinstance(enemy, Enemy) and enemy.type == "SNOW_DRAGON":
                from .tower import TowerManager  # Avoid circular import
                if isinstance(self.path, TowerManager):
                    enemy.use_frost_breath(self.path.towers)

    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)