from functools import wraps
from models.game import game_to_dict, get_attendee, get_game
from flask import abort, redirect, url_for
from game.dataclasses import Game

def game_or_404(redirect_to=None):
  def callable(original_function, **kwargs):
    @wraps(original_function)
    def fn(*args, **kwargs):
      game_id = kwargs['game_id']
      game = get_game(game_id)
      if game is None:
        if redirect_to is not None:
          return redirect(url_for(redirect_to))
        abort(404)
      kwargs['db_game'] = game
      kwargs['game'] = game_to_dict(game)
      kwargs['game_dc'] = Game.from_dict(kwargs['game'])
      return original_function(*args, **kwargs)
    return fn
  return callable

def attendee_or_404(original_function):
  @wraps(original_function)
  def fn(*args, **kwargs):
    player_token = kwargs['player_token']
    db_game = kwargs['db_game']
    attendee = get_attendee(db_game, player_token)
    if attendee is None:
      abort(404)
    kwargs['db_attendee'] = attendee
    return original_function(*args, **kwargs)
  return fn