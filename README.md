# Snakes and Ladders Game

A beautiful, animated implementation of the classic Snakes and Ladders board game with high-quality visuals and smooth animations.

## Features

About the Game This is an AI-driven Snake and Ladder game where snakes and ladders appear dynamically on the board instead of being fixed. The game offers three difficulty modes: Easy, Medium, and Hard, each adjusting the challenge level based on time limits and the number and size of snakes. AI Algorithms Used:



Monte Carlo Simulation This algorithm predicts the player’s possible future positions by running thousands of simulations before each move. Based on the resulting probability distribution: Snakes are placed on the most likely cells the user might land on. Ladders appear on less likely cells to reduce chances of rapid progress.



MiniMax Algorithm This algorithm works to minimize the player’s progress toward cell 100. As the player approaches the goal, the AI increases the difficulty by placing more and larger snakes. The intensity of this behavior varies by difficulty mode.



Difficulty Modes: Easy: Fewer and shorter snakes, more time to play. Medium: Increased number and size of snakes, with less time. Hard: Most snakes, largest in size, and minimal thinking time.



Objective: Just like the traditional Snake and Ladder game, your goal is to reach cell 100. However, with dynamic obstacles and AI predictions, every move counts — and the snakes are much smarter now.



Enjoy the game!

## How to Play

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the game:
   ```
   python snakes_and_ladders.py
   ```

3. Game Rules:
   - Players take turns rolling the dice
   - Move your piece forward according to the dice value
   - Land on a ladder to climb up
   - Land on a snake and slide down
   - First player to reach or exceed position 100 wins!

## Game Controls

- Click the "Start Game" button to begin
- Click the "Roll Dice" button on your turn
- Click "Play Again" at the end to restart

## Technical Details

The game is built using Python with Pygame for rendering and animations. It features:
- Object-oriented architecture
- Smooth animations using frame-based timing
- Bezier curves for snake rendering
- Custom UI components
- State-based game flow

Enjoy playing! 
