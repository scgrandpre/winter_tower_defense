import random
import pygame
from .constants import *

class MathQuiz:
    def __init__(self):
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.current_question = None
        self.answer = None
        self.input_text = ""
        self.active = False
        self.correct_answer = False
        self.show_result = False
        self.result_timer = 0

        # Multi-question tracking
        self.total_questions = 0
        self.current_question_num = 0
        self.correct_count = 0
        self.quiz_complete = False

    def start_quiz(self, quiz_type, num_questions):
        """Start a new quiz with specified number of questions"""
        self.quiz_type = quiz_type
        self.total_questions = num_questions
        self.current_question_num = 0
        self.correct_count = 0
        self.quiz_complete = False
        self.generate_next_question()

    def generate_next_question(self):
        """Generate the next question in the quiz"""
        self.current_question_num += 1

        if self.quiz_type == "HOPE":  # Multiplication for Hope
            num1 = random.randint(0, 12)
            num2 = random.randint(0, 12)
            self.answer = num1 * num2
            self.answer_fraction = None  # Not a fraction for HOPE
            self.current_question = f"What is {num1} × {num2}?"
        else:  # Fraction multiplication and division for Bryce
            operation = random.choice(["multiply", "divide"])

            if operation == "multiply":
                # Generate two fractions
                num1 = random.randint(1, 12)
                den1 = random.randint(1, 12)
                num2 = random.randint(1, 12)
                den2 = random.randint(1, 12)

                # Calculate answer: (num1/den1) * (num2/den2) = (num1*num2)/(den1*den2)
                answer_num = num1 * num2
                answer_den = den1 * den2

                # Simplify the fraction
                from math import gcd
                common = gcd(answer_num, answer_den)
                answer_num //= common
                answer_den //= common

                self.current_question = f"What is {num1}/{den1} × {num2}/{den2}? (answer as fraction)"
                self.answer_fraction = (answer_num, answer_den)
                self.answer = answer_num / answer_den  # Keep decimal for display

            else:  # division
                # Generate two fractions
                num1 = random.randint(1, 12)
                den1 = random.randint(1, 12)
                num2 = random.randint(1, 12)
                den2 = random.randint(1, 12)

                # Calculate answer: (num1/den1) ÷ (num2/den2) = (num1*den2)/(den1*num2)
                answer_num = num1 * den2
                answer_den = den1 * num2

                # Simplify
                from math import gcd
                common = gcd(answer_num, answer_den)
                answer_num //= common
                answer_den //= common

                self.current_question = f"What is {num1}/{den1} ÷ {num2}/{den2}? (answer as fraction)"
                self.answer_fraction = (answer_num, answer_den)
                self.answer = answer_num / answer_den  # Keep decimal for display

        self.input_text = ""
        self.active = True
        self.show_result = False
        self.correct_answer = False
        if not hasattr(self, 'answer_fraction'):
            self.answer_fraction = None

    def _parse_fraction(self, text):
        """Parse fraction input like '3/4', '1 1/2', '5', etc. Returns (numerator, denominator) or None"""
        text = text.strip()
        if not text:
            return None
        
        try:
            # Check for mixed number like "1 1/2"
            if ' ' in text:
                parts = text.split(' ')
                if len(parts) == 2:
                    whole = int(parts[0])
                    if '/' in parts[1]:
                        num, den = map(int, parts[1].split('/'))
                        if den == 0:
                            return None
                        # Convert to improper fraction
                        return (whole * den + num, den)
                    else:
                        return None
            
            # Check for simple fraction like "3/4"
            if '/' in text:
                parts = text.split('/')
                if len(parts) == 2:
                    num = int(parts[0])
                    den = int(parts[1])
                    if den == 0:
                        return None
                    return (num, den)
            
            # Check for whole number like "5"
            whole = int(text)
            return (whole, 1)
        except (ValueError, IndexError):
            return None

    def generate_question(self, quiz_type):
        """Legacy method - start a single question quiz"""
        self.start_quiz(quiz_type, 1)

    def handle_input(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                try:
                    # Handle both integer and decimal answers for HOPE
                    if self.quiz_type == "HOPE":
                        user_answer = float(self.input_text)
                        # For multiplication, accept both integer and decimal format
                        # Allow small tolerance for floating point comparison
                        self.correct_answer = abs(user_answer - self.answer) < 0.01
                    else:  # BRYCE - fraction answers
                        # Parse fraction input (supports "3/4", "1 1/2", "1/2", etc.)
                        user_fraction = self._parse_fraction(self.input_text)
                        if user_fraction and self.answer_fraction:
                            # Compare fractions by cross-multiplying
                            user_num, user_den = user_fraction
                            ans_num, ans_den = self.answer_fraction
                            # Fractions are equal if num1*den2 == num2*den1
                            self.correct_answer = (user_num * ans_den == ans_num * user_den)
                        else:
                            self.correct_answer = False
                    if self.correct_answer:
                        self.correct_count += 1

                    self.show_result = True
                    self.result_timer = pygame.time.get_ticks()
                    self.active = False

                    # Check if quiz is complete
                    if self.current_question_num >= self.total_questions:
                        self.quiz_complete = True
                        return True  # Signal quiz completion
                    return False  # More questions remain

                except ValueError:
                    self.input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key >= pygame.K_0 and event.key <= pygame.K_9:
                if len(self.input_text) < 15:  # Allow longer for fractions
                    self.input_text += event.unicode
            elif event.key == pygame.K_SLASH or event.key == pygame.K_KP_DIVIDE:
                # Allow slash for fraction input (BRYCE only)
                if self.quiz_type == "BRYCE" and '/' not in self.input_text:
                    self.input_text += '/'
            elif event.key == pygame.K_PERIOD:
                # Allow decimal point for HOPE
                if self.quiz_type == "HOPE" and '.' not in self.input_text:
                    self.input_text += '.'
            elif event.key == pygame.K_SPACE:
                # Allow space for mixed numbers like "1 1/2" (BRYCE only)
                if self.quiz_type == "BRYCE" and ' ' not in self.input_text:
                    self.input_text += ' '

        return False

    def draw(self, screen):
        if not (self.active or self.show_result):
            return

        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        if self.active:
            # Draw progress indicator
            progress_text = self.small_font.render(f"Question {self.current_question_num} of {self.total_questions}", True, (200, 200, 200))
            progress_rect = progress_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            screen.blit(progress_text, progress_rect)

            # Draw score
            score_text = self.small_font.render(f"Correct: {self.correct_count}", True, (100, 255, 100))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70))
            screen.blit(score_text, score_rect)

            # Draw question
            question_text = self.font.render(self.current_question, True, (255, 255, 255))
            question_rect = question_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            screen.blit(question_text, question_rect)

            # Draw input box
            input_text = self.font.render(self.input_text + "_", True, (255, 255, 255))
            input_rect = input_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            screen.blit(input_text, input_rect)

            # Draw instructions
            if self.quiz_type == "BRYCE":
                instructions = self.small_font.render("Type your answer as a fraction (e.g., 3/4 or 1 1/2) and press Enter", True, (200, 200, 200))
            else:
                instructions = self.small_font.render("Type your answer and press Enter", True, (200, 200, 200))
            inst_rect = instructions.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
            screen.blit(instructions, inst_rect)

        elif self.show_result:
            current_time = pygame.time.get_ticks()
            if current_time - self.result_timer < 1500:  # Show result for 1.5 seconds
                if self.correct_answer:
                    result_text = self.font.render("Correct!", True, (50, 255, 50))
                else:
                    # Display answer in appropriate format
                    if self.quiz_type == "BRYCE" and self.answer_fraction:
                        ans_num, ans_den = self.answer_fraction
                        if ans_den == 1:
                            answer_display = str(ans_num)
                        else:
                            answer_display = f"{ans_num}/{ans_den}"
                    else:
                        answer_display = str(int(self.answer)) if self.answer == int(self.answer) else str(self.answer)
                    result_text = self.font.render(f"Incorrect! The answer was {answer_display}", True, (255, 50, 50))
                result_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(result_text, result_rect)

                # Show final summary if quiz is complete
                if self.quiz_complete:
                    summary_text = self.small_font.render(f"Quiz Complete: {self.correct_count}/{self.total_questions} correct!", True, (255, 255, 100))
                    summary_rect = summary_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
                    screen.blit(summary_text, summary_rect)
            else:
                self.show_result = False
                # If more questions remain, generate the next one
                if not self.quiz_complete:
                    self.generate_next_question()

    def is_active(self):
        return self.active or self.show_result
