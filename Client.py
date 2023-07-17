import Pyro5.api
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox
from PyQt5.QtCore import pyqtSlot, QTimer
import random


class GameClient(QWidget):
    POLLING_INTERVAL = 1  # Polling interval in seco.nds
    REMATCH_POLLING_INTERVAL = 1  # Polling interval in seconds for rematch state

    def __init__(self, player_name, server, position):
        """
        Inizializzazione del client del gioco.

        Args:
            player_name (str): Il nome del giocatore.
            server (Pyro5.Proxy): Il proxy per il server del gioco.
            position (tuple): La posizione iniziale della finestra del client.
        """
        super(GameClient, self).__init__()
        self.setWindowTitle(f"Player: {player_name}")
        self.setGeometry(*position, 250, 250)
        self.player_name = player_name
        self.server = server
        self.game_id = None
        self.made_move = False  # Flag per tenere traccia se il client ha fatto una mossa
        self.rematch_button = None

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
        self.polling_timer.timeout.connect(self.poll_game_state)
        self.polling_timer.start(self.POLLING_INTERVAL * 1000)

        self.rematch_polling_timer = QTimer()
        self.rematch_polling_timer.timeout.connect(self.poll_rematch_status)
        # self.rematch_polling_timer.start(self.REMATCH_POLLING_INTERVAL * 1000)

    @pyqtSlot()
    def make_choice(self):
        """
        Registra la scelta di una mossa effettuata dal giocatore.
        """
        if not self.made_move:  # Permette di fare una mossa solo se non e' gia' stata fatta una mossa.
            sender = self.sender()
            choice = sender.text()
            self.server.make_choice(self.game_id, self.player_name, choice)
            self.made_move = True  # Setta il flag a True per indicare che il giocatore ha fatto una mossa.
            self.move_label.setText(f"Your move: {choice}")
            sender.setEnabled(False)  # Disable the chosen button
            print(f"Player: {self.player_name} chose: {choice}")

    def check_winner(self):
        """
        Controlla il vincitore della partita.
        """
        winner = self.server.determine_winner(self.game_id)
        if winner:
            self.show_winner(winner)

    def show_winner(self, winner):
        """
        Mostra il vincitore della partita.

        Args:
            winner (str): Lo stato del vincitore ("Draw", "Winner", "Loser").
        """
        print(f'self.player_name: {self.player_name}: {winner}')
        if winner == "Draw":
            print("It's a draw.")
            text = "It's a draw."
        elif winner == "Winner":
            print("You win!")
            text = "You win!"
        else:
            print("You lose!")
            text = "You lose!"
        self.result_label.setText(text)
        self.polling_timer.stop()  # Stop polling dopo aver mostrato il risultato.
        self.rematch_polling_timer.start(self.REMATCH_POLLING_INTERVAL * 1000)
        self.update_score()
        self.rematch_button.setEnabled(True)  # Enable the rematch button

    def update_score(self):
        """
        Aggiorna il punteggio del giocatore.
        """
        score = self.server.get_score(self.player_name)
        self.score_label.setText(f"Score: {score}")

    def poll_game_state(self):
        """
        Esegue il polling dello stato attuale della partita.
        """
        game_state = self.server.get_game_state(self.game_id, self.player_name)
        # print(f"[POLLING] Game state: {game_state}")
        if game_state:
            self.show_winner(game_state)

    def poll_rematch_status(self):
        """
        Esegue il polling dello stato di rematch della partita.
        """
        rematch_status = self.server.get_rematch_status(self.game_id)
        # print(f"[POLLING] Rematch status: {rematch_status}")
        if rematch_status == "REMATCH":
            self.reset_game_state()
            self.rematch_button.setEnabled(False)

    def request_rematch(self):
        """
        Gestisce la richiesta di rematch da parte del giocatore.
        """
        reply = QMessageBox.question(self, "Rematch", "Do you want to request a rematch?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            rematch_requested = self.server.rematch(self.game_id, self.player_name)
            if rematch_requested:
                self.rematch_button.setEnabled(
                    False)  # Disabilita il pulsante di rematch per evitare che venga premuto piu' volte
                self.reset_game_state()
                self.server.reset_rematch_status(self.game_id)  # Resetta lo stato di rematch della partita

    def reset_game_state(self):
        """
        Resetta lo stato della partita per iniziarne una nuova.
        """
        for btn in self.buttons:
            btn.setEnabled(True)
        self.move_label.clear()
        self.result_label.clear()
        self.made_move = False
        self.polling_timer.start(self.POLLING_INTERVAL * 1000)
        self.rematch_polling_timer.stop()


from PyQt5.QtWidgets import QInputDialog, QMessageBox


def main():
    """
    Funzione principale per avviare il client del gioco.
    """
    app = QApplication([])

    game_server = Pyro5.api.Proxy("PYRO:MorraCinese.game@localhost:55894")

    while True:
        player_name, ok = QInputDialog.getText(None, "Player Registration", "Enter player name:")
        if ok and player_name:
            try:
                game_id = game_server.register(player_name)
                break  # Esce dal ciclo se la registrazione e' andata a buon fine
            except ValueError as e:
                # Mostra un messaggio di errore se il nome del giocatore e' gia' stato registrato
                QMessageBox.critical(None, "Registration Error", str(e))
        else:
            print("Player registration cancelled.")
            sys.exit()  # Esce dal programma se il giocatore annulla la registrazione

    print(f"Player name: {player_name}")

    # Ottieni le dimensioni dello schermo
    screen_resolution = QtWidgets.QDesktopWidget().screenGeometry(-1)
    screen_width = screen_resolution.width()
    screen_height = screen_resolution.height()

    # Calcola il range di posizionamento
    x_range = (0, int(screen_width * 0.75))  # fino al 75% della larghezza dello schermo
    y_range = (0, int(screen_height * 0.25))  # fino al 25% dell'altezza dello schermo

    # Genera una posizione random nel range
    position = (random.randint(*x_range), random.randint(*y_range))

    client = GameClient(player_name, game_server, position)
    client.game_id = game_id
    client.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
