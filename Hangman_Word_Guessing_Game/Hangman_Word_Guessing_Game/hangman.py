"""
HANGMAN WORD GUESSING GAME
A beginner-friendly, modular console game written in Python 3.

Run:
    python hangman.py

Use another word list:
    python hangman.py --word-list my_words.txt
"""

import argparse
import random
import sys
from pathlib import Path

MAX_MISTAKES = 6

# One drawing for each possible number of incorrect guesses:
# index 0 = no mistakes, index 6 = game over.
HANGMAN_STAGES = [
    r"""
     +---+
     |   |
         |
         |
         |
         |
    =========
""",
    r"""
     +---+
     |   |
     O   |
         |
         |
         |
    =========
""",
    r"""
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========
""",
    r"""
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========
""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
         |
         |
    =========
""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
    /    |
         |
    =========
""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
    / \  |
         |
    =========
""",
]


def load_words(file_path):
    """Read valid English words from a text file."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Word list not found: {path}")

    words = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            word = line.strip().upper()

            # Accept only A-Z words between 3 and 15 letters.
            if word.isascii() and word.isalpha() and 3 <= len(word) <= 15:
                words.append(word)

    if not words:
        raise ValueError("No valid words found. Add English words (3-15 letters) to the file.")

    return words


def choose_secret_word(words):
    """Choose one word randomly from the available words."""
    return random.choice(words)


def display_word(secret_word, correct_guesses):
    """Show guessed letters and hide the letters not guessed yet."""
    displayed_letters = []

    for letter in secret_word:
        if letter in correct_guesses:
            displayed_letters.append(letter)
        else:
            displayed_letters.append("_")

    return " ".join(displayed_letters)


def is_word_guessed(secret_word, correct_guesses):
    """Return True when every letter in the secret word has been guessed."""
    return all(letter in correct_guesses for letter in secret_word)


def get_player_guess(guessed_letters):
    """Get one new English letter from the player."""
    while True:
        guess = input("Enter one letter (A-Z): ").strip().upper()

        if len(guess) != 1 or guess not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            print("Invalid input! Please enter exactly one letter from A to Z.")
        elif guess in guessed_letters:
            print(f"You already guessed '{guess}'. Try another letter.")
        else:
            return guess


def show_game_state(secret_word, correct_guesses, guessed_letters, mistakes):
    """Display the gallows, hidden word, guessed letters, and attempts."""
    print(HANGMAN_STAGES[mistakes])
    print("Word:             ", display_word(secret_word, correct_guesses))
    print("Guessed letters:  ", " ".join(sorted(guessed_letters)) or "None")
    print(f"Wrong attempts:    {mistakes}/{MAX_MISTAKES}")
    print(f"Attempts left:     {MAX_MISTAKES - mistakes}")
    print()


def play_round(words):
    """Play one round and return True for a win or False for a loss."""
    secret_word = choose_secret_word(words)
    correct_guesses = set()
    guessed_letters = set()
    mistakes = 0

    print("\n" + "=" * 48)
    print("             HANGMAN WORD GAME")
    print("=" * 48)
    print("Guess the hidden word one letter at a time.")
    print(f"You have {MAX_MISTAKES} incorrect attempts. Good luck!\n")

    while mistakes < MAX_MISTAKES:
        show_game_state(
            secret_word, correct_guesses, guessed_letters, mistakes
        )

        # Check for victory before asking for another letter.
        if is_word_guessed(secret_word, correct_guesses):
            print("Congratulations! You guessed the word.")
            print(f"The word was: {secret_word}")
            print("              YOU WIN!")
            return True

        guess = get_player_guess(guessed_letters)
        guessed_letters.add(guess)

        if guess in secret_word:
            correct_guesses.add(guess)
            print(f"Correct! '{guess}' is in the word.\n")
        else:
            mistakes += 1
            print(f"Sorry! '{guess}' is not in the word.\n")

    # Show the final drawing after the sixth incorrect guess.
    show_game_state(secret_word, correct_guesses, guessed_letters, mistakes)
    print("Game over! You have used all 6 incorrect attempts.")
    print(f"The hidden word was: {secret_word}")
    print("              YOU LOSE!")
    return False


def ask_play_again():
    """Ask whether the player wants to start another round."""
    while True:
        answer = input("Would you like to play again? (y/n): ").strip().lower()

        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False

        print("Please enter 'y' for yes or 'n' for no.")


def main():
    """Load the word list and control the complete game session."""
    parser = argparse.ArgumentParser(
        description="Play the console Hangman word guessing game."
    )
    parser.add_argument(
        "--word-list",
        default=str(Path(__file__).with_name("words.txt")),
        help="Path to a text file containing one English word per line.",
    )
    args = parser.parse_args()

    try:
        words = load_words(args.word_list)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    total_rounds = 0
    total_wins = 0

    while True:
        total_rounds += 1

        if play_round(words):
            total_wins += 1

        if not ask_play_again():
            break

    print("\n" + "-" * 40)
    print("Thanks for playing Hangman!")
    print(f"Rounds played: {total_rounds}")
    print(f"Rounds won:    {total_wins}")
    print("-" * 40)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
