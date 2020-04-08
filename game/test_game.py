from game import guess, make_game
from game.outcomes import SUDDEN_DEATH, NO_MORE_TIME, YELLOW, BLACK, GREEN
from assertpy import assert_that

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
}

def test_should_enter_sudden_death():
  """Sudden death is triggered when last bystander is killed"""
  game = get_game()
  game['bystanders'] = 1

  outcome, game = guess(game, 1, 'z')

  assert_that(outcome).is_equal_to(SUDDEN_DEATH)
  assert_that(game['lost']).is_false()
  assert_that(game['sudden_death']).is_true()
  assert_that(game['next_up']).is_none()

def test_should_lose_on_yellow_in_sudden_death():
  """During sudden death, yellow means lose"""
  game = get_game()
  game['sudden_death'] = True

  outcome, game = guess(game, 1, 'z')

  assert_that(outcome).is_equal_to(NO_MORE_TIME)
  assert_that(game['lost']).is_true()

def test_should_handle_yellow():
  """Yellow kills a bystander and alternates roles"""
  game = get_game()
  game['bystanders'] = 8

  outcome, game = guess(game, 1, 'z')

  assert_that(outcome).is_equal_to(YELLOW)
  assert_that(game['lost']).is_false()
  assert_that(game['bystanders']).is_equal_to(7)

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