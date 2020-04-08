from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Hint:
  word: str
  count: int

@dataclass_json
@dataclass
class Player:
  black: List[str]
  green: List[str]
  name: str
  attempted_words: List[str]
  loaded: bool
  hints: List[Hint]

@dataclass_json
@dataclass
class Game:
  player1: Player
  player2: Player
  words: List[str]
  found: List[str]
  sudden_death: bool
  decks: List[str]
  next_up: Optional[int]
  bystanders: int
  initialBystanders: int
  lost: bool
  won: bool
  agents: int
  keys: int