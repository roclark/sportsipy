from flexmock import flexmock
from mock import patch, PropertyMock
from sportsreference.mlb.roster import _cleanup, Player


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


class TestMLBPlayer:
    def setup_method(self):
        flexmock(Player) \
            .should_receive('_parse_player_data') \
            .and_return(None)
        flexmock(Player) \
            .should_receive('_find_initial_index') \
            .and_return(None)

    def test_no_int_returns_default_value(self):
        mock_runs = PropertyMock(return_value=[''])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._runs = mock_runs
        type(player)._index = mock_index

        result = player.runs

        assert result is None

    def test_no_float_returns_default_value(self):
        mock_batting_average = PropertyMock(return_value=[''])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._batting_average = mock_batting_average
        type(player)._index = mock_index

        result = player.batting_average

        assert result is None

    def test_no_recent_returns_default_value(self):
        mock_position = PropertyMock(return_value=[''])
        mock_season = PropertyMock(return_value='2018')
        mock_seasons = PropertyMock(return_value=['2018'])
        player = Player(None)
        type(player)._position = mock_position
        type(player)._season = mock_seasons
        type(player)._most_recent_season = mock_season

        result = player.position

        assert result is None

    @patch('requests.get', side_effect=mock_pyquery)
    def test_invalid_url_return_none(self, *args, **kwargs):
        mock_id = PropertyMock(return_value='BAD')
        player = Player(None)
        type(player)._player_id = mock_id

        result = player._retrieve_html_page()

        assert result is None

    def test_cleanup_of_none_returns_default(self):
        result = _cleanup(None)

        assert result == ''
