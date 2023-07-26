import Pyro5.api
from collections import defaultdict
from game import Game
from enums import Move, Result, MatchStatus


@Pyro5.api.expose
class GameServer(object):
    """
    The main class for managing games on the server.
    Handles game creation, player registration, player choices, game state, etc.

    Attributes:
        games (defaultdict(Game)): A dictionary to track ongoing games.
        players_game (defaultdict(int)): A dictionary to track players and their corresponding games.
        players_score (defaultdict(int)): A dictionary to track scores of the players.
    """

    def __init__(self):
        """
        Initialize a new instance of the GameServer.
        """
        self.games = defaultdict(Game)  # Dizionario per tenere traccia delle partite
        self.players_game = defaultdict(
            int)  # Dizionario per tenere traccia dei giocatori e delle partite a cui sono registrati
        self.players_score = defaultdict(int)  # Dizionario per tenere traccia dei punteggi dei giocatori

    def create_game(self):
        """
        Create a new game and return its identifier.

        Returns:
            int: The identifier of the new game.
        """
        # Crea una partita con un game_id che non e' già presente nel dizionario self.games
        game_id = 1
        while str(game_id) in self.games:
            game_id += 1

        game = Game()
        self.games[str(game_id)] = game
        game.game_id = game_id

        print(f'Nuova partita creata con id {game_id}')
        print(f'Partite attive: {self.games}')

        return game

    def add_player_to_game(self, player_name, old_match_id=None):
        """
        Add a player to an available game or create a new game.

        Args:
            player_name (str): The name of the player.
            old_match_id (int, optional): The identifier of the old match, if any. Defaults to None.
        """
        game = self.find_available_game(player_name, old_match_id)

        if game is None:
            new_game = self.create_game()
            new_game.players.append(player_name)
            new_game.scores[player_name] = 0
            new_game.moves[player_name] = None
            self.players_game[player_name] = new_game.game_id
            print(f"Giocatore {player_name} inserito in un nuovo game.")
        else:
            game.players.append(player_name)
            game.scores[player_name] = 0
            game.moves[player_name] = None
            self.players_game[player_name] = game.game_id
            print(f"Giocatore {player_name} inserito in un game disponibile.")
            game.match_status = MatchStatus.ONGOING

        # Stampa i dizionari per scopi di debugging
        self.players_game = {k: v for k, v in sorted(self.players_game.items(), key=lambda item: item[1])}
        print(f"players_game: {self.players_game}")

    def register_player(self, player_name):
        """
        Registers a player to a specified game.

        Args:
            player_name (str): The name of the player.
        """
        if player_name in self.players_game:
            raise ValueError(f'Player with name {player_name} already exists. Please choose another name.')
        self.players_score[player_name] = 0

        self.add_player_to_game(player_name)

    def find_available_game(self, player_name, old_match_id=None):
        """
        Finds an available game (with only one registered player).

        Args:
            player_name (str): The name of the player.
            old_match_id (int, optional): The identifier of the old match, if any. Defaults to None.

        Returns:
            Game or None: The Game object of the available game if present, None otherwise.
        """

        # game_id viene convertito in stringa perche' il dizionario self.games ha come chiavi stringhe
        if old_match_id is not None:
            old_match_id = str(old_match_id)

        for game_id, game in self.games.items():
            if len(game.players) == 1 and player_name not in game.players:
                if old_match_id is not None and game_id == old_match_id:
                    print(f"Partita disponibile trovata: {game_id} ma è la stessa partita di prima.")
                    continue  # Skip the current game if it has the same ID as the old_match_id
                else:
                    print(f'game_id: {game_id}, old_game_id: {old_match_id}')
                    print(f"Nuova partita disponibile trovata: {game_id}")
                    return game
        return None

    def make_choice(self, player_name, choice):
        """
        Registers a player's move choice in the current game.

        Args:
            player_name (str): The name of the player.
            choice (str): The move choice made by the player.

        Returns:
            bool: True if both player's moves have been registered and the winner is determined, False otherwise.
        """

        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        game.make_choice(player_name, choice)

    def get_game_state(self, player_name):
        """
        Gets the current game state for a specific player.

        Args:
            player_name (str): The name of the player.

        Returns:
            str or None: The current game state ("Winner", "Loser", "Draw") if available, None otherwise.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.get_player_state(player_name)

    def rematch(self, player_name):
        """
        Handles a rematch request from a player.

        Args:
            player_name (str): The name of the player requesting the rematch.

        Returns:
            bool: True if the rematch was requested successfully, False otherwise.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]

        # controlla che in partita ci siano due giocatori, se no ritorna NONE
        if len(game.players) != 2:
            return None
        else:
            return game.request_rematch(player_name)

    def new_match(self, player_name):
        """
        Handles a new match request from a player.

        Args:
            player_name (str): The name of the player requesting the new match.
        """

        print(f"Giocatore {player_name} ha richiesto un nuovo match.")

        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        old_match_id = game.game_id
        game.request_new_match(player_name)

        self.add_player_to_game(player_name, old_match_id)

        if len(game.players) == 0:
            del self.games[str(game_id)]
            print(f"Partita {game_id} rimossa.")
            print(f"Partite attive: {self.games}")

        # printa i giocatori e a che partita sono registrati
        # print(f"players_game: {self.players_game}")
        # ordina self.players_game per game_id
        self.players_game = {k: v for k, v in sorted(self.players_game.items(), key=lambda item: item[1])}
        print(f"players_game: {self.players_game}")

        # ora printa il player in questione e a che partita e' registrato
        print(f"player_name: {player_name}, registered to game: {self.players_game[player_name]}")

    def get_match_status(self, player_name):
        """
        Gets the rematch status for a specific game.

        Args:
            player_name (str): The name of the player.

        Returns:
            str or None: The rematch status ("REMATCH") if available, None otherwise.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.get_match_status()

    def get_score(self, player_name):
        """
        Gets the current score of a specific player.

        Args:
            player_name (str): The name of the player.

        Returns:
            int: The current score of the player.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.get_score(player_name)

    def get_game(self, player_name):
        """
         Retrieves the current game of a specific player.

         Args:
             player_name (str): The name of the player.

         Returns:
             Game: The game instance associated with the player.
         """
        return self.games[str(self.players_game[player_name])]

    def reset_state_after_single_match(self, player_name):
        """
        Resets the game state after a single match.

        Args:
            player_name (str): The name of the player.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.reset_state_after_single_match(player_name)

    def get_winner_of_series(self, player_name):
        """
        Gets the winner of the series of games.

        Args:
            player_name (str): The name of the player.

        Returns:
            str: The name of the winning player.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        # return game.get_winner_of_series()
        return game.get_winner_of_series()

    def update_general_score(self, player_name):
        """
        Updates the general score of the player.

        Args:
            player_name (str): The name of the player.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        game_winner = game.get_winner_of_series()

        print(f"game_winner: {game_winner}")

        if game_winner == player_name:
            self.players_score[player_name] += 1

    def get_general_score(self, player_name):
        """
        Gets the general score of the player.

        Args:
            player_name (str): The name of the player.

        Returns:
            int: The general score of the player.
        """
        return self.players_score[player_name]

    def get_num_of_match(self, player_name):
        """
        Gets the number of the ongoing match in the series.

        Args:
            player_name (str): The name of the player.

        Returns:
            int: The number of the ongoing match.
        """

        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.get_num_of_match()

    def get_opponent_name(self, player_name):
        """
        Gets the name of the opponent.

        Args:
            player_name (str): The name of the player.

        Returns:
            str: The name of the opponent player.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.get_opponent_name(player_name)

    def unregister_player(self, player_name):
        """
        Unregisters a player from the game.

        Args:
            player_name (str): The name of the player.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        game.remove_player(player_name)
        del self.players_game[player_name]
        print(f"Giocatore {player_name} rimosso dalla partita.")
        print(f"players_game: {self.players_game}")
        if len(game.players) == 0:  # se nel game non ci sono piu' giocatori, rimuovi il game
            del self.games[str(game_id)]
            print(f"Partita {game_id} rimossa.")
            print(f"Partite attive: {self.games}")

    def reset_after_left(self, player_name):
        """
        Resets the game after a player leaves.

        Args:
            player_name (str): The name of the player.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.reset_after_left(player_name)


def main():
    """
    Main function for the GameServer.
    """
    daemon = Pyro5.api.Daemon()

    game_server = GameServer()  # Creazione di una singola istanza del server

    Pyro5.api.Daemon.serveSimple(
        {
            game_server: "MorraCinese.game"
        },
        port=55894,
        ns=False)

    daemon.requestLoop()


if __name__ == "__main__":
    main()
