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

## Requirements

- Python 3.x
- Python's built-in `collections` library
- PyQt6 for the GUI
- Pyro5 for remote method invocation

## Installation

```bash
pip install pyqt6 pyro5
```

## Documentation

To build the javadoc documentation:

```bash
pip install sphinx sphinx_rtd_theme
cd docs
make html
```


