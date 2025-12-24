import pygame
from .constants import *

class Path:
    def __init__(self):
        self.points = [
            (0, SCREEN_HEIGHT//2),
            (SCREEN_WIDTH//4, SCREEN_HEIGHT//2),
            (SCREEN_WIDTH//4, SCREEN_HEIGHT//4),
            (SCREEN_WIDTH//2, SCREEN_HEIGHT//4),
            (SCREEN_WIDTH//2, SCREEN_HEIGHT*3//4),
            (SCREEN_WIDTH*3//4, SCREEN_HEIGHT*3//4),
            (SCREEN_WIDTH*3//4, SCREEN_HEIGHT//2),
            (SCREEN_WIDTH, SCREEN_HEIGHT//2)
        ]

        # Initialize path tile as a simple surface instead of loading sprite
        self.tile_sprite = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tile_sprite.fill((220, 220, 240))  # Light gray color for path
        pygame.draw.rect(self.tile_sprite, (200, 200, 220), 
                        (0, 0, TILE_SIZE, TILE_SIZE), 2)  # Add border

    def is_on_path(self, pos):
        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]

            # Check if point is near path segment
            if p1[0] == p2[0]:  # Vertical segment
                if (min(p1[1], p2[1]) - 20 <= pos[1] <= max(p1[1], p2[1]) + 20
                    and abs(pos[0] - p1[0]) <= 20):
                    return True
            else:  # Horizontal segment
                if (min(p1[0], p2[0]) - 20 <= pos[0] <= max(p1[0], p2[0]) + 20
                    and abs(pos[1] - p1[1]) <= 20):
                    return True
        return False

    def draw(self, screen):
        try:
            # Draw path segments
            for i in range(len(self.points) - 1):
                p1 = self.points[i]
                p2 = self.points[i + 1]

                # Draw path tiles
                if p1[0] == p2[0]:  # Vertical segment
                    for y in range(min(p1[1], p2[1]), max(p1[1], p2[1]), TILE_SIZE):
                        screen.blit(self.tile_sprite,
                                  (p1[0] - TILE_SIZE//2, y))
                else:  # Horizontal segment
                    for x in range(min(p1[0], p2[0]), max(p1[0], p2[0]), TILE_SIZE):
                        screen.blit(self.tile_sprite,
                                  (x, p1[1] - TILE_SIZE//2))
        except pygame.error as e:
            print(f"Error drawing path: {e}")