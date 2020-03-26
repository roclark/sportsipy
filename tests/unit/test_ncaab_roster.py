from flexmock import flexmock
from mock import patch, PropertyMock
from sportsreference.ncaab.player import (AbstractPlayer,
                                          _cleanup as _cleanup_player)
from sportsreference.ncaab.roster import _cleanup, Player


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


class TestNCAABPlayer:
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

    def test_no_int_return_default_value_abstract_class(self):
        mock_field_goals = PropertyMock(return_value=[''])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._field_goals = mock_field_goals
        type(player)._index = mock_index

        result = player.field_goals

        assert result is None

    def test_no_float_returns_default_value_abstract_class(self):
        mock_percentage = PropertyMock(return_value=[''])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._field_goal_percentage = mock_percentage
        type(player)._index = mock_index

        result = player.field_goal_percentage

        assert result is None

    def test_no_int_return_default_value_player_class(self):
        mock_games = PropertyMock(return_value=[''])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._games_played = mock_games
        type(player)._index = mock_index

        result = player.games_played

        assert result is None

    def test_no_float_returns_default_value_player_class(self):
        mock_player_efficiency_rating = PropertyMock(return_value=[''])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._player_efficiency_rating = mock_player_efficiency_rating
        type(player)._index = mock_index

        result = player.player_efficiency_rating

        assert result is None

    @patch('requests.get', side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        mock_id = PropertyMock(return_value='BAD')
        player = Player(None)
        type(player)._player_id = mock_id

        result = player._retrieve_html_page()

        assert result is None

    def test_cleanup_of_none_returns_default(self):
        result = _cleanup(None)

        assert result == ''

    def test_cleanup_of_none_returns_default_for_player(self):
        result = _cleanup_player(None)

        assert result == ''

    def test_player_with_no_stats(self):
        player = Player(None)
        result = player._combine_season_stats(None, None, {})

        assert result == {}

    def test_player_with_no_weight_returns_none(self):
        mock_weight = PropertyMock(return_value=None)
        player = Player(None)
        type(player)._weight = mock_weight

        result = player.weight

        assert result is None
