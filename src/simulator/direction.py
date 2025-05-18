from enum import Enum


class Direction(Enum):

    LONG = 1
    SHORT = -1

    def __str__(self):
        return 'LONG' if self.value == 1 else 'SHORT'
    
    @property
    def opposite(self) -> 'Direction':
        return Direction(-self.value)
    