import enum

class Kind(enum.Enum):
  GUESS = 'guess'
  GREEN = 'green'
  STOP = 'stop'
  BLACK = 'black'
  CREATED = 'created'
  LOST = 'lost'
  WON = 'won'
  SUDDEN_DEATH = 'sudden_death'
