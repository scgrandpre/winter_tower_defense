import pygame
import math
from .constants import *

class Projectile:
    def __init__(self, start_pos, target_pos, damage, projectile_type="snowball"):
        self.pos = list(start_pos)
        self.target_pos = target_pos
        self.damage = damage
        self.active = True
        self.has_hit = False
        self.projectile_type = projectile_type
        self.rotation = 0  # For rotating projectiles

        # Set properties based on projectile type
        if projectile_type == "snowball":
            self.speed = 8
            self.size = 6
            self.color = (255, 255, 255)  # Pure white
        elif projectile_type == "ice_block":
            self.speed = 6
            self.size = 8
            self.color = (180, 220, 255)  # Light blue
        elif projectile_type == "ice_shard":
            self.speed = 12
            self.size = 4
            self.color = (150, 200, 255)  # Crystal blue
        elif projectile_type == "hope_beam":
            self.speed = 15
            self.size = 10
            self.color = (255, 223, 0)  # Golden yellow
        elif projectile_type == "lightning_bolt":
            self.speed = 20
            self.size = 3
            self.color = (65, 105, 225)  # Royal blue
        elif projectile_type == "mud_blob":
            self.speed = 5
            self.size = 8
            self.color = (139, 69, 19)  # Brown
        elif projectile_type == "missile":
            self.speed = 10
            self.size = 8
            self.color = (169, 169, 169)  # Gray for missile

        # Calculate direction
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        self.dx = (dx / distance) * self.speed
        self.dy = (dy / distance) * self.speed

        # Calculate rotation angle for special projectiles
        if self.projectile_type in ["ice_shard", "lightning_bolt"]:
            self.rotation = math.atan2(dy, dx)

    def update(self):
        if self.active and not self.has_hit:
            self.pos[0] += self.dx
            self.pos[1] += self.dy

            # Rotate certain projectiles
            if self.projectile_type in ["ice_shard", "lightning_bolt"]:
                self.rotation += 0.2  # Spin while moving

            # Deactivate if too far
            if abs(self.pos[0]) > SCREEN_WIDTH or abs(self.pos[1]) > SCREEN_HEIGHT:
                self.active = False

    def draw(self, screen):
        if self.active and not self.has_hit:
            if self.projectile_type == "hope_beam":
                # Draw golden beam with glow effect
                pygame.draw.circle(screen, (255, 255, 200, 128),
                                (int(self.pos[0]), int(self.pos[1])), self.size + 4)
                pygame.draw.circle(screen, self.color,
                                (int(self.pos[0]), int(self.pos[1])), self.size)
            elif self.projectile_type == "lightning_bolt":
                # Draw zigzag lightning effect
                points = [
                    (self.pos[0], self.pos[1]),
                    (self.pos[0] + math.cos(self.rotation + 0.2) * self.size * 2,
                     self.pos[1] + math.sin(self.rotation + 0.2) * self.size * 2),
                    (self.pos[0] + math.cos(self.rotation) * self.size * 4,
                     self.pos[1] + math.sin(self.rotation) * self.size * 4)
                ]
                pygame.draw.lines(screen, self.color, False,
                               [(int(x), int(y)) for x, y in points], 2)
            elif self.projectile_type == "mud_blob":
                # Draw brown blob with ripple effect
                pygame.draw.circle(screen, self.color,
                                (int(self.pos[0]), int(self.pos[1])), self.size)
                pygame.draw.circle(screen, (101, 67, 33),
                                (int(self.pos[0]), int(self.pos[1])), self.size - 2)
            else:
                # Default projectile drawing (snowball, ice_block, ice_shard)
                if self.projectile_type == "snowball":
                    # Draw snowball with highlight
                    pygame.draw.circle(screen, self.color,
                                        (int(self.pos[0]), int(self.pos[1])), self.size)
                    # Add highlight effect
                    pygame.draw.circle(screen, (220, 220, 220),
                                        (int(self.pos[0] - 2), int(self.pos[1] - 2)),
                                        self.size // 2)
                elif self.projectile_type == "ice_block":
                    # Draw square ice block with crystal pattern
                    pygame.draw.rect(screen, self.color,
                                      (int(self.pos[0] - self.size),
                                       int(self.pos[1] - self.size),
                                       self.size * 2, self.size * 2))
                    # Add crystal detail
                    pygame.draw.line(screen, (255, 255, 255),
                                      (int(self.pos[0] - self.size), int(self.pos[1] - self.size)),
                                      (int(self.pos[0] + self.size), int(self.pos[1] + self.size)), 1)
                elif self.projectile_type == "ice_shard":
                    # Draw rotating diamond-shaped ice shard
                    points = [
                        (self.pos[0] + math.cos(self.rotation) * self.size,
                         self.pos[1] + math.sin(self.rotation) * self.size),
                        (self.pos[0] - math.sin(self.rotation) * self.size,
                         self.pos[1] + math.cos(self.rotation) * self.size),
                        (self.pos[0] - math.cos(self.rotation) * self.size,
                         self.pos[1] - math.sin(self.rotation) * self.size),
                        (self.pos[0] + math.sin(self.rotation) * self.size,
                         self.pos[1] - math.cos(self.rotation) * self.size)
                    ]
                    pygame.draw.polygon(screen, self.color,
                                        [(int(x), int(y)) for x, y in points])


    def apply_effects(self, enemy):
        if self.projectile_type == "mud_blob":
            # Apply slow effect from Rivers tower (use level 0 defaults)
            enemy.apply_slow(TOWER_PROPERTIES["RIVERS"]["slow_duration"][0],
                          TOWER_PROPERTIES["RIVERS"]["slow_factor"][0])
            return True
        return False

    def collides_with(self, enemy):
        if not self.active or self.has_hit:
            return False

        # Create collision rectangles
        projectile_rect = pygame.Rect(
            self.pos[0] - self.size,
            self.pos[1] - self.size,
            self.size * 2,
            self.size * 2
        )

        enemy_rect = pygame.Rect(
            enemy.pos[0] - 15,
            enemy.pos[1] - 15,
            30,
            30
        )

        hit = projectile_rect.colliderect(enemy_rect)
        if hit:
            print(f"{self.projectile_type} hit! Position: ({self.pos[0]:.1f}, {self.pos[1]:.1f})")
            self.has_hit = True
        return hit

class ProjectileManager:
    def __init__(self):
        self.projectiles = []

    def create_projectile(self, start_pos, target_pos, damage, projectile_type="snowball"):
        self.projectiles.append(Projectile(start_pos, target_pos, damage, projectile_type))

    def update(self, enemies):
        for projectile in self.projectiles[:]:
            projectile.update()

            if not projectile.active or projectile.has_hit:
                self.projectiles.remove(projectile)
                continue

            for enemy in enemies:
                if projectile.collides_with(enemy):
                    enemy.take_damage(projectile.damage)
                    projectile.apply_effects(enemy)  # Apply any special effects
                    print(f"Hit confirmed! Damage: {projectile.damage}")
                    break

    def draw(self, screen):
        for projectile in self.projectiles:
            projectile.draw(screen)