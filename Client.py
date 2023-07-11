import Pyro5.api
import tkinter as tk
from tkinter import messagebox
import random


class GameClient(object):
    def __init__(self, root, player_name, server, position):
        self.root = root
        self.root.geometry(f"250x250+{position[0]}+{position[1]}")
        self.player_name = player_name
        self.server = server
        self.game_id = None
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.choices = ["rock", "paper", "scissors"]
        self.button_colors = ["red", "green", "blue"]
        for i in range(3):
            button = tk.Button(self.frame, text=self.choices[i], command=lambda choice=self.choices[i]: self.make_choice(choice),
                               height=2, width=10, bg=self.button_colors[i], activebackground=self.button_colors[i])
            button.pack(side="left")
        self.result_label = tk.Label(self.root)
        self.result_label.pack()

        self.player_label = tk.Label(self.root, text=f"Player: {self.player_name}")
        self.player_label.pack()

        self.opponent_choice = None

    def make_choice(self, choice):
        if self.opponent_choice is None:
            messagebox.showinfo("Waiting", "Waiting for the other player to make a move.")
        else:
            self.server.make_choice(self.game_id, self.player_name, choice)
            self.check_winner()

    def check_winner(self):
        winner = self.server.determine_winner(self.game_id)
        if winner == "Waiting for the other player to make a move.":
            messagebox.showinfo("Waiting", winner)
        elif winner:
            self.show_winner(winner)

    def show_winner(self, winner):
        if winner == "Draw":
            text = "It's a draw."
        elif winner == self.player_name:
            text = "You win!"
        else:
            text = "You lose!"
        self.result_label.config(text=text)

    def set_opponent_choice(self, choice):
        self.opponent_choice = choice


def main():
    player_name = input("Enter your name: ")
    game_server = Pyro5.api.Proxy("PYRO:MorraCinese.game@localhost:50693")
    game_id = game_server.register(player_name)

    root = tk.Tk()
    # generate random positions for the window
    position = (random.randint(0, 800), random.randint(0, 600))
    client = GameClient(root, player_name, game_server, position)
    client.game_id = game_id
    print(f"Partita {game_id} - Benvenuto {player_name} e buona partita")

    root.mainloop()


if __name__ == "__main__":
    main()
