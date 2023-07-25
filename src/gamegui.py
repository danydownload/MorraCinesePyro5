from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class GameGUI(QWidget):
    close_game = pyqtSignal()

    def __init__(self, player_name):
        super(GameGUI, self).__init__()

        self.player_name = player_name

        self.result_label = QLabel()
        self.player_label = QLabel(f"Player: {self.player_name}")
        self.num_of_matches_label = QLabel()
        self.num_of_matches_label.setStyleSheet("color: red;")
        self.move_label = QLabel()
        self.move_label.setStyleSheet("color: blue;")
        self.score_label = QLabel()
        self.general_score_label = QLabel()
        self.general_score_label.setStyleSheet("color: green;")
        self.playing_against_label = QLabel()
        self.playing_against_label.setStyleSheet("color: purple;")

        self.choices = ["rock", "paper", "scissors"]
        self.buttons = []
        for choice in self.choices:
            btn = QPushButton(choice)
            btn.setEnabled(False)
            self.buttons.append(btn)

        vbox = QVBoxLayout()
        vbox.addWidget(self.player_label)
        vbox.addWidget(self.playing_against_label)
        vbox.addWidget(self.num_of_matches_label)
        vbox.addWidget(self.result_label)
        vbox.addWidget(self.move_label)
        vbox.addWidget(self.score_label)
        vbox.addWidget(self.general_score_label)

        for btn in self.buttons:
            vbox.addWidget(btn)

        self.rematch_button = QPushButton("Rematch")
        self.rematch_button.setEnabled(False)
        self.new_match_button = QPushButton("New match")
        self.new_match_button.setEnabled(False)
        vbox.addWidget(self.rematch_button)
        vbox.addWidget(self.new_match_button)

        self.setLayout(vbox)

        self.playing_against_label.setText("Playing against: None")
        self.num_of_matches_label.setText("Match 1 of 5")
        self.score_label.setText("Score of the series: 0")
        self.general_score_label.setText("General score: 0")

    def show_game_state(self, game):
        self.result_label.setText(game.result)
        self.move_label.setText(game.move)
        self.score_label.setText(game.score)

    def show_winner(self, winner, winner_of_series):
        if not winner_of_series:
            if winner == "Draw":
                self.result_label.setText("It's a draw.")
            elif winner == "Winner":
                self.result_label.setText("You win!")
            else:
                self.result_label.setText("You lose!")
        else:
            self.clear_labels(self.move_label, self.result_label)

            if winner_of_series == self.player_name:
                self.result_label.setText("You won the series!")
            else:
                if winner_of_series == "Draw":
                    self.result_label.setText("This series ends with a draw!")
                else:
                    self.result_label.setText("You lost the series!")

    def enable_buttons(self):
        for btn in self.buttons:
            btn.setEnabled(True)

    def disable_buttons(self):
        for btn in self.buttons:
            btn.setEnabled(False)

    def disable_list_of_buttons(self, *buttons):
        for btn in buttons:
            btn.setEnabled(False)

    # general function that clear all the labels passed as input
    def clear_labels(self, *labels):
        for label in labels:
            label.clear()

    def closeEvent(self, event):
        """
        Overridden function to handle the window's close event.

        Args:
            event (QCloseEvent): The close event.
        """
        self.close_game.emit()  # Emit a custom signal to indicate that the game window is closing
        event.accept()
