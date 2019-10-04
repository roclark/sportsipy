from flexmock import flexmock
from mock import patch, PropertyMock
from sportsreference.nba.player import (AbstractPlayer,
                                        _cleanup as _cleanup_player)
from sportsreference.nba.roster import _cleanup, Player


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
            self.url = url
            self.reason = 'Bad URL'  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ(None)


class TestNBAPlayer:
    def setup_method(self):
        flexmock(AbstractPlayer) \
            .should_receive('_parse_player_data') \
            .and_return(None)
        flexmock(Player) \
            .should_receive('__init__') \
            .and_return(None)

    def test_no_float_returns_default_value_abstract_class(self):
        mock_percentage = PropertyMock(return_value=[''])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._field_goal_percentage = mock_percentage
        type(player)._index = mock_index

        result = player.field_goal_percentage

        assert result is None

    def test_no_float_returns_default_value_player_class(self):
        mock_rating = PropertyMock(return_value=[''])
        mock_index = PropertyMock(return_value=0)
        player = Player(None)
        type(player)._player_efficiency_rating = mock_rating
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


class TestInvalidNBAPlayer:
    def test_no_player_data_returns_no_stats(self):
        flexmock(Player) \
            .should_receive('_retrieve_html_page') \
            .and_return(None)

        stats = Player(None)._pull_player_data()

        assert stats is None
