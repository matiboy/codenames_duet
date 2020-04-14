from pytest import mark
from jaipur.model.game import Game, DECK
from jaipur.actions.initial import set_up
from assertpy.assertpy import assert_that
from jaipur.cards import camel_cards

@mark.jaipur
def test_should_have_five_open_cards():
  game = Game.initialize()
  set_up(game)

  assert_that(game.open_cards).is_length(5)

@mark.jaipur
def test_should_have_at_least_3_open_camels():
  game = Game.initialize()
  set_up(game)
  open_camel_cards = camel_cards(cards=game.open_cards)

  assert_that(len(open_camel_cards)).is_greater_than_or_equal_to(3)

@mark.jaipur
def test_should_have_given_5_cards_to_each_player():
  game = Game.initialize()
  set_up(game)

  assert_that(game.player1.cards).is_length(5)
  assert_that(game.player2.cards).is_length(5)

@mark.jaipur
def test_should_have_40_cards_left_in_deck():
  game = Game.initialize()
  set_up(game)

  assert_that(game.cards).is_length(40)

@mark.jaipur
def test_should_have_40_cards_left_in_deck():
  game = Game.initialize()
  set_up(game)

  assert_that(game.cards).is_length(40)