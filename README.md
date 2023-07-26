# Rock-Paper-Scissors Game

This project is a Python-based implementation of the classic game, Rock-Paper-Scissors with a graphical user interface. Players can compete against each other in a series of matches with the final winner being the player who wins the best of five games. The game can be played in a distributed system using Pyro5 for remote method invocation.

## Features

- Support for multiple rounds within a single game series.
- Player's choices and scores are stored and managed for each round.
- The game supports rematch functionality.
- The game keeps track of the overall series winner.
- Exception handling to manage already registered players and full game scenarios.
- GUI for easier interaction and better user experience.
- Pyro5 is used to support remote method invocation for a distributed system environment.

## How to Use

The game is implemented as a `Game` class and `GameClient` class, where each instance represents a separate game or match series. You can use the following methods to interact with the game:

- `register_player(player_name)`: To register a new player to the game.
- `make_choice(player_name, choice)`: To make a choice for a player. Choice must be one of 'rock', 'paper', or 'scissors'.
- `get_game_state(player_name)`: To get the current state of a player within a game.
- `request_rematch(player_name)`: To request a rematch by a player.
- `request_new_match(player_name)`: To request a new match by a player.
- `get_score(player_name)`: To get the current score of a player.
- `get_player_state(player_name)`: To get the current state of a player within a game.
- `get_match_status()`: To get the current status of the match.
- `get_winner_of_series()`: To get the winner of the series.
- `get_num_of_match()`: To get the number of matches played in the series.
- `get_opponent_name(player_name)`: To get the name of the opponent for a given player.
- `remove_player(player_name)`: To remove a player from the game.

## Requirements

- Python 3.x
- Python's built-in `collections` library
- PyQt6 for the GUI
- Pyro5 for remote method invocation

## Installation

```bash
pip install pyqt6 pyro5
