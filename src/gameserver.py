import Pyro5.api
from collections import defaultdict
from game import Game
from enums import Move, Result, MatchStatus


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
        Aggiunge un giocatore a un game disponibile o crea un nuovo game.

        Args:
            player_name (str): Il nome del giocatore.
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
        Registra un giocatore nella partita specificata.

        Args:
            game_id (int): L'identificatore della partita.
            player_name (str): Il nome del giocatore.

        """
        if player_name in self.players_game:
            raise ValueError(f'È già presente un giocatore con il nome {player_name}. Perfavore scegli un altro nome.')

        self.players_score[player_name] = 0

        self.add_player_to_game(player_name)

    def find_available_game(self, player_name, old_match_id=None):
        """
        Trova una partita disponibile (con un solo giocatore registrato).

        Returns:
            Game or None: L'oggetto Game della partita disponibile se presente, None altrimenti.
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

        # controlla che in partita ci siano due giocatori, se no ritorna NONE
        if len(game.players) != 2:
            return None
        else:
            return game.request_rematch(player_name)

    def new_match(self, player_name):
        """
        Gestisce la richiesta di rematch da parte di un giocatore.

        Args:
            player_name (str): Il nome del giocatore che richiede il rematch.

        Returns:
            bool: True se il rematch è stato richiesto con successo, False altrimenti.
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

        print(f"game_winner: {game_winner}")

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

    def get_opponent_name(self, player_name):
        """
        Ottiene il nome dell'avversario.
        """
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.get_opponent_name(player_name)

    def unregister_player(self, player_name):
        """
        Cancella un giocatore dalla partita.

        Args:
            player_name (str): Il nome del giocatore.
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
        game_id = self.players_game[player_name]
        game = self.games[str(game_id)]
        return game.reset_after_left(player_name)


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
