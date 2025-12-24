import pygame
import random
import math
from .constants import *

class Particle:
    def __init__(self, pos, color, velocity, lifetime, size=2, particle_type="snow"):
        self.pos = list(pos)
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.age = 0
        self.size = size
        self.wobble = random.uniform(0, math.pi * 2)  # Random phase for snowflake wobble
        self.particle_type = particle_type
        self.alpha = 255

    def update(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        if self.particle_type == "snow":
            # Add gentle wobble to snow particles
            self.pos[0] += math.sin(self.wobble + self.age * 0.1) * 0.3
        elif self.particle_type == "freeze":
            # Spiral outward for freeze ray
            self.size = max(1, self.size - 0.1)
            self.alpha = int(255 * (1 - self.age/self.lifetime))
        elif self.particle_type == "blizzard":
            # Swirl pattern for blizzard
            angle = self.age * 0.1
            radius = self.age * 0.5
            self.pos[0] += math.cos(angle) * radius * 0.1
            self.pos[1] += math.sin(angle) * radius * 0.1

        self.age += 1

    def is_alive(self):
        return self.age < self.lifetime

    def draw(self, screen):
        if self.particle_type == "freeze":
            color = (*self.color, self.alpha)
            pygame.draw.circle(screen, color,
                            (int(self.pos[0]), int(self.pos[1])), int(self.size))
        elif self.particle_type == "blizzard":
            alpha = int(255 * (1 - self.age/self.lifetime))
            color = (*self.color, alpha)
            size = int(self.size * (1 - self.age/self.lifetime * 0.5))
            pygame.draw.circle(screen, color,
                            (int(self.pos[0]), int(self.pos[1])), size)
        else:  # Regular snow
            alpha = int(255 * (1 - self.age/self.lifetime))
            color = (*self.color, alpha)
            pygame.draw.circle(screen, color,
                            (int(self.pos[0]), int(self.pos[1])), self.size)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.active_effects = {}  # Tracks active power-up effects

    def create_hit_effect(self, pos):
        # Create snowball explosion effect
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 4)
            velocity = (math.cos(angle) * speed,
                       math.sin(angle) * speed)
            color = (255, 255, 255)
            lifetime = random.randint(15, 25)
            size = random.randint(2, 4)
            self.particles.append(Particle(pos, color, velocity, lifetime, size))

    def create_freeze_ray_effect(self, start_pos, target_pos):
        # Create freeze ray beam effect with more particles
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        direction = (dx/distance, dy/distance)

        # Create more particles for a more dramatic effect
        num_particles = int(distance * 1.5)  # Increased particle density
        for i in range(num_particles):
            pos = [start_pos[0] + direction[0] * i * (distance/num_particles),
                  start_pos[1] + direction[1] * i * (distance/num_particles)]

            # Add some randomness to particle positions for a wider beam
            offset = random.uniform(-5, 5)
            pos[0] += offset
            pos[1] += offset

            velocity = (random.uniform(-1, 1), random.uniform(-1, 1))
            color = (150, 220, 255)  # Ice blue
            lifetime = random.randint(30, 40)  # Longer lifetime
            size = random.randint(4, 6)  # Larger particles

            self.particles.append(
                Particle(pos, color, velocity, lifetime, size, "freeze"))

        # Add sparkle effects at the target
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, 15)
            sparkle_pos = [target_pos[0] + math.cos(angle) * radius,
                          target_pos[1] + math.sin(angle) * radius]
            velocity = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
            self.particles.append(
                Particle(sparkle_pos, (255, 255, 255), velocity, 20, 2, "freeze"))

    def create_blizzard_effect(self, center_pos, radius):
        # Create swirling blizzard effect
        for _ in range(50):  # Create multiple particles per frame
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius)
            pos = [center_pos[0] + math.cos(angle) * distance,
                  center_pos[1] + math.sin(angle) * distance]

            # Swirling velocity
            speed = random.uniform(1, 3)
            velocity = (-math.sin(angle) * speed, math.cos(angle) * speed)

            color = (200, 230, 255)  # Light blue for blizzard
            lifetime = random.randint(40, 60)
            size = random.randint(2, 4)
            self.particles.append(
                Particle(pos, color, velocity, lifetime, size, "blizzard"))

    def create_snow_effect(self):
        if random.random() < 0.2:  # Increased snow density
            x = random.randint(0, SCREEN_WIDTH)
            velocity = (random.uniform(-0.5, 0.5), random.uniform(1, 2))
            color = (255, 255, 255)
            lifetime = random.randint(200, 300)
            size = random.randint(1, 3)  # Varied snowflake sizes
            self.particles.append(
                Particle((x, -5), color, velocity, lifetime, size, "snow"))

    def update(self):
        self.create_snow_effect()

        # Update active effects
        current_time = pygame.time.get_ticks() / 1000
        for effect_type, effect_data in list(self.active_effects.items()):
            if current_time > effect_data["end_time"]:
                del self.active_effects[effect_type]
                continue

            if effect_type == "BLIZZARD":
                self.create_blizzard_effect(
                    effect_data["position"],
                    POWERUP_PROPERTIES["BLIZZARD"]["radius"])

        # Update existing particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

    def start_effect(self, effect_type, position):
        current_time = pygame.time.get_ticks() / 1000
        properties = POWERUP_PROPERTIES[effect_type]

        self.active_effects[effect_type] = {
            "start_time": current_time,
            "end_time": current_time + properties["duration"],
            "position": position
        }

    def is_effect_active(self, effect_type):
        return effect_type in self.active_effects