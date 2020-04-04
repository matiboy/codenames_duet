from app import db

class Game(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  token = db.Column(db.String(50), index=True, unique=True)
  game_details = db.Column(db.Text)
  
  def __repr__(self):
    return '<Game {}>'.format(self.token)
