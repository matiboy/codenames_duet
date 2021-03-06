from game import get_other_player, guess, make_game, skip_player, stop_guessing
from game.dataclasses import Game
from game.outcomes import SUDDEN_DEATH, NO_MORE_TIME, YELLOW, BLACK, GREEN, SKIPPED, CANNOT_SKIP, NOT_YOUR_TURN, STOPPED_GUESSING, Outcomes
from assertpy import assert_that
from pytest import mark
import random
from words import Decks
from history.kinds import Kind

def get_game():
  return {
  'words': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
  'sudden_death': False,
  'decks': ['Codenames'],
  'player1': {
    'name': 'John',
    'black': ['a', 'b', 'c'],
    'green': ['d', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm'],
    'attempted_words': [],
    'loaded': False,
    'hints': []
  },
  'next_up': None,
  'player2': {
    'name': 'Jane',
    'black': ['a', 'd', 'n'],
    'green': ['e', 'f', 'g', 'o', 'p', 'q', 'r', 's', 't'],
    'attempted_words': [],
    'loaded': False,
    'hints': []
  },
  'bystanders': 9,
  'initialBystanders': 9,
  'agents': 15,
  'found': [],
  'lost': False,
  'won': False,
  'keys': 0,
  'hint': {'count': 0, 'word': ''},
  'history': {'entries': [
    {'kind': Kind.CREATED, 'context': {}}
  ]}
}

def get_game_dc() -> Game:
  return Game.from_dict(get_game(), infer_missing=True)

@mark.sudden_death
def test_should_enter_sudden_death():
  """Sudden death is triggered when last bystander is killed"""
  game = get_game()
  game['bystanders'] = 1

  outcome, game = guess(game, 1, 'z')

  assert_that(outcome).is_equal_to(SUDDEN_DEATH)
  assert_that(game['lost']).is_false()
  assert_that(game['sudden_death']).is_true()
  assert_that(game['next_up']).is_none()

@mark.sudden_death
def test_should_enter_sudden_death_on_stop():
  """Sudden death is triggered when last bystander is killed"""
  game = get_game_dc()
  game.next_up = 2
  game.bystanders = 1

  outcome, game = stop_guessing(game, 2)

  assert_that(outcome).is_equal_to(Outcomes.SUDDEN_DEATH)
  assert_that(game.lost).is_false()
  assert_that(game.hint.word).is_empty()
  assert_that(game.sudden_death).is_true()
  assert_that(game.next_up).is_none()

@mark.sudden_death
def test_should_lose_on_yellow_in_sudden_death():
  """During sudden death, yellow means lose"""
  game = get_game()
  game['sudden_death'] = True

  outcome, game = guess(game, 1, 'z')

  assert_that(outcome).is_equal_to(NO_MORE_TIME)
  assert_that(game['lost']).is_true()

@mark.standard_play
def test_should_reduce_bystanders_on_stop():
  game = get_game_dc()
  game.bystanders = 5
  game.next_up = 1

  outcome, game = stop_guessing(game, 1)
  assert_that(outcome).is_equal_to(Outcomes.STOPPED_GUESSING)
  assert_that(game).has_bystanders(4)
  assert_that(game).has_next_up(2)

@mark.standard_play
def test_should_not_allow_wrong_player_on_stop():
  game = get_game_dc()
  game.bystanders = 2
  game.next_up = 1

  outcome, game = stop_guessing(game, 2)
  assert_that(outcome).is_equal_to(Outcomes.NOT_YOUR_TURN)
  assert_that(game).has_bystanders(2)
  assert_that(game).has_next_up(1)

@mark.standard_play
def test_should_allow_correct_player():
  game = get_game()
  game['next_up'] = 1

  outcome, game = guess(game, 1, 'z')
  assert_that(outcome).is_equal_to(YELLOW)

@mark.standard_play
def test_should_disallow_wrong_player():
  game = get_game()
  game['next_up'] = 1

  outcome, game = guess(game, 2, 'z')
  assert_that(outcome).is_equal_to(NOT_YOUR_TURN)
  assert_that(game).has_next_up(1) # unchanged

@mark.standard_play
def test_should_allow_any_player_if_not_initialized():
  game = get_game()

  outcome, game = guess(game, 2, 'z')
  assert_that(outcome).is_equal_to(YELLOW)
  assert_that(game).has_next_up(1) # other player is next since failed

@mark.sudden_death
def test_should_allow_any_player_during_sudden_death():
  game = get_game()
  game['next_up'] = 1
  game['sudden_death'] = True
  
  outcome, game = guess(game, 2, 'z') #"wrong" player
  assert_that(outcome).is_not_equal_to(NOT_YOUR_TURN)

@mark.sudden_death
def test_should_not_set_next_up_on_green():
  game = get_game()
  game['sudden_death'] = True
  
  outcome, game = guess(game, 2, random.choice(game['player1']['green'])) # player 2 finding green from player 1
  assert_that(outcome).is_equal_to(GREEN)
  assert_that(game).has_next_up(None)

@mark.parametrize("this_player, that_player",
  [(1, 2), (2, 1)]
)
def test_get_other_player(this_player, that_player):
  other_player = get_other_player(this_player)
  assert_that(other_player).is_equal_to(that_player)

def test_should_handle_yellow():
  """Yellow kills a bystander and alternates roles"""
  game = get_game()
  game['bystanders'] = 8

  outcome, game = guess(game, 1, 'z')

  assert_that(outcome).is_equal_to(YELLOW)
  assert_that(game).has_lost(False)
  assert_that(game).has_bystanders(7)

def test_should_lose_on_black():
  """Black is immediate loss"""
  game = get_game()

  outcome, game = guess(game, 1, 'd')

  assert_that(outcome).is_equal_to(BLACK)
  assert_that(game['lost']).is_true()

def test_should_not_lose_on_own_black():
  """Black only counts on other player"""
  game = get_game()

  outcome, game = guess(game, 2, 'n')

  assert_that(outcome).is_equal_to(YELLOW)
  assert_that(game['lost']).is_false()
  assert_that(game['next_up']).is_equal_to(1)

def test_read_decks_from_string():
  """Decks will be passed as string, transformed to enum"""
  game = make_game('Bob', 'Diane', 12, [Decks.Codenames.value, Decks.Duet_2.value])
  
  assert_that(game['decks']).is_equal_to(['Codenames', 'Duet #2'])

def test_should_have_correct_commonality():
  """Per the rules, one common black, one black is green, one black is yellow and three common greens"""
  game = make_game('Bob', 'Diane', 12, ['Codenames'])
  player1 = game['player1']
  player2 = game['player2']

  common_black = [word for word in player1['black'] if word in player2['black']]
  common_green = [word for word in player1['green'] if word in player2['green']]
  black_green_common_1 = [word for word in player1['black'] if word in player2['green']]
  black_green_common_2 = [word for word in player2['black'] if word in player1['green']]

  assert_that(common_black).is_length(1)
  assert_that(common_green).is_length(3)
  assert_that(black_green_common_1).is_length(1)
  assert_that(black_green_common_2).is_length(1)
  assert_that(player1['green']).is_length(9)
  assert_that(player2['green']).is_length(9)
  assert_that(player1['black']).is_length(3)
  assert_that(player2['black']).is_length(3)
  assert_that(game['lost']).is_false()
  assert_that(game['next_up']).is_none()

def test_should_allow_skipping_when_no_more_words():
  game = get_game()
  # All player 1 found
  game['found'] = ['d', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'g']
  game['next_up'] = 2 # that's next for guessing
  
  outcome, game = skip_player(game, 1)

  assert_that(outcome).is_equal_to(SKIPPED)
  assert_that(game['next_up']).is_equal_to(1)
  # No bystander killed
  assert_that(game['bystanders']).is_equal_to(9)

def test_should_not_allow_skipping_wrong_player():
  game = get_game()
  # All player 1 found - should not matter here
  game['found'] = ['d', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'g']
  game['next_up'] = 2 # that's next for guessing
  
  # Player 2 trying to skip, but not their turn to hint
  outcome, game = skip_player(game, 2)

  assert_that(outcome).is_equal_to(CANNOT_SKIP)
  # unchanged
  assert_that(game['next_up']).is_equal_to(2)


def test_should_not_allow_skipping_some_words_left():
  game = get_game()
  # Not all player 1 found
  game['found'] = ['d', 'e', 'f', 'g']
  game['next_up'] = 2
  
  outcome, game = skip_player(game, 1)

  assert_that(outcome).is_equal_to(CANNOT_SKIP)
  # unchanged
  assert_that(game['next_up']).is_equal_to(2)
  assert_that(game['bystanders']).is_equal_to(9)

def test_should_state_losing_reason_assassin():
  game = get_game_dc()
  game.next_up = 2

  outcome, game = guess(game.to_dict(), 2, 'b')
  assert_that(outcome).is_equal_to(BLACK)
  assert_that(game).has_lost_reason('Jane was killed by an assassin')

def test_should_state_losing_reason_out_of_time():
  game = get_game_dc()
  game.sudden_death = True

  outcome, game = guess(game.to_dict(), 2, 'z')
  assert_that(outcome).is_equal_to(NO_MORE_TIME)
  assert_that(game).has_lost_reason('You ran out of time')