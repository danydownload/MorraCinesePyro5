import Pyro5.api
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import pyqtSlot, QTimer
import random
import time


class GameClient(QWidget):
    POLLING_INTERVAL = 2  # Polling interval in seconds

    def __init__(self, player_name, server, position):
        super(GameClient, self).__init__()
        self.setWindowTitle(f"Player: {player_name}")
        self.setGeometry(*position, 250, 250)
        self.player_name = player_name
        self.server = server
        self.game_id = None
        self.made_move = False  # Flag to track if the client has made a move
        self.rematch_button = None  # Rematch button

        self.result_label = QLabel(self)
        self.player_label = QLabel(f"Player: {self.player_name}", self)
        self.move_label = QLabel(self)
        self.score_label = QLabel(self)

        self.choices = ["rock", "paper", "scissors"]
        self.buttons = []
        for choice in self.choices:
            btn = QPushButton(choice, self)
            btn.clicked.connect(self.make_choice)
            self.buttons.append(btn)

        vbox = QVBoxLayout()
        vbox.addWidget(self.player_label)
        vbox.addWidget(self.result_label)
        vbox.addWidget(self.move_label)
        vbox.addWidget(self.score_label)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addStretch()

        vbox_buttons = QVBoxLayout()
        for btn in self.buttons:
            vbox_buttons.addWidget(btn)
        hbox.addLayout(vbox_buttons)

        self.rematch_button = QPushButton("Rematch", self)
        self.rematch_button.setEnabled(False)
        self.rematch_button.clicked.connect(self.request_rematch)
        hbox.addWidget(self.rematch_button)

        self.setLayout(hbox)

        self.polling_timer = QTimer()
        self.polling_timer.timeout.connect(self.poll_state)
        self.polling_timer.start(self.POLLING_INTERVAL * 1000)

    @pyqtSlot()
    def make_choice(self):
        if not self.made_move:  # Only allow making a move if a move has not been made yet
            sender = self.sender()
            choice = sender.text()
            self.server.make_choice(self.game_id, self.player_name, choice)
            self.made_move = True  # Set the flag to indicate that a move has been made
            self.move_label.setText(f"Your move: {choice}")
            sender.setEnabled(False)  # Disable the chosen button

    def check_winner(self):
        winner = self.server.determine_winner(self.game_id)
        if winner:
            self.show_winner(winner)

    def show_winner(self, winner):
        if winner == "Draw":
            text = "It's a draw."
        elif winner == "Winner":
            text = "You win!"
        else:
            text = "You lose!"
        self.result_label.setText(text)
        self.polling_timer.stop()  # Stop polling after displaying the result
        self.update_score()
        self.rematch_button.setEnabled(True)  # Enable the rematch button

    def update_score(self):
        state = self.server.get_state(self.game_id, self.player_name)
        if state:
            score = state.count("Winner")
            self.score_label.setText(f"Score: {score}")

    def poll_state(self):
        state = self.server.get_state(self.game_id, self.player_name)
        if state:
            self.show_winner(state)

    def request_rematch(self):
        reply = QMessageBox.question(self, "Rematch", "Do you want to request a rematch?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            rematch_requested = self.server.rematch(self.game_id)
            if rematch_requested:
                self.rematch_button.setEnabled(False)  # Disable the rematch button until the other player requests a rematch
                self.reset_game_state()

    def reset_game_state(self):
        for btn in self.buttons:
            btn.setEnabled(True)
        self.move_label.clear()
        self.result_label.clear()
        self.made_move = False
        self.polling_timer.start(self.POLLING_INTERVAL * 1000)

    def rematch(self):
        reply = QMessageBox.question(self, "Rematch", "Do you want to rematch?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.server.rematch(self.game_id)
            self.reset_game_state()


def main():
    player_name = "Player" + str(random.randint(1, 100))  # Generate a random player name
    game_server = Pyro5.api.Proxy("PYRO:MorraCinese.game@localhost:50693")
    game_id = game_server.register(player_name)

    app = QApplication([])
    position = (random.randint(0, 800), random.randint(0, 600))
    client = GameClient(player_name, game_server, position)
    client.game_id = game_id
    client.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
