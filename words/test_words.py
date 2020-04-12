from words import Decks
from game.dataclasses import decks_to_str, str_to_decks
from assertpy import assert_that

def test_should_make_decks_to_string():
  decks = [Decks.Duet_2, Decks.Codenames]

  assert_that(decks_to_str(decks)).is_equal_to(['Duet #2', 'Codenames'])

def test_should_make_string_to_decks():
  decks = ['Duet #2', 'Codenames']

  assert_that(str_to_decks(decks)).is_equal_to([Decks.Duet_2, Decks.Codenames])