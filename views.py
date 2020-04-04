
from app import app
from flask import request, make_response, jsonify, render_template, redirect, url_for
import base64
import hmac
import string
import time
import hashlib
from models import Room, Game
from game import Game as NonDbGame, make_game, guess, stop_guessing
from app import db
from utils import id_generator
import json
import random
from words import DECKS

# @app.route('/signature')
# def make_signature():
#     data = {'apiKey': "Vll7I_NaS6KORk06NjJ8qw" ,
#     'apiSecret': "DOMoWSVWYKC7OACsfmbHpi1DDio4owIKqKVm",
#     'meetingNumber': request.args.get('meeting'),
#     'role': request.args.get('role', type=int)}
#     return generateSignature(data)

def generateSignature(data):
    ts = int(round(time.time() * 1000)) - 30000
    msg = data['apiKey'] + str(data['meetingNumber']) + str(ts) + str(data['role'])
    message = base64.b64encode(bytes(msg, 'utf-8'))
    secret = bytes(data['apiSecret'], 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    hash =  base64.b64encode(hash.digest())
    hash = hash.decode("utf-8")
    tmpString = "%s.%s.%s.%s.%s" % (data['apiKey'], str(data['meetingNumber']), str(ts), str(data['role']), hash)
    signature = base64.b64encode(bytes(tmpString, "utf-8"))
    signature = signature.decode("utf-8")
    return signature.rstrip("=")

# @app.route('/join_room')
# def join_room():
#     id = request.args.get('id')
#     room = Room.query.filter_by(token=id).first()
#     if room is None:
#       room = Room()

#     if room.is_full:
#       return make_response(jsonify({'code': 'ROOM_FULL'}), 400)
#     participant = room.join(request.args.get('name'))
#     return jsonify(
#       room=id,
#       players=room.participant_names,
#       player=participant.serialize()
#     )

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

def safe_game(game, id):
  del game['player1']['black']
  del game['player2']['black']
  del game['player1']['green']
  del game['player2']['green']
  game.update({'id': id})
  return game

def update_game(game: dict, id: str):
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
    update_game(game, game_id)
    return render_template('key.html', player=player, key=key, words=[
      [game['words'].pop(0) for _ in range(5)] for __ in range(5)
    ])

@app.route('/stop/<game_id>', methods=['POST'])
def stop_route(game_id):
  content = request.get_json()
  game = get_game(game_id, as_dict=True)
  result, game = stop_guessing(game, content['player'])
  update_game(game, game_id)
  return {
    'result': result,
    'game': safe_game(game, game_id)
  }

@app.route('/guess/<game_id>', methods=['POST'])
def guess_route(game_id):
  content = request.get_json()
  game = get_game(game_id, as_dict=True)
  result, game = guess(game, **content)
  update_game(game, game_id)
  return {
    'result': result,
    'game': safe_game(game, game_id)
  }