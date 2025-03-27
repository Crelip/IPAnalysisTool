from enum import Enum
class TimeInterval(Enum):
    DAY = 1
    WEEK = 2
    MONTH = 3
    YEAR = 4
    ALL = 5

    def __str__(self):
        return f'{self.name}'