# enums.py

from enum import Enum


# Enum for moves
class Move(Enum):
    """
    Enum class representing the different moves in a Rock Paper Scissors game.
    """
    ROCK = "rock"  # Represents the Rock move
    PAPER = "paper"  # Represents the Paper move
    SCISSORS = "scissors"  # Represents the Scissors move


# Enum for results
class Result(Enum):
    """
    Enum class representing the possible results of a single match in a Rock Paper Scissors game.
    """
    WIN = "Winner"  # Represents a win
    LOSE = "Loser"  # Represents a loss
    DRAW = "Draw"  # Represents a draw


# Enum for match status
class MatchStatus(Enum):
    """
    Enum class representing the various possible states of a Rock Paper Scissors match.
    """
    REMATCH = "REMATCH"  # Indicates that a rematch is requested
    OVER = "OVER"  # Indicates that the match is over
    ONGOING = "ONGOING"  # Indicates that the match is ongoing
    SERIES_OVER = "SERIES_OVER"  # Indicates that the series of matches is over
    NONE = "NONE"  # Indicates that no match is in progress
    LEFT = "LEFT"  # Indicates that a player has left the game
