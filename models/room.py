from app import db
from utils import id_generator
import sys

class Participant(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  token = db.Column(db.String(50), index=True, unique=True)
  name = db.Column(db.String(255))
  room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)

  def __init__(self, name, room_id):
    self.token = id_generator(16)
    self.name = name
    self.room_id = room_id

  def serialize(self):
    return {
      'token': self.token,
      'name': self.name
    }

class Room(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  token = db.Column(db.String(50), index=True, unique=True)
  max_participants = db.Column(db.Integer, default=2)
  participants = db.relationship('Participant', backref='room', lazy=True)
  def __repr__(self):
    return '<Room {}>'.format(self.token)

  def __init__(self, max_participants=2):
    self.token = id_generator(16)
    self.max_participants = max_participants

  def join(self, name):
    participant = Participant(name, self.id)
    db.session.add(participant)
    db.session.commit()
    return participant

  @property
  def participant_names(self):
    return [x.name for x in self.participants]

  @property
  def is_full(self):
    return self.participants.__len__() >= self.max_participants
  
  def has_player(self, token: str):
    return any((player.token == token for player in self.participants))