from flexmock import flexmock
from mock import patch, PropertyMock
from sportsreference.nba.roster import cleanup, Player


class MockItem:
    def attr(self, item):
        return 'contracts_'


class MockInfo:
    def __call__(self, item):
        return self

    def items(self):
        return [MockItem()]


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ(None)


class TestNBAPlayer:
    def setup_method(self):
        flexmock(Player) \
            .should_receive('_parse_player_data') \
            .and_return(None)
        flexmock(Player) \
            .should_receive('_find_initial_index') \
            .and_return(None)

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
        flexmock(Player) \
            .should_receive('_build_url') \
            .and_return('')

        result = Player(None)._retrieve_html_page()

        assert result is None

    def test_cleanup_of_none_returns_default(self):
        result = cleanup(None)

        assert result == ''

    def test_empty_contract_is_none(self):
        player_info = MockInfo()

        flexmock(Player) \
            .should_receive('_parse_contract_headers') \
            .and_return(None)

        flexmock(Player) \
            .should_receive('_parse_contract_wages') \
            .and_return(None)

        flexmock(Player) \
            .should_receive('_combine_contract') \
            .and_return({})

        player = Player(None)

        result = player._parse_contract(player_info)

        assert player._contract is None
