from app import app, signer
from auth.login import read_login_token
from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_refresh_token_required
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AuthToken:
  refresh_token: str
  access_token: str

  @staticmethod
  def with_identity(identity):
    return AuthToken(
      access_token=create_access_token(identity),
      refresh_token=create_refresh_token(identity),
    )

def login():
  if request.method == 'GET':
    token = request.args.get('token')
  else:
    data = request.get_json()
    token = data['token']
  game, player = read_login_token(signer, token)
  if game is not None:
    return AuthToken.with_identity({'game': game, 'player': player}).to_dict()
  return jsonify({'message': 'Invalid token'}), 401

@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200