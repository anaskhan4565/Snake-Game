import pygame
import sys
import random
import math
import time
import numpy as np
from pygame import gfxdraw
from collections import deque, defaultdict

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BOARD_SIZE = 700
GRID_SIZE = 10
CELL_SIZE = BOARD_SIZE // GRID_SIZE
DICE_SIZE = 100
ANIMATION_SPEED = 15

# Difficulty settings
DIFFICULTY_TIMES = {
    "easy": 200,    # 10 minutes in seconds
    "medium": 120,  # 7 minutes in seconds
    "hard": 40,    # 5 minutes in seconds
}

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
PURPLE = (138, 43, 226)
TEAL = (0, 128, 128)
PINK = (255, 105, 180)
ORANGE = (255, 140, 0)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GREEN = (144, 238, 144)
BOARD_BG = (240, 230, 210)
BOARD_BORDER = (160, 82, 45)
HIGHLIGHT = (255, 255, 200)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snakes and Ladders")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 72)
button_font = pygame.font.Font(None, 36)
info_font = pygame.font.Font(None, 30)
cell_font = pygame.font.Font(None, 24)

class Player:
    def __init__(self, color, name, offset=(0, 0)):
        self.position = 1
        self.color = color
        self.name = name
        self.offset = offset
        self.target_position = 1
        self.is_moving = False
        self.move_progress = 0
        self.win = False
        
    def move(self, steps):
        self.target_position = min(self.position + steps, 100)
        self.is_moving = True
        self.move_progress = 0
        
    def update_animation(self):
        if self.is_moving:
            self.move_progress += 0.1
            if self.move_progress >= 1:
                self.position = self.target_position
                self.is_moving = False
                return True
        return False

    def get_current_display_position(self):
        if not self.is_moving:
            return self.position
        
        # Linear interpolation between current and target position
        return self.position + (self.target_position - self.position) * self.move_progress

    def draw(self, board):
        pos = self.get_current_display_position()
        x, y = board.get_coordinates(pos)
        x += self.offset[0]
        y += self.offset[1]
        
        # Draw player
        pygame.draw.circle(screen, self.color, (x, y), CELL_SIZE // 4)
        pygame.draw.circle(screen, BLACK, (x, y), CELL_SIZE // 4, 2)

class Board:
    def __init__(self):
        # Start with empty snakes and ladders
        self.snakes = {}
        self.ladders = {}
        
        # AI adaptive placement system
        self.roll_history = []  # Store all rolls
        self.current_position = 1
        self.ai_enabled = True
        self.last_placement_position = 1
        self.placement_threshold = 8  # Reduced: Player must advance this far for new placements
        self.max_elements = 20  # Increased: Maximum combined snakes and ladders
        self.last_prediction_time = 0
        self.prediction_interval = 2000  # ms between predictions
        self.difficulty = "easy"  # Default difficulty
        
        # Target ratios based on difficulty (increased snake ratios)
        self.difficulty_settings = {
            "easy": {
                "early_snake_ratio": 0.4,  # 40% snakes in early game (was 0.2)
                "mid_snake_ratio": 0.6,    # 60% snakes in mid game (was 0.4)
                "late_snake_ratio": 0.7,   # 70% snakes in late game (was 0.6)
                "snake_length_factor": 1.0, # Base snake length multiplier
                "ladder_length_factor": 1.0 # Base ladder length multiplier
            },
            "medium": {
                "early_snake_ratio": 0.6,  # 60% snakes in early game (was 0.4)
                "mid_snake_ratio": 0.7,    # 70% snakes in mid game (was 0.6)
                "late_snake_ratio": 0.85,  # 85% snakes in late game (was 0.8)
                "snake_length_factor": 1.3, # 30% longer snakes
                "ladder_length_factor": 0.8 # 20% shorter ladders
            },
            "hard": {
                "early_snake_ratio": 0.7,  # 70% snakes in early game (was 0.6)
                "mid_snake_ratio": 0.85,   # 85% snakes in mid game (was 0.8)
                "late_snake_ratio": 0.95,  # 95% snakes in late game (was 0.9)
                "snake_length_factor": 1.6, # 60% longer snakes
                "ladder_length_factor": 0.6 # 40% shorter ladders
            }
        }
        
        # Generate gradient for board cells
        self.cell_colors = []
        for i in range(GRID_SIZE):
            row = []
            for j in range(GRID_SIZE):
                # Alternate cell colors in a pattern
                if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):
                    color = (LIGHT_BLUE[0], LIGHT_BLUE[1], LIGHT_BLUE[2], 100)
                else:
                    color = (LIGHT_GREEN[0], LIGHT_GREEN[1], LIGHT_GREEN[2], 100)
                row.append(color)
            self.cell_colors.append(row)
    
    def configure_difficulty(self, difficulty):
        """Configure board settings based on difficulty"""
        self.difficulty = difficulty
        # Clear any existing elements
        self.snakes = {}
        self.ladders = {}
        
    def get_current_snake_ratio(self):
        """Get target snake ratio based on difficulty and player progress"""
        settings = self.difficulty_settings[self.difficulty]
        
        # Determine ratio based on progress
        if self.current_position < 30:
            return settings["early_snake_ratio"]
        elif self.current_position < 70:
            return settings["mid_snake_ratio"]
        else:
            return settings["late_snake_ratio"]
            
    def get_element_length_factors(self):
        """Get length factors for snakes and ladders based on difficulty and progress"""
        settings = self.difficulty_settings[self.difficulty]
        progress = self.current_position / 100
        
        # Base factors from difficulty
        snake_factor = settings["snake_length_factor"]
        ladder_factor = settings["ladder_length_factor"]
        
        # Modify factors based on progress (0-100%)
        # Snakes get longer as player advances
        progress_snake_boost = 1.0 + (progress * 1.0)  # 1.0-2.0x multiplier
        # Ladders get shorter as player advances
        progress_ladder_reduction = 1.0 - (progress * 0.5)  # 1.0-0.5x multiplier
        
        return snake_factor * progress_snake_boost, ladder_factor * progress_ladder_reduction
    
    def monte_carlo_simulation(self, current_position, num_simulations=1000, num_steps=3):
        """Run Monte Carlo simulation to predict likely future positions"""
        cell_counts = defaultdict(int)

        for _ in range(num_simulations):
            pos = current_position

            for _ in range(num_steps):
                dice = random.randint(1, 6)
                pos += dice
                
                # Apply any existing snakes and ladders in simulation
                if pos in self.snakes:
                    pos = self.snakes[pos]
                elif pos in self.ladders:
                    pos = self.ladders[pos]
                
                if pos > 100:
                    break
                    
                # Only count final positions for placement decisions
                if _ == num_steps - 1:
                    cell_counts[pos] += 1

        # Convert counts to probabilities
        total_hits = sum(cell_counts.values())
        if total_hits == 0:
            return {}
        cell_probabilities = {cell: count / total_hits for cell, count in cell_counts.items()}
        return cell_probabilities
    
    def update_player_position(self, new_position):
        """Update the player's current position for the AI"""
        self.current_position = new_position
        
        # Check if player has advanced enough for a new placement
        if new_position - self.last_placement_position >= self.placement_threshold:
            if random.random() < 0.7:  # 70% chance to add new elements
                self.add_adaptive_placements()
                self.last_placement_position = new_position
    
    def add_adaptive_placements(self):
        """Add new snakes and ladders based on Monte Carlo predictions"""
        # Get target snake ratio based on difficulty and progress
        target_snake_ratio = self.get_current_snake_ratio()
        
        # Current ratio of snakes
        total_elements = len(self.snakes) + len(self.ladders)
        current_snake_ratio = len(self.snakes) / max(total_elements, 1)
        
        # Get length factors
        snake_length_factor, ladder_length_factor = self.get_element_length_factors()
        
        # Check if we should add multiple elements at once based on progress
        # This helps populate the board faster with more snakes
        progress = self.current_position / 100
        max_additions = 1
        if progress > 0.3 and total_elements < self.max_elements * 0.5:
            max_additions = 2  # Add up to 2 elements at once in mid-game
        
        # Don't exceed maximum number of elements
        if total_elements >= self.max_elements:
            # Remove elements to maintain target ratio
            if current_snake_ratio < target_snake_ratio and self.ladders:
                # Remove a ladder to make room for a snake
                key_to_remove = random.choice(list(self.ladders.keys()))
                del self.ladders[key_to_remove]
            elif current_snake_ratio > target_snake_ratio and self.snakes:
                # Remove a snake to make room for a ladder
                key_to_remove = random.choice(list(self.snakes.keys()))
                del self.snakes[key_to_remove]
            else:
                # Can't adjust ratio further
                return
        
        # Run Monte Carlo simulation
        predictions = self.monte_carlo_simulation(self.current_position)
        if not predictions:
            return
            
        # Find high and low probability cells
        sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        
        # Higher chance of adding snakes over ladders (overriding target ratio slightly)
        snake_bias = 0.2  # Add 20% to snake probability
        should_add_snake = (current_snake_ratio < target_snake_ratio) or (random.random() < target_snake_ratio + snake_bias)
        
        elements_added = 0
        while elements_added < max_additions and total_elements + elements_added < self.max_elements:
            # Place snake at a high probability position (where player is likely to land)
            if should_add_snake:
                added = self._add_snake(sorted_predictions, snake_length_factor)
                if added:
                    elements_added += 1
                    # For next iteration (if any), still favor snakes but give some chance for ladders
                    should_add_snake = random.random() < 0.7  # 70% chance to add another snake
                else:
                    break  # Couldn't add a snake
            # Place ladder at a low probability position (where player is unlikely to land)
            else:
                added = self._add_ladder(sorted_predictions, ladder_length_factor)
                if added:
                    elements_added += 1
                    # For next iteration (if any), favor adding a snake
                    should_add_snake = random.random() < 0.8  # 80% chance to add a snake next
                else:
                    # If we couldn't add a ladder, try adding a snake instead
                    added = self._add_snake(sorted_predictions, snake_length_factor)
                    if added:
                        elements_added += 1
                    break
    
    def _add_snake(self, sorted_predictions, snake_length_factor):
        """Helper method to add a snake at a high probability position"""
        # Try multiple positions in case some are invalid
        for cell, prob in sorted_predictions[:8]:  # Increased from top 5 to top 8 most likely positions
            # Ensure we're not overwriting existing elements
            if cell not in self.snakes and cell not in self.ladders and 10 < cell < 95:
                # Calculate drop distance based on probability, progress and difficulty
                base_drop = 10
                progress = self.current_position / 100
                
                # Higher probability and higher progress means longer snake
                drop_distance = int(base_drop + prob * 30 * snake_length_factor)
                drop_distance = min(drop_distance, cell - 1)  # Don't go below 1
                new_pos = max(cell - drop_distance, 1)
                self.snakes[cell] = new_pos
                return True
        return False
    
    def _add_ladder(self, sorted_predictions, ladder_length_factor):
        """Helper method to add a ladder at a low probability position"""
        for cell, prob in sorted_predictions[-8:]:  # Increased from bottom 5 to bottom 8 least likely positions
            # Ensure we're not overwriting existing elements
            if cell not in self.snakes and cell not in self.ladders and 5 < cell < 80:
                # Calculate climb distance - shorter based on difficulty and progress
                base_climb = 10
                
                # Lower probability means bigger climb, but reduced by ladder_length_factor
                climb_distance = int(base_climb + (1 - prob) * 30 * ladder_length_factor)
                new_pos = min(cell + climb_distance, 99)  # Don't go directly to 100
                self.ladders[cell] = new_pos
                return True
        return False
    
    def get_coordinates(self, position):
        # Convert the position (1-100) to (x, y) coordinates
        position -= 1  # Convert to 0-99
        row = GRID_SIZE - 1 - position // GRID_SIZE
        col = position % GRID_SIZE if (GRID_SIZE - 1 - row) % 2 == 0 else GRID_SIZE - 1 - position % GRID_SIZE
        
        # Add board offset
        board_x = (SCREEN_WIDTH - BOARD_SIZE) // 2
        board_y = (SCREEN_HEIGHT - BOARD_SIZE) // 2
        
        x = board_x + col * CELL_SIZE + CELL_SIZE // 2
        y = board_y + row * CELL_SIZE + CELL_SIZE // 2
        
        return x, y
        
    def draw(self):
        # Draw board background
        board_x = (SCREEN_WIDTH - BOARD_SIZE) // 2
        board_y = (SCREEN_HEIGHT - BOARD_SIZE) // 2
        
        # Draw fancy board with shadow
        shadow_offset = 10
        pygame.draw.rect(screen, (0, 0, 0, 120), 
                        (board_x + shadow_offset, board_y + shadow_offset, BOARD_SIZE, BOARD_SIZE), 
                        border_radius=15)
        pygame.draw.rect(screen, BOARD_BG, (board_x, board_y, BOARD_SIZE, BOARD_SIZE), border_radius=10)
        pygame.draw.rect(screen, BOARD_BORDER, (board_x, board_y, BOARD_SIZE, BOARD_SIZE), 5, border_radius=10)
        
        # Draw grid cells with numbers
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                cell_x = board_x + j * CELL_SIZE
                cell_y = board_y + i * CELL_SIZE
                
                # Determine cell number
                row = GRID_SIZE - 1 - i
                col = j if row % 2 == 0 else GRID_SIZE - 1 - j
                cell_num = row * GRID_SIZE + col + 1
                
                # Draw cell with translucent color
                pygame.draw.rect(screen, self.cell_colors[i][j], 
                                (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, BLACK, 
                                (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1)
                
                # Draw cell number
                num_text = cell_font.render(str(cell_num), True, BLACK)
                num_rect = num_text.get_rect(bottomright=(cell_x + CELL_SIZE - 5, cell_y + CELL_SIZE - 5))
                screen.blit(num_text, num_rect)
        
        # Draw snakes
        for start, end in self.snakes.items():
            start_x, start_y = self.get_coordinates(start)
            end_x, end_y = self.get_coordinates(end)
            
            # Draw fancy snake curve
            self.draw_snake(start_x, start_y, end_x, end_y)
        
        # Draw ladders
        for start, end in self.ladders.items():
            start_x, start_y = self.get_coordinates(start)
            end_x, end_y = self.get_coordinates(end)
            
            # Draw fancy ladder
            self.draw_ladder(start_x, start_y, end_x, end_y)
    
    def draw_snake(self, x1, y1, x2, y2):
        # Calculate midpoints for Bezier curve
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Create a curved path
        ctrl_x = x1 + dy/3
        ctrl_y = y1 + dx/3
        
        # Draw the snake body
        points = []
        steps = int(distance / 5)
        steps = max(steps, 20)  # Ensure enough points for a smooth curve
        
        for i in range(steps + 1):
            t = i / steps
            # Quadratic Bezier curve formula
            x = (1-t)**2 * x1 + 2 * (1-t) * t * ctrl_x + t**2 * x2
            y = (1-t)**2 * y1 + 2 * (1-t) * t * ctrl_y + t**2 * y2
            
            # Add some sine wave effect for a more snake-like appearance
            wave = math.sin(i / 2) * 10
            perp_x = -dy / distance
            perp_y = dx / distance
            x += perp_x * wave
            y += perp_y * wave
            
            points.append((x, y))
        
        # Draw the snake body with gradient
        for i in range(len(points) - 1):
            progress = i / (len(points) - 1)
            thickness = 6 - progress * 2  # Make the snake thinner towards the tail
            color_r = int(RED[0] * (1 - progress) + ORANGE[0] * progress)
            color_g = int(RED[1] * (1 - progress) + ORANGE[1] * progress)
            color_b = int(RED[2] * (1 - progress) + ORANGE[2] * progress)
            color = (color_r, color_g, color_b)
            
            pygame.draw.line(screen, color, points[i], points[i+1], int(thickness))
        
        # Draw snake head
        pygame.draw.circle(screen, RED, points[0], 8)
        pygame.draw.circle(screen, BLACK, points[0], 8, 1)
        
        # Draw eyes
        pygame.draw.circle(screen, WHITE, (points[0][0] - 3, points[0][1] - 3), 3)
        pygame.draw.circle(screen, WHITE, (points[0][0] + 3, points[0][1] - 3), 3)
        pygame.draw.circle(screen, BLACK, (points[0][0] - 3, points[0][1] - 3), 1)
        pygame.draw.circle(screen, BLACK, (points[0][0] + 3, points[0][1] - 3), 1)

    def draw_ladder(self, x1, y1, x2, y2):
        # Ladder parameters
        width = 20
        rungs = 5 + int(math.sqrt((x2-x1)**2 + (y2-y1)**2) / 40)
        
        # Calculate direction and perpendicular vectors
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        dx, dy = dx/length, dy/length
        
        # Perpendicular direction for ladder width
        px, py = -dy, dx
        
        # Draw ladder sides
        for side in [-1, 1]:
            pygame.draw.line(screen, BROWN, 
                           (x1 + side * width/2 * px, y1 + side * width/2 * py),
                           (x2 + side * width/2 * px, y2 + side * width/2 * py), 5)
        
        # Draw rungs
        for i in range(rungs):
            t = i / (rungs - 1)
            rx = x1 + t * (x2 - x1)
            ry = y1 + t * (y2 - y1)
            
            pygame.draw.line(screen, BROWN, 
                           (rx - width/2 * px, ry - width/2 * py),
                           (rx + width/2 * px, ry + width/2 * py), 4)

class Dice:
    def __init__(self):
        self.value = 1
        self.rolling = False
        self.roll_frames = 0
        self.total_frames = 20
        self.x = SCREEN_WIDTH - 150
        self.y = SCREEN_HEIGHT // 2
        
    def roll(self):
        self.rolling = True
        self.roll_frames = 0
        self.value = random.randint(1, 6)
        
    def update(self):
        if self.rolling:
            self.roll_frames += 1
            if self.roll_frames < self.total_frames:
                # Show random values while rolling
                self.value = random.randint(1, 6)
            else:
                self.rolling = False
                return True
        return False
                
    def draw(self):
        # Draw dice with 3D effect
        size = DICE_SIZE
        pygame.draw.rect(screen, WHITE, (self.x - size//2, self.y - size//2, size, size), border_radius=10)
        
        # Add shadow for 3D effect
        if not self.rolling or self.roll_frames > self.total_frames * 0.7:
            shadow_size = 4
            pygame.draw.rect(screen, (200, 200, 200), 
                            (self.x - size//2 + shadow_size, self.y - size//2 + shadow_size, 
                             size - shadow_size*2, size - shadow_size*2), 
                            border_radius=8)
        
        # Draw border
        pygame.draw.rect(screen, BLACK, (self.x - size//2, self.y - size//2, size, size), 2, border_radius=10)
        
        # Draw dots based on dice value
        dot_positions = {
            1: [(0, 0)],
            2: [(-0.3, -0.3), (0.3, 0.3)],
            3: [(-0.3, -0.3), (0, 0), (0.3, 0.3)],
            4: [(-0.3, -0.3), (-0.3, 0.3), (0.3, -0.3), (0.3, 0.3)],
            5: [(-0.3, -0.3), (-0.3, 0.3), (0, 0), (0.3, -0.3), (0.3, 0.3)],
            6: [(-0.3, -0.3), (-0.3, 0), (-0.3, 0.3), (0.3, -0.3), (0.3, 0), (0.3, 0.3)]
        }
        
        dot_color = BLACK
        if self.rolling:
            # Pulse effect while rolling
            pulse = math.sin(self.roll_frames * 0.5) * 0.5 + 0.5
            dot_color = (int(pulse * 255), 0, 0)
            
        for pos in dot_positions[self.value]:
            x = self.x + pos[0] * size * 0.6
            y = self.y + pos[1] * size * 0.6
            pygame.draw.circle(screen, dot_color, (int(x), int(y)), size // 10)

class Button:
    def __init__(self, x, y, width, height, text, color=BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.pressed = False
        
    def draw(self):
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        if self.pressed:
            # Draw pressed effect
            pygame.draw.rect(screen, BLACK, (self.rect.x + 3, self.rect.y + 3, self.rect.width, self.rect.height), border_radius=8)
        
        # Draw button with shadow
        pygame.draw.rect(screen, (50, 50, 50), (self.rect.x + 3, self.rect.y + 3, self.rect.width, self.rect.height), border_radius=8)
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
        
        # Draw text
        text_surface = button_font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.pressed = True
            return True
        return False
    
    def reset(self):
        self.pressed = False

class Game:
    def __init__(self):
        self.board = Board()
        self.player = Player(RED, "Player", (0, 0))
        self.dice = Dice()
        self.state = "difficulty"  # difficulty, playing, end
        self.difficulty = None
        self.time_left = 0
        self.start_time = 0
        self.message = ""
        self.message_time = 0
        self.last_dice_value = 0
        self.previous_position = 1
        
        # Buttons
        btn_width, btn_height = 150, 50
        self.easy_button = Button(
            SCREEN_WIDTH // 2 - btn_width // 2, SCREEN_HEIGHT // 2 - 100,
            btn_width, btn_height, "Easy", GREEN
        )
        self.medium_button = Button(
            SCREEN_WIDTH // 2 - btn_width // 2, SCREEN_HEIGHT // 2,
            btn_width, btn_height, "Medium", YELLOW
        )
        self.hard_button = Button(
            SCREEN_WIDTH // 2 - btn_width // 2, SCREEN_HEIGHT // 2 + 100,
            btn_width, btn_height, "Hard", RED
        )
        self.roll_button = Button(
            SCREEN_WIDTH - 225, SCREEN_HEIGHT - 150, 
            btn_width, btn_height, "Roll Dice", GREEN
        )
        self.restart_button = Button(
            SCREEN_WIDTH // 2 - btn_width // 2, SCREEN_HEIGHT // 2 + 100,
            btn_width, btn_height, "Play Again", GREEN
        )
        
        # Animation flags
        self.animating = False
        self.animation_done = False
        self.show_win_popup = False
        self.confetti_particles = []
        
    def set_message(self, text):
        self.message = text
        self.message_time = pygame.time.get_ticks()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "difficulty":
                    if self.easy_button.check_click(event.pos):
                        self.difficulty = "easy"
                        self.start_game()
                    elif self.medium_button.check_click(event.pos):
                        self.difficulty = "medium"
                        self.start_game()
                    elif self.hard_button.check_click(event.pos):
                        self.difficulty = "hard"
                        self.start_game()
                
                elif self.state == "playing" and not self.animating:
                    if self.roll_button.check_click(event.pos):
                        self.dice.roll()
                        self.animating = True
                
                elif self.state == "end" and self.restart_button.check_click(event.pos):
                    self.__init__()  # Reset the game
                    
            if event.type == pygame.MOUSEBUTTONUP:
                self.roll_button.reset()
                self.easy_button.reset()
                self.medium_button.reset()
                self.hard_button.reset()
                self.restart_button.reset()
                    
    def start_game(self):
        self.state = "playing"
        self.time_left = DIFFICULTY_TIMES[self.difficulty]
        self.start_time = time.time()
        
        # Configure board based on difficulty
        self.board.configure_difficulty(self.difficulty)
        
    def update(self):
        if self.state == "playing":
            # Update timer
            elapsed = time.time() - self.start_time
            self.time_left = max(0, DIFFICULTY_TIMES[self.difficulty] - elapsed)
            
            if self.time_left <= 0:
                self.state = "end"
                self.set_message("Time's up! Game Over!")
                return
                
            if self.animating:
                # Dice rolling animation
                if self.dice.update() and not self.animation_done:
                    # After dice roll is complete, move player
                    self.last_dice_value = self.dice.value
                    self.previous_position = self.player.position
                    self.player.move(self.dice.value)
                    self.animation_done = True
                    self.set_message(f"You rolled a {self.dice.value}")
                
                # Player movement animation
                if self.animation_done:
                    if self.player.update_animation():
                        # After player movement is complete
                        position = self.player.position
                        
                        # If player has moved forward, spawn new snakes and ladders
                        if position > self.previous_position:
                            # Update AI with new player position and check if we should add elements
                            self.board.update_player_position(position)
                            
                            # Add notification if new elements were added
                            if len(self.board.snakes) + len(self.board.ladders) > 0:
                                self.set_message("AI adapting the board...")
                        
                        # Check for snakes
                        if position in self.board.snakes:
                            new_pos = self.board.snakes[position]
                            self.player.move(new_pos - position)
                            self.set_message("Oh no! You hit a snake!")
                            return
                            
                        # Check for ladders
                        if position in self.board.ladders:
                            new_pos = self.board.ladders[position]
                            self.player.move(new_pos - position)
                            self.set_message("Yay! You climbed a ladder!")
                            return
                            
                        # Check for win
                        if position == 100:
                            self.state = "end"
                            self.set_message("Congratulations! You won!")
                            self.show_win_popup = True
                            self.create_confetti()
                            return
                        
                        self.animating = False
                        self.animation_done = False
    
    def create_confetti(self):
        # Create colorful confetti particles
        self.confetti_particles = []
        colors = [RED, GREEN, BLUE, YELLOW, PURPLE, PINK, ORANGE]
        for _ in range(150):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(-SCREEN_HEIGHT, 0)
            size = random.randint(5, 15)
            speed = random.uniform(2, 8)
            angle = random.uniform(0, math.pi * 2)
            color = random.choice(colors)
            self.confetti_particles.append({
                'x': x, 'y': y, 'size': size, 'speed': speed, 
                'angle': angle, 'color': color
            })
    
    def update_confetti(self):
        # Update confetti animation
        if not self.confetti_particles:
            return
            
        for particle in self.confetti_particles:
            # Add gravity and some horizontal movement
            particle['y'] += particle['speed']
            particle['x'] += math.sin(particle['angle']) * 2
            # If particle goes off screen, reset from top
            if particle['y'] > SCREEN_HEIGHT:
                particle['y'] = random.randint(-50, 0)
                particle['x'] = random.randint(0, SCREEN_WIDTH)
    
    def draw_win_popup(self):
        # Draw a celebration popup window
        if not self.show_win_popup:
            return
            
        # Update and draw confetti
        self.update_confetti()
        for particle in self.confetti_particles:
            pygame.draw.rect(
                screen, 
                particle['color'], 
                (particle['x'], particle['y'], particle['size'], particle['size'])
            )
        
        # Draw popup window
        popup_width, popup_height = 500, 300
        popup_x = SCREEN_WIDTH // 2 - popup_width // 2
        popup_y = SCREEN_HEIGHT // 2 - popup_height // 2
        
        # Draw shadow
        pygame.draw.rect(
            screen, 
            (0, 0, 0, 150), 
            (popup_x + 10, popup_y + 10, popup_width, popup_height),
            border_radius=15
        )
        
        # Draw popup
        pygame.draw.rect(
            screen, 
            WHITE, 
            (popup_x, popup_y, popup_width, popup_height),
            border_radius=15
        )
        pygame.draw.rect(
            screen, 
            GOLD, 
            (popup_x, popup_y, popup_width, popup_height),
            5,
            border_radius=15
        )
        
        # Draw congratulations text
        congrats_text = title_font.render("CONGRATULATIONS!", True, GOLD)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, popup_y + 80))
        screen.blit(congrats_text, congrats_rect)
        
        # Draw win message
        minutes_taken = int(DIFFICULTY_TIMES[self.difficulty] - self.time_left) // 60
        seconds_taken = int(DIFFICULTY_TIMES[self.difficulty] - self.time_left) % 60
        
        win_message = [
            f"You've completed the game in",
            f"{minutes_taken:02d}:{seconds_taken:02d}",
            f"on {self.difficulty.capitalize()} difficulty!"
        ]
        
        for i, line in enumerate(win_message):
            text = info_font.render(line, True, BLACK)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, popup_y + 140 + i * 30))
            screen.blit(text, rect)
            
        # Draw close button
        close_btn_rect = pygame.Rect(popup_x + popup_width - 40, popup_y + 15, 30, 30)
        pygame.draw.rect(screen, RED, close_btn_rect, border_radius=15)
        pygame.draw.rect(screen, BLACK, close_btn_rect, 2, border_radius=15)
        close_text = info_font.render("X", True, WHITE)
        close_rect = close_text.get_rect(center=close_btn_rect.center)
        screen.blit(close_text, close_rect)
        
        # Check if close button is clicked
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and close_btn_rect.collidepoint(mouse_pos):
            self.show_win_popup = False
    
    def draw(self):
        # Fill background with a gradient
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            r = int(173 + (230 - 173) * progress)
            g = int(216 + (230 - 216) * progress)
            b = int(230 + (210 - 230) * progress)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
        if self.state == "difficulty":
            # Draw title screen
            title_text = title_font.render("Snakes and Ladders", True, (70, 50, 120))
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            screen.blit(title_text, title_rect)
            
            # Draw instructions
            instructions = [
                "Choose your difficulty level:",
                "Easy: 10 minutes",
                "Medium: 7 minutes",
                "Hard: 5 minutes",
                "",
                "The AI will place snakes and ladders as you move!",
                "Snakes appear where you're likely to land, ladders where you're not."
            ]
            
            for i, instruction in enumerate(instructions):
                text = info_font.render(instruction, True, BLACK)
                rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200 + i * 30))
                screen.blit(text, rect)
            
            self.easy_button.draw()
            self.medium_button.draw()
            self.hard_button.draw()
            
        elif self.state == "playing" or self.state == "end":
            # Draw the game board
            self.board.draw()
            
            # Draw player
            self.player.draw(self.board)
            
            # Draw dice
            self.dice.draw()
            
            # Draw player info
            box_y = 100
            pygame.draw.rect(screen, self.player.color, (50, box_y, 200, 50), border_radius=8)
            pygame.draw.rect(screen, BLACK, (50, box_y, 200, 50), 2, border_radius=8)
            
            # Player name and position
            name_text = info_font.render(f"Position: {self.player.position}", True, WHITE)
            name_rect = name_text.get_rect(center=(150, box_y + 25))
            screen.blit(name_text, name_rect)
            
            # Draw timer
            minutes = int(self.time_left // 60)
            seconds = int(self.time_left % 60)
            timer_text = info_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, BLACK)
            timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(timer_text, timer_rect)
            
            # Draw buttons in playing state
            if self.state == "playing":
                self.roll_button.draw()
                
                # Show snake/ladder counts
                elements_text = info_font.render(f"Snakes: {len(self.board.snakes)}  Ladders: {len(self.board.ladders)}", True, BLACK)
                elements_rect = elements_text.get_rect(topleft=(50, 50))
                screen.blit(elements_text, elements_rect)
            
            # Draw message
            if self.message and pygame.time.get_ticks() - self.message_time < 3000:
                message_text = info_font.render(self.message, True, BLACK)
                message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
                # Draw background for better readability
                bg_rect = message_rect.inflate(20, 10)
                pygame.draw.rect(screen, (255, 255, 200, 180), bg_rect, border_radius=5)
                pygame.draw.rect(screen, BLACK, bg_rect, 1, border_radius=5)
                screen.blit(message_text, message_rect)
            
            # Draw game over screen if in end state
            if self.state == "end":
                # Semi-transparent overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))
                
                # Draw game over message
                if self.player.position == 100:
                    win_text = title_font.render("You Won!", True, GREEN)
                else:
                    win_text = title_font.render("Game Over!", True, RED)
                win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                
                # Draw text shadow for better visibility
                shadow_text = title_font.render(win_text.get_text(), True, BLACK)
                shadow_rect = shadow_text.get_rect(center=(win_rect.centerx + 3, win_rect.centery + 3))
                screen.blit(shadow_text, shadow_rect)
                screen.blit(win_text, win_rect)
                
                self.restart_button.draw()
                
                # Draw win popup if player won
                if self.show_win_popup and self.player.position == 100:
                    self.draw_win_popup()

def main():
    game = Game()
    
    # Main game loop
    while True:
        game.handle_events()
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main() 