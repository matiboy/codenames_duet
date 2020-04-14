from jaipur.model.game import Game, Player, Card, CardKinds, TokenKinds, DECK, n_cards_from_top
from typing import List
import random

def set_up(game: Game):
  # Make a copy of the deck
  deck = list(DECK)
  # Pop 3 camels into open
  game.open_cards = n_cards_from_top(3, deck)
  # Now shuffle balance deck
  random.shuffle(deck)
  # Pick 2 more cards for the open
  game.open_cards += n_cards_from_top(2, deck)
  # 5 cards to each player
  game.player1.cards = n_cards_from_top(5, deck)
  game.player2.cards = n_cards_from_top(5, deck)
  # Balance in the deck
  game.cards = deck