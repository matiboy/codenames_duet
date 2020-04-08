from dataclasses import dataclass
from dataclasses_json import dataclass_json
from game.dataclasses import Game


@dataclass_json
@dataclass
class ApiResponse:
  result: int
  game: Game

def build_json_response(result, game):
  return {
    'result': result,
    'game': game
  }

json_error = {
  'result': 0
}