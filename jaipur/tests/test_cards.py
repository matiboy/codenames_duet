from pytest import mark
from jaipur.model.game import Card, Player
from assertpy.assertpy import assert_that
from jaipur.cards import camel_cards, non_camel_cards
from jaipur.model.cards import CardKinds

@mark.jaipur
def test_camel_cards_some():
  player = Player.initialize()
  player.cards = [Card.camel(), Card(kind=CardKinds.Gems), Card(kind=CardKinds.Gems), Card.camel(), Card(kind=CardKinds.Gold)]

  assert_that(camel_cards(player=player)).is_length(2)

@mark.jaipur
def test_camel_cards_none():
  player = Player.initialize()
  player.cards = [Card(kind=CardKinds.Gems), Card(kind=CardKinds.Gold)]

  assert_that(camel_cards(player=player)).is_empty()

@mark.jaipur
def test_camel_cards_only():
  player = Player.initialize()
  player.cards = [Card.camel(), Card.camel(), Card.camel()]

  assert_that(camel_cards(player=player)).is_length(3)

@mark.jaipur
def test_non_camel_cards_some():
  player = Player.initialize()
  player.cards = [Card(kind=CardKinds.Leather), Card.camel(), Card(kind=CardKinds.Gems), Card.camel(), Card(kind=CardKinds.Gold)]

  assert_that(non_camel_cards(player=player)).is_length(3)

@mark.jaipur
def test_non_camel_cards_none():
  player = Player.initialize()
  player.cards = [Card.camel(), Card.camel(), Card.camel()]

  assert_that(non_camel_cards(player=player)).is_empty()

@mark.jaipur
def test_non_camel_cards_only():
  player = Player.initialize()
  player.cards = [Card(kind=CardKinds.Gems), Card(kind=CardKinds.Gold)]

  assert_that(non_camel_cards(player=player)).is_length(2)

@mark.jaipur
def test_camel_cards_some_from_card_list():
  cards = [Card.camel(), Card(kind=CardKinds.Gems), Card(kind=CardKinds.Gems), Card.camel(), Card(kind=CardKinds.Gold)]

  assert_that(camel_cards(cards=cards)).is_length(2)

@mark.jaipur
def test_camel_cards_none_from_card_list():
  cards = [Card(kind=CardKinds.Gems), Card(kind=CardKinds.Gold)]

  assert_that(camel_cards(cards=cards)).is_empty()

@mark.jaipur
def test_camel_cards_only_from_card_list():
  cards = [Card.camel(), Card.camel(), Card.camel()]

  assert_that(camel_cards(cards=cards)).is_length(3)

@mark.jaipur
def test_non_camel_cards_some_from_card_list():
  cards = [Card(kind=CardKinds.Leather), Card.camel(), Card(kind=CardKinds.Gems), Card.camel(), Card(kind=CardKinds.Gold)]

  assert_that(non_camel_cards(cards=cards)).is_length(3)

@mark.jaipur
def test_non_camel_cards_none_from_card_list():
  cards = [Card.camel(), Card.camel(), Card.camel()]

  assert_that(non_camel_cards(cards=cards)).is_empty()

@mark.jaipur
def test_non_camel_cards_only_from_card_list():
  cards = [Card(kind=CardKinds.Gems), Card(kind=CardKinds.Gold)]

  assert_that(non_camel_cards(cards=cards)).is_length(2)