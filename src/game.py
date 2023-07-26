from collections import defaultdict

from enums import Move, Result, MatchStatus

BEST_OF_FIVE = 5


class Game:
    """
    This class encapsulates the logic of the game. It manages players, their moves, scores and the results.
    It also controls the state of the match and processes rematch requests. The game can be part of a series,
    where the winner is determined by the "best of five" rule.

    Attributes:
        game_id (int): Unique identifier for the game.
        players (list): List of players in the game.
        moves (dict): Dictionary storing players' moves.
        results (dict): Dictionary storing match results for each player.
        scores (dict): Dictionary storing players' scores.
        rematch_counter (int): Counter for how many players have requested a rematch.
        game_series (int): Number of games played in the series.
        winner (str): The winner of the game. Initially, this is set to None.
        match_status (MatchStatus): The status of the match (ongoing, over, series over, rematch, none).
        ready_to_play_again (int): Counter for how many players are ready to play again.

    Note:
        In a game series, a player must win three out of five games (best of five) to be declared the series winner.
    """
    def __init__(self):
        """
        Initializes the game.
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
        Registers a player to the game.

        Args:
            player_name (str): Name of the player to be registered.

        Raises:
            ValueError: If a player with the same name already exists or the game is full.

        Returns:
            bool: True if the player was successfully registered, False otherwise.
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
        Registers a player's move in the game.

        Args:
            player_name (str): Name of the player.
            choice (str): Player's move.

        Notes:
            The game state and series status are updated based on the moves. The winner is determined if all players made their moves.
        """
        # print player_name, choice and self.moves.values()
        print(f'player_name: {player_name}, choice: {choice}')
        print(f'players: {self.players}')
        print(f'moves: {self.moves}')

        if all(move is None for move in self.moves.values()):
            # print("(None, None) in self.moves.values()")
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
        Determines the winner of the game based on the players' moves.

        Notes:
            The results, scores, and winner of the game are updated based on the comparison of the moves.
        """

        # print(f'Determining winner...')

        move_1, move_2 = self.moves.values()

        # print(f'Move 1: {move_1} - Move 2: {move_2}')

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
        Resets the state of the game after a single match.

        Args:
            player_name (str): Name of the player.

        Notes:
            The game's status is updated to ongoing if all players are ready to play again.
        """

        self.ready_to_play_again += 1
        self.moves[player_name] = None
        self.results[player_name] = None

        if self.ready_to_play_again == 2:
            self.match_status = MatchStatus.ONGOING
            self.ready_to_play_again = 0

    def get_game_state(self, player_name):
        """
        Gets the current state of the game for a specific player.

        Args:
            player_name (str): Name of the player.

        Returns:
            str or None: Current state of the game ("Winner", "Loser", "Draw") if available, None otherwise.
        """
        return self.results[player_name]

    def request_rematch(self, player_name):
        """
        Handles a player's rematch request.

        Args:
            player_name (str): Name of the player requesting a rematch.

        Notes:
            The game's status is updated to rematch if both players request a rematch.
        """

        self.rematch_counter += 1
        print(f'{player_name} ha richiesto un rematch.')
        self.moves[player_name] = None
        self.results[player_name] = None
        self.scores[player_name] = 0

        if self.rematch_counter == 2:
            print(f'Entrambi i giocatori hanno richiesto un rematch.')
            print(f'Inizio una nuova partita.')
            # print('Mosse resettate: ', self.moves)
            self.match_status = MatchStatus.REMATCH
            self.rematch_counter = 0
            self.winner = None

    def request_new_match(self, player_name):
        """
        Handles a player's request to start a new match.

        Args:
            player_name (str): Name of the player requesting a new match.

        Notes:
            The game's status is updated to none.
        """
        self.moves[player_name] = None
        self.moves.pop(player_name)
        self.results[player_name] = None
        self.scores.pop(player_name)
        self.scores[player_name] = 0
        self.results.pop(player_name)

        self.players.remove(player_name)
        self.winner = None
        self.match_status = MatchStatus.NONE

    def reset_after_left(self, player_name):
        """
        Resets the game state after a player has left.

        Args:
            player_name (str): Name of the player who left.
        """
        self.moves[player_name] = None
        self.results[player_name] = None
        self.scores[player_name] = 0
        self.winner = None

    def get_score(self, player_name):
        """
        Gets a player's score.

        Args:
            player_name (str): Name of the player.

        Returns:
            int: The player's score.
        """
        return self.scores[player_name]

    def get_player_state(self, player_name):
        """
        Gets a player's state.

        Args:
            player_name (str): Name of the player.

        Returns:
            str or None: Current state of the player ("Winner", "Loser", "Draw") if available, None otherwise.
        """
        return self.results[player_name]

    def determine_series_winner(self):
        """
        Determines the winner of the series.

        Notes:
            The winner is determined based on the comparison of the scores.
        """

        if self.scores[self.players[0]] == self.scores[self.players[1]]:
            self.winner = "Draw"
        elif self.scores[self.players[0]] > self.scores[self.players[1]]:
            self.winner = self.players[0]
        else:
            self.winner = self.players[1]

        print(f'Winner of the series: {self.winner}')

    def get_match_status(self):
        """
        Gets the current status of the match.

        Returns:
            MatchStatus: The current status of the match.
        """
        return self.match_status

    def get_winner_of_series(self):
        """
        Gets the winner of the series.

        Returns:
            str: The winner of the series.
        """
        return self.winner

    def get_num_of_match(self):
        """
        Gets the number of matches played in the series.

        Returns:
            int: The number of matches played in the series.
        """
        return self.game_series

    def get_opponent_name(self, player_name):
        """
        Gets the name of the opponent.

        Args:
            player_name (str): Name of the player.

        Returns:
            str or None: The name of the opponent if available, None otherwise.
        """
        if len(self.players) == 1:
            return None
        else:
            if player_name == self.players[0]:
                return self.players[1]
            elif player_name == self.players[1]:
                return self.players[0]



    def remove_player(self, player_name):
        """
        Removes a player from the game.

        Args:
            player_name (str): Name of the player to be removed.

        Notes:
            The game's status is updated to left. If the game has no winner, the remaining player is set as the winner.
        """
        self.players.remove(player_name)
        self.moves.pop(player_name)
        self.results.pop(player_name)
        self.scores.pop(player_name)
        self.match_status = MatchStatus.LEFT
        for player in self.players:
            if player != player_name:
                if self.winner is None:
                    self.winner = player

        print(f'player {player_name} ha abbandonato la partita.')

