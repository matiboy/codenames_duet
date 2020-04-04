from app import db
import json

class Game(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  token = db.Column(db.String(50), index=True, unique=True)
  meeting_id = db.Column(db.String(50), index=True, unique=True)
  meeting_details = db.Column(db.Text)
  game_details = db.Column(db.Text)
  
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

  def add_attendee(self, unique_id, attendee, index):
    db_attendee = Attendee(token=unique_id, name='', game_id=self.id, attendee_details=json.dumps(attendee), index=index)
    db.session.add(db_attendee)
    db.session.commit()
    return db_attendee

class Attendee(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  index = db.Column(db.Integer, index=True)
  token = db.Column(db.String(50), index=True, unique=True)
  name = db.Column(db.String(255))
  attendee_details = db.Column(db.Text)
  game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=True)

  def serialize(self):
    return {
      'token': self.token,
      'name': self.name
    }
