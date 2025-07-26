from enum import StrEnum, auto


class Difficulty(StrEnum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()
    PROJECT = auto()


class Priority(StrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    URGENT = auto()
