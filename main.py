import os
import pygame
import sys
import math
from game.constants import *
from game.tower import TowerManager
from game.enemy import EnemyManager, Enemy #Import Enemy class here
from game.projectile import ProjectileManager
from game.particle import ParticleSystem
from game.path import Path
from game.ui import UI
from game.quiz import MathQuiz

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Winter Tower Defense")

        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            print("Display initialized successfully")
        except pygame.error as e:
            print(f"Failed to initialize display: {e}")
            sys.exit(1)

        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.difficulty = "NORMAL"  # Default difficulty
        self.show_player_menu = True  # Show player selection first
        self.show_difficulty_menu = False
        self.game_started = False

        # Initialize game components (will be reset when difficulty is selected)
        self.path = Path()
        self.projectile_manager = ProjectileManager()
        self.tower_manager = TowerManager(self.path, self.projectile_manager)
        self.enemy_manager = EnemyManager(self.path, self.difficulty)
        self.particle_system = ParticleSystem()
        self.ui = UI()

        self.score = 0
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.game_won = False
        self.quiz = MathQuiz()
        self.quiz_type = "BRYCE"  # Multiplication problems
        self.current_wave = 1


    def start_game_with_difficulty(self, difficulty):
        """Initialize game with selected difficulty"""
        self.difficulty = difficulty
        self.show_difficulty_menu = False
        self.game_started = True

        # Get difficulty settings
        settings = DIFFICULTY_SETTINGS[difficulty]

        # Reset game with difficulty settings
        self.money = settings["starting_money"]
        self.lives = settings["starting_lives"]
        self.score = 0
        self.current_wave = 1
        self.game_won = False

        # Reinitialize game components
        self.path = Path()
        self.projectile_manager = ProjectileManager()
        self.tower_manager = TowerManager(self.path, self.projectile_manager)
        self.enemy_manager = EnemyManager(self.path, difficulty)
        self.particle_system = ParticleSystem()

        print(f"Game started on {difficulty} difficulty!")
        print(f"Starting money: ${self.money}, Lives: {self.lives}")

    def draw_player_menu(self):
        """Draw the player selection menu"""
        self.screen.fill(BACKGROUND_COLOR)

        # Title
        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render("Winter Tower Defense", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        subtitle_font = pygame.font.Font(None, 36)
        subtitle_text = subtitle_font.render("Who's Playing?", True, TEXT_COLOR)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 160))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Player buttons
        button_font = pygame.font.Font(None, 48)
        button_height = 80
        button_width = 300
        start_y = 250
        spacing = 100

        players = [
            ("HOPE", "Hope - Multiplication (0-12)"),
            ("BRYCE", "Bryce - Fraction × and ÷")
        ]

        self.player_buttons = []
        for i, (player, desc) in enumerate(players):
            y = start_y + i * spacing
            button_rect = pygame.Rect((SCREEN_WIDTH - button_width) // 2, y, button_width, button_height)
            self.player_buttons.append((button_rect, player))

            # Draw button
            pygame.draw.rect(self.screen, UI_COLOR, button_rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, button_rect, 3)

            # Draw player name
            text = button_font.render(player, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(button_rect.centerx, button_rect.centery - 10))
            self.screen.blit(text, text_rect)

            # Draw description
            desc_font = pygame.font.Font(None, 24)
            desc_text = desc_font.render(desc, True, TEXT_COLOR)
            desc_rect = desc_text.get_rect(center=(button_rect.centerx, button_rect.centery + 20))
            self.screen.blit(desc_text, desc_rect)

        pygame.display.flip()

    def draw_difficulty_menu(self):
        """Draw the difficulty selection menu"""
        self.screen.fill(BACKGROUND_COLOR)

        # Title
        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render("Winter Tower Defense", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        subtitle_font = pygame.font.Font(None, 36)
        subtitle_text = subtitle_font.render("Select Difficulty", True, TEXT_COLOR)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 160))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Difficulty buttons
        button_font = pygame.font.Font(None, 40)
        button_height = 50
        button_width = 300
        start_y = 220
        spacing = 60

        difficulties = [
            ("EASY", "Easy - More money, more lives"),
            ("NORMAL", "Normal - Balanced"),
            ("HARD", "Hard - Tough challenge"),
            ("EXTRA_HARD", "Extra Hard - Very difficult"),
            ("IMPOSSIBLE", "Impossible - Good luck!")
        ]

        self.difficulty_buttons = []
        for i, (diff, desc) in enumerate(difficulties):
            y = start_y + i * spacing
            button_rect = pygame.Rect((SCREEN_WIDTH - button_width) // 2, y, button_width, button_height)
            self.difficulty_buttons.append((button_rect, diff))

            # Draw button
            pygame.draw.rect(self.screen, UI_COLOR, button_rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, button_rect, 2)

            # Draw difficulty name
            text = button_font.render(diff.replace("_", " ").title(), True, TEXT_COLOR)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)

            # Draw description
            desc_font = pygame.font.Font(None, 20)
            desc_text = desc_font.render(desc, True, TEXT_COLOR)
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH//2, y + button_height + 10))
            self.screen.blit(desc_text, desc_rect)

        pygame.display.flip()

    def spawn_treasure_chest(self):
        # Remove cooldown check, spawn immediately when T is pressed
        difficulty_multipliers = {
            "health": self.enemy_manager.difficulty_settings["enemy_health_multiplier"],
            "speed": self.enemy_manager.difficulty_settings["enemy_speed_multiplier"]
        }
        enemy = Enemy(self.path, "TREASURE", difficulty_multipliers)
        self.enemy_manager.enemies.append(enemy)
        print("Spawned a treasure chest!")
        return True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Handle player selection menu
            if self.show_player_menu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for button_rect, player in self.player_buttons:
                        if button_rect.collidepoint(mouse_pos):
                            self.quiz_type = player
                            self.show_player_menu = False
                            self.show_difficulty_menu = True
                            print(f"{player} selected!")
                            break
                continue

            # Handle difficulty menu
            if self.show_difficulty_menu:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for button_rect, difficulty in self.difficulty_buttons:
                        if button_rect.collidepoint(mouse_pos):
                            self.start_game_with_difficulty(difficulty)
                            break
                continue

            # Game events (only when game is started)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.quiz.is_active():  # Only allow pause toggle if quiz is not active
                        self.paused = not self.paused
                        if not self.paused:
                            print(f"Starting Wave {self.current_wave}!")
                elif event.key == pygame.K_t and not self.paused and not self.quiz.is_active():
                    self.spawn_treasure_chest()
                    print("Spawned a treasure chest!")
                elif self.quiz.is_active():
                    # Handle quiz input - returns True when quiz is complete
                    quiz_finished = self.quiz.handle_input(event)

                    # If current question answered but more remain, show next question after delay
                    if not self.quiz.active and not self.quiz.quiz_complete:
                        # Will show next question after result display
                        pass

                    # If entire quiz is complete, award bonuses
                    if quiz_finished and self.quiz.quiz_complete:
                        # Calculate bonus based on percentage of correct answers
                        percentage_correct = self.quiz.correct_count / self.quiz.total_questions
                        base_bonus = int(self.money * 0.5)  # 50% of current money as base
                        bonus = int(base_bonus * percentage_correct)  # Scale by performance

                        self.money += bonus
                        print(f"Quiz complete! {self.quiz.correct_count}/{self.quiz.total_questions} correct")
                        print(f"Money bonus: ${bonus} ({int(percentage_correct*100)}% of ${base_bonus})")
                        self.paused = False  # Unpause after quiz completion
                        print(f"Starting Wave {self.current_wave}!")

            elif event.type == pygame.MOUSEBUTTONDOWN and not self.paused and not self.quiz.is_active():
                mouse_pos = pygame.mouse.get_pos()

                # Check for power-up activation first
                powerup_type = self.ui.is_powerup_button_clicked(mouse_pos)
                if powerup_type and self.money >= POWERUP_COSTS[powerup_type]:
                    self.activate_powerup(powerup_type, mouse_pos)
                    continue

                # Check if clicking on existing tower for upgrade
                clicked_tower = None
                for tower in self.tower_manager.towers:
                    distance = math.sqrt((tower.pos[0] - mouse_pos[0])**2 + 
                                          (tower.pos[1] - mouse_pos[1])**2)
                    if distance < 20:  # Click radius for towers
                        clicked_tower = tower
                        break

                if clicked_tower:
                    # Deselect previously selected tower
                    for tower in self.tower_manager.towers:
                        if tower != clicked_tower:
                            tower.selected = False

                    # Toggle selection of clicked tower
                    clicked_tower.selected = not clicked_tower.selected

                    # If tower is selected and can be upgraded
                    if clicked_tower.selected and clicked_tower.can_upgrade():
                        upgrade_cost = clicked_tower.get_upgrade_cost()
                        if self.money >= upgrade_cost:
                            if clicked_tower.upgrade():
                                self.money -= upgrade_cost
                                print(f"Upgraded {clicked_tower.type} to level {clicked_tower.level + 1}")
                        else:
                            print(f"Not enough money for upgrade (need ${upgrade_cost})")
                else:
                    # If not clicking on existing tower, handle new tower placement
                    if not self.ui.is_tower_button_clicked(mouse_pos):
                        selected_tower = self.ui.get_selected_tower()
                        if self.money >= TOWER_COSTS[selected_tower]:
                            if self.tower_manager.place_tower(mouse_pos, selected_tower):
                                self.money -= TOWER_COSTS[selected_tower]
                                print(f"Tower placed at {mouse_pos}")
                            else:
                                print("Cannot place tower here")

    def activate_powerup(self, powerup_type, mouse_pos):
        if powerup_type == "FREEZE_RAY":
            # Apply freeze to all enemies on screen
            affected_count = 0
            for enemy in self.enemy_manager.enemies:
                # Create freeze effect from the power-up button to each enemy
                self.particle_system.create_freeze_ray_effect(
                    (SCREEN_WIDTH - 60, 50), enemy.pos)
                enemy.apply_freeze(POWERUP_PROPERTIES["FREEZE_RAY"]["freeze_time"])
                affected_count += 1

            if affected_count > 0:
                self.money -= POWERUP_COSTS["FREEZE_RAY"]
                self.ui.start_powerup_cooldown("FREEZE_RAY")
                print(f"Freeze Ray activated, freezing {affected_count} enemies")

        elif powerup_type == "BLIZZARD":
            # Apply blizzard effect to all enemies in range
            self.particle_system.start_effect("BLIZZARD", mouse_pos)
            blizzard_radius = POWERUP_PROPERTIES["BLIZZARD"]["radius"]
            slow_factor = POWERUP_PROPERTIES["BLIZZARD"]["slow_factor"]
            duration = POWERUP_PROPERTIES["BLIZZARD"]["duration"]

            affected_count = 0
            for enemy in self.enemy_manager.enemies:
                distance = math.sqrt((enemy.pos[0] - mouse_pos[0])**2 +
                                      (enemy.pos[1] - mouse_pos[1])**2)
                if distance <= blizzard_radius:
                    enemy.apply_slow(duration, slow_factor)
                    affected_count += 1

            if affected_count > 0:
                self.money -= POWERUP_COSTS["BLIZZARD"]
                self.ui.start_powerup_cooldown("BLIZZARD")
                print(f"Blizzard activated, affecting {affected_count} enemies")

    def update(self):
        # Don't update game if showing player or difficulty menu
        if self.show_player_menu or self.show_difficulty_menu:
            return

        if not self.paused and not self.game_won:
            # Update game entities
            self.enemy_manager.update()
            self.tower_manager.update(self.enemy_manager.enemies)
            self.projectile_manager.update(self.enemy_manager.enemies)
            self.particle_system.update()

            # Handle collisions
            for projectile in self.projectile_manager.projectiles[:]:
                if not projectile.active or projectile.has_hit:
                    continue

                for enemy in self.enemy_manager.enemies[:]:
                    if projectile.collides_with(enemy):
                        enemy.take_damage(projectile.damage)
                        print(f"Hit confirmed! Damage: {projectile.damage}")
                        self.particle_system.create_hit_effect(projectile.pos)
                        projectile.active = False
                        projectile.has_hit = True
                        break

            # Remove defeated enemies and update score
            for enemy in self.enemy_manager.enemies[:]:
                if enemy.health <= 0:
                    print(f"Enemy defeated! Score before: {self.score}")
                    self.enemy_manager.enemies.remove(enemy)
                    reward = enemy.properties["reward"]  # Get reward from enemy properties
                    self.money += reward
                    self.score += 20
                    print(f"Earned ${reward}! New score: {self.score}")

                elif enemy.reached_end:
                    self.enemy_manager.enemies.remove(enemy)
                    self.lives -= 1

            # Check game over condition
            if self.lives <= 0:
                print(f"Game Over! Final Score: {self.score}")
                self.running = False

            # Sync current wave with enemy manager
            self.current_wave = self.enemy_manager.wave_number

            # Check for victory condition (completed wave 20)
            if self.current_wave > MAX_WAVE and not self.game_won:
                print(f"Victory! Completed all {MAX_WAVE} waves on {self.difficulty} difficulty!")
                self.game_won = True

            # Check if wave is complete and start quiz.  Pause game during quiz
            if self.enemy_manager.wave_complete and not self.quiz.is_active():
                # Check if player won before starting next wave
                if self.current_wave >= MAX_WAVE:
                    if not self.game_won:
                        print(f"Victory! Completed all {MAX_WAVE} waves on {self.difficulty} difficulty!")
                        self.game_won = True
                else:
                    self.paused = True #Pause the game while quiz is active.
                    # Start quiz with 2 questions per wave
                    self.quiz.start_quiz(self.quiz_type, 2)
                    print(f"Wave {self.current_wave} complete! Answer 2 math questions!")
            elif self.quiz.is_active() and self.enemy_manager.wave_complete == False:
                self.paused = True #Keep game paused until quiz is finished.


    def draw(self):
        try:
            # Show player menu first
            if self.show_player_menu:
                self.draw_player_menu()
                return

            # Show difficulty menu if not started
            if self.show_difficulty_menu:
                self.draw_difficulty_menu()
                return

            # Draw background
            self.screen.fill(BACKGROUND_COLOR)

            # Draw game elements
            self.path.draw(self.screen)
            self.tower_manager.draw(self.screen)
            self.enemy_manager.draw(self.screen)
            self.projectile_manager.draw(self.screen)
            self.particle_system.draw(self.screen)

            # Draw UI with updated score display and wave number
            self.ui.draw(self.screen, self.score, self.money, self.lives, self.current_wave, self.quiz_type)

            if self.paused:
                self.ui.draw_pause_menu(self.screen)
            elif self.game_won:
                # Draw victory message
                font = pygame.font.Font(None, 64)
                text = font.render("Victory!", True, (50, 200, 50))
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
                self.screen.blit(text, text_rect)

                # Draw difficulty and score
                small_font = pygame.font.Font(None, 36)
                difficulty_text = small_font.render(f"{self.difficulty.replace('_', ' ').title()} Mode", True, (50, 200, 50))
                difficulty_rect = difficulty_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
                self.screen.blit(difficulty_text, difficulty_rect)

                score_text = small_font.render(f"Final Score: {self.score}", True, (50, 200, 50))
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
                self.screen.blit(score_text, score_rect)

                # Draw exit message
                tiny_font = pygame.font.Font(None, 24)
                subtext = tiny_font.render("Press ESC to exit", True, (50, 200, 50))
                subtext_rect = subtext.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90))
                self.screen.blit(subtext, subtext_rect)

            # Draw quiz if active
            self.quiz.draw(self.screen)

            pygame.display.flip()
        except pygame.error as e:
            print(f"Drawing error: {e}")

    def run(self):
        print("Game started! Place towers to defend against incoming monsters!")
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
        except Exception as e:
            print(f"Game error: {e}")
        finally:
            pygame.quit()
            sys.exit()

    def set_quiz_type(self, quiz_type):
        """Set the quiz type based on who's playing (HOPE or BRYCE)"""
        self.quiz_type = quiz_type
        print(f"Quiz type set to: {quiz_type}")

if __name__ == "__main__":
    game = Game()
    game.run()