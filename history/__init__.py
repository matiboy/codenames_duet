from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Dict, List
from history.kinds import Kind

@dataclass_json
@dataclass
class Entry:
  kind: Kind
  context: Dict

  @staticmethod
  def of_kind(kind: Kind):
    return Entry(kind=kind, context={})

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

def start_history(history: History) -> History:
  history.entries.append(Entry.of_kind(Kind.CREATED))
