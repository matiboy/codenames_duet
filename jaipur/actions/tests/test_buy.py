from pytest import mark
from jaipur.model.game import Card, DECK, Game
from assertpy.assertpy import assert_that, soft_assertions
from jaipur.cards import camel_cards
from jaipur.actions.initial import set_up
from jaipur.actions.buy import buy_one
from jaipur.model.cards import CardKinds
from jaipur.actions.outcomes import Outcomes

@mark.jaipur
def test_buy_single_card():
  game = Game.initialize()
  set_up(game)
  game.next_up = 2
  index = 3
  # Let's keep the current open cards as reference
  open_cards = list(game.open_cards)
  player_s_cards = list(game.player2.cards)
  top_card = game.cards[0]
  cards_left = len(game.cards)
  outcome = buy_one(game, index)
  with soft_assertions():
    assert_that(Card.camel()).is_equal_to(Card.camel())
    assert_that(game).has_next_up(1)
    assert_that(game.open_cards).is_length(5)
    assert_that(game.cards).is_length(cards_left - 1)
    assert_that(game.open_cards).is_equal_to(open_cards[:index] + [top_card] + open_cards[index+1:])
    assert_that(game.player2.cards).is_equal_to(player_s_cards + [open_cards[index]])
    assert_that(outcome).is_equal_to(Outcomes.NEXT_PLAYER)

@mark.jaipur
def test_buy_single_card_too_many_non_camel():
  game = Game.initialize()
  set_up(game)
  game.next_up = 1
  # Give next player 7 cards
  game.player1.cards = [Card(kind=CardKinds.Leather)]*7

  open_cards = list(game.open_cards)
  player_s_cards = list(game.player2.cards)
  top_card = game.cards[0]
  cards_left = len(game.cards)

  outcome = buy_one(game, 2)
  with soft_assertions():
    assert_that(outcome).is_equal_to(Outcomes.TOO_MANY_CARDS)
    assert_that(game.cards).is_length(cards_left)
    assert_that(game.player1.cards).is_length(7)
