import pytest
from flexmock import flexmock
from mock import patch, PropertyMock
from sportsreference.ncaaf.player import AbstractPlayer
from sportsreference.ncaaf.roster import Player


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.url = url
            self.reason = 'Bad URL'  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ(None)


class TestNCAAFPlayer:
    def setup_method(self):
        flexmock(AbstractPlayer) \
            .should_receive('_parse_player_data') \
            .and_return(None)
        flexmock(Player) \
            .should_receive('_pull_player_data') \
            .and_return(None)
        flexmock(Player) \
            .should_receive('_find_initial_index') \
            .and_return(None)

    @patch('requests.get', side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        mock_id = PropertyMock(return_value='BAD')
        player = Player(None)
        type(player)._player_id = mock_id

        result = player._retrieve_html_page()

        assert result is None

    @patch('requests.get', side_effect=mock_pyquery)
    def test_missing_weight_returns_none(self, *args, **kwargs):
        mock_weight = PropertyMock(return_value=None)
        player = Player(None)
        type(player)._player_id = mock_weight

        result = player.weight

        assert result is None

    @patch('requests.get', side_effect=mock_pyquery)
    def test_attempted_passes_has_deprecation_warning(self, *args, **kwargs):
        mock_passes = PropertyMock(return_value=[32])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._pass_attempts = mock_passes
        type(player)._index = mock_index

        with pytest.deprecated_call():
            result = player.attempted_passes

            assert result == 32
