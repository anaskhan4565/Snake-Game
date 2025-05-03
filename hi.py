import random
from collections import defaultdict

# --- Monte Carlo Simulation Function ---
def monte_carlo_simulation(current_position, num_simulations=1000, num_steps=1):
    cell_counts = defaultdict(int)

    for _ in range(num_simulations):
        pos = current_position

        for _ in range(num_steps):
            dice = random.randint(1, 6)
            pos += dice
            if pos > 100:
                break
            cell_counts[pos] += 1

    # Convert counts to probabilities
    total_hits = sum(cell_counts.values())
    if total_hits == 0:
        return {}
    cell_probabilities = {cell: count / total_hits for cell, count in cell_counts.items()}
    return cell_probabilities


# --- Main Program ---
def roll_dice():
    return random.randint(1, 6)

def display_predictions(probabilities):
    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    print("\n🔮 AI Prediction: Most likely future positions:")
    for cell, prob in sorted_probs[:5]:
        print(f"➡️ Cell {cell}: {prob * 100:.2f}% chance")

def game_loop():
    current_position = 1
    print("🎲 Welcome to AI-Powered Snake & Ladder Prediction!")
    print("Reach cell 100 to win. Let's go!\n")

    while current_position < 100:
        input("Press Enter to roll the dice...")

        roll = roll_dice()
        current_position += roll
        if current_position > 100:
            current_position = 100

        print(f"\n🎯 You rolled a {roll}! Now at cell {current_position}")

        # AI Prediction after player's move
        predictions = monte_carlo_simulation(current_position, num_simulations=1000, num_steps=1)
        display_predictions(predictions)

        if current_position == 100:
            print("\n🏆 You reached cell 100! You win!")
            break

# Run the game
if __name__ == "__main__":
    game_loop()
import random
from collections import defaultdict

# --- Monte Carlo Simulation Function ---
def monte_carlo_simulation(current_position, num_simulations=1000, num_steps=5):
    cell_counts = defaultdict(int)

    for _ in range(num_simulations):
        pos = current_position

        for _ in range(num_steps):
            dice = random.randint(1, 6)
            pos += dice
            if pos > 100:
                break
            cell_counts[pos] += 1

    # Convert counts to probabilities
    total_hits = sum(cell_counts.values())
    if total_hits == 0:
        return {}
    cell_probabilities = {cell: count / total_hits for cell, count in cell_counts.items()}
    return cell_probabilities


# --- Main Program ---
def roll_dice():
    return random.randint(1, 6)

def display_predictions(probabilities):
    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    print("\n🔮 AI Prediction: Most likely future positions:")
    for cell, prob in sorted_probs[:5]:
        print(f"➡️ Cell {cell}: {prob * 100:.2f}% chance")

def game_loop():
    true_predictions=0
    current_position = 1
    print("🎲 Welcome to AI-Powered Snake & Ladder Prediction!")
    print("Reach cell 100 to win. Let's go!\n")

    while current_position < 100:
        input("Press Enter to roll the dice...")

        roll = roll_dice()
        current_position += roll
        if current_position > 100:
            current_position = 100

        print(f"\n🎯 You rolled a {roll}! Now at cell {current_position}")
        # AI Prediction after player's move
        predictions = monte_carlo_simulation(current_position, num_simulations=1000, num_steps=2)
        display_predictions(predictions)
        if current_position == 100:
            print("\n🏆 You reached cell 100! You win!")
            break

# Run the game
if __name__ == "__main__":
    game_loop()
