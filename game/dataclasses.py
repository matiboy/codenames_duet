from typing import List, Optional, Union
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from words import Decks
from history import History

@dataclass_json
@dataclass
class Hint:
  count: int
  word: str

  @staticmethod
  def blank():
    return Hint(count=0, word='')

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Player:
  attempted_words: List[str]
  black: List[str]
  green: List[str]
  hints: List[Hint]
  loaded: bool
  name: str

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Game:
  agents: int
  bystanders: int
  decks: List[Decks]
  found: List[str]
  history: History
  initialBystanders: int
  keys: int
  lost: bool
  next_up: Union[int, None]
  player1: Player
  player2: Player
  sudden_death: bool
  won: bool
  words: List[str]
  hint: Optional[Hint]