import Pyro5.api
from collections import defaultdict

@Pyro5.api.expose
class GameServer(object):
    def __init__(self):
        self.players = defaultdict(list)  # keep track of players for each game
        self.moves = defaultdict(dict)  # keep track of moves for each game
        self.results = defaultdict(dict)  # keep track of results for each game
        self.game_count = 0

    def register(self, name):
        if self.game_count in self.players and len(self.players[self.game_count]) < 2:
            self.players[self.game_count].append(name)
        else:
            self.game_count += 1
            self.players[self.game_count].append(name)
        print(f"Partita {self.game_count} - Benvenuto {name} e buona partita")
        return self.game_count

    def make_choice(self, game_id, player, choice):
        if game_id in self.players and player in self.players[game_id]:
            self.moves[game_id][player] = choice
            print(f"{player} ha scelto: {choice}")
            if len(self.moves[game_id]) == 2:
                return self.determine_winner(game_id)
            elif len(self.moves[game_id]) == 1:
                return "Waiting for the other player to make a move."
        return None

    def determine_winner(self, game_id):
        print(f"Partita {game_id} - Determining winner")
        print(len(self.moves[game_id]))
        print(self.moves[game_id])
        if game_id in self.moves and len(self.moves[game_id]) == 2:
            print(f"Partita {game_id} - Determining winner")
            move_1, move_2 = self.moves[game_id].values()
            del self.moves[game_id]  # Reset the moves for this game_id
            if move_1 == move_2:
                print("Draw")
                self.results[game_id][self.players[game_id][0]] = "Draw"
                self.results[game_id][self.players[game_id][1]] = "Draw"
                return "Draw"
            elif (move_1, move_2) in [("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")]:
                print(f"{self.players[game_id][0]} wins")
                self.results[game_id][self.players[game_id][0]] = "Winner"
                self.results[game_id][self.players[game_id][1]] = "Loser"
                return self.players[game_id][0]  # return the name of the winner
            else:
                print(f"{self.players[game_id][1]} wins")
                self.results[game_id][self.players[game_id][0]] = "Loser"
                self.results[game_id][self.players[game_id][1]] = "Winner"
                return self.players[game_id][1]  # return the name of the winner
        return False

    def get_state(self, game_id, player):
        if game_id in self.results and player in self.results[game_id]:
            return self.results[game_id][player]
        return None

    def rematch(self, game_id):
        if game_id in self.players:
            self.moves[game_id] = {}
            self.results[game_id] = {}
            return True
        return False


def main():
    daemon = Pyro5.api.Daemon()

    game_server = GameServer()  # Create a single instance of GameServer

    Pyro5.api.Daemon.serveSimple(
        {
            game_server: "MorraCinese.game"
        },
        port=50693,
        ns=False)

    daemon.requestLoop()


if __name__ == "__main__":
    main()
