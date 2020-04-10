from pytest import mark
from auth.login import read_login_token, make_login_token
from itsdangerous import URLSafeSerializer
from assertpy.assertpy import assert_that

@mark.auth
def test_login_fails():
  rubbish = 'dsdasdsada'
  signer = URLSafeSerializer('lala')

  game, player = read_login_token(signer, rubbish)

  assert_that(game).is_none()
  assert_that(player).is_none()

@mark.auth
def test_login_success():
  signer = URLSafeSerializer('some_secret')
  token = make_login_token(signer, 'ABC', 42)
  
  game, player = read_login_token(signer, token)

  assert_that(game).is_equal_to('ABC')
  assert_that(player).is_equal_to(42)