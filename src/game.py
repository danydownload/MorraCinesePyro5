from collections import defaultdict
from enums import Move, Result, MatchStatus

BEST_OF_FIVE = 5


class Game:
    def __init__(self):
        """
        Inizializzazione del gioco.
        """
        self.game_id = 0  # Identificatore della partita
        self.players = []  # Elenco dei giocatori nella partita
        self.moves = defaultdict(lambda: None)  # Mosse effettuate dai giocatori
        self.results = defaultdict(lambda: None)  # Risultati della partita
        self.scores = defaultdict(int)  # Punteggi dei giocatori
        self.rematch_counter = 0  # Flag per indicare se è stata richiesta una rematch
        self.game_series = 0  # Numero di partite giocate nella serie
        self.winner = None  # Vincitore della partita
        self.match_status = MatchStatus.ONGOING  # Stato del match

    def register_player(self, player_name):
        """
        Registra un giocatore nella partita.

        Args:
            player_name (str): Il nome del giocatore.

        Returns:
            bool: True se il giocatore è stato registrato con successo, False altrimenti.
        """

        # controllo se il giocatore è già registrato e se si ritorno errore. Il nome del giocatore è univoco
        if player_name in self.players:
            raise ValueError(
                f'E\' già presente un giocatore con il nome {player_name}. Perfavore scegli un altro nome.')

        if len(self.players) < 2 and player_name not in self.players:
            self.players.append(player_name)
            self.moves[player_name] = None
            return True
        else:
            raise ValueError(f'La partita è già al completo. Non è possibile aggiungere un nuovo giocatore.')

    def make_choice(self, player_name, choice):
        """
        Registra la scelta di una mossa effettuata da un giocatore nella partita.

        Args:
            player_name (str): Il nome del giocatore.
            choice (str): La mossa scelta dal giocatore.

        Returns:
            bool: True se la mossa è stata registrata con successo, False altrimenti.
        """
        print('self.moves: ', self.moves.values())
        if all(move is None for move in self.moves.values()):
            print("(None, None) in self.moves.values()")
            self.match_status = MatchStatus.ONGOING

        if player_name in self.players and self.moves[player_name] is None:
            self.moves[player_name] = choice
            if len(self.moves) == 2 and None not in self.moves.values():
                if self.game_series == BEST_OF_FIVE:
                    self.determine_series_winner()
                else:
                    self.determine_winner()
                    self.game_series += 1

            print(f'\nall moves: {self.moves}')

    def determine_winner(self):
        """
        Determina il vincitore della partita in base alle mosse dei giocatori.
        """
        move_1, move_2 = self.moves.values()
        if move_1 == move_2:
            self.results[self.players[0]] = "Draw"
            self.results[self.players[1]] = "Draw"
        elif (move_1, move_2) in [("scissors", "rock"), ("paper", "scissors"), ("rock", "paper")]:
            self.results[self.players[0]] = "Loser"
            self.results[self.players[1]] = "Winner"
            self.scores[self.players[1]] += 1
        else:
            self.results[self.players[0]] = "Winner"
            self.results[self.players[1]] = "Loser"
            self.scores[self.players[0]] += 1

    def get_game_state(self, player_name):
        """
        Ottiene lo stato attuale della partita per un giocatore specifico.

        Args:
            player_name (str): Il nome del giocatore.

        Returns:
            str or None: Lo stato attuale della partita ("Winner", "Loser", "Draw") se disponibile, None altrimenti.
        """
        return self.results[player_name]

    def request_rematch(self, player_name):
        """
        Gestisce la richiesta di rematch da parte di un giocatore.

        Args:
            player_name (str): Il nome del giocatore che richiede il rematch.

        Returns:
            bool: True se la richiesta di rematch è stata effettuata con successo, False altrimenti.
        """

        self.rematch_counter += 1
        print(f'{player_name} ha richiesto un rematch.')
        self.moves[player_name] = None
        self.results[player_name] = None

        if self.rematch_counter == 2:
            print(f'Entrambi i giocatori hanno richiesto un rematch.')
            print(f'Inizio una nuova partita.')
            print('Mosse resettate: ', self.moves)
            self.match_status = MatchStatus.REMATCH
            self.rematch_counter = 0

    def get_score(self, player_name):
        """
        Ottiene il punteggio di un giocatore.

        Args:
            player_name (str): Il nome del giocatore.

        Returns:
            int: Il punteggio del giocatore.
        """
        return self.scores[player_name]

    def get_player_state(self, player_name):
        return self.results[player_name]

    # TODO: considerare il rematch
    def is_game_over(self):
        if self.game_series == BEST_OF_FIVE:
            return True
        return False

    def determine_series_winner(self):
        # check the winner of the series
        if self.scores[self.players[0]] == self.scores[self.players[1]]:
            self.winner = "Draw"
        elif self.scores[self.players[0]] > self.scores[self.players[1]]:
            self.winner = self.players[0]
        else:
            self.winner = self.players[1]

    def get_match_status(self):
        return self.match_status

