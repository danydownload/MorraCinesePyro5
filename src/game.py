from collections import defaultdict

from enums import Move, Result, MatchStatus

BEST_OF_FIVE = 3


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
        self.game_series = 1  # Numero di partite giocate nella serie
        self.winner = None  # Vincitore della partita
        self.match_status = MatchStatus.NONE  # Stato del match
        self.ready_to_play_again = 0  # Flag per indicare se i giocatori sono pronti a giocare di nuovo

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
        #print player_name, choice and self.moves.values()
        print(f'player_name: {player_name}, choice: {choice}')
        print(f'players: {self.players}')
        print(f'moves: {self.moves}')

        if all(move is None for move in self.moves.values()):
            #print("(None, None) in self.moves.values()")
            self.match_status = MatchStatus.ONGOING

        if player_name in self.players and self.moves[player_name] is None:
            self.moves[player_name] = choice
            print(f'{player_name} ha scelto {choice}.')
            if len(self.moves) == 2 and None not in self.moves.values():

                self.determine_winner()

                if self.game_series == BEST_OF_FIVE or abs(
                        self.scores[self.players[0]] - self.scores[self.players[1]]) > BEST_OF_FIVE - self.game_series:
                    self.determine_series_winner()
                    self.match_status = MatchStatus.SERIES_OVER
                    self.game_series = 1
                else:
                    self.game_series += 1
                    self.match_status = MatchStatus.OVER

            # print(f'all moves: {self.moves}')

    def determine_winner(self):
        """
        Determina il vincitore della partita in base alle mosse dei giocatori.
        """

        #print(f'Determining winner...')

        move_1, move_2 = self.moves.values()

        #print(f'Move 1: {move_1} - Move 2: {move_2}')

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

    def reset_state_after_single_match(self, player_name):
        """
        Resetta lo stato della partita dopo una singola partita.
        """


        self.ready_to_play_again += 1
        self.moves[player_name] = None
        self.results[player_name] = None

        if self.ready_to_play_again == 2:
            self.match_status = MatchStatus.ONGOING
            self.ready_to_play_again = 0

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
        self.scores[player_name] = 0

        if self.rematch_counter == 2:
            print(f'Entrambi i giocatori hanno richiesto un rematch.')
            print(f'Inizio una nuova partita.')
            #print('Mosse resettate: ', self.moves)
            self.match_status = MatchStatus.REMATCH
            self.rematch_counter = 0
            self.winner = None


    def request_new_match(self, player_name):
        self.moves[player_name] = None
        self.moves.pop(player_name)
        self.results[player_name] = None
        self.scores.pop(player_name)
        self.scores[player_name] = 0
        self.results.pop(player_name)

        self.players.remove(player_name)
        self.winner = None
        self.match_status = MatchStatus.NONE



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

    def determine_series_winner(self):
        # check the winner of the series
        if self.scores[self.players[0]] == self.scores[self.players[1]]:
            self.winner = "Draw"
        elif self.scores[self.players[0]] > self.scores[self.players[1]]:
            self.winner = self.players[0]
        else:
            self.winner = self.players[1]

        print(f'Winner of the series: {self.winner}')

    def get_match_status(self):
        return self.match_status

    def get_winner_of_series(self):
        return self.winner

    def get_num_of_match(self):
        return self.game_series

