from flexmock import flexmock
from mock import patch, PropertyMock
from sportsreference.ncaab.roster import cleanup, Player


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ(None)


class TestNCAABPlayer:
    def setup_method(self):
        flexmock(Player) \
            .should_receive('_parse_player_data') \
            .and_return(None)
        flexmock(Player) \
            .should_receive('_find_initial_index') \
            .and_return(None)

    def test_no_int_return_default_value(self):
        mock_field_goals = PropertyMock(return_value=[''])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._field_goals = mock_field_goals
        type(player)._index = mock_index

        result = player.field_goals

        assert result == 0

    def test_no_float_returns_default_value(self):
        mock_percentage = PropertyMock(return_value=[''])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._field_goal_percentage = mock_percentage
        type(player)._index = mock_index

        result = player.field_goal_percentage

        assert result == 0.0

    @patch('requests.get', side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        mock_id = PropertyMock(return_value='BAD')
        player = Player(None)
        type(player)._player_id = mock_id

        result = player._retrieve_html_page()

        assert result is None

    def test_cleanup_of_none_returns_default(self):
        result = cleanup(None)

        assert result == ''
