# Morra Cinese con Pyro5

Questo progetto implementa una semplice versione di Morra Cinese (Rock, Paper, Scissors) utilizzando Pyro5 per la comunicazione tra client e server. Il progetto è costituito da due file principali: `server.py` e `client.py`.

## Funzionalità del Codice

### Server.py
Il server gestisce l'intero stato del gioco. Le funzionalità principali includono:

- Gestione delle partite, dei giocatori, delle mosse, dei risultati e delle richieste di rematch.
- Mantenimento dello storico dei punteggi dei giocatori.

#### Metodi Principali

- `register(name)`: Registra un nuovo giocatore per una partita.
- `make_choice(game_id, player, choice)`: Consente a un giocatore di fare una mossa.
- `determine_winner(game_id)`: Determina il vincitore di una partita.
- `get_game_state(game_id, player)`: Ritorna lo stato attuale della partita per un determinato giocatore.
- `rematch(game_id, player_name)`: Gestisce le richieste di rematch.
- `get_rematch_status(game_id)`: Ritorna lo stato attuale della richiesta di rematch.
- `get_score(player_name)`: Ritorna il punteggio attuale di un giocatore.

### Client.py
Il client crea un'interfaccia utente per il gioco, permettendo ai giocatori di interagire con il server.

#### Funzionalità Principali

- Permette ai giocatori di fare una mossa e mostra il risultato della partita.
- Permette ai giocatori di richiedere un rematch alla fine di una partita.
- Mostra lo stato attuale della partita e il punteggio dei giocatori.

## Installazione e Utilizzo

1. Assicurati di avere installato Python e Pyro5 sul tuo computer.
2. Clona o scarica questo repository.
3. Esegui `server.py` per avviare il server di gioco.
4. Esegui `client.py` per ogni giocatore che vuole unirsi al gioco.
5. Segui le istruzioni visualizzate sull'interfaccia del client per giocare.

## Dipendenze

- Python 3.8+
- Pyro5
- PyQt5

Nota: Assicurati di installare tutte le dipendenze prima di eseguire il codice. Puoi installare le dipendenze con il seguente comando:

```shell
pip install pyro5 pyqt5
```

## Struttura del Codice

### Server.py
```python
import Pyro5.api

@Pyro5.api.expose
class GameServer(object):
    def __init__(self):
        # Initialize game state

    def register(self, name):
        # Register a new player for a game

    def make_choice(self, game_id, player, choice):
        # Allow a player to make a move

    def determine_winner(self, game_id):
        # Determine the winner of a game

    def get_game_state(self, game_id, player):
        # Return the current state of the game for a certain player

    def rematch(self, game_id, player_name):
        # Handle rematch requests

    def get_rematch_status(self, game_id):
        # Return the current state of the rematch request

    def get_score(self, player_name):
        # Return the current score of a player
```

### Client.py
```python
import Pyro5.api

class GameClient(object):
    def __init__(self):
        # Initialize client state

    def make_choice(self):
        # Let the player make a move

    def request_rematch(self):
        # Let the player request a rematch

    def get_game_state(self):
        # Show the current state of the game

    def get_score(self):
        # Show the current score of the player
```

