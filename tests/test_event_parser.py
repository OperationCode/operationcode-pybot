import pytest
from pybot.endpoints.slack.events import match_edit_or_delete
from tests.event_data import *


def test_matches_message_edit():
    assert match_edit_or_delete(edit_message) is True


def test_matches_message_delete():
    assert match_edit_or_delete(delete_message) is True


def test_not_matches_new_message():
    assert match_edit_or_delete(new_message) is False
