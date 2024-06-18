import pathlib
import random
import tkinter as tk
from tkinter import messagebox
from string import ascii_letters


class WordList:
    def __init__(self, filepath):
        self.filepath = filepath
        self.words = self.load_words()

    def load_words(self):
        wordlist_path = pathlib.Path(self.filepath)
        if not wordlist_path.is_file():
            raise FileNotFoundError(f"Wordlist file '{self.filepath}' not found.")
        return [
            word.upper()
            for word in wordlist_path.read_text(encoding="utf-8").split("\n")
            if len(word) == 5 and all(letter in ascii_letters for letter in word)
        ]

    def get_random_word(self):
        return random.choice(self.words)


class WyrdlGame(tk.Tk):
    def __init__(self, wordlist_path):
        super().__init__()

        self.title("Wyrdl Game")
        self.geometry("600x800")
        self.word_list = WordList(wordlist_path)
        self.word = self.word_list.get_random_word()
        self.max_attempts = 5
        self.guess_num = 1

        self.create_widgets()

    def create_widgets(self):
        self.guess_label = tk.Label(self, text=f"Guess {self.guess_num}", font=("Helvetica", 14))
        self.guess_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.guess_entry = tk.Entry(self, font=("Helvetica", 14), width=10)
        self.guess_entry.grid(row=1, column=0, columnspan=2, pady=10)
        self.guess_entry.bind("<Return>", self.process_guess)

        self.previous_guesses_frame = tk.Frame(self)
        self.previous_guesses_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.correct_label = tk.Label(self, text="Correct letters:", font=("Helvetica", 12))
        self.correct_label.grid(row=3, column=0, pady=5)

        self.correct_listbox = tk.Listbox(self, font=("Helvetica", 12), width=20, height=5)
        self.correct_listbox.grid(row=4, column=0, pady=5)

        self.misplaced_label = tk.Label(self, text="Misplaced letters:", font=("Helvetica", 12))
        self.misplaced_label.grid(row=3, column=1, pady=5)

        self.misplaced_listbox = tk.Listbox(self, font=("Helvetica", 12), width=20, height=5)
        self.misplaced_listbox.grid(row=4, column=1, pady=5)

        self.alphabet_frame = tk.Frame(self)
        self.alphabet_frame.grid(row=5, column=0, columnspan=2, pady=10)

        self.alphabet_labels = {}
        for i, letter in enumerate(ascii_letters[:26]):
            label = tk.Label(self.alphabet_frame, text=letter.upper(), font=("Helvetica", 14), width=2)
            label.grid(row=0, column=i)
            self.alphabet_labels[letter.lower()] = label

    def process_guess(self, event):
        guess = self.guess_entry.get().upper()
        if len(guess) != 5 or not all(letter in ascii_letters.upper() for letter in guess):
            messagebox.showerror("Invalid Guess", "Please enter a valid 5-letter word.")
            return

        self.guess_entry.delete(0, tk.END)
        if guess == self.word:
            messagebox.showinfo("Correct", "You guessed the word!")
            self.quit()
            return

        correct_letters, misplaced_letters, wrong_letters = self.evaluate_guess(guess)
        self.show_feedback(guess, correct_letters, misplaced_letters, wrong_letters)

        self.guess_num += 1
        self.guess_label.config(text=f"Guess {self.guess_num}")

        if self.guess_num > self.max_attempts:
            self.game_over()

    def evaluate_guess(self, guess):
        correct_letters = []
        misplaced_letters = []
        wrong_letters = []

        word_letter_count = {letter: self.word.count(letter) for letter in set(self.word)}

        # First pass: Identify correct letters
        for i, letter in enumerate(guess):
            if letter == self.word[i]:
                correct_letters.append((letter, i))
                word_letter_count[letter] -= 1

        # Second pass: Identify misplaced and wrong letters
        for i, letter in enumerate(guess):
            if (letter, i) not in correct_letters:
                if letter in self.word and word_letter_count[letter] > 0:
                    misplaced_letters.append((letter, i))
                    word_letter_count[letter] -= 1
                else:
                    wrong_letters.append((letter, i))

        return correct_letters, misplaced_letters, wrong_letters

    def show_feedback(self, guess, correct_letters, misplaced_letters, wrong_letters):
        guess_frame = tk.Frame(self.previous_guesses_frame)
        guess_frame.pack()

        correct_positions = {pos for _, pos in correct_letters}
        misplaced_positions = {pos for _, pos in misplaced_letters}

        for i, letter in enumerate(guess):
            if i in correct_positions:
                bg_color = "green"
            elif i in misplaced_positions:
                bg_color = "yellow"
            else:
                bg_color = "grey"

            label = tk.Label(guess_frame, text=letter, font=("Helvetica", 14), bg=bg_color, width=2)
            label.pack(side=tk.LEFT)

        # Update the lists of correct and misplaced letters
        self.correct_listbox.insert(tk.END, ", ".join(sorted(set(letter for letter, _ in correct_letters))))
        self.misplaced_listbox.insert(tk.END, ", ".join(sorted(set(letter for letter, _ in misplaced_letters))))

        # Update the alphabet labels
        for letter in ascii_letters[:26]:
            if letter.lower() in [l.lower() for l, _ in correct_letters]:
                self.alphabet_labels[letter.lower()].config(bg="green")
            elif letter.lower() in [l.lower() for l, _ in misplaced_letters]:
                self.alphabet_labels[letter.lower()].config(bg="yellow")
            elif letter.lower() in [l.lower() for l, _ in wrong_letters]:
                self.alphabet_labels[letter.lower()].config(bg="grey")

    def game_over(self):
        messagebox.showinfo("Game Over", f"The word was {self.word}.")
        self.quit()


if __name__ == "__main__":
    wordlist_path = "wordlist.txt"  # Replace with your wordlist file
    try:
        game = WyrdlGame(wordlist_path)
        game.mainloop()
    except FileNotFoundError as e:
        print(e)
