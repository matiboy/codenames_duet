import enum
from .duet import words as duet
from .duet_2 import words as duet_2
from .codenames import words as codenames
from .francais import words as francais
from .german import words as deutsch

class Decks(enum.Enum):
  Duet = 'Duet'
  Duet_2 = 'Duet #2'
  Codenames = 'Codenames'
  Francais = "Francais"
  Deutsch = "Deutsch"

DECKS = {
  Decks.Duet: duet,
  Decks.Duet_2: duet_2,
  Decks.Codenames: codenames,
  Decks.Francais: francais,
  Decks.Deutsch: deutsch
}