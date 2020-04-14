from jaipur.model.game import Game, next_player, top_card, switch_to_next_player
from jaipur.cards import non_camel_cards
from jaipur.actions.outcomes import Outcomes

def buy_one(game: Game, card_index: int) -> Outcomes:
  player = next_player(game)
  if non_camel_cards(player=player).__len__() == 7:
    return Outcomes.TOO_MANY_CARDS

  # Take card from market
  selected_card = game.open_cards.pop(card_index)
  # Put into player cards
  player.cards.append(selected_card)
  # Replace with top card
  new_card = top_card(game.cards)
  game.open_cards.insert(card_index, new_card)
  switch_to_next_player(game)
  return Outcomes.NEXT_PLAYER
  