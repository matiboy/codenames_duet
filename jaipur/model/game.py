from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import Enum
from typing import Dict, List, Tuple
from jaipur.model.cards import CardKinds
from jaipur.model.goods import GoodsKinds
from jaipur.model.tokens import TokenKinds


@dataclass_json
@dataclass
class Card:
  kind: CardKinds

  @staticmethod
  def camel():
    return Card(kind=CardKinds.Camel)

  def __repr__(self):
    return CardKinds(self.kind).value

@dataclass_json
@dataclass
class Token:
  kind: TokenKinds
  value: int

def n_cards_of_that_kind(n: int, kind: CardKinds) -> Tuple[Card]:
  return (Card(kind=kind), ) * n

def n_tokens_of_that_kind(values: List[int], kind: TokenKinds) -> Tuple[Token]:
  return (Token(kind=kind, value=value) for value in values)

DECK = n_cards_of_that_kind(11, CardKinds.Camel) \
  + n_cards_of_that_kind(6, CardKinds.Gems) \
  + n_cards_of_that_kind(6, CardKinds.Gold) \
  + n_cards_of_that_kind(6, CardKinds.Silver) \
  + n_cards_of_that_kind(8, CardKinds.Silk) \
  + n_cards_of_that_kind(8, CardKinds.Spices) \
  + n_cards_of_that_kind(10, CardKinds.Leather) \

TOKENS = {
  TokenKinds.Gems: n_tokens_of_that_kind([7,7,5,5,5], TokenKinds.Gems),
  TokenKinds.Gold: n_tokens_of_that_kind([6,6,5,5,5], TokenKinds.Gold),
  TokenKinds.Silver: n_tokens_of_that_kind([5,5,5,5,5], TokenKinds.Silver),
  TokenKinds.Silk: n_tokens_of_that_kind([5,3,3,2,2,1,1], TokenKinds.Silk),
  TokenKinds.Spices: n_tokens_of_that_kind([4,3,3,2,2,1,1], TokenKinds.Spices),
  TokenKinds.Leather: n_tokens_of_that_kind([4,3,2,1,1,1,1,1,1], TokenKinds.Leather),
}

@dataclass_json
@dataclass
class Player:
  cards: List[Card]
  tokens: List[Token]

  @staticmethod
  def initialize():
    return Player(cards=[], tokens=[])

@dataclass_json
@dataclass
class Game:
  cards: List[Card]
  tokens: Dict[TokenKinds, List[Token]]
  open_cards: List[Card]
  player1: Player
  player2: Player
  next_up: int
  ended: bool

  @staticmethod
  def initialize():
    return Game(
      cards=[],
      tokens=[],
      open_cards=[],
      player1=Player.initialize(),
      player2=Player.initialize(),
      next_up=1,
      ended=False
    )

def next_player(game: Game) -> Player:
  if game.next_up == 1:
    return game.player1
  elif game.next_up == 2:
    return game.player2
  else:
    return None

def n_cards_from_top(n: int, deck: List[Card]) -> List[Card]:
  """Get n cards from the top of the deck
  This modifies the passed in deck
  """
  return [deck.pop(0) for _ in range(n)]

def top_card(deck: List[Card]) -> Card:
  return n_cards_from_top(1, deck)[0]

def switch_to_next_player(game: Game):
  game.next_up = 3 - game.next_up
