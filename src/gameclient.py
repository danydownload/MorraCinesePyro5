import Pyro5.api
import sys
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QApplication, QMessageBox, QInputDialog
from PyQt6.QtCore import QTimer
import random
from gamegui import GameGUI
from enums import Move, Result, MatchStatus

MARGIN = 50
WINDOW_WIDTH = 260
WINDOW_HEIGHT = 250
WINDOW_TITLE = "Morra Cinese"
TIME_TO_MOVE = 120  # Time to make a move in seconds


class GameClient:
    """
    The GameClient class handles the client-side interactions of the game. It manages the user interface, player moves,
    game state polling, match status, and player unregistration. The client communicates with the game server,
    manages the game GUI, processes player choices, and handles rematch and new match requests.

    Attributes:
        server (Pyro5.api.Proxy): The game server object that the client interacts with.
        player_name (str): The player's name.
        game_id (int): Unique identifier for the game. Initially, this is set to None.
        made_move (bool): Flag to track if the client has made a move. Initially, this is set to False.
        series_over (bool): Flag to track if the match has ended. Initially, this is set to False.
        gui (GameGUI): The GUI object for the game.
        polling_timer (QTimer): Timer object to periodically check the game state.
        rematch_polling_timer (QTimer): Timer object to periodically check the match status.
        timer (QTimer): Timer object to manage the time allotted for a player to make a move.
    """
    POLLING_INTERVAL = 1  # Polling interval in seconds
    REMATCH_POLLING_INTERVAL = 1  # Polling interval in seconds for rematch state

    def __init__(self, player_name, server):
        """
        Initialize the GameClient with a player's name, the server object, and a position for the game window.

        Args:
            player_name (str): The name of the player.
            server (Pyro5.api.Proxy): The game server object.
        """
        self.player_name = player_name
        self.server = server
        self.game_id = None
        self.made_move = False  # Flag to track if the client has made a move
        self.series_over = False  # Flag to track if the match has ended

        self.gui = GameGUI(player_name)
        for btn in self.gui.buttons:
            btn.clicked.connect(self.make_choice)

        self.gui.rematch_button.clicked.connect(self.request_rematch)
        self.gui.new_match_button.clicked.connect(self.request_new_match)

        self.polling_timer = QTimer()
        self.polling_timer.timeout.connect(self.poll_game_state)
        self.polling_timer.start(self.POLLING_INTERVAL * 1000)

        self.rematch_polling_timer = QTimer()
        self.rematch_polling_timer.timeout.connect(self.poll_match_status)

        self.gui.closeEvent = self.handle_close_event

        # Set the timer for the time to make a move
        self.timer = QTimer()
        self.timer.timeout.connect(self.unregister_player)

    def make_choice(self):
        """
        Function to make a move in the game.
        """
        print("Making choice...")
        if not self.made_move:
            print("Choice made...")
            sender = self.gui.sender()
            choice = sender.text()

            print(f'player_name: {self.player_name}, choice: {choice}')

            self.server.make_choice(self.player_name, choice)
            self.made_move = True
            self.gui.move_label.setText(f"Your move: {choice}")
            print("Stopping timer...")
            self.timer.stop()

            for button in self.gui.buttons:
                button.setEnabled(False)

    def show_winner(self, winner, winner_of_series=None):
        """
        Function to show the winner of the game.

        Args:
            winner (str): The name of the player who won.
            winner_of_series (str): The name of the player who won the series (optional).
        """
        print("Showing winner...")

        if winner_of_series is not None:
            self.server.update_general_score(self.player_name)
            self.gui.general_score_label.setText(
                f"General score: {self.server.get_general_score(self.player_name)}")

        self.gui.show_winner(winner, winner_of_series)
        self.polling_timer.stop()
        self.rematch_polling_timer.start(self.REMATCH_POLLING_INTERVAL * 1000)

        self.update_score()

        # solo se lo stato della partita e' REMATCH, allora abilito il pulsante per il rematch
        if MatchStatus(self.server.get_match_status(self.player_name)) == MatchStatus.SERIES_OVER:
            self.gui.rematch_button.setEnabled(True)  # Enable the rematch button
            self.gui.new_match_button.setEnabled(True)  # Enable the new match button
            self.made_move = False

    def update_score(self):
        """
        Function to update the score of the current game series.
        """
        score = self.server.get_score(self.player_name)
        self.gui.score_label.setText(f"Score of the series: {score}")

    def poll_game_state(self):
        """
        Function to poll the game state from the server and update the GUI.
        """
        game_state = self.server.get_game_state(self.player_name)
        match_status = MatchStatus(self.server.get_match_status(self.player_name))
        winner_of_series = self.server.get_winner_of_series(self.player_name)
        # print("Winner of series: ", winner_of_series)
        # print(f'game_state: {game_state}, match_status: {match_status}')

        if match_status == MatchStatus.LEFT:
            self.gui.disable_buttons()
            self.gui.playing_against_label.setText(
                f"Playing against: {self.server.get_opponent_name(self.player_name)}")
            # self.gui.result_label.setText("Your opponent left the match. You win!")
            self.gui.move_label.clear()
            self.gui.rematch_button.setEnabled(False)
            self.gui.new_match_button.setEnabled(True)
            self.made_move = False
            self.polling_timer.stop()
            self.rematch_polling_timer.start(self.REMATCH_POLLING_INTERVAL * 1000)

            print("Self.series_over: ", self.series_over)
            if not self.series_over:
                print("GAME-STATE LEFT: Updating general score")
                self.gui.result_label.setText("Your opponent left the match. You win!")
                self.server.update_general_score(self.player_name)

            self.gui.general_score_label.setText(
                f"General score: {self.server.get_general_score(self.player_name)}")
            self.server.reset_after_left(self.player_name)

        if match_status == MatchStatus.ONGOING and not self.made_move:
            if not self.timer.isActive():
                print("Starting timer...")
                self.timer.start(TIME_TO_MOVE * 1000)
            # print("[POLL GAME STATE]: Match is ongoing - move not made yet")
            self.gui.enable_buttons()
            self.gui.disable_list_of_buttons(self.gui.rematch_button, self.gui.new_match_button)
            self.gui.playing_against_label.setText(
                f"Playing against: {self.server.get_opponent_name(self.player_name)}")

        if game_state and match_status == MatchStatus.OVER:
            self.show_winner(game_state)
            self.series_over = False

        if match_status == MatchStatus.SERIES_OVER:
            self.show_winner(game_state, winner_of_series)
            self.server.get_general_score(self.player_name)
            # TODO check if this is correct
            self.series_over = True
            # if not self.series_over:
            #     self.server.update_general_score(self.player_name)
            #     self.gui.general_score_label.setText(
            #         f"General score: {self.server.get_general_score(self.player_name)}")

    def poll_match_status(self):
        """
        Function to poll the match status from the server and update the GUI.
        """
        match_status = self.server.get_match_status(self.player_name)
        # match_status e' una stringa invece che un MatchStatus.
        # Questo e' un workaround perche' Pyro non riesce a serializzare l'enum MatchStatus
        match_status = MatchStatus(match_status)

        # print(f'match_status: {match_status}')
        # print(f'made_move: {self.made_move}')

        if match_status == MatchStatus.LEFT:
            self.gui.disable_buttons()
            self.gui.playing_against_label.setText(
                f"Playing against: {self.server.get_opponent_name(self.player_name)}")
            self.gui.move_label.clear()
            self.gui.rematch_button.setEnabled(False)
            self.gui.new_match_button.setEnabled(True)
            self.made_move = False
            self.polling_timer.stop()
            self.rematch_polling_timer.start(self.REMATCH_POLLING_INTERVAL * 1000)
            print("[MS]Self.series_over: ", self.series_over)
            if not self.series_over:
                print("MATCH-STATUS LEFT: Updating general score")
                self.gui.result_label.setText("Your opponent left the match. You win!")
                self.server.update_general_score(self.player_name)

            self.gui.general_score_label.setText(
                f"General score: {self.server.get_general_score(self.player_name)}")
            self.server.reset_after_left(self.player_name)

        if match_status == MatchStatus.ONGOING and not self.made_move:
            print("[POLL GAME STATUS]: Match is ongoing - move not made yet")
            self.reset_game_state(new_match=True)
            self.gui.enable_buttons()
            self.gui.playing_against_label.setText(
                f"Playing against: {self.server.get_opponent_name(self.player_name)}")
        if match_status == MatchStatus.OVER:
            print("Match is over")
            self.made_move = False
            self.server.reset_state_after_single_match(self.player_name)
            QTimer.singleShot(1000, self.reset_game_state)
        elif match_status == MatchStatus.REMATCH:
            self.reset_game_state()
            self.update_score()
            self.gui.rematch_button.setEnabled(False)

    def request_rematch(self):
        """
        Function to request a rematch at the end of the game series.
        """
        print("Requesting rematch...")
        reply = QMessageBox.question(self.gui, "Rematch", "Do you want to request a rematch?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = self.server.rematch(self.player_name)
            if result is not None:
                self.gui.rematch_button.setEnabled(False)
                self.gui.new_match_button.setEnabled(False)
                self.made_move = False

    def request_new_match(self):
        """
         Function to request a new match.
         """
        print("Requesting new match...")
        reply = QMessageBox.question(self.gui, "New match", "Do you want to request a new match?")
        if reply == QMessageBox.StandardButton.Yes:
            self.server.new_match(self.player_name)
            self.gui.rematch_button.setEnabled(False)
            self.gui.new_match_button.setEnabled(False)
            self.made_move = False

    def reset_game_state(self, new_match=False):
        """
        Function to reset the game state in preparation for a new match or rematch.

        Args:
            new_match (bool): Flag to indicate if this is a new match.
        """
        print("Resetting game state...")
        num_of_match = self.server.get_num_of_match(self.player_name)
        self.gui.num_of_matches_label.setText(f"Match {num_of_match} of 5")
        self.gui.enable_buttons()
        self.gui.move_label.clear()
        self.gui.result_label.clear()
        self.made_move = False
        self.series_over = False
        self.polling_timer.start(self.POLLING_INTERVAL * 1000)
        self.rematch_polling_timer.stop()
        if new_match:
            self.gui.score_label.clear()
            self.gui.playing_against_label.clear()
            self.gui.score_label.setText(f"Score of the series: {self.server.get_score(self.player_name)}")

    def handle_close_event(self, event):
        """
        Custom function to handle the window's close event.

        Args:
            event (QCloseEvent): The close event.
        """
        reply = QMessageBox.question(self.gui, "Exit Game", "Are you sure you want to exit the game?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Unregister the player before closing the window
            print(f"Unregistering player {self.player_name}...")
            self.server.unregister_player(self.player_name)
            event.accept()
        else:
            event.ignore()

    def unregister_player(self):
        """
        Function to unregister the player from the server.
        """
        print(f"Unregistering player {self.player_name}...")
        self.server.unregister_player(self.player_name)


def main():
    """
    Main function to start the application.
    """
    app = QApplication([])

    game_server = Pyro5.api.Proxy("PYRO:MorraCinese.game@localhost:55894")

    # player_name = f'Player {random.randint(1, 100)}'
    # game_id = game_server.register_player(player_name)

    while True:
        player_name, ok = QInputDialog.getText(QtWidgets.QWidget(), "Player Registration", "Enter player name:")
        if not ok:
            print("Player registration cancelled.")
            sys.exit()
        if player_name == "" or player_name.upper().strip() == "NONE" or player_name.isspace():
            QMessageBox.critical(None, "Registration Error", "Player name cannot be empty or None or whitespace.")
            continue
        if ok and player_name:
            try:
                game_id = game_server.register_player(player_name)
                break
            except ValueError as e:
                QMessageBox.critical(None, "Registration Error", str(e))
        else:
            print("Player registration cancelled.")
            sys.exit()

    screen_resolution = QtGui.QGuiApplication.primaryScreen().availableGeometry()

    screen_width = screen_resolution.width()
    screen_height = screen_resolution.height()

    x_range = (MARGIN, screen_width - WINDOW_WIDTH - MARGIN)
    y_range = (MARGIN, screen_height - WINDOW_HEIGHT - MARGIN)
    position = (random.randint(*x_range), random.randint(*y_range))

    client = GameClient(player_name, game_server)
    client.game_id = game_id
    client.gui.setGeometry(*position, WINDOW_WIDTH, WINDOW_HEIGHT)  # Imposta le dimensioni della finestra
    client.gui.setWindowTitle(f"{WINDOW_TITLE} - {player_name}")
    client.gui.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
