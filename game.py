import random
import string
from words import DECKS
from typing import List
from utils import id_generator

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

def make_game(player1_name, player2_name, bystanders, decks, agents=15):
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
    'player1': {
      'name': player1_name,
      'black': player1_black,
      'green': player1_green,
      'attempted_words': []
    },
    'next_up': None,
    'player2': {
      'name': player2_name,
      'black': player2_black,
      'green': player2_green,
      'attempted_words': []
    },
    'bystanders': bystanders,
    'initialBystanders': bystanders,
    'agents': agents,
    'found': [],
    'keys': 0,
  }

NO_MORE_TIME = 1
GREEN = 2
YELLOW = 3
BLACK = 4
WIN = 5
ALREADY_GUESSED = 6
INVALID_WORD = 7
STOPPED_GUESSING = 8

def get_other_player(player: int) -> int:
  return 3 - player

def stop_guessing(game, player: int) -> (int, dict):
  game['bystanders'] -= 1
  game['next_up'] = get_other_player(player)
  if game['bystanders'] <= 0:
    return (NO_MORE_TIME, game)
  return (STOPPED_GUESSING, game)

def guess(game, player: int, word: str) -> (int, dict):
  player_key = f'player{player}'
  other_player = get_other_player(player)
  other_player_key = f'player{other_player}' 
  player_object = game[player_key]
  other_player_object = game[other_player_key]
  if word not in game['words']:
    return (INVALID_WORD, game)
  if word in player_object['attempted_words']:
    return (ALREADY_GUESSED, game)
  player_object['attempted_words'].append(word)
  if word in other_player_object['black']:
    return (BLACK, game)
  if word in other_player_object['green']:
    game['next_up'] = player # player keeps playing
    game['found'].append(word)
    if game['found'].__len__() == game['agents']:
      return (WIN, game)
    else:
      return (GREEN, game)
  else:
    game['bystanders'] -= 1
    game['next_up'] = other_player
    if game['bystanders'] == 0:
      return (NO_MORE_TIME, game)
    return (YELLOW, game)

class Game(object):
  players = []
  id = ''
  next_player = None
  history = None
  hint = None
  hint_count = None
  def __init__(self, deck, player1_name, player2_name):
      self.id = id_generator()
      randomized_words = CODENAMES_WORDS.copy()
      random.shuffle(randomized_words)
      self.words = [randomized_words.pop() for _ in range(25)]
      words = self.words.copy()
      random.shuffle(words)
      player1_black = [words.pop() for _ in range(3)]
      player1_green = [words.pop() for _ in range(9)]
      player1_yellow = words.copy()
      player2_black = [player1_green[0], player1_black[0], player1_yellow[0]]
      player2_green = player1_green[1:4]
      words = [word for word in self.words if word not in player2_black and word not in player2_green]
      player2_green = player2_green + [words.pop() for _ in range(6)]
      self.players.append(Player(player1_name, player1_black, player1_green))
      self.players.append(Player(player2_name, player2_black, player2_green))
      self.history = []

  def serialize(self):
    return {
      'words': self.words,
      'player1': {
        'black': self.players[0].black_words,
        'green': self.players[0].green_words
      },
      'player2': {
        'black': self.players[1].black_words,
        'green': self.players[1].green_words
      }
    }

  def get_player_name(self, player: str):
    for play in self.players:
      if play.id == player:
        return play.name

  def player_by_id(self, id):
    return next((x for x in self.players if x == id), None)

  def give_hint(self, player: str,  hint: str, hint_count: int):
    if self.next_player is not None and player != self.next_player:
      raise WrongPlayerException
    self.next_player = self.player_by_id(player)
    self.hint = hint
    self.hint_count = hint_count
    player_name = self.get_player_name(player)
    self.history.append(f'{player_name} gave hint "{hint}" with a count of {hint_count}')
