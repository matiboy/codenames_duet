import random
import string
from typing import List
from words import DECKS
from utils import id_generator
from game.outcomes import NO_MORE_TIME, GREEN, YELLOW, BLACK, WIN, ALREADY_GUESSED, INVALID_WORD, STOPPED_GUESSING, NOT_YOUR_TURN, SUDDEN_DEATH

class WrongPlayerException(Exception):
  """ Raised when it is not this player s turn """
  pass

class Player(object):
  id = ''
  name = ''
  black_words = None
  green_words = None
  def __init__(self, name, black_words, green_words):
    self.id = id_generator()
    self.name = name
    self.black_words = black_words
    self.green_words = green_words

  def __eq__(self, other):
    if type(other) is Player:
      return other.id == self.id
    return other == self.id or other == self.name

def make_game(player1_name: str, player2_name: str, bystanders: int, decks, agents=15):
  randomized_words = set()
  randomized_words.update(*[DECKS[deck] for deck in decks])
  
  randomized_words = list(randomized_words).copy()
  random.shuffle(randomized_words)
  all_words = [randomized_words.pop() for _ in range(25)]
  words = all_words.copy()

  player1_black = []
  player1_green = []
  player1_yellow = []
  player2_black = []
  player2_green = []
  player2_yellow = []

  # Pick 3 common greens
  common_greens = [words.pop() for _ in range(3)]

  #1 common black
  common_black = [words.pop() for _ in range(1)]
  player1_black = common_black.copy()
  player2_black = common_black.copy()

  player1_green += [words.pop() for _ in range(6)]
  player2_green += [words.pop() for _ in range(6)]
  
  # one black for other player green, but not common one
  player1_black += [player2_green[0]]
  player2_black += [player1_green[0]]

  player1_black += [words.pop()]
  player2_black += [words.pop()]

  player1_green += common_greens
  player2_green += common_greens

  random.shuffle(all_words)

  return {
    'words': all_words,
    'sudden_death': False,
    'decks': decks,
    'player1': {
      'name': player1_name,
      'black': player1_black,
      'green': player1_green,
      'attempted_words': [],
      'loaded': False,
      'hints': []
    },
    'next_up': None,
    'player2': {
      'name': player2_name,
      'black': player2_black,
      'green': player2_green,
      'attempted_words': [],
      'loaded': False,
      'hints': []
    },
    'bystanders': bystanders,
    'initialBystanders': bystanders,
    'agents': agents,
    'found': [],
    'lost': False,
    'won': False,
    'keys': 0,
  }


def get_other_player(player: int) -> int:
  return 3 - player

def record_viewed(game, player_key: str):
  game[player_key]['loaded'] = True
  return game

def give_hint(game, db_attendee, hint_text: str, hint_count: int):
  game['hint'] = {
    'word': hint_text,
    'count': hint_count
  }
  get_player_dict(game, db_attendee.index)['hints'].append(game['hint'])
  # If not yet started, we set up who is next; otherwise it doesnt change
  if game['next_up'] is None:
    game['next_up'] = get_other_player(db_attendee.index)
  return game

def stop_guessing(game, player: int) -> (int, dict):
  game['bystanders'] -= 1
  game['next_up'] = get_other_player(player)
  game['hint'] = {}
  if game['bystanders'] <= 0:
    game['lost'] = True
    return (NO_MORE_TIME, game)
  return (STOPPED_GUESSING, game)

def guess(game, player: int, word: str) -> (int, dict):
  player_key = f'player{player}'
  other_player = get_other_player(player)
  other_player_key = f'player{other_player}' 
  player_object = game[player_key]
  other_player_object = game[other_player_key]
  # Basic validations
  # Correct player is up
  if game['next_up'] is not None and player != game['next_up']:
    return (NOT_YOUR_TURN, game)
  # No random words
  if word not in game['words']:
    return (INVALID_WORD, game)
  # Same player can't click same word again
  if word in player_object['attempted_words']:
    return (ALREADY_GUESSED, game)
  # Passed all validations
  player_object['attempted_words'].append(word)
  if word in other_player_object['black']:
    game['lost'] = True
    return (BLACK, game)
  if word in other_player_object['green']:
    game['next_up'] = player # player keeps playing
    game['found'].append(word)
    if game['found'].__len__() == game['agents']:
      game['won'] = True
      return (WIN, game)
    else:
      return (GREEN, game)
  else:
    # In sudden death, yellow is lost
    if game['sudden_death']:
      game['lost'] = True
      return (NO_MORE_TIME, game)
    game['bystanders'] -= 1
    # Enter sudden death
    if game['bystanders'] == 0:
      game['sudden_death'] = True
      # There is no "next" player, it's anyone's turn
      game['next_up'] = None
      return (SUDDEN_DEATH, game)
    else:
      game['next_up'] = other_player
      game['hint'] = {}
      return (YELLOW, game)

def get_player_dict(game, player: int):
  return game[f'player{player}']

def safe_game(game, id, players=None):
  players = players or ['player1', 'player2']
  for player in players:
    del game[player]['black']
    del game[player]['green']
  game.update({'id': id})
  return game