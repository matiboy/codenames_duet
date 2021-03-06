from app import db
import json
import uuid
from typing import Union, Dict
from game.dataclasses import Game as GameDC

class Game(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  token = db.Column(db.String(50), index=True, unique=True)
  meeting_id = db.Column(db.String(50), index=True, unique=True)
  meeting_details = db.Column(db.Text)
  game_details = db.Column(db.Text)
  attendees = db.relationship('Attendee', backref='game', lazy=True)
  
  def __repr__(self):
    return '<Game {}>'.format(self.token)

  def set_meeting(self, meeting):
    self.meeting_id = meeting['Meeting']['MeetingId']
    self.meeting_details = json.dumps(meeting['Meeting'])
    db.session.commit()

  def delete_meeting(self):
    self.meeting_details = '{}'
    self.meeting_id = None
    db.session.commit()

  @property
  def meeting(self):
    return json.loads(self.meeting_details)

  def add_attendee(self, unique_id, attendee, index):
    db_attendee = Attendee(token=unique_id, name='', game_id=self.id, attendee_details=json.dumps(attendee), index=index)
    db.session.add(db_attendee)
    db.session.commit()
    return db_attendee

  def add_pending_attendee(self, name, index):
    db_attendee = Attendee(token=str(uuid.uuid4()), name=name, game_id=self.id, attendee_details='{}', index=index)
    db.session.add(db_attendee)
    db.session.commit()
    return db_attendee

class Attendee(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  index = db.Column(db.Integer, index=True)
  token = db.Column(db.String(50), index=True, unique=True)
  name = db.Column(db.String(255))
  attendee_details = db.Column(db.Text)
  initial_token = db.Column(db.String(50), index=False, unique=True)
  game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=True)

  def serialize(self):
    return {
      'token': self.token,
      'name': self.name
    }

  def update_attendee_details(self, attendee):
    self.attendee_details = json.dumps(attendee)
    db.session.commit()

def read_from_initial_token(game, token):
  attendee = Attendee.query.with_parent(game).filter_by(initial_token=token).first()
  if attendee is not None:
    attendee.initial_token = ''
  db.session.commit()
  return attendee

def get_attendee(game, player_token):
  return Attendee.query.with_parent(game).filter_by(token=player_token).first()

def get_game(id: str, as_dict=False):
  game = Game.query.filter_by(token=id).first()
  if not as_dict:
    return game
  if game is not None:
    return game_to_dict(game)

def game_to_dict(game: Game) -> dict:
  return json.loads(game.game_details)

def update_game_details(game: Union[Dict, GameDC], id: str):
  db_game = get_game(id)
  if type(game) is GameDC:
    db_game.game_details = game.to_json()
  else:
    db_game.game_details = json.dumps(game)
  db.session.commit()

