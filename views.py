
from app import app
from flask import request, make_response, jsonify, render_template, redirect, url_for, send_from_directory
import base64
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
from chime import create_attendee, create_meeting, get_client_from_env

# @app.route('/signature')
# def make_signature():
#     data = {'apiKey': "Vll7I_NaS6KORk06NjJ8qw" ,
#     'apiSecret': "DOMoWSVWYKC7OACsfmbHpi1DDio4owIKqKVm",
#     'meetingNumber': request.args.get('meeting'),
#     'role': request.args.get('role', type=int)}
#     return generateSignature(data)

@app.route('/delete_game')
def delete_game():
  id = request.args.get('id')
  game = get_game(id)
  db.session.delete(game)
  db.session.commit()
  return 'Ok'

def get_game(id, as_dict=False):
  game = Game.query.filter_by(token=id).first()
  if not as_dict:
    return game
  if game is not None:
    return json.loads(game.game_details)


def update_game_details(game: dict, id: str):
  db_game = get_game(id)
  db_game.game_details = json.dumps(game)
  db.session.commit()

@app.route('/')
def setup_game():
  decks = list(DECKS.keys())
  decks.sort()
  return render_template('setup.html', decks=decks)

@app.route('/game/<game_id>', methods=['GET'])
def start_game(game_id=None):
  game = get_game(game_id, True)
  if game is None:
    return redirect(url_for('setup_game'))
  game = safe_game(game, game_id)
  if request.is_json:
    return {
      'game': game
    }
  return render_template('game.html', game=game)

@app.route('/game/<game_id>/player<player_id>', methods=['GET'])
def start_game_split(game_id=None, player_id=0):
  game = get_game(game_id)
  if game is None:
    return redirect(url_for('setup_game'))

  # AWS video stuff
  client = get_client_from_env()
  if game.meeting_id is None:
    _, meeting = create_meeting(client)
    game.set_meeting(meeting)
  
  meeting = game.meeting_details
  # Create an attendee
  try:
    unique_id, attendee = create_attendee(client, game.meeting_id)
  except client.exceptions.ForbiddenException:
    # Likely the meeting expired, delete and try again
    game.delete_meeting()
    # Probably should do something about this potential infinite redirect
    return redirect(request.url)
  game.add_attendee(unique_id, attendee, player_id)

  # Actual game stuff
  game = get_game(game_id, True)
  
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
    API_KEY=os.environ['ZOOM_API_KEY'],
    API_SECRET=os.environ['ZOOM_API_SECRET']
  )

@app.route('/index.js')
def index_js():
  root_dir = os.path.dirname(os.getcwd())
  # raise Exception(root_dir)
  return send_from_directory('/code', 'index.js')

@app.route('/game', methods=['POST'])
def build_game():
    content = request.get_json()
    player1_name = content.get('player1Name', 'Player 1')
    player2_name = content.get('player2Name', 'Player 2')
    decks = content.get('decks', ['codenames'])
    bystanders = content.get('bystanders', 9)
    game = make_game(player1_name, player2_name, bystanders, decks)
    db_game = Game(token=id_generator(size=30), game_details=json.dumps(game))
    db.session.add(db_game)
    db.session.commit()
    game = safe_game(game, db_game.token)
    return {
      'gameUrl': url_for('start_game', game_id=db_game.token),
      'keyUrl': url_for('key', game_id=db_game.token),
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

@app.route('/stop/<game_id>', methods=['POST'])
def stop_route(game_id):
  content = request.get_json()
  game = get_game(game_id, as_dict=True)
  result, game = stop_guessing(game, content['player'])
  update_game_details(game, game_id)
  return {
    'result': result,
    'game': safe_game(game, game_id)
  }

@app.route('/guess/<game_id>', methods=['POST'])
def guess_route(game_id):
  content = request.get_json()
  game = get_game(game_id, as_dict=True)
  result, game = guess(game, **content)
  update_game_details(game, game_id)
  return {
    'result': result,
    'game': safe_game(game, game_id)
  }