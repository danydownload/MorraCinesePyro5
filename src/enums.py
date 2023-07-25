# enums.py

from enum import Enum


# Enum per le mosse
class Move(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


# Enum per i risultati
class Result(Enum):
    WIN = "Winner"
    LOSE = "Loser"
    DRAW = "Draw"


# Enum per lo stato della partita
class MatchStatus(Enum):
    REMATCH = "REMATCH"
    OVER = "OVER"
    ONGOING = "ONGOING"
    SERIES_OVER = "SERIES_OVER"
    NONE = "NONE"
    LEFT = "LEFT"
