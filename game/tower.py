import pygame
import math
import io
try:
    from cairosvg import svg2png
    HAS_CAIROSVG = True
except (ImportError, OSError):
    HAS_CAIROSVG = False
    print("CairoSVG not available - using fallback tower rendering")
from .constants import *

class Tower:
    def __init__(self, pos, tower_type):
        self.pos = pos
        self.type = tower_type
        self.level = 0  # Start at level 0 (base level)
        self.upgrade_cost = int(TOWER_COSTS[tower_type] * UPGRADE_COST_MULTIPLIER)
        self._update_properties()
        self.last_shot = 0
        self.selected = False
        self.sprite = None
        self.frozen_until = 0
        self.scale = 1.0  # Base scale for the sprite

        # Attempt to load tower sprite
        self._load_sprite()

    def _update_properties(self):
        props = TOWER_PROPERTIES[self.type]
        self.range = props["range"][self.level]
        self.fire_rate = props["fire_rate"][self.level]
        self.damage = props["damage"][self.level]
        self.projectile_type = props["projectile_type"]
        self.projectile_size = props["projectile_size"][self.level]
        if self.type == "RIVERS":
            self.slow_duration = props["slow_duration"][self.level]
            self.slow_factor = props["slow_factor"][self.level]

    def can_upgrade(self):
        return self.level < MAX_UPGRADE_LEVEL - 1

    def get_upgrade_cost(self):
        if not self.can_upgrade():
            return None
        base_cost = TOWER_COSTS[self.type]
        return int(base_cost * (UPGRADE_COST_MULTIPLIER ** (self.level + 1)))

    def upgrade(self):
        if self.can_upgrade():
            self.level += 1
            self._update_properties()
            self.scale = 1.0 + (self.level * 0.1)  # Increase size by 10% per level
            self._load_sprite()  # Reload sprite with new scale
            return True
        return False

    def _load_sprite(self):
        if not HAS_CAIROSVG:
            self.sprite = None
            return

        try:
            filename_map = {
                "SNOWMAN": "snowman",
                "IGLOO": "igloo",
                "ICE": "ice",
                "HOPE": "hope_tower",
                "BRYCE": "bryce_tower",
                "RIVERS": "rivers_tower",
                "ANDRII": "andrii_helicopter"
            }

            base_name = filename_map.get(self.type, self.type.lower())
            svg_filename = f"assets/{base_name}.svg"

            # Calculate size based on level
            size = int(40 * self.scale)

            with open(svg_filename, "rb") as svg_file:
                svg_data = svg_file.read()
                png_data = svg2png(bytestring=svg_data,
                                 output_width=size,
                                 output_height=size)
                png_file = io.BytesIO(png_data)
                self.sprite = pygame.image.load(png_file)

                # Add visual upgrades based on level
                if self.level > 0:
                    # Add glow effect
                    glow = pygame.Surface((size+4, size+4), pygame.SRCALPHA)
                    glow_color = (255, 255, 200, 100)  # Yellow glow
                    pygame.draw.circle(glow, glow_color, (size//2+2, size//2+2), size//2+2)
                    self.glow = glow

                print(f"Successfully loaded sprite for {self.type} level {self.level}")
        except Exception as e:
            print(f"Using fallback rendering for {self.type}: {str(e)}")
            self.sprite = None

    def can_shoot(self, current_time):
        if current_time < self.frozen_until:
            return False
        return current_time - self.last_shot >= 1 / self.fire_rate

    def get_closest_enemy(self, enemies):
        closest_enemy = None
        min_distance = float('inf')

        for enemy in enemies:
            distance = math.sqrt((enemy.pos[0] - self.pos[0])**2 + 
                               (enemy.pos[1] - self.pos[1])**2)
            if distance <= self.range and distance < min_distance:
                closest_enemy = enemy
                min_distance = distance

        return closest_enemy

    def draw(self, screen):
        try:
            if self.sprite:
                # Draw glow effect for upgraded towers
                if self.level > 0 and hasattr(self, 'glow'):
                    screen.blit(self.glow, 
                              (self.pos[0] - self.glow.get_width()//2,
                               self.pos[1] - self.glow.get_height()//2))

                screen.blit(self.sprite, 
                          (self.pos[0] - self.sprite.get_width()//2,
                           self.pos[1] - self.sprite.get_height()//2))

                # Draw level indicator
                if self.level > 0:
                    font = pygame.font.Font(None, 20)
                    level_text = font.render(str(self.level + 1), True, (255, 255, 0))
                    screen.blit(level_text, 
                              (self.pos[0] + self.sprite.get_width()//2 - 10,
                               self.pos[1] - self.sprite.get_height()//2))
            else:
                # Fallback rendering with level-based size increases
                base_size = 12 * (1 + self.level * 0.1)

                if self.type == "SNOWMAN":
                    pygame.draw.circle(screen, (255, 255, 255), 
                                     (self.pos[0], self.pos[1] + base_size*0.6), base_size)
                    pygame.draw.circle(screen, (255, 255, 255), 
                                     (self.pos[0], self.pos[1] - base_size*0.3), base_size*0.8)
                    pygame.draw.circle(screen, (255, 255, 255), 
                                     (self.pos[0], self.pos[1] - base_size), base_size*0.6)
                elif self.type == "IGLOO":
                    # Draw igloo as a dome shape
                    pygame.draw.arc(screen, (200, 220, 255), 
                                  (self.pos[0] - base_size, self.pos[1] - base_size, base_size*2, base_size*2),
                                  0, 3.14, 3)
                    pygame.draw.rect(screen, (180, 200, 240),
                                   (self.pos[0] - base_size, self.pos[1], base_size*2, base_size*0.5))
                elif self.type == "ICE":
                    # Draw ice as a crystal/diamond shape
                    points = [
                        (self.pos[0], self.pos[1] - base_size),
                        (self.pos[0] + base_size*0.7, self.pos[1]),
                        (self.pos[0], self.pos[1] + base_size),
                        (self.pos[0] - base_size*0.7, self.pos[1])
                    ]
                    pygame.draw.polygon(screen, (200, 240, 255), points)
                elif self.type == "HOPE":
                    # Draw Hope tower as a bright star/beam
                    pygame.draw.circle(screen, (255, 255, 200), self.pos, base_size)
                    pygame.draw.circle(screen, (255, 255, 100), self.pos, base_size*0.6)
                elif self.type == "BRYCE":
                    # Draw Bryce tower as lightning bolt shape
                    points = [
                        (self.pos[0], self.pos[1] - base_size),
                        (self.pos[0] + base_size*0.4, self.pos[1] - base_size*0.3),
                        (self.pos[0] + base_size*0.2, self.pos[1]),
                        (self.pos[0] + base_size*0.6, self.pos[1] + base_size*0.3),
                        (self.pos[0], self.pos[1] + base_size),
                        (self.pos[0] - base_size*0.6, self.pos[1] + base_size*0.3),
                        (self.pos[0] - base_size*0.2, self.pos[1]),
                        (self.pos[0] - base_size*0.4, self.pos[1] - base_size*0.3)
                    ]
                    pygame.draw.polygon(screen, (255, 255, 100), points)
                elif self.type == "RIVERS":
                    # Draw Rivers tower as mud blob (brown/green blob)
                    pygame.draw.circle(screen, (139, 90, 43), self.pos, base_size)  # Brown
                    pygame.draw.circle(screen, (101, 67, 33), self.pos, base_size*0.7)  # Darker brown
                    # Add some green spots for mud effect
                    pygame.draw.circle(screen, (85, 107, 47), 
                                     (self.pos[0] - base_size*0.3, self.pos[1] - base_size*0.3), base_size*0.3)
                elif self.type == "ANDRII":
                    # Draw Andrii as helicopter (circle with rotor)
                    pygame.draw.circle(screen, (100, 100, 120), self.pos, base_size)
                    pygame.draw.line(screen, (150, 150, 150), 
                                   (self.pos[0] - base_size*1.2, self.pos[1]), 
                                   (self.pos[0] + base_size*1.2, self.pos[1]), 2)
                    pygame.draw.line(screen, (150, 150, 150), 
                                   (self.pos[0], self.pos[1] - base_size*1.2), 
                                   (self.pos[0], self.pos[1] + base_size*1.2), 2)
                else:
                    # Generic fallback - just a colored circle
                    color_map = {
                        "SNOWMAN": (255, 255, 255),
                        "IGLOO": (200, 220, 255),
                        "ICE": (200, 240, 255),
                        "HOPE": (255, 255, 200),
                        "BRYCE": (255, 255, 100),
                        "RIVERS": (139, 90, 43),
                        "ANDRII": (100, 100, 120)
                    }
                    color = color_map.get(self.type, (150, 150, 150))
                    pygame.draw.circle(screen, color, self.pos, base_size)

            # Draw range circle and upgrade indicator when selected
            if self.selected:
                # Draw range circle
                pygame.draw.circle(screen, (200, 200, 255, 128),
                                 self.pos, self.range, 2)

                # Draw upgrade information if available
                if self.can_upgrade():
                    cost = self.get_upgrade_cost()
                    font = pygame.font.Font(None, 24)
                    upgrade_text = font.render(f"Upgrade: ${cost}", True, (255, 255, 0))
                    screen.blit(upgrade_text, 
                              (self.pos[0] - upgrade_text.get_width()//2,
                               self.pos[1] + 30))

        except pygame.error as e:
            print(f"Error drawing tower {self.type}: {e}")

class TowerManager:
    def __init__(self, path, projectile_manager):
        self.towers = []
        self.path = path
        self.selected_tower = None
        self.projectile_manager = projectile_manager

    def place_tower(self, pos, tower_type):
        if not self.path.is_on_path(pos):
            for tower in self.towers:
                distance = math.sqrt((tower.pos[0] - pos[0])**2 +
                                   (tower.pos[1] - pos[1])**2)
                if distance < 40:  # Minimum distance between towers
                    return False

            new_tower = Tower(pos, tower_type)
            self.towers.append(new_tower)
            print(f"Placed {tower_type} tower at {pos}")
            return True
        return False

    def update(self, enemies):
        current_time = pygame.time.get_ticks() / 1000
        for tower in self.towers:
            if tower.can_shoot(current_time):
                target = tower.get_closest_enemy(enemies)
                if target:
                    self.projectile_manager.create_projectile(
                        tower.pos,
                        target.pos,
                        tower.damage,
                        tower.projectile_type
                    )
                    tower.last_shot = current_time

    def draw(self, screen):
        for tower in self.towers:
            tower.draw(screen)