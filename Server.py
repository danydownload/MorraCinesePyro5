import Pyro5.api
from collections import defaultdict

@Pyro5.api.expose
class GameServer(object):
    def __init__(self):
        self.players = defaultdict(list)  # keep track of players for each game
        self.moves = defaultdict(dict)  # keep track of moves for each game
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
        return None

    def determine_winner(self, game_id):
        if game_id in self.moves and len(self.moves[game_id]) == 2:
            move_1, move_2 = self.moves[game_id].values()
            if move_1 == move_2:
                return "Draw"
            elif (move_1, move_2) in [("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")]:
                return list(self.moves[game_id].keys())[0]  # return the name of the player who made the first move
            else:
                return list(self.moves[game_id].keys())[1]  # return the name of the player who made the second move
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
