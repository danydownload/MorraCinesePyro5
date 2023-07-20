import Pyro5.api
from collections import defaultdict
from game import Game


@Pyro5.api.expose
class GameServer(object):
    def __init__(self):
        """
        Inizializzazione del server del gioco.
        """
        self.games = defaultdict(Game)  # Dizionario per tenere traccia delle partite
        self.players_game = defaultdict(
            int)  # Dizionario per tenere traccia dei giocatori e delle partite a cui sono registrati
        self.players_score = defaultdict(int)  # Dizionario per tenere traccia dei punteggi dei giocatori

    def create_game(self):
        """
        Crea una nuova partita e restituisce il suo identificatore.

        Returns:
            int: L'identificatore della nuova partita.
        """
        game_id = len(self.games) + 1
        game = Game()
        self.games[str(game_id)] = game
        game.game_id = game_id

        print(f'Nuova partita creata con id {game_id}')
        print(f'Partite attive: {self.games}')

        return game

    def register_player(self, player_name):
        """
        Registra un giocatore nella partita specificata.

        Args:
            game_id (int): L'identificatore della partita.
            player_name (str): Il nome del giocatore.

        Returns:
            bool: True se il giocatore è stato registrato con successo, False altrimenti.
        """
        if player_name in self.players_game:
            raise ValueError(f'È già presente un giocatore con il nome {player_name}. Perfavore scegli un altro nome.')

        self.players_score[player_name] = 0

        game = self.find_available_game()
        if game is None:
            new_game = self.create_game()
            new_game.players.append(player_name)
            new_game.scores[player_name] = 0
            new_game.moves[player_name] = None
            self.players_game[player_name] = new_game.game_id
        else:
            # se la partita è disponibile allora registro il giocatore (1 giocatore già registrato)
            game.players.append(player_name)
            game.scores[player_name] = 0
            game.moves[player_name] = None
            self.players_game[player_name] = game.game_id

        # Stampa i dizionari per scopi di debugging
        print(f'players_game: {self.players_game}')
        print(f'games: {self.games}')

    def find_available_game(self):
        """
        Trova una partita disponibile (con un solo giocatore registrato).

        Returns:
            Game or None: L'oggetto Game della partita disponibile se presente, None altrimenti.
        """
        for game_id, game in self.games.items():
            if len(game.players) == 1:
                return game
        return None

    def make_choice(self, player_name, choice):
        """
        Registra la scelta di una mossa effettuata da un giocatore nella partita corrente.

        Args:
            player_name (str): Il nome del giocatore.
            choice (str): La mossa scelta dal giocatore.

        Returns:
            bool: True se la mossa di entrambi i giocatori è stata registrata e viene determinato il vincitore,
                  False altrimenti.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        game.make_choice(player_name, choice)

    def get_game_state(self, player_name):
        """
        Ottiene lo stato attuale della partita per un giocatore specifico.

        Args:
            player_name (str): Il nome del giocatore.

        Returns:
            str or None: Lo stato attuale della partita ("Winner", "Loser", "Draw") se disponibile, None altrimenti.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.get_player_state(player_name)

    def rematch(self, player_name):
        """
        Gestisce la richiesta di rematch da parte di un giocatore.

        Args:
            player_name (str): Il nome del giocatore che richiede il rematch.

        Returns:
            bool: True se il rematch è stato richiesto con successo, False altrimenti.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.request_rematch(player_name)

    def get_match_status(self, player_name):
        """
        Ottiene lo stato di rematch per una partita specifica.

        Args:
            player_name (str): Il nome del giocatore.

        Returns:
            str or None: Lo stato di rematch ("REMATCH") se disponibile, None altrimenti.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.get_match_status()

    def get_score(self, player_name):
        """
        Ottiene il punteggio attuale di un giocatore specifico.

        Args:
            player_name (str): Il nome del giocatore.

        Returns:
            int: Il punteggio attuale del giocatore.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.get_score(player_name)

    def get_game(self, player_name):
        return self.games[str(self.players_game[player_name])]

    def reset_state_after_single_match(self, player_name):
        """
        Resetta lo stato del gioco dopo una partita singola.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.reset_state_after_single_match(player_name)

    def get_winner_of_series(self, player_name):
        """
        Ottiene il vincitore della serie di partite.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        # return game.get_winner_of_series()
        return game.get_winner_of_series()

    def update_general_score(self, player_name):
        """
        Aggiorna il punteggio generale del giocatore.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        game_winner = game.get_winner_of_series()

        if game_winner == player_name:
            self.players_score[player_name] += 1

    def get_general_score(self, player_name):
        """
        Ottiene il punteggio generale del giocatore.
        """
        return self.players_score[player_name]

    def get_num_of_match(self, player_name):
        """
        Ottiene il numero di partita in corso della serie.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.get_num_of_match()

def main():
    """
    Funzione principale per avviare il server del gioco.
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
