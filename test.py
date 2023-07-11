import Pyro5.api
import threading
import random

@Pyro5.api.expose
class Client(object):
    def __init__(self):
        self.server = Pyro5.api.Proxy("PYRO:MorraCinese.game@localhost:50693")
        self.player_name = None
        self.game_id = None

    def notify_winner(self, winner):
        print(f"The winner is: {winner}")

    def register(self, player_name):
        self.player_name = player_name
        daemon = Pyro5.api.Daemon()
        uri = daemon.register(self)
        self.game_id = self.server.register(player_name, uri)

        threading.Thread(target=daemon.requestLoop).start()

    def make_choice(self, choice):
        try:
            response = self.server.make_choice(self.game_id, self.player_name, choice)
            print(response)
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    client = Client()
    client.register("player1"+str(random.randint(0, 100)))
    client.make_choice("rock")

if __name__ == "__main__":
    main()
