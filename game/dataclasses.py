from typing import List, Optional, Union
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from words import Decks
from history import History

@dataclass_json
@dataclass
class Hint:
  count: int
  word: str

  @classmethod
  def blank(cls):
    return cls(count=0, word='')

@dataclass_json()
@dataclass
class Player:
  attempted_words: List[str]
  black: List[str]
  green: List[str]
  hints: List[Hint]
  loaded: bool
  name: str

def decks_to_str(value: List[Decks]):
  return [Decks(v).value for v in value]

def str_to_decks(value: List[str]):
  return [Decks[v] for v in value]

@dataclass_json()
@dataclass
class Game:
  decks: List[Decks] = field(
    metadata=config(
        encoder=decks_to_str,
        decoder=str_to_decks
    )
  )
  agents: int
  bystanders: int
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
  lost_reason: Optional[str]