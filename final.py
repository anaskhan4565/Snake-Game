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

# Get screen info for fullscreen
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
BOARD_SIZE = min(SCREEN_HEIGHT - 150, 800)  # Adjusted board size for fullscreen
GRID_SIZE = 10
CELL_SIZE = BOARD_SIZE // GRID_SIZE
DICE_SIZE = 80  # Adjusted dice size for fullscreen
ANIMATION_SPEED = 15

# Difficulty settings
DIFFICULTY_TIMES = {
    "easy": 120,    # 2 minutes in seconds
    "medium": 60,  # 1  minutes 20 in seconds
    "hard": 30,    # 5 minutes in seconds
}

# Colors - Forest Theme
# Primary colors
WHITE = (255, 255, 255)
BLACK = (33, 33, 33)
PRIMARY = (34, 139, 34)  # Forest Green
SECONDARY = (85, 107, 47)  # Dark Olive Green
ACCENT = (218, 165, 32)  # Golden Rod

# Game elements
BOARD_BG = (240, 248, 255)  # Alice Blue (light sky color)
BOARD_BORDER = (139, 69, 19)  # Saddle Brown (wood color)
CELL_COLOR_1 = (144, 238, 144)  # Light Green
CELL_COLOR_2 = (154, 205, 50)  # Yellow Green
GRID_LINE_COLOR = (85, 107, 47, 100)  # Semi-transparent Dark Olive Green

# Power-up colors
POWER_UP_COLORS = {
    "time_boost": (50, 205, 50),  # Lime Green
    "snake_killer": (178, 34, 34),  # Firebrick Red
    "immunity": (186, 85, 211)  # Medium Orchid
}

# UI elements
BUTTON_COLOR = (34, 139, 34)  # Forest Green
BUTTON_HOVER = (60, 179, 113)  # Medium Sea Green
SUCCESS_COLOR = (50, 205, 50)  # Lime Green
WARNING_COLOR = (205, 133, 63)  # Peru (brownish orange)
ERROR_COLOR = (178, 34, 34)  # Firebrick Red

# Game pieces
PLAYER_COLOR = (218, 165, 32)  # Golden Rod
SNAKE_COLOR = (139, 69, 19)  # Saddle Brown
LADDER_COLOR = (160, 82, 45)  # Sienna (wood color)
LADDER_RUNG_COLOR = (139, 69, 19)  # Saddle Brown for rungs
GIFT_BOX = (186, 85, 211)  # Medium Orchid

# Text colors
TEXT_PRIMARY = (33, 33, 33)  # Dark Gray
TEXT_SECONDARY = (85, 107, 47)  # Dark Olive Green
TEXT_LIGHT = (240, 248, 255)  # Alice Blue

# Forest Theme Elements
LEAF_COLORS = [
    (34, 139, 34),  # Forest Green
    (50, 205, 50),  # Lime Green
    (107, 142, 35),  # Olive Drab
    (85, 107, 47),  # Dark Olive Green
    (154, 205, 50)  # Yellow Green
]

TREE_COLORS = [
    (139, 69, 19),  # Saddle Brown
    (160, 82, 45),  # Sienna
    (165, 42, 42),  # Brown
    (128, 0, 0),    # Maroon
    (205, 133, 63)  # Peru
]

# Power-up types and their effects
POWER_UPS = {
    "time_boost": {
        "name": "Time Boost",
        "description": "Adds 5 seconds to the timer",
        "color": POWER_UP_COLORS["time_boost"],
        "effect": lambda game: game.add_time(5)  # Use a method instead of direct attribute change
    },
    "snake_killer": {
        "name": "Snake Killer",
        "description": "Removes a random snake from the board",
        "color": POWER_UP_COLORS["snake_killer"],
        "effect": lambda game: game.board.remove_random_snake()
    },
    "immunity": {
        "name": "Immunity",
        "description": "Protects from next snake bite",
        "color": POWER_UP_COLORS["immunity"],
        "effect": lambda game: setattr(game.player, 'has_immunity', True)
    }
}

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Snakes and Ladders")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 72)  # Reduced font size
button_font = pygame.font.Font(None, 36)  # Reduced font size
info_font = pygame.font.Font(None, 28)  # Reduced font size
cell_font = pygame.font.Font(None, 24)  # Reduced font size

class Player:
    def __init__(self, color, name, offset=(0, 0)):
        self.position = 1
        self.color = PLAYER_COLOR
        self.name = name
        self.offset = offset
        self.target_position = 1
        self.is_moving = False
        self.move_progress = 0
        self.win = False
        self.power_ups = []
        self.has_immunity = False
        self.max_power_ups = 3
        self.moving_down = False
        self.animation_speed = 0.1
        self.current_display_pos = 1
        self.animation_start_pos = 1
        
    def move(self, steps):
        self.animation_start_pos = self.position
        self.target_position = min(self.position + steps, 100)
        self.is_moving = True
        self.move_progress = 0
        self.moving_down = steps < 0
        self.animation_speed = 0.1
        
    def update_animation(self):
        if self.is_moving:
            self.move_progress += self.animation_speed
            self.current_display_pos = self.animation_start_pos + (self.target_position - self.animation_start_pos) * self.move_progress
            
            if self.move_progress >= 1:
                self.position = self.target_position
                self.current_display_pos = self.target_position
                self.is_moving = False
                return True
        return False

    def get_current_display_position(self):
        return self.current_display_pos

    def draw(self, board):
        pos = self.get_current_display_position()
        x, y = board.get_coordinates(pos)
        x += self.offset[0]
        y += self.offset[1]
        
        # Draw player with glow effect if has immunity
        if self.has_immunity:
            glow_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*POWER_UP_COLORS["immunity"], 100),
                             (CELL_SIZE//2, CELL_SIZE//2), CELL_SIZE//2)
            screen.blit(glow_surface, (x - CELL_SIZE//2, y - CELL_SIZE//2))
        
        # Draw player
        pygame.draw.circle(screen, self.color, (x, y), CELL_SIZE // 4)
        pygame.draw.circle(screen, BLACK, (x, y), CELL_SIZE // 4, 2)

    def add_power_up(self, power_up):
        if len(self.power_ups) < self.max_power_ups:
            self.power_ups.append(power_up)
            return True
        return False
        
    def use_power_up(self, index):
        if 0 <= index < len(self.power_ups):
            return self.power_ups.pop(index)
        return None
        
    def draw_power_ups(self):
        """Draw power-up inventory with improved visuals"""
        panel_x = SCREEN_WIDTH - 300  # Adjusted for fullscreen
        panel_y = 50
        panel_width = 280  # Increased for fullscreen
        panel_height = 400  # Increased for fullscreen
        shadow_offset = 5
        
        # Draw panel background with shadow
        shadow_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (*BLACK, 50),
                        (0, 0, panel_width, panel_height),
                        border_radius=10)
        screen.blit(shadow_surface,
                   (panel_x + shadow_offset, panel_y + shadow_offset))
        
        # Draw main panel with forest theme
        pygame.draw.rect(screen, BOARD_BG,
                        (panel_x, panel_y, panel_width, panel_height),
                        border_radius=10)
        pygame.draw.rect(screen, BOARD_BORDER,
                        (panel_x, panel_y, panel_width, panel_height),
                        2, border_radius=10)
        
        # Draw title with forest theme
        title_bg = pygame.Rect(panel_x + 5, panel_y + 5, panel_width - 10, 40)
        pygame.draw.rect(screen, (*SECONDARY, 200), title_bg, border_radius=8)
        pygame.draw.rect(screen, BLACK, title_bg, 2, border_radius=8)
        
        title_text = info_font.render("Power-ups", True, TEXT_LIGHT)
        title_rect = title_text.get_rect(center=title_bg.center)
        screen.blit(title_text, title_rect)
        
        # Draw power-up slots
        slot_y = panel_y + 60
        slot_height = 45  # Reduced slot height
        slot_spacing = 10  # Reduced spacing
        
        for i, power_up in enumerate(self.power_ups):
            # Draw slot background with hover effect
            mouse_pos = pygame.mouse.get_pos()
            slot_rect = pygame.Rect(panel_x + 10, slot_y + i * (slot_height + slot_spacing),
                                  panel_width - 20, slot_height)
            
            is_hovered = slot_rect.collidepoint(mouse_pos)
            slot_color = POWER_UPS[power_up]["color"] if not is_hovered else tuple(min(c + 30, 255) for c in POWER_UPS[power_up]["color"])
            
            # Draw slot with shadow
            pygame.draw.rect(screen, (*BLACK, 50),
                           (slot_rect.x + 2, slot_rect.y + 2, slot_rect.width, slot_rect.height),
                           border_radius=8)
            pygame.draw.rect(screen, slot_color, slot_rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, slot_rect, 2, border_radius=8)
            
            # Draw power-up info
            name_text = info_font.render(POWER_UPS[power_up]["name"], True, TEXT_LIGHT)
            desc_text = cell_font.render(POWER_UPS[power_up]["description"], True, TEXT_LIGHT)
            
            name_rect = name_text.get_rect(topleft=(slot_rect.x + 10, slot_rect.y + 5))
            desc_rect = desc_text.get_rect(topleft=(slot_rect.x + 10, slot_rect.y + 25))
            
            screen.blit(name_text, name_rect)
            screen.blit(desc_text, desc_rect)
            
            # Draw use button
            use_btn = pygame.Rect(slot_rect.right - 50, slot_rect.centery - 15, 40, 30)
            
            # Button hover effect
            btn_color = SUCCESS_COLOR if not is_hovered else tuple(min(c + 30, 255) for c in SUCCESS_COLOR)
            pygame.draw.rect(screen, (*BLACK, 50),
                           (use_btn.x + 2, use_btn.y + 2, use_btn.width, use_btn.height),
                           border_radius=6)
            pygame.draw.rect(screen, btn_color, use_btn, border_radius=6)
            pygame.draw.rect(screen, BLACK, use_btn, 2, border_radius=6)
            
            use_text = cell_font.render("Use", True, TEXT_LIGHT)
            use_rect = use_text.get_rect(center=use_btn.center)
            screen.blit(use_text, use_rect)
            
            yield use_btn, i

class Board:
    def __init__(self):
        # Start with empty snakes and ladders
        self.snakes = {}
        self.ladders = {}
        self.power_ups = {}  # Dictionary mapping positions to power-up types
        self.gift_boxes = set()  # Set of positions with gift boxes
        self.max_power_ups = 5  # Maximum number of power-ups per game
        
        # AI adaptive placement system
        self.roll_history = []  # Store all rolls
        self.current_position = 1
        self.ai_enabled = True
        self.last_placement_position = 1
        self.placement_threshold = 8  # Reduced: Player must advance this far for new placements
        self.max_elements = 20  # Maximum combined snakes and ladders
        self.last_prediction_time = 0
        self.prediction_interval = 2000  # ms between predictions
        self.difficulty = "easy"  # Default difficulty
        
        # Enhanced difficulty settings
        self.difficulty_settings = {
            "easy": {
                "early_snake_ratio": 0.4,    # 40% snakes in early game
                "mid_snake_ratio": 0.6,      # 60% snakes in mid game
                "late_snake_ratio": 0.7,     # 70% snakes in late game
                "snake_length_factor": 1.0,   # Base snake length multiplier
                "ladder_length_factor": 1.0,  # Base ladder length multiplier
                "minimax_depth": 2,          # Shallow search for easy mode
                "monte_carlo_sims": 500,     # Fewer simulations for easy mode
                "placement_threshold": 10,    # More frequent placements
                "snake_aggression": 0.5      # Lower snake aggression
            },
            "medium": {
                "early_snake_ratio": 0.6,    # 60% snakes in early game
                "mid_snake_ratio": 0.7,      # 70% snakes in mid game
                "late_snake_ratio": 0.85,    # 85% snakes in late game
                "snake_length_factor": 1.3,   # 30% longer snakes
                "ladder_length_factor": 0.8,  # 20% shorter ladders
                "minimax_depth": 3,          # Medium search depth
                "monte_carlo_sims": 1000,    # More simulations
                "placement_threshold": 8,     # Balanced placement frequency
                "snake_aggression": 0.7      # Medium snake aggression
            },
            "hard": {
                "early_snake_ratio": 0.7,    # 70% snakes in early game
                "mid_snake_ratio": 0.85,     # 85% snakes in mid game
                "late_snake_ratio": 0.95,    # 95% snakes in late game
                "snake_length_factor": 1.6,   # 60% longer snakes
                "ladder_length_factor": 0.6,  # 40% shorter ladders
                "minimax_depth": 4,          # Deeper search for hard mode
                "monte_carlo_sims": 2000,    # More simulations for better prediction
                "placement_threshold": 6,     # More frequent placements
                "snake_aggression": 0.9      # High snake aggression
            }
        }
        
        # Generate gradient for board cells
        self.cell_colors = []
        for i in range(GRID_SIZE):
            row = []
            for j in range(GRID_SIZE):
                # Alternate cell colors in a pattern
                if (i % 2 == 0 and j % 2 == 0) or (i % 2 == 1 and j % 2 == 1):
                    color = (*CELL_COLOR_1, 100)
                else:
                    color = (*CELL_COLOR_2, 100)
                row.append(color)
            self.cell_colors.append(row)
        
        self.initialize_gift_boxes()
        
        # Minimax parameters
        self.max_depth = 3  # How far ahead to look
        self.evaluation_cache = {}  # Cache for evaluation results
    
    def initialize_gift_boxes(self):
        """Place initial gift boxes in random cells"""
        available_cells = set(range(2, 99)) - set(self.snakes.keys()) - set(self.ladders.keys())
        num_initial_gifts = min(5, len(available_cells))  # Start with 5 gift boxes
        
        # Clear existing power-ups
        self.power_ups.clear()
        self.gift_boxes.clear()
        
        # Place new power-ups
        for cell in random.sample(list(available_cells), num_initial_gifts):
            self.add_power_up(cell)
        # Ladders will be placed dynamically through add_adaptive_placements
    
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
    
    def monte_carlo_simulation(self, current_position, num_simulations=None, num_steps=3):
        """Enhanced Monte Carlo simulation with difficulty-based parameters"""
        if num_simulations is None:
            num_simulations = self.difficulty_settings[self.difficulty]["monte_carlo_sims"]
            
        cell_counts = defaultdict(int)
        settings = self.difficulty_settings[self.difficulty]
        
        for _ in range(num_simulations):
            pos = current_position
            steps_taken = 0
            
            while steps_taken < num_steps and pos < 100:
                # Simulate dice roll with weighted probabilities based on difficulty
                if self.difficulty == "hard":
                    # In hard mode, favor lower numbers
                    dice = random.choices(range(1, 7), weights=[0.3, 0.25, 0.2, 0.15, 0.07, 0.03])[0]
                elif self.difficulty == "medium":
                    # In medium mode, balanced distribution
                    dice = random.randint(1, 6)
                else:
                    # In easy mode, favor higher numbers
                    dice = random.choices(range(1, 7), weights=[0.03, 0.07, 0.15, 0.2, 0.25, 0.3])[0]
                
                pos += dice
                steps_taken += 1
                
                # Apply existing snakes and ladders
                if pos in self.snakes:
                    pos = self.snakes[pos]
                elif pos in self.ladders:
                    pos = self.ladders[pos]
                
                if pos > 100:
                    break
                    
                # Only count final positions for placement decisions
                if steps_taken == num_steps:
                    cell_counts[pos] += 1

        # Convert counts to probabilities with difficulty-based weighting
        total_hits = sum(cell_counts.values())
        if total_hits == 0:
            return {}
            
        # Apply difficulty-based weighting to probabilities
        weighted_probabilities = {}
        for cell, count in cell_counts.items():
            base_prob = count / total_hits
            # Adjust probability based on difficulty and position
            if self.difficulty == "hard":
                # In hard mode, increase probability for positions near snakes
                if any(abs(cell - snake_pos) < 5 for snake_pos in self.snakes.keys()):
                    base_prob *= 1.5
            elif self.difficulty == "easy":
                # In easy mode, increase probability for positions near ladders
                if any(abs(cell - ladder_pos) < 5 for ladder_pos in self.ladders.keys()):
                    base_prob *= 1.5
                    
            weighted_probabilities[cell] = base_prob
            
        return weighted_probabilities
    
    def update_player_position(self, new_position):
        """Update the player's current position for the AI"""
        self.current_position = new_position
        
        # Only allow adaptive placements if player has moved significantly from start
        # and has advanced enough from last placement
        if new_position > 20 and new_position - self.last_placement_position >= self.placement_threshold:
            if random.random() < 0.7:  # 70% chance to add new elements
                self.add_adaptive_placements()
                self.last_placement_position = new_position
    
    def get_potential_snake_positions(self, current_pos):
        """Calculate optimal positions for snake placement using algorithm"""
        positions = []
        progress = current_pos / 100
        
        # Use Monte Carlo simulation to predict likely positions
        predictions = self.monte_carlo_simulation(current_pos)
        if predictions:
            # Sort positions by probability
            sorted_positions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
            
            # Take top positions based on progress
            if progress < 0.3:  # Early game
                positions = [pos for pos, _ in sorted_positions[:5] if pos < 100]
            elif progress < 0.7:  # Mid game
                positions = [pos for pos, _ in sorted_positions[:8] if pos < 100]
            else:  # Late game
                positions = [pos for pos, _ in sorted_positions[:10] if pos < 100]
        
        # Add positions based on game progress
        if current_pos < 90:
            # Add positions that are ahead of the player
            positions.extend(range(current_pos + 1, min(current_pos + 15, 99)))  # Changed 100 to 99
        
        # Remove duplicates and sort
        return sorted(list(set(positions)))

    def calculate_ladder_placement_score(self, start_pos, end_pos):
        """Calculate a score for potential ladder placement"""
        score = 0
        
        # Base score on ladder length
        length = end_pos - start_pos
        score += length * 2  # Longer ladders get higher scores
        
        # Bonus for ladders that help avoid snakes
        for snake_pos in self.snakes.keys():
            if start_pos < snake_pos < end_pos:
                score += 10  # Bonus for ladders that help avoid snakes
        
        # Penalty for ladders too close to each other
        for ladder_start in self.ladders.keys():
            if abs(ladder_start - start_pos) < 5:
                score -= 15  # Penalty for ladders too close
        
        # Bonus for strategic positions
        if start_pos <= 30:  # Early game
            score += 5
        elif start_pos <= 60:  # Mid game
            score += 3
        
        return score

    def find_optimal_ladder_placement(self):
        """Find optimal ladder placement using Monte Carlo simulation"""
        best_score = float('-inf')
        best_placement = None
        
        # Get current player position
        current_pos = self.current_position
        
        # Use Monte Carlo simulation to predict likely positions
        predictions = self.monte_carlo_simulation(current_pos)
        
        # Consider positions based on game progress
        if current_pos < 30:  # Early game
            potential_starts = range(2, 31)
        elif current_pos < 60:  # Mid game
            potential_starts = range(31, 61)
        else:  # Late game
            potential_starts = range(61, 90)
        
        # Try multiple placements
        for start_pos in potential_starts:
            if start_pos in self.snakes or start_pos in self.ladders:
                continue
                
            # Try different ladder lengths based on difficulty
            min_length = 5
            max_length = {
                "easy": 20,
                "medium": 15,
                "hard": 10
            }[self.difficulty]
            
            for length in range(min_length, max_length):
                end_pos = start_pos + length
                if end_pos >= 100 or end_pos in self.snakes or end_pos in self.ladders.values():
                    continue
                
                # Calculate score for this placement
                score = self.calculate_ladder_placement_score(start_pos, end_pos)
                
                # Add bonus based on Monte Carlo predictions
                if predictions and end_pos in predictions:
                    score += predictions[end_pos] * 20
                
                # Bonus for strategic positions
                if start_pos <= 30:  # Early game
                    score += 5
                elif start_pos <= 60:  # Mid game
                    score += 3
                
                # Penalty for ladders too close to each other
                for ladder_start in self.ladders.keys():
                    if abs(ladder_start - start_pos) < 5:
                        score -= 15
                
                if score > best_score:
                    best_score = score
                    best_placement = (start_pos, end_pos)
        
        return best_placement

    def _add_balancing_ladder(self):
        """Add a ladder to balance the difficulty using the optimal placement algorithm"""
        # Find optimal ladder placement
        placement = self.find_optimal_ladder_placement()
        
        if placement:
            start_pos, end_pos = placement
            
            # Verify the placement is valid
            if (start_pos not in self.snakes and 
                start_pos not in self.ladders and 
                end_pos not in self.snakes and 
                end_pos not in self.ladders.values() and
                not any(abs(pos - start_pos) < 5 for pos in self.ladders.keys())):
                
                # Calculate base length
                base_length = end_pos - start_pos
                
                # Get player progress (0 to 1)
                progress = self.current_position / 100
                
                # Adjust length based on difficulty and progress
                if self.difficulty == "easy":
                    # In easy mode, longer ladders that get shorter as player progresses
                    length_multiplier = 1.5 - (progress * 0.5)  # 1.5 to 1.0
                    max_length = 25 - int(progress * 10)  # 25 to 15 cells
                elif self.difficulty == "medium":
                    # In medium mode, balanced ladders that maintain consistent length
                    length_multiplier = 1.0
                    max_length = 15
                else:  # hard mode
                    # In hard mode, shorter ladders that get even shorter as player progresses
                    length_multiplier = 0.7 - (progress * 0.2)  # 0.7 to 0.5
                    max_length = 10 - int(progress * 5)  # 10 to 5 cells
                
                # Calculate final length
                new_length = min(int(base_length * length_multiplier), max_length)
                final_end_pos = start_pos + new_length
                
                # Ensure the ladder is at least 3 cells long and not too steep
                if final_end_pos - start_pos >= 3:
                    # Calculate the vertical distance between start and end
                    start_x, start_y = self.get_coordinates(start_pos)
                    end_x, end_y = self.get_coordinates(final_end_pos)
                    vertical_distance = abs(end_y - start_y)
                    
                    # Only place the ladder if it's not too steep
                    if vertical_distance >= CELL_SIZE:
                        # Place the ladder
                        self.ladders[start_pos] = final_end_pos
                        print(f"Added ladder from {start_pos} to {final_end_pos}")
                        return True
        
        return False

    def add_adaptive_placements(self):
        """Add new snakes and ladders using minimax algorithm"""
        # Clear evaluation cache for new calculations
        self.evaluation_cache.clear()
        
        # Get current player position
        current_pos = self.current_position
        
        # Calculate how close we are to the goal
        progress = current_pos / 100
        
        # Adjust number of snakes based on progress
        num_snakes_to_place = 1
        if progress > 0.7:  # After 70% progress
            num_snakes_to_place = 2
        if progress > 0.9:  # After 90% progress
            num_snakes_to_place = 3
            
        # Get potential positions from algorithm
        potential_positions = self.get_potential_snake_positions(current_pos)
        
        # Place multiple snakes
        for _ in range(num_snakes_to_place):
            best_score = float('-inf')
            best_snake_pos = None
            
            # Consider positions from algorithm
            for potential_pos in potential_positions:
                if potential_pos not in self.snakes and potential_pos not in self.ladders and potential_pos < 100:
                    # Simulate snake placement
                    original_snakes = self.snakes.copy()
                    snake_length = self.get_snake_length(potential_pos)
                    self.snakes[potential_pos] = max(1, potential_pos - snake_length)
                    
                    # Evaluate this placement
                    score = self.minimax(current_pos, self.max_depth, float('-inf'), float('inf'), True)
                    
                    # Restore original state
                    self.snakes = original_snakes
                    
                    # Update best placement
                    if score > best_score:
                        best_score = score
                        best_snake_pos = potential_pos
            
            # Place the optimal snake if found
            if best_snake_pos is not None:
                snake_length = self.get_snake_length(best_snake_pos)
                self.snakes[best_snake_pos] = max(1, best_snake_pos - snake_length)
                
                # Add a balancing ladder if needed (reduced chance in hard mode)
                ladder_chance = {
                    "easy": 0.7,    # 70% chance in easy mode
                    "medium": 0.5,  # 50% chance in medium mode
                    "hard": 0.3     # 30% chance in hard mode
                }[self.difficulty]
                
                if random.random() < ladder_chance:
                    self._add_balancing_ladder()

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
        
    def draw_cell(self, x, y, cell_num, i, j):
        """Draw a single cell with improved visuals"""
        # Alternating cell colors
        color = self.cell_colors[i][j]
        
        # Draw cell background with gradient effect
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect)
        
        # Draw subtle grid pattern
        pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)
        
        # Draw cell number with shadow
        text_color = (50, 50, 50)  # Dark gray for better readability
        shadow_offset = 1
        
        num_text = cell_font.render(str(cell_num), True, text_color)
        num_rect = num_text.get_rect(bottomright=(x + CELL_SIZE - 5, y + CELL_SIZE - 5))
        
        # Draw number shadow
        shadow_text = cell_font.render(str(cell_num), True, (0, 0, 0, 100))
        shadow_rect = shadow_text.get_rect(bottomright=(num_rect.right + shadow_offset, num_rect.bottom + shadow_offset))
        screen.blit(shadow_text, shadow_rect)
        screen.blit(num_text, num_rect)
    
    def draw_gift_box(self, x, y):
        """Draw an improved gift box with animation"""
        current_time = pygame.time.get_ticks()
        bounce_offset = math.sin(current_time / 500) * 3  # Gentle bouncing animation
        
        size = CELL_SIZE // 2.5
        y = y + bounce_offset  # Apply bounce effect
        
        # Draw gift box shadow
        shadow_size = size * 1.1
        shadow_surface = pygame.Surface((int(shadow_size), int(shadow_size)), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 50), 
                        (0, 0, shadow_size, shadow_size), border_radius=5)
        screen.blit(shadow_surface, 
                   (x - shadow_size//2, y - shadow_size//2 + 5))
        
        # Draw main box with gradient effect
        box_surface = pygame.Surface((int(size), int(size)), pygame.SRCALPHA)
        for i in range(int(size)):
            progress = i / size
            color = (
                int(255 - progress * 30),
                int(182 - progress * 30),
                int(193 - progress * 30),
                255
            )
            pygame.draw.line(box_surface, color, (0, i), (size, i))
        
        # Apply box surface
        box_rect = box_surface.get_rect(center=(x, y))
        screen.blit(box_surface, box_rect)
        
        # Draw ribbon
        ribbon_width = size // 4
        ribbon_color = (220, 20, 60)  # Bright red
        
        # Vertical ribbon
        pygame.draw.rect(screen, ribbon_color,
                        (x - ribbon_width//2, y - size//2, ribbon_width, size),
                        border_radius=2)
        
        # Horizontal ribbon
        pygame.draw.rect(screen, ribbon_color,
                        (x - size//2, y - ribbon_width//2, size, ribbon_width),
                        border_radius=2)
        
        # Draw bow
        bow_size = size // 3
        bow_color = (200, 0, 40)  # Darker red for bow
        
        # Draw bow loops
        angle = math.sin(current_time / 1000) * 0.1  # Subtle bow animation
        for direction in [-1, 1]:
            bow_surface = pygame.Surface((bow_size, bow_size), pygame.SRCALPHA)
            pygame.draw.ellipse(bow_surface, bow_color,
                              (0, 0, bow_size, bow_size))
            rotated = pygame.transform.rotate(bow_surface, 45 * direction + math.degrees(angle))
            screen.blit(rotated,
                       (x - rotated.get_width()//2 + direction * bow_size//2,
                        y - rotated.get_height()//2))
        
        # Add sparkle effect
        sparkle_points = [(size//2, -size//2), (-size//2, size//2),
                         (size//2, size//2), (-size//2, -size//2)]
        sparkle_size = size // 8
        sparkle_alpha = int(abs(math.sin(current_time / 200)) * 255)  # Twinkling effect
        sparkle_color = (255, 255, 200, sparkle_alpha)
        
        for px, py in sparkle_points:
            pygame.draw.circle(screen, sparkle_color,
                             (int(x + px), int(y + py)), sparkle_size)
    
    def draw(self):
        # Calculate board position for centering
        board_x = (SCREEN_WIDTH - BOARD_SIZE) // 2
        board_y = (SCREEN_HEIGHT - BOARD_SIZE) // 2
        
        # Draw board background with shadow
        shadow_offset = 15
        shadow_surface = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 50),
                        (0, 0, BOARD_SIZE, BOARD_SIZE),
                        border_radius=15)
        screen.blit(shadow_surface,
                   (board_x + shadow_offset, board_y + shadow_offset))
        
        # Draw main board background
        pygame.draw.rect(screen, BOARD_BG,
                        (board_x, board_y, BOARD_SIZE, BOARD_SIZE),
                        border_radius=10)
        
        # Draw cells
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                cell_x = board_x + j * CELL_SIZE
                cell_y = board_y + i * CELL_SIZE
                
                # Determine cell number
                row = GRID_SIZE - 1 - i
                col = j if row % 2 == 0 else GRID_SIZE - 1 - j
                cell_num = row * GRID_SIZE + col + 1
                
                self.draw_cell(cell_x, cell_y, cell_num, i, j)
        
        # Draw board border
        pygame.draw.rect(screen, BOARD_BORDER,
                        (board_x, board_y, BOARD_SIZE, BOARD_SIZE),
                        5, border_radius=10)
        
        # Draw gift boxes
        for position in self.gift_boxes:
            x, y = self.get_coordinates(position)
            self.draw_gift_box(x, y)
        
        # Draw snakes and ladders
        for start, end in self.snakes.items():
            start_x, start_y = self.get_coordinates(start)
            end_x, end_y = self.get_coordinates(end)
            self.draw_snake(start_x, start_y, end_x, end_y)
        
        for start, end in self.ladders.items():
            start_x, start_y = self.get_coordinates(start)
            end_x, end_y = self.get_coordinates(end)
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
        steps = max(steps, 20)
        
        for i in range(steps + 1):
            t = i / steps
            x = (1-t)**2 * x1 + 2 * (1-t) * t * ctrl_x + t**2 * x2
            y = (1-t)**2 * y1 + 2 * (1-t) * t * ctrl_y + t**2 * y2
            
            wave = math.sin(i / 2) * 10
            perp_x = -dy / distance
            perp_y = dx / distance
            x += perp_x * wave
            y += perp_y * wave
            
            points.append((x, y))
        
        # Draw the snake body with gradient
        for i in range(len(points) - 1):
            progress = i / (len(points) - 1)
            thickness = 6 - progress * 2
            color = (
                int(SNAKE_COLOR[0] * (1 - progress) + WARNING_COLOR[0] * progress),
                int(SNAKE_COLOR[1] * (1 - progress) + WARNING_COLOR[1] * progress),
                int(SNAKE_COLOR[2] * (1 - progress) + WARNING_COLOR[2] * progress)
            )
            pygame.draw.line(screen, color, points[i], points[i+1], int(thickness))
        
        # Draw snake head
        pygame.draw.circle(screen, SNAKE_COLOR, points[0], 8)
        pygame.draw.circle(screen, BLACK, points[0], 8, 1)
        
        # Draw eyes
        pygame.draw.circle(screen, WHITE, (points[0][0] - 3, points[0][1] - 3), 3)
        pygame.draw.circle(screen, WHITE, (points[0][0] + 3, points[0][1] - 3), 3)
        pygame.draw.circle(screen, BLACK, (points[0][0] - 3, points[0][1] - 3), 1)
        pygame.draw.circle(screen, BLACK, (points[0][0] + 3, points[0][1] - 3), 1)

    def draw_ladder(self, x1, y1, x2, y2):
        """Draw a simple diagonal ladder"""
        # Calculate direction and length
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        # Calculate angle for rotation (in radians)
        angle = math.atan2(dy, dx)
        
        # Create a surface for the ladder
        width = CELL_SIZE // 3  # Ladder width
        ladder_surface = pygame.Surface((int(length), width), pygame.SRCALPHA)
        
        # Draw the two sides of the ladder
        pygame.draw.line(ladder_surface, LADDER_COLOR, (0, 0), (length, 0), 3)
        pygame.draw.line(ladder_surface, LADDER_COLOR, (0, width), (length, width), 3)
        
        # Draw the rungs
        num_rungs = 8
        for i in range(num_rungs):
            t = i / (num_rungs - 1)
            rung_x = t * length
            pygame.draw.line(ladder_surface, LADDER_COLOR, 
                           (rung_x, 0), (rung_x, width), 2)
        
        # Rotate the ladder surface to match the diagonal direction
        rotated_ladder = pygame.transform.rotate(ladder_surface, -math.degrees(angle))
        
        # Calculate the center point between start and end
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        # Calculate the offset to center the rotated ladder
        offset_x = rotated_ladder.get_width() // 2
        offset_y = rotated_ladder.get_height() // 2
        
        # Position the ladder
        pos_x = center_x - offset_x
        pos_y = center_y - offset_y
        
        # Ensure ladder stays within board boundaries
        board_x = (SCREEN_WIDTH - BOARD_SIZE) // 2
        board_y = (SCREEN_HEIGHT - BOARD_SIZE) // 2
        pos_x = max(board_x, min(pos_x, board_x + BOARD_SIZE - rotated_ladder.get_width()))
        pos_y = max(board_y, min(pos_y, board_y + BOARD_SIZE - rotated_ladder.get_height()))
        
        # Draw the ladder
        screen.blit(rotated_ladder, (pos_x, pos_y))

    def remove_random_snake(self):
        """Remove a random snake from the board"""
        if self.snakes:
            snake_head = random.choice(list(self.snakes.keys()))
            del self.snakes[snake_head]
            return True
        return False
    
    def add_power_up(self, position):
        """Add a random power-up at the given position"""
        if len(self.power_ups) >= self.max_power_ups:
            return False
            
        if position not in self.snakes and position not in self.ladders:
            power_up = random.choice(list(POWER_UPS.keys()))
            self.power_ups[position] = power_up
            self.gift_boxes.add(position)
            return True
        return False

    def get_snake_length(self, position):
        """Calculate optimal snake length based on position and difficulty"""
        # Base length starts smaller and increases with position
        base_length = 5  # Reduced from 10 to start with smaller snakes
        
        # Calculate progress (0 to 1)
        progress = position / 100
        
        # Snake length increases with:
        # 1. Higher difficulty
        # 2. Closer to goal
        # 3. Current progress
        difficulty_multiplier = {
            "easy": 0.8,
            "medium": 1.2,
            "hard": 1.6
        }[self.difficulty]
        
        # Exponential increase in snake length near goal
        position_multiplier = 1 + (position / 100) ** 2  # Quadratic increase
        progress_multiplier = 1 + progress * 2  # Doubled progress impact
        
        # Calculate final length
        length = int(base_length * difficulty_multiplier * position_multiplier * progress_multiplier)
        
        # Ensure minimum length of 3 and maximum of 30
        return max(3, min(30, length))

    def evaluate_position(self, position):
        """Enhanced evaluation function with difficulty-based scoring"""
        settings = self.difficulty_settings[self.difficulty]
        
        # Base evaluation based on position
        evaluation = (100 - position) * 10
        
        # Consider difficulty level
        difficulty_factor = {
            "easy": 0.5,
            "medium": 1.0,
            "hard": 1.5
        }[self.difficulty]
        
        # Enhanced snake evaluation
        snake_score = 0
        for snake_start, snake_end in self.snakes.items():
            snake_length = snake_start - snake_end
            
            # Strategic positioning factors
            position_factor = 1.0
            
            # Snakes near goal are more dangerous
            if snake_start >= 90:
                position_factor *= 2.0
            elif snake_start >= 70:
                position_factor *= 1.5
                
            # Snakes that create "traps" are more effective
            if snake_start - snake_end > 10:
                position_factor *= 1.3
                
            # Snakes that block common paths are more effective
            if snake_start % 10 in [5, 6, 7, 8, 9]:
                position_factor *= 1.2
                
            # Add difficulty-based aggression
            position_factor *= settings["snake_aggression"]
                
            snake_score += snake_length * position_factor * difficulty_factor
            
        # Enhanced ladder evaluation
        ladder_score = 0
        for ladder_start, ladder_end in self.ladders.items():
            ladder_length = ladder_end - ladder_start
            
            # Strategic positioning factors
            position_factor = 1.0
            
            # Ladders near start are more helpful
            if ladder_start <= 30:
                position_factor *= 1.5
            elif ladder_start <= 50:
                position_factor *= 1.2
                
            # Ladders that bypass snakes are more effective
            if any(snake_start > ladder_start and snake_start < ladder_end 
                  for snake_start in self.snakes.keys()):
                position_factor *= 0.7
                
            # Add difficulty-based adjustment
            position_factor *= (2 - settings["snake_aggression"])  # Inverse of snake aggression
                
            ladder_score += ladder_length * position_factor * difficulty_factor
            
        # Combine scores with difficulty-based weighting
        final_score = evaluation - snake_score + ladder_score
        return final_score

    def minimax(self, position, depth=None, alpha=float('-inf'), beta=float('inf'), is_maximizing=True):
        """Enhanced minimax algorithm with difficulty-based depth"""
        if depth is None:
            depth = self.difficulty_settings[self.difficulty]["minimax_depth"]
            
        # Cache key for current state
        cache_key = (position, depth, is_maximizing)
        if cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]
            
        # Base cases
        if depth == 0 or position >= 100:
            return self.evaluate_position(position)
            
        if is_maximizing:
            # AI's turn - trying to maximize difficulty
            max_eval = float('-inf')
            
            # Calculate potential snake positions based on player's position
            potential_positions = self.get_potential_snake_positions(position)
            
            for potential_pos in potential_positions:
                if potential_pos not in self.snakes and potential_pos not in self.ladders and potential_pos < 100:
                    # Simulate snake placement
                    original_snakes = self.snakes.copy()
                    snake_length = self.get_snake_length(potential_pos)
                    self.snakes[potential_pos] = max(1, potential_pos - snake_length)
                    
                    # Recursive call with difficulty-based depth
                    eval = self.minimax(position, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    
                    # Restore original state
                    self.snakes = original_snakes
                    
                    # Alpha-beta pruning
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
                        
            self.evaluation_cache[cache_key] = max_eval
            return max_eval
        else:
            # Player's turn - trying to minimize difficulty
            min_eval = float('inf')
            
            # Consider different dice rolls with difficulty-based weights
            dice_weights = {
                "easy": [0.03, 0.07, 0.15, 0.2, 0.25, 0.3],    # Favor higher numbers
                "medium": [1/6] * 6,                           # Equal probability
                "hard": [0.3, 0.25, 0.2, 0.15, 0.07, 0.03]     # Favor lower numbers
            }[self.difficulty]
            
            for dice in range(1, 7):
                # Apply dice weights
                weight = dice_weights[dice-1]
                new_pos = min(position + dice, 100)
                
                if new_pos in self.snakes:
                    new_pos = self.snakes[new_pos]
                elif new_pos in self.ladders:
                    new_pos = self.ladders[new_pos]
                    
                eval = self.minimax(new_pos, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval * weight)  # Weight the evaluation
                
                # Alpha-beta pruning
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                    
            self.evaluation_cache[cache_key] = min_eval
            return min_eval

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
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.pressed = False
        
    def is_clicked(self, pos):
        """Check if button is clicked and update pressed state"""
        was_pressed = self.rect.collidepoint(pos)
        if was_pressed:
            self.pressed = True
        return was_pressed
        
    def draw(self):
        """Draw button with improved visuals"""
        # Determine button color based on state
        color = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        
        # Draw button shadow
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (*BLACK, 100), shadow_rect, border_radius=10)
        
        # Draw main button
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        # Draw text with shadow
        text_surface = button_font.render(self.text, True, TEXT_LIGHT)
        text_shadow = button_font.render(self.text, True, BLACK)
        
        # Center text
        text_rect = text_surface.get_rect(center=self.rect.center)
        shadow_rect = text_shadow.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        
        # Draw text shadow and main text
        screen.blit(text_shadow, shadow_rect)
        screen.blit(text_surface, text_rect)
        
    def reset(self):
        """Reset button state"""
        self.pressed = False

class Game:
    def __init__(self):
        self.board = Board()
        self.player = Player(PLAYER_COLOR, "Player", (0, 0))
        self.dice = Dice()
        self.state = "difficulty"  # difficulty, playing, end
        self.difficulty = None
        self.time_left = 0
        self.start_time = 0
        self.message = ""
        self.message_time = 0
        self.last_dice_value = 0
        self.previous_position = 1
        self.power_up_cooldown = 0  # Cooldown for power-up usage
        self.power_up_cooldown_time = 1000  # 1 second cooldown in milliseconds
        self.last_time_update = 0  # Track last time update for smooth display
        self.time_boost = 0  # Track additional time from boosts
        self.snake_bite = False  # Add flag for snake bite state
        self.snake_bite_position = None  # Store snake bite position
        self.snake_bite_target = None  # Store snake bite target position
        
        # Buttons with new colors and positions adjusted for fullscreen
        btn_width, btn_height = 200, 60
        self.easy_button = Button(
            SCREEN_WIDTH // 2 - btn_width // 2, SCREEN_HEIGHT // 2 - 150,
            btn_width, btn_height, "Easy", SUCCESS_COLOR
        )
        self.medium_button = Button(
            SCREEN_WIDTH // 2 - btn_width // 2, SCREEN_HEIGHT // 2,
            btn_width, btn_height, "Medium", WARNING_COLOR
        )
        self.hard_button = Button(
            SCREEN_WIDTH // 2 - btn_width // 2, SCREEN_HEIGHT // 2 + 150,
            btn_width, btn_height, "Hard", ERROR_COLOR
        )
        self.roll_button = Button(
            SCREEN_WIDTH - 250, SCREEN_HEIGHT - 150, 
            btn_width, btn_height, "Roll Dice", BUTTON_COLOR
        )
        self.restart_button = Button(
            SCREEN_WIDTH // 2 - btn_width // 2, SCREEN_HEIGHT // 2 + 150,
            btn_width, btn_height, "Play Again", BUTTON_COLOR
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and self.state == "playing":
                    self.restart_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "difficulty":
                    if self.easy_button.is_clicked(event.pos):
                        self.start_game("easy")
                    elif self.medium_button.is_clicked(event.pos):
                        self.start_game("medium")
                    elif self.hard_button.is_clicked(event.pos):
                        self.start_game("hard")
                elif self.state == "playing":
                    if self.roll_button.is_clicked(event.pos) and not self.animating:
                        self.roll_dice()
                    else:
                        # Check power-up usage
                        current_time = pygame.time.get_ticks()
                        if current_time - self.power_up_cooldown >= self.power_up_cooldown_time:
                            for use_btn, index in self.player.draw_power_ups():
                                if use_btn.collidepoint(event.pos):
                                    power_up = self.player.use_power_up(index)
                                    if power_up:
                                        self.power_up_cooldown = current_time
                                        POWER_UPS[power_up]["effect"](self)
                                        self.set_message(f"Used {POWER_UPS[power_up]['name']}!")
                                        self.animating = False
                                        self.animation_done = False
                                        break
                elif self.state == "end":
                    if self.restart_button.is_clicked(event.pos):
                        self.restart_game()
                    elif self.show_win_popup:
                        # Check close button
                        close_btn_rect = pygame.Rect(
                            SCREEN_WIDTH // 2 + 230,  # Adjusted for new popup size
                            SCREEN_HEIGHT // 2 - 135,  # Adjusted for new popup size
                            30, 30
                        )
                        if close_btn_rect.collidepoint(event.pos):
                            self.show_win_popup = False
                            self.state = "end"

    def add_time(self, seconds):
        """Add time to the timer and update display"""
        self.time_boost += seconds
        self.time_left += seconds
        self.set_message(f"Added {seconds} seconds!")

    def start_game(self, difficulty):
        self.state = "playing"
        self.difficulty = difficulty
        self.time_left = DIFFICULTY_TIMES[difficulty]
        self.start_time = time.time()
        self.time_boost = 0  # Reset time boost counter
        
        # Configure board based on difficulty
        self.board.configure_difficulty(difficulty)
        self.board.initialize_gift_boxes()
        
        # Reset player position
        self.player.position = 1
        self.player.target_position = 1
        self.player.is_moving = False
        self.player.move_progress = 0
        
        # Reset animation flags
        self.animating = False
        self.animation_done = False
        
        # Clear any existing messages
        self.message = ""
        self.message_time = 0

    def update(self):
        if self.state == "playing":
            current_time = time.time()
            if current_time - self.last_time_update >= 0.1:
                base_time = DIFFICULTY_TIMES[self.difficulty] - (current_time - self.start_time)
                self.time_left = max(0, base_time + self.time_boost)
                self.last_time_update = current_time
            
            if self.time_left <= 0:
                self.state = "end"
                self.set_message("Time's up! Game Over!")
                return
                
            if self.animating:
                # Dice rolling animation
                if self.dice.update() and not self.animation_done:
                    self.last_dice_value = self.dice.value
                    self.previous_position = self.player.position
                    self.player.move(self.dice.value)
                    self.animation_done = True
                    self.set_message(f"You rolled a {self.dice.value}")
                
                # Player movement animation
                if self.animation_done:
                    if self.player.update_animation():
                        position = self.player.position
                        
                        # Check for power-up collection
                        if position in self.board.power_ups:
                            power_up = self.board.power_ups[position]
                            if len(self.player.power_ups) < 3:
                                self.player.add_power_up(power_up)
                                del self.board.power_ups[position]
                                self.board.gift_boxes.remove(position)
                                self.set_message(f"Collected {POWER_UPS[power_up]['name']}!")
                            else:
                                self.set_message("Power-up inventory full!")
                        
                        # Update AI with new player position
                        if position > self.previous_position:
                            self.board.update_player_position(position)
                        
                        # Check for snakes
                        if position in self.board.snakes and not self.snake_bite:
                            if self.player.has_immunity:
                                self.player.has_immunity = False
                                self.set_message("Immunity protected you from the snake!")
                                self.animating = False
                                self.animation_done = False
                            else:
                                self.snake_bite = True
                                self.snake_bite_position = position
                                self.snake_bite_target = self.board.snakes[position]
                                # Directly place player at snake end position
                                self.player.position = self.snake_bite_target
                                self.player.current_display_pos = self.snake_bite_target
                                self.set_message("Oh no! You hit a snake!")
                                self.snake_bite = False
                                self.snake_bite_position = None
                                self.snake_bite_target = None
                                self.animating = False
                                self.animation_done = False
                            return
                            
                        # Check for ladders
                        if position in self.board.ladders:
                            new_pos = self.board.ladders[position]
                            self.player.position = new_pos
                            self.player.current_display_pos = new_pos
                            self.set_message("Yay! You climbed a ladder!")
                            self.animating = False
                            self.animation_done = False
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
        # Create colorful confetti particles using forest theme colors
        self.confetti_particles = []
        colors = [
            PRIMARY,      # Forest Green
            SECONDARY,    # Dark Olive Green
            ACCENT,       # Golden Rod
            SUCCESS_COLOR,# Lime Green
            WARNING_COLOR,# Peru
            GIFT_BOX,    # Medium Orchid
            LADDER_COLOR  # Wood color
        ]
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
        shadow_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (*BLACK, 100),
                        (0, 0, popup_width, popup_height),
                        border_radius=15)
        screen.blit(shadow_surface,
                    (popup_x + 10, popup_y + 10))
        
        # Draw popup
        pygame.draw.rect(screen, BOARD_BG,
                        (popup_x, popup_y, popup_width, popup_height),
                        border_radius=15)
        pygame.draw.rect(screen, PRIMARY,
                        (popup_x, popup_y, popup_width, popup_height),
                        5, border_radius=15)
        
        # Draw congratulations text with shadow
        text = "CONGRATULATIONS!"
        shadow_text = title_font.render(text, True, TEXT_PRIMARY)
        main_text = title_font.render(text, True, PRIMARY)
        
        text_rect = main_text.get_rect(center=(SCREEN_WIDTH // 2, popup_y + 80))
        shadow_rect = shadow_text.get_rect(center=(text_rect.centerx + 3, text_rect.centery + 3))
        
        screen.blit(shadow_text, shadow_rect)
        screen.blit(main_text, text_rect)
        
        # Draw win message
        minutes_taken = int(DIFFICULTY_TIMES[self.difficulty] - self.time_left) // 60
        seconds_taken = int(DIFFICULTY_TIMES[self.difficulty] - self.time_left) % 60
        
        win_message = [
            f"You've completed the game in",
            f"{minutes_taken:02d}:{seconds_taken:02d}",
            f"on {self.difficulty.capitalize()} difficulty!"
        ]
        
        for i, line in enumerate(win_message):
            text = info_font.render(line, True, TEXT_PRIMARY)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, popup_y + 140 + i * 30))
            screen.blit(text, rect)
        
        # Draw close button with hover effect
        close_btn_rect = pygame.Rect(popup_x + popup_width - 40, popup_y + 15, 30, 30)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = close_btn_rect.collidepoint(mouse_pos)
        
        # Button shadow
        pygame.draw.rect(screen, (*ERROR_COLOR, 200) if is_hovered else (*ERROR_COLOR, 150),
                        (close_btn_rect.x + 2, close_btn_rect.y + 2,
                         close_btn_rect.width, close_btn_rect.height),
                        border_radius=15)
        
        # Main button
        pygame.draw.rect(screen, ERROR_COLOR if is_hovered else (*ERROR_COLOR, 200),
                        close_btn_rect, border_radius=15)
        pygame.draw.rect(screen, BLACK,
                        close_btn_rect, 2, border_radius=15)
        
        close_text = info_font.render("×", True, WHITE)
        close_rect = close_text.get_rect(center=close_btn_rect.center)
        screen.blit(close_text, close_rect)
        
        # Check if close button is clicked
        if pygame.mouse.get_pressed()[0] and is_hovered:
            self.show_win_popup = False
    
    def draw_start_screen(self):
        """Draw the start screen with forest theme"""
        # Fill background with forest gradient
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            r = int(CELL_COLOR_1[0] + (CELL_COLOR_2[0] - CELL_COLOR_1[0]) * progress)
            g = int(CELL_COLOR_1[1] + (CELL_COLOR_2[1] - CELL_COLOR_1[1]) * progress)
            b = int(CELL_COLOR_1[2] + (CELL_COLOR_2[2] - CELL_COLOR_1[2]) * progress)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Draw forest elements (trees at corners)
        tree_positions = [
            (100, SCREEN_HEIGHT - 100),
            (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100),
            (100, 100),
            (SCREEN_WIDTH - 100, 100)
        ]
        
        for x, y in tree_positions:
            # Draw simple tree
            trunk_width = 40
            trunk_height = 120
            pygame.draw.rect(screen, TREE_COLORS[0],
                           (x - trunk_width//2, y - trunk_height, trunk_width, trunk_height))
            
            # Draw tree crown
            crown_radius = 60
            pygame.draw.circle(screen, LEAF_COLORS[0],
                             (x, y - trunk_height), crown_radius)
        
        # Draw title
        title_shadow = title_font.render("Snakes and Ladders", True, TEXT_PRIMARY)
        title_text = title_font.render("Snakes and Ladders", True, PRIMARY)
        
        title_y = SCREEN_HEIGHT // 6
        screen.blit(title_shadow, title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, title_y + 3)))
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, title_y)))
        
        # Draw game description panel
        desc_panel = pygame.Surface((600, 200), pygame.SRCALPHA)  # Reduced height
        pygame.draw.rect(desc_panel, (*BOARD_BG, 230), desc_panel.get_rect(), border_radius=15)
        pygame.draw.rect(desc_panel, BOARD_BORDER, desc_panel.get_rect(), 2, border_radius=15)
        
        description = [
            "Welcome to Snakes and Ladders!",
            "",
            "Watch Your Steps --- The Snakes Are Smarter Now!",
            "",
            "🎁 Collect power-ups:",
            "   Time+5s | Snake Killer | Immunity"  # Updated time boost description
        ]
        
        desc_y = 30
        for line in description:
            color = PRIMARY if line.startswith("Welcome") else TEXT_PRIMARY
            font = button_font if line.startswith("Welcome") else info_font
            text = font.render(line, True, color)
            desc_panel.blit(text, (30, desc_y))
            desc_y += 35
        
        screen.blit(desc_panel, ((SCREEN_WIDTH - 600) // 2, title_y + 100))
        
        # Draw difficulty buttons with proper spacing
        btn_y_start = SCREEN_HEIGHT // 2 + 50
        btn_spacing = 100
        
        # Easy button
        self.easy_button.rect.centerx = SCREEN_WIDTH // 2
        self.easy_button.rect.y = btn_y_start
        self.easy_button.draw()
        
        # Medium button
        self.medium_button.rect.centerx = SCREEN_WIDTH // 2
        self.medium_button.rect.y = btn_y_start + btn_spacing
        self.medium_button.draw()
        
        # Hard button
        self.hard_button.rect.centerx = SCREEN_WIDTH // 2
        self.hard_button.rect.y = btn_y_start + btn_spacing * 2
        self.hard_button.draw()
        
        # Draw time info below each button
        for i, (btn, diff) in enumerate([(self.easy_button, "easy"), 
                                       (self.medium_button, "medium"),
                                       (self.hard_button, "hard")]):
            minutes = DIFFICULTY_TIMES[diff] // 60
            time_text = info_font.render(f"{minutes} min", True, TEXT_PRIMARY)
            time_rect = time_text.get_rect(center=(btn.rect.centerx, btn.rect.bottom + 20))
            screen.blit(time_text, time_rect)

    def draw_decorative_elements(self):
        """Simplified forest theme decorations"""
        # Draw grass at bottom
        grass_height = 50
        pygame.draw.rect(screen, LEAF_COLORS[0],
                        (0, SCREEN_HEIGHT - grass_height, SCREEN_WIDTH, grass_height))
        
        # Add some variation to grass
        for x in range(0, SCREEN_WIDTH, 30):
            height = random.randint(30, 50)
            pygame.draw.rect(screen, LEAF_COLORS[1],
                           (x, SCREEN_HEIGHT - height, 20, height))

    def draw_end_screen(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*BLACK, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw end message
        if self.time_left <= 0:
            message = "Time's Up!"
        else:
            message = "Game Over!"
            
        text = title_font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        screen.blit(text, text_rect)
        
        # Draw final score
        minutes = int(DIFFICULTY_TIMES[self.difficulty] - self.time_left) // 60
        seconds = int(DIFFICULTY_TIMES[self.difficulty] - self.time_left) % 60
        score_text = info_font.render(f"Time taken: {minutes:02d}:{seconds:02d}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_text, score_rect)
        
        # Draw restart button
        self.restart_button.draw()

    def draw(self):
        # Fill background with a gradient
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            r = int(BOARD_BG[0] + (SECONDARY[0] - BOARD_BG[0]) * progress)
            g = int(BOARD_BG[1] + (SECONDARY[1] - BOARD_BG[1]) * progress)
            b = int(BOARD_BG[2] + (SECONDARY[2] - BOARD_BG[2]) * progress)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
        if self.state == "difficulty":
            # Draw start screen
            self.draw_start_screen()
        elif self.state == "playing":
            # Draw game board
            self.board.draw()
            
            # Draw player
            self.player.draw(self.board)
            
            # Draw dice
            self.dice.draw()
            
            # Draw roll button
            self.roll_button.draw()
            
            # Draw power-ups panel
            for _ in self.player.draw_power_ups():
                pass  # Just draw the power-ups panel
            
            # Draw timer with improved visibility
            minutes = int(self.time_left) // 60
            seconds = int(self.time_left) % 60
            
            # Draw timer background
            timer_bg = pygame.Surface((200, 50), pygame.SRCALPHA)  # Increased size for fullscreen
            pygame.draw.rect(timer_bg, (*BLACK, 100), timer_bg.get_rect(), border_radius=8)
            screen.blit(timer_bg, (20, 20))
            
            # Draw timer text with shadow
            timer_text = info_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, TEXT_LIGHT)
            timer_shadow = info_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, BLACK)
            
            # Draw shadow first
            screen.blit(timer_shadow, (22, 22))
            # Draw main text
            screen.blit(timer_text, (20, 20))
            
            # Draw message if any
            if self.message and pygame.time.get_ticks() - self.message_time < 2000:
                # Draw message background
                message_bg = pygame.Surface((400, 50), pygame.SRCALPHA)  # Increased size for fullscreen
                pygame.draw.rect(message_bg, (*BLACK, 100), message_bg.get_rect(), border_radius=8)
                message_rect = message_bg.get_rect(center=(SCREEN_WIDTH // 2, 50))
                screen.blit(message_bg, message_rect)
                
                # Draw message text with shadow
                message_text = info_font.render(self.message, True, TEXT_LIGHT)
                message_shadow = info_font.render(self.message, True, BLACK)
                
                # Draw shadow first
                shadow_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2 + 2, 52))
                screen.blit(message_shadow, shadow_rect)
                # Draw main text
                text_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
                screen.blit(message_text, text_rect)
        elif self.state == "end":
            # Draw end screen
            self.draw_end_screen()
            
        # Draw win popup if needed
        if self.show_win_popup:
            self.draw_win_popup()

    def roll_dice(self):
        """Handle dice rolling"""
        if not self.animating:
            self.dice.roll()
            self.animating = True
            self.animation_done = False
            self.set_message("Rolling...")

    def restart_game(self):
        """Restart the game"""
        self.__init__()

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