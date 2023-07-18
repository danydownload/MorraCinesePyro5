import Pyro5.api
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
from PyQt5.QtCore import QTimer
import random
from gamegui import GameGUI
from enums import Move, Result, MatchStatus

MARGIN = 50
WINDOW_WIDTH = 250
WINDOW_HEIGHT = 250
WINDOW_TITLE = "Morra Cinese"


class GameClient:
    POLLING_INTERVAL = 1  # Polling interval in seconds
    REMATCH_POLLING_INTERVAL = 1  # Polling interval in seconds for rematch state

    def __init__(self, player_name, server, position):
        self.player_name = player_name
        self.server = server
        self.game_id = None
        self.made_move = False  # Flag to track if the client has made a move

        self.gui = GameGUI(player_name)
        for btn in self.gui.buttons:
            btn.clicked.connect(self.make_choice)

        self.gui.rematch_button.clicked.connect(self.request_rematch)

        self.polling_timer = QTimer()
        self.polling_timer.timeout.connect(self.poll_game_state)
        self.polling_timer.start(self.POLLING_INTERVAL * 1000)

        self.rematch_polling_timer = QTimer()
        self.rematch_polling_timer.timeout.connect(self.poll_match_status)

    def make_choice(self):
        if not self.made_move:
            sender = self.gui.sender()
            choice = sender.text()

            self.server.make_choice(self.player_name, choice)
            self.made_move = True
            self.gui.move_label.setText(f"Your move: {choice}")

            for button in self.gui.buttons:
                button.setEnabled(False)

    def show_winner(self, winner):
        self.gui.show_winner(winner)
        self.polling_timer.stop()
        self.rematch_polling_timer.start(self.REMATCH_POLLING_INTERVAL * 1000)
        self.update_score()
        self.gui.rematch_button.setEnabled(True)  # Enable the rematch button

    def update_score(self):
        score = self.server.get_score(self.player_name)
        self.gui.score_label.setText(f"Score: {score}")

    def poll_game_state(self):
        game_state = self.server.get_game_state(self.player_name)
        if game_state:
            self.show_winner(game_state)

    # TODO: fixare rematch. Poi dovra' essere possibile fare il rematch soltanto dopo che la serie di partite e' finita
    def poll_match_status(self):
        match_status = self.server.get_match_status(self.player_name)
        # match_status e' una stringa invece che un MatchStatus.
        # Questo e' un workaround perche' Pyro non riesce a serializzare l'enum MatchStatus
        match_status = MatchStatus(match_status)
        if match_status == MatchStatus.REMATCH:
            print("Rematch accepted. Resetting game...")
            self.reset_game_state()
            self.gui.rematch_button.setEnabled(False)
        else:
            print("Waiting for rematch...")

    def request_rematch(self):
        print("Requesting rematch...")
        reply = QMessageBox.question(self.gui, "Rematch", "Do you want to request a rematch?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.server.rematch(self.player_name)
            self.gui.rematch_button.setEnabled(False)


    def reset_game_state(self):
        self.gui.enable_buttons()
        self.gui.move_label.clear()
        self.gui.result_label.clear()
        self.made_move = False
        self.polling_timer.start(self.POLLING_INTERVAL * 1000)
        self.rematch_polling_timer.stop()


def main():
    app = QApplication([])

    game_server = Pyro5.api.Proxy("PYRO:MorraCinese.game@localhost:55894")

    while True:
        player_name, ok = QInputDialog.getText(QtWidgets.QWidget(), "Player Registration", "Enter player name:")
        if ok and player_name:
            try:
                game_id = game_server.register_player(player_name)
                break
            except ValueError as e:
                QMessageBox.critical(None, "Registration Error", str(e))
        else:
            print("Player registration cancelled.")
            sys.exit()

    screen_resolution = QtWidgets.QDesktopWidget().availableGeometry()
    screen_width = screen_resolution.width()
    screen_height = screen_resolution.height()

    x_range = (MARGIN, screen_width - WINDOW_WIDTH - MARGIN)
    y_range = (MARGIN, screen_height - WINDOW_HEIGHT - MARGIN)
    position = (random.randint(*x_range), random.randint(*y_range))

    client = GameClient(player_name, game_server, position)
    client.game_id = game_id
    client.gui.setGeometry(*position, WINDOW_WIDTH, WINDOW_HEIGHT)  # Imposta le dimensioni della finestra
    client.gui.setWindowTitle(f"{WINDOW_TITLE} - {player_name}")
    client.gui.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
