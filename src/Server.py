import Pyro5.api
from collections import defaultdict


@Pyro5.api.expose
class GameServer(object):
    def __init__(self):
        """
        Inizializzazione del server del gioco.
        """
        self.players = defaultdict(list)  # Tiene traccia dei giocatori per ogni partita
        self.moves = defaultdict(dict)  # Tiene traccia delle mosse per ogni partita
        self.results = defaultdict(dict)  # Tiene traccia dei risultati per ogni partita
        self.scores = defaultdict(int)  # Tiene traccia dei punteggi per ogni giocatore
        self.rematch_requests = defaultdict(set)  # Tiene traccia delle richieste di rematch per ogni partita
        self.rematch_status = {}  # Tiene traccia dello stato di rematch per ogni partita
        self.game_count = 0

    def register(self, name):
        """
        Registra un giocatore nel gioco e assegna un identificatore di partita.

        Args:
            name (str): Il nome del giocatore.

        Returns:
            int: L'identificatore di partita assegnato al giocatore.

        Raises:
            ValueError: Se il giocatore è già registrato nella partita corrente.
        """
        if name in self.players[self.game_count]:
            raise ValueError(
                f"Player {name} has already registered for the current game. Please choose a different name.")

        if self.game_count in self.players and len(self.players[self.game_count]) < 2:
            self.players[self.game_count].append(name)
            self.moves[self.game_count][name] = None
        else:
            self.game_count += 1
            self.players[self.game_count].append(name)
            self.moves[self.game_count][name] = None

        print(f"Partita {self.game_count} - Benvenuto {name} e buona partita")
        print("moves: ", self.moves[self.game_count])
        return self.game_count

    def make_choice(self, game_id, player, choice):
        """
        Registra la scelta di una mossa effettuata da un giocatore nella partita corrente.

        Args:
            game_id (int): L'identificatore di partita.
            player (str): Il nome del giocatore.
            choice (str): La mossa scelta dal giocatore.

        Returns:
            bool: True se la mossa di entrambi i giocatori è stata registrata e viene determinato il vincitore,
                  False altrimenti.
        """
        if game_id in self.players and player in self.players[game_id]:
            self.moves[game_id][player] = choice
            print(f"{player} ha scelto: {choice}")

            if len(self.moves[game_id]) == 2 and None not in self.moves[game_id].values():
                return self.determine_winner(game_id)
        return None

    def determine_winner(self, game_id):
        """
        Determina il vincitore della partita in base alle mosse dei giocatori.

        Args:
            game_id (int): L'identificatore di partita.

        Returns:
            bool: True se la partita è stata determinata correttamente, False altrimenti.
        """
        print(f"Partita {game_id} - Determining winner")
        print(len(self.moves[game_id]))
        print(self.moves[game_id])
        if game_id in self.moves and len(self.moves[game_id]) == 2:
            self.rematch_status[game_id] = None  # Resetta il rematch status per questo game_id
            print(f"Partita {game_id} - Determining winner")
            print(f'mosse: {self.moves[game_id]}')
            move_1, move_2 = self.moves[game_id].values()
            del self.moves[game_id]  # Resetta le mosse per questo game_id
            if move_1 == move_2:
                print("Draw")
                self.results[game_id][self.players[game_id][0]] = "Draw"
                self.results[game_id][self.players[game_id][1]] = "Draw"
            elif (move_1, move_2) in [("scissors", "rock"), ("paper", "scissors"), ("rock", "paper")]:
                print('player 1 wins')
                print(f"{self.players[game_id][1]} wins")
                self.results[game_id][self.players[game_id][0]] = "Loser"
                self.results[game_id][self.players[game_id][1]] = "Winner"
                self.scores[self.players[game_id][1]] += 1  # Aumenta il punteggio del vincitore
            else:
                print('player 0 wins')
                print(f"{self.players[game_id][0]} wins")
                self.results[game_id][self.players[game_id][0]] = "Winner"
                self.results[game_id][self.players[game_id][1]] = "Loser"
                self.scores[self.players[game_id][0]] += 1  # Aumenta il punteggio del vincitore

        return True

    def get_game_state(self, game_id, player):
        """
        Ottiene lo stato attuale della partita per un giocatore specifico.

        Args:
            game_id (int): L'identificatore di partita.
            player (str): Il nome del giocatore.

        Returns:
            str or None: Lo stato attuale della partita ("Winner", "Loser", "Draw") se disponibile, None altrimenti.
        """
        if game_id in self.results and player in self.results[game_id]:
            return self.results[game_id][player]
        return None

    def reset_rematch_status(self, game_id):
        """
        Resetta lo stato di rematch per una partita specifica.

        Args:
            game_id (int): L'identificatore di partita.

        Returns:
            bool: True se lo stato di rematch è stato resettato con successo, False altrimenti.
        """
        if game_id in self.rematch_status:
            return True
        return False

    def rematch(self, game_id, player_name):
        """
        Gestisce la richiesta di rematch da parte di un giocatore.

        Args:
            game_id (int): L'identificatore di partita.
            player_name (str): Il nome del giocatore che richiede il rematch.

        Returns:
            bool: True se il rematch è stato richiesto con successo, False altrimenti.
        """
        if game_id in self.players:
            self.rematch_requests[game_id].add(player_name)

            # Se entrambi i giocatori hanno richiesto il rematch, setta il rematch status e resetta lo stato del gioco
            if len(self.rematch_requests[game_id]) == len(self.players[game_id]):
                print(f"Partita {game_id} - Rematch accepted")
                self.rematch_status[game_id] = "REMATCH"
                self.rematch_requests[game_id].clear()

                self.moves[game_id][self.players[game_id][0]] = None
                self.moves[game_id][self.players[game_id][1]] = None
                self.results[game_id] = {}  # Cancella i risultati della partita
                return True

        return False

    def get_rematch_status(self, game_id):
        """
        Ottiene lo stato di rematch per una partita specifica.

        Args:
            game_id (int): L'identificatore di partita.

        Returns:
            str or None: Lo stato di rematch ("REMATCH") se disponibile, None altrimenti.
        """
        if game_id in self.rematch_status:
            return self.rematch_status[game_id]
        else:
            return None

    def get_score(self, player_name):
        """
        Ottiene il punteggio attuale di un giocatore specifico.

        Args:
            player_name (str): Il nome del giocatore.

        Returns:
            int: Il punteggio attuale del giocatore.
        """
        return self.scores[player_name]


def main():
    """
    Funzione principale per avviare il server del gioco.
    """
    daemon = Pyro5.api.Daemon()

    game_server = GameServer()  # Create una singola istanza del server

    Pyro5.api.Daemon.serveSimple(
        {
            game_server: "MorraCinese.game"
        },
        port=55894,
        ns=False)

    daemon.requestLoop()


if __name__ == "__main__":
    main()
