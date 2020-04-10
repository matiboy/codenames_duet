from itsdangerous import URLSafeSerializer
from itsdangerous.exc import BadData
from typing import Tuple

LOGIN_SALT = 'login'

def make_login_token(signer: URLSafeSerializer, game_id: str, player_number: int) -> str:
  return signer.dumps({'player': player_number, 'game': game_id}, salt=LOGIN_SALT)

def read_login_token(signer: URLSafeSerializer, token: str) -> Tuple[str, int]:
  try:
    data = signer.loads(token, salt=LOGIN_SALT)
  except BadData:
    return (None, None)
  return data['game'], data['player']
