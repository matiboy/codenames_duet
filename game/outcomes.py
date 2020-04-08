import enum

NO_MORE_TIME = 1
GREEN = 2
YELLOW = 3
BLACK = 4
WIN = 5
ALREADY_GUESSED = 6
INVALID_WORD = 7
STOPPED_GUESSING = 8
NOT_YOUR_TURN = 9
SUDDEN_DEATH = 10
SKIPPED = 11
CANNOT_SKIP = 12

class Outcomes(enum.Enum):
  NO_MORE_TIME = 'NO_MORE_TIME'
  GREEN = 'GREEN'
  YELLOW = 'YELLOW'
  BLACK = 'BLACK'
  WIN = 'WIN'
  ALREADY_GUESSED = 'ALREADY_GUESSED'
  INVALID_WORD = 'INVALID_WORD'
  STOPPED_GUESSING = 'STOPPED_GUESSING'
  NOT_YOUR_TURN = 'NOT_YOUR_TURN'
  SUDDEN_DEATH = 'SUDDEN_DEATH'
  SKIPPED = 'SKIPPED'
  CANNOT_SKIP = 'CANNOT_SKIP'