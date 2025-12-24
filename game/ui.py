import pygame
import io
try:
    from cairosvg import svg2png
    HAS_CAIROSVG = True
except (ImportError, OSError):
    HAS_CAIROSVG = False
from .constants import *

class UI:
    def __init__(self):
        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 64)  # Even larger font for score
        self.small_font = pygame.font.Font(None, 24)
        self.selected_tower = "SNOWMAN"
        self.tower_buttons = self._create_tower_buttons()
        self.powerup_buttons = self._create_powerup_buttons()
        self.last_score = 0  # Track score changes for visual feedback
        self.powerup_cooldowns = {type: 0 for type in POWERUP_TYPES}

        # Load player avatars
        self.player_avatars = {}
        self._load_player_avatars()

    def _create_tower_buttons(self):
        buttons = {}
        y = 50
        for tower_type in TOWER_TYPES:
            buttons[tower_type] = pygame.Rect(10, y, 100, 60)  # Made buttons taller
            y += 70  # Increased spacing
        return buttons

    def _create_powerup_buttons(self):
        buttons = {}
        x = SCREEN_WIDTH - 110  # Right side of screen
        y = 50
        for powerup_type in POWERUP_TYPES:
            buttons[powerup_type] = pygame.Rect(x, y, 100, 60)
            y += 70
        return buttons

    def _load_player_avatars(self):
        """Load Hope and Bryce avatars from SVG files"""
        players = {"HOPE": "hope_tower.svg", "BRYCE": "bryce_tower.svg"}

        if HAS_CAIROSVG:
            for player, filename in players.items():
                try:
                    with open(f"assets/{filename}", "rb") as svg_file:
                        svg_data = svg_file.read()
                    # Make avatars bigger - 80x80 pixels
                    png_data = svg2png(bytestring=svg_data, output_width=80, output_height=80)
                    png_file = io.BytesIO(png_data)
                    self.player_avatars[player] = pygame.image.load(png_file)
                    print(f"Loaded {player} avatar")
                except Exception as e:
                    print(f"Error loading {player} avatar: {e}")
                    self.player_avatars[player] = None
        else:
            print("CairoSVG not available - player avatars will not be shown")

    def is_tower_button_clicked(self, pos):
        for tower_type, rect in self.tower_buttons.items():
            if rect.collidepoint(pos):
                self.selected_tower = tower_type
                return True
        return False

    def is_powerup_button_clicked(self, pos):
        current_time = pygame.time.get_ticks() / 1000
        for powerup_type, rect in self.powerup_buttons.items():
            if rect.collidepoint(pos):
                if current_time >= self.powerup_cooldowns[powerup_type]:
                    return powerup_type
        return None

    def get_selected_tower(self):
        return self.selected_tower

    def start_powerup_cooldown(self, powerup_type):
        current_time = pygame.time.get_ticks() / 1000
        cooldown = POWERUP_PROPERTIES[powerup_type]["cooldown"]
        self.powerup_cooldowns[powerup_type] = current_time + cooldown

    def draw(self, screen, score, money, lives, wave_number, quiz_type="BRYCE"):
        try:
            # Draw tower selection menu background
            pygame.draw.rect(screen, UI_COLOR, (0, 0, 120, SCREEN_HEIGHT))
            # Draw power-up menu background
            pygame.draw.rect(screen, UI_COLOR, (SCREEN_WIDTH - 120, 0, 120, SCREEN_HEIGHT))

            # Draw player avatar at the bottom of the left panel
            if quiz_type in self.player_avatars and self.player_avatars[quiz_type]:
                avatar_y = SCREEN_HEIGHT - 120  # Position near bottom
                avatar_x = 20  # Centered in left panel
                screen.blit(self.player_avatars[quiz_type], (avatar_x, avatar_y))

                # Draw player name below avatar
                player_text = self.small_font.render(quiz_type, True, TEXT_COLOR)
                player_rect = player_text.get_rect(center=(70, avatar_y + 90))
                screen.blit(player_text, player_rect)

            # Draw game stats with enhanced visibility
            # Score - larger and centered at top
            score_text = self.large_font.render(f"Score: {score}", True, TEXT_COLOR)
            score_rect = score_text.get_rect(midtop=(SCREEN_WIDTH//2, 10))
            screen.blit(score_text, score_rect)

            # Show current wave number
            wave_text = self.font.render(f"Wave: {wave_number}", True, TEXT_COLOR)
            wave_rect = wave_text.get_rect(midtop=(SCREEN_WIDTH//2, score_rect.bottom + 5))
            screen.blit(wave_text, wave_rect)

            # Show score increase effect
            if score > self.last_score:
                increase = score - self.last_score
                increase_text = self.font.render(f"+{increase}", True, (50, 200, 50))
                screen.blit(increase_text, (score_rect.right + 10, score_rect.top))
                self.last_score = score

            # Money and Lives - normal size on the side
            money_text = self.font.render(f"Money: ${money}", True, TEXT_COLOR)
            screen.blit(money_text, (10, 10))

            lives_text = self.font.render(f"Lives: {lives}", True, TEXT_COLOR)
            screen.blit(lives_text, (10, 30))

            # Draw tower buttons
            for tower_type, rect in self.tower_buttons.items():
                color = (180, 200, 255) if tower_type == self.selected_tower else UI_COLOR
                pygame.draw.rect(screen, color, rect)
                text = self.font.render(f"{tower_type}", True, TEXT_COLOR)
                screen.blit(text, (rect.x + 5, rect.y + 5))
                cost = self.small_font.render(f"${TOWER_COSTS[tower_type]}", True, TEXT_COLOR)
                screen.blit(cost, (rect.x + 5, rect.y + 35))

            # Draw power-up buttons with cooldown indicators
            current_time = pygame.time.get_ticks() / 1000
            for powerup_type, rect in self.powerup_buttons.items():
                # Check cooldown status
                cooldown_remaining = max(0, self.powerup_cooldowns[powerup_type] - current_time)
                if cooldown_remaining > 0:
                    color = (150, 150, 150)  # Grayed out during cooldown
                else:
                    color = UI_COLOR

                pygame.draw.rect(screen, color, rect)

                # Draw power-up name and cost
                text = self.small_font.render(powerup_type.replace("_", " "), True, TEXT_COLOR)
                screen.blit(text, (rect.x + 5, rect.y + 5))
                cost = self.small_font.render(f"${POWERUP_COSTS[powerup_type]}", True, TEXT_COLOR)
                screen.blit(cost, (rect.x + 5, rect.y + 25))

                # Draw cooldown timer if active
                if cooldown_remaining > 0:
                    cooldown_text = self.small_font.render(
                        f"{int(cooldown_remaining)}s", True, TEXT_COLOR)
                    screen.blit(cooldown_text, (rect.x + 5, rect.y + 45))

        except pygame.error as e:
            print(f"Error drawing UI: {e}")

    def draw_pause_menu(self, screen):
        try:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))

            # Draw pause text
            text = self.font.render("PAUSED", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)

            instruction = self.font.render("Press ESC to resume", True, (255, 255, 255))
            inst_rect = instruction.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            screen.blit(instruction, inst_rect)
        except pygame.error as e:
            print(f"Error drawing pause menu: {e}")