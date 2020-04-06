
from app import app
from flask import request, make_response, abort, jsonify, render_template, redirect, url_for, send_from_directory
import base64
from functools import wraps
import hmac
import string
import time
import hashlib
from models import Room, Game, Attendee
from game import guess, make_game, record_viewed, safe_game, stop_guessing
from app import db
from utils import id_generator
import json
import random
from words import DECKS
import os
import pusher
from response import json_error, build_json_response
from chime import create_attendee, create_meeting, get_client_from_env
from models.game import get_attendee, update_game_details
from request import game_or_404, attendee_or_404

# @app.route('/signature')
# def make_signature():
#     data = {'apiKey': "Vll7I_NaS6KORk06NjJ8qw" ,
#     'apiSecret': "DOMoWSVWYKC7OACsfmbHpi1DDio4owIKqKVm",
#     'meetingNumber': request.args.get('meeting'),
#     'role': request.args.get('role', type=int)}
#     return generateSignature(data)

pusher_client = pusher.Pusher(
  app_id=os.environ['PUSHER_APP_ID'],
  key=os.environ['PUSHER_APP_KEY'],
  secret=os.environ['PUSHER_APP_SECRET'],
  cluster='ap1',
  ssl=True
)

@app.route('/delete_game')
def delete_game():
  # TODO this should be admin only
  id = request.args.get('id')
  game = get_game(id)
  db.session.delete(game)
  db.session.commit()
  return 'Ok'

@app.route('/')
def setup_game():
  decks = list(DECKS.keys())
  decks.sort()
  return render_template('setup.html', decks=decks)

@app.route('/game/<game_id>/<player_token>', methods=['GET'])
@game_or_404(redirect_to='setup_game')
def get_game_details(db_game, game, db_attendee, **kwargs):
  game = safe_game(game, game_id)
  if request.is_json:
    return {
      'game': game
    }
  return render_template('game.html', game=game)

@app.route('/game/<game_id>/new', methods=['POST'])
def start_new_game(game_id=''):
  game = get_game(game_id, True)
  if game is None:
    return {
      'result': 0,
      'game': None
    }
  game = make_game(game['player1']['name'], game['player2']['name'], game['initialBystanders'], decks=game['decks'])
  update_game_details(game, game_id)
  game = safe_game(game, game_id)
  return {
    'result': 1,
    'game': game
  }
  


@app.route('/game/<game_id>/player/<player_token>', methods=['GET'], endpoint='start_game_split')
@game_or_404(redirect_to='setup_game')
@attendee_or_404
def start_game_split(game_id='', player_token='', db_game=None, game=None, db_attendee=None):
  if request.is_json:
    return get_game_details(game_id=game_id, player_token=player_token)

  # Get the corresponding attendee
  db_attendee = get_attendee(db_game, player_token)
  if db_attendee is None:
    return redirect(url_for('setup_game'))

  player_id = db_attendee.index

  # AWS video stuff
  client = get_client_from_env()
  if db_game.meeting_id is None:
    _, meeting = create_meeting(client)
    db_game.set_meeting(meeting)
  
  meeting = db_game.meeting_details
  # Create an attendee
  try:
    unique_id, attendee = create_attendee(client, db_game.meeting_id, db_attendee.token)
  except (client.exceptions.ForbiddenException, client.exceptions.NotFoundException):
    # Likely the meeting expired, delete and try again
    db_game.delete_meeting()
    # Probably should do something about this potential infinite redirect
    return redirect(request.url)
  db_attendee.update_attendee_details(attendee)

  # Actual game stuff
  player_key = f'player{player_id}'
  player = dict(game[player_key])
  record_viewed(game, player_key)
  update_game_details(game, game_id)
  game = safe_game(game, game_id)
  words_copy = game['words'].copy()
  words=[
    [words_copy.pop(0) for _ in range(5)] for __ in range(5)
  ]
  return render_template('game_split.html', game=game, player=player, words=words, player_number=player_id,
    attendee=attendee,
    meeting=db_game.meeting,
    pusher_key=os.environ['PUSHER_APP_KEY'],
    pusher_cluster='ap1',
    thisPlayerName=player['name'],
    channel=build_channels(db_game)[player_id - 1],
    otherPlayerName= game[f'player{3-player_id}']['name']
  )

@app.route('/dynamic/<player>.js')
def player_js(player):
  response = make_response('console.log("YAY")')
  response.mimetype = 'text/javascript'
  return response

@app.route('/game', methods=['POST'])
def build_game():
    content = request.get_json()
    player1_name = content.get('player1Name', 'Player 1')
    player2_name = content.get('player2Name', 'Player 2')
    decks = content.get('decks', ['Codenames'])
    bystanders = content.get('bystanders', 9)
    game = make_game(player1_name, player2_name, bystanders, decks)
    db_game = Game(token=id_generator(size=30), game_details=json.dumps(game))
    db.session.add(db_game)
    db.session.commit()
    # Create 2 attendees to be used later
    player1 = db_game.add_pending_attendee(name=player1_name, index=1)
    player2 = db_game.add_pending_attendee(name=player2_name, index=2)
    game = safe_game(game, db_game.token)
    return {
      'gameUrlPlayer1': url_for('start_game_split', game_id=db_game.token, player_token=player1.token),
      'gameUrlPlayer2': url_for('start_game_split', game_id=db_game.token, player_token=player2.token),
    }


@app.route('/key/<game_id>', endpoint='key')
def key(game_id):
    game = get_game(game_id, True)
    player = None
    key = None
    if game['keys'] == 0:
      player = 'player1'
    elif game['keys'] == 1:
      player = 'player2'
    if player is not None:
      key = game[player]
    if key is not None:
      player = key['name']
    game['keys'] += 1
    update_game_details(game, game_id)
    return render_template('key.html', player=player, key=key, words=[
      [game['words'].pop(0) for _ in range(5)] for __ in range(5)
    ])

@app.route('/stop/<game_id>/<player_token>', methods=['POST'], endpoint='stop_route')
@game_or_404
def stop_route(game_id, player_token):
  content = request.get_json()
  game = get_game(game_id, as_dict=True)
  attendee = get_attendee(get_game(game_id), player_token)
  if attendee is None:
    return {
      'result': 0
    }
  index = attendee.index
  result, game = stop_guessing(game, index)
  update_game_details(game, game_id)
  channel = get_other_player_channel(game, player_token)
  pusher_client.trigger(channel, 'game_update', {})
  return {
    'result': result,
    'game': safe_game(game, game_id)
  }

@app.route('/guess/<game_id>/<player_token>', methods=['POST'], endpoint='guess_route')
@game_or_404()
@attendee_or_404
def guess_route(game_id, game, db_game, player_token, db_attendee):
  content = request.get_json()
  index = db_attendee.index
  result, game = guess(game, word=content['word'], player=index)
  update_game_details(game, game_id)
  channel = get_other_player_channel(db_game, player_token)
  app.logger.info(f'Triggering update on socket channel {channel}')
  pusher_client.trigger(channel, 'game_update', {})
  return {
    'result': result,
    'game': safe_game(game, game_id)
  }

def get_other_player_channel(game: Game, player_token):
  (attendee1, attendee2) = game.attendees
  if attendee1.token == player_token:
    return make_channel(game.token, attendee2.token)
  else:
    return make_channel(game.token, attendee1.token)

def make_channel(game_id, token):
  return f'{game_id}@{token}'

def build_channels(game: Game):
  (attendee1, attendee2) = game.attendees
  return make_channel(game.token, attendee1.token), make_channel(game.token, attendee2.token)