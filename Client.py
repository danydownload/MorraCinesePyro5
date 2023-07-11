import Pyro5.api
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import pyqtSlot
import random


class GameClient(QWidget):

    def __init__(self, player_name, server, position):
        super(GameClient, self).__init__()
        self.setWindowTitle(f"Player: {player_name}")
        self.setGeometry(*position, 250, 250)
        self.player_name = player_name
        self.server = server
        self.game_id = None

        self.result_label = QLabel(self)
        self.player_label = QLabel(f"Player: {self.player_name}", self)

        vbox = QVBoxLayout()
        vbox.addWidget(self.player_label)
        vbox.addWidget(self.result_label)

        self.choices = ["rock", "paper", "scissors"]
        for choice in self.choices:
            btn = QPushButton(choice, self)
            btn.clicked.connect(self.make_choice)
            vbox.addWidget(btn)

        self.setLayout(vbox)

    @pyqtSlot()
    def make_choice(self):
        sender = self.sender()
        self.server.make_choice(self.game_id, self.player_name, sender.text())
        self.check_winner()

    def check_winner(self):
        winner = self.server.determine_winner(self.game_id)
        if winner:
            self.show_winner(winner)

    def show_winner(self, winner):
        if winner == "Draw":
            text = "It's a draw."
        elif winner == self.player_name:
            text = "You win!"
        else:
            text = "You lose!"
        self.result_label.setText(text)


def main():
    player_name = input("Enter your name: ")
    game_server = Pyro5.api.Proxy("PYRO:MorraCinese.game@localhost:50693")
    game_id = game_server.register(player_name)

    app = QApplication([])
    # generate random positions for the window
    position = (random.randint(0, 800), random.randint(0, 600))
    client = GameClient(player_name, game_server, position)
    client.game_id = game_id
    client.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
