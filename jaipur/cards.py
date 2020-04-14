from typing import List
from jaipur.model.game import Card, Player
from jaipur.model.cards import CardKinds

def camel_cards(*, player: Player=None, cards: List[Card]=None) -> List[Card]:
  if player is not None:
    return camel_cards(cards=player.cards)
  return [card for card in cards if card.kind == CardKinds.Camel]

def non_camel_cards(*, player: Player=None, cards: List[Card]=None) -> List[Card]:
  if player is not None:
    return non_camel_cards(cards=player.cards)
  return [card for card in cards if card.kind != CardKinds.Camel]

