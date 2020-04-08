from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Dict, List
from history.kinds import Kind

@dataclass_json
@dataclass
class Entry:
  kind: Kind
  context: Dict

@dataclass_json
@dataclass
# @dataclass_json
class History:
  entries: List[Entry]

  @staticmethod
  def blank():
    return History(entries=[])

def add_guess(history: History, word: str) -> History:
  history.entries.append(Entry(kind=Kind.GUESS, context={'word': word}))
  return history
