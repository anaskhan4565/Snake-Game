import pygame
import sys
import random
import math
import time
from pygame import gfxdraw

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
        self.snakes = {
            16: 6,
            46: 25,
            49: 11,
            62: 19,
            64: 60,
            74: 53,
            89: 68,
            92: 88,
            95: 75,
            99: 80
        }
        
        self.ladders = {
            2: 38,
            7: 14,
            8: 31,
            15: 26,
            21: 42,
            28: 84,
            36: 44,
            51: 67,
            71: 91,
            78: 98
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

# Colors
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

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
        self.players = [
            Player(RED, "Player 1", (-10, -10)),
            Player(BLUE, "Player 2", (10, 10))
        ]
        self.current_player = 0
        self.dice = Dice()
        self.state = "start"  # start, playing, end
        self.winner = None
        self.message = ""
        self.message_time = 0
        
        # Buttons
        btn_width, btn_height = 150, 50
        self.roll_button = Button(
            SCREEN_WIDTH - 225, SCREEN_HEIGHT - 150, 
            btn_width, btn_height, "Roll Dice", GREEN
        )
        self.start_button = Button(
            SCREEN_WIDTH // 2 - btn_width // 2, SCREEN_HEIGHT // 2 + 100,
            btn_width, btn_height, "Start Game", GREEN
        )
        self.restart_button = Button(
            SCREEN_WIDTH // 2 - btn_width // 2, SCREEN_HEIGHT // 2 + 100,
            btn_width, btn_height, "Play Again", GREEN
        )
        
        # Animation flags
        self.animating = False
        self.animation_done = False
        
    def set_message(self, text):
        self.message = text
        self.message_time = pygame.time.get_ticks()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "start" and self.start_button.check_click(event.pos):
                    self.state = "playing"
                
                elif self.state == "playing" and not self.animating:
                    if self.roll_button.check_click(event.pos):
                        self.dice.roll()
                        self.animating = True
                
                elif self.state == "end" and self.restart_button.check_click(event.pos):
                    self.__init__()  # Reset the game
                    
            if event.type == pygame.MOUSEBUTTONUP:
                self.roll_button.reset()
                self.start_button.reset()
                self.restart_button.reset()
                    
    def update(self):
        if self.state == "playing":
            if self.animating:
                # Dice rolling animation
                if self.dice.update() and not self.animation_done:
                    # After dice roll is complete, move player
                    current = self.players[self.current_player]
                    current.move(self.dice.value)
                    self.animation_done = True
                    self.set_message(f"{current.name} rolled a {self.dice.value}")
                
                # Player movement animation
                if self.animation_done:
                    current = self.players[self.current_player]
                    if current.update_animation():
                        # After player movement is complete
                        position = current.position
                        
                        # Check for snakes
                        if position in self.board.snakes:
                            new_pos = self.board.snakes[position]
                            current.move(new_pos - position)
                            self.set_message(f"Oh no! {current.name} hit a snake and slides down!")
                            return
                            
                        # Check for ladders
                        if position in self.board.ladders:
                            new_pos = self.board.ladders[position]
                            current.move(new_pos - position)
                            self.set_message(f"Yay! {current.name} climbs a ladder!")
                            return
                            
                        # Check for win
                        if position == 100:
                            current.win = True
                            self.state = "end"
                            self.winner = self.current_player
                            return
                        
                        # Next player's turn
                        self.current_player = (self.current_player + 1) % len(self.players)
                        self.animating = False
                        self.animation_done = False
    
    def draw(self):
        # Fill background with a gradient
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            r = int(173 + (230 - 173) * progress)
            g = int(216 + (230 - 216) * progress)
            b = int(230 + (210 - 230) * progress)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
        if self.state == "start":
            # Draw title screen
            title_text = title_font.render("Snakes and Ladders", True, (70, 50, 120))
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            screen.blit(title_text, title_rect)
            
            # Draw instructions
            instructions = [
                "Roll the dice and move your piece forward.",
                "Climb up ladders to advance faster.",
                "Avoid snakes that will slide you back down.",
                "First player to reach square 100 wins!"
            ]
            
            for i, instruction in enumerate(instructions):
                text = info_font.render(instruction, True, BLACK)
                rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60 + i * 30))
                screen.blit(text, rect)
            
            self.start_button.draw()
            
        elif self.state == "playing" or self.state == "end":
            # Draw the game board
            self.board.draw()
            
            # Draw players
            for player in self.players:
                player.draw(self.board)
            
            # Draw dice
            self.dice.draw()
            
            # Draw player info
            for i, player in enumerate(self.players):
                # Player indicator box
                box_y = 100 + i * 60
                pygame.draw.rect(screen, player.color, (50, box_y, 200, 50), border_radius=8)
                pygame.draw.rect(screen, BLACK, (50, box_y, 200, 50), 2, border_radius=8)
                
                # Player name and position
                name_text = info_font.render(f"{player.name}: {player.position}", True, WHITE)
                name_rect = name_text.get_rect(center=(150, box_y + 25))
                screen.blit(name_text, name_rect)
                
                # Highlight current player
                if i == self.current_player and self.state == "playing":
                    pygame.draw.rect(screen, GOLD, (45, box_y - 5, 210, 60), 3, border_radius=10)
            
            # Draw roll button in playing state
            if self.state == "playing":
                self.roll_button.draw()
            
            # Draw message
            if self.message and pygame.time.get_ticks() - self.message_time < 3000:
                message_text = info_font.render(self.message, True, BLACK)
                message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
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
                
                # Draw winner message
                winner = self.players[self.winner]
                win_text = title_font.render(f"{winner.name} Wins!", True, winner.color)
                win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                
                # Draw text shadow for better visibility
                shadow_text = title_font.render(f"{winner.name} Wins!", True, BLACK)
                shadow_rect = shadow_text.get_rect(center=(win_rect.centerx + 3, win_rect.centery + 3))
                screen.blit(shadow_text, shadow_rect)
                screen.blit(win_text, win_rect)
                
                self.restart_button.draw()

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