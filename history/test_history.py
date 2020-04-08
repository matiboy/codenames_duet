from pytest import mark
from history import History, add_guess
from assertpy.assertpy import assert_that
from history.kinds import Kind

@mark.history
def test_build_blank_history():
  history = History.blank()
  assert_that(history).is_type_of(History)
  assert_that(history.entries).is_length(0)

@mark.history
def test_add_guess_to_empty():
  history = History.blank()

  add_guess(history, 'yellow')

  assert_that(history.entries).is_length(1)
  assert_that(history.entries[0]).has_kind(Kind.GUESS)
  assert_that(history.entries[0]).has_context({"word": "yellow"})