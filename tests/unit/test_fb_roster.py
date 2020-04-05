import mock
import pytest
from flexmock import flexmock
from pyquery import PyQuery as pq
from sportsreference.fb.roster import SquadPlayer, Roster
from urllib.error import HTTPError


class MockSquadPlayer:
    def __init__(self, name=None, player_id=None):
        self.name = name
        self.player_id = player_id

    def __call__(self, obj):
        return pq('<tr></tr>')


def mock_httperror(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 504
            self.html_contents = html_contents
            self.text = html_contents
            self.url = url
            self.reason = HTTPError
            self.headers = None

    return MockPQ(None)


class TestFBRoster:
    def setup_method(self):
        flexmock(Roster) \
            .should_receive('__init__') \
            .and_return(None)
        flexmock(SquadPlayer) \
            .should_receive('_parse_player_stats') \
            .and_return(None)
        self.roster = Roster(None)
        self.player = SquadPlayer(None, None)

    def test_no_country_returns_none(self):
        result = self.player._parse_nationality(pq('<tr></tr>'))

        assert not result

    def test_no_player_name_or_player_id_raises_value_error(self):
        self.roster._players = [MockSquadPlayer()]

        with pytest.raises(ValueError):
            self.roster('')

    def test_invalid_player_id_returns_none(self):
        result = self.roster._player_id(pq('<th data-stat="player"></th>'))

        assert not result

    def test_no_player_id_skips_player(self):
        result = self.roster._add_stats_data([MockSquadPlayer()], {})

        assert result == {}

    @mock.patch('requests.get', side_effect=mock_httperror)
    def test_invalid_http_page_error(self, *args, **kwargs):
        flexmock(Roster) \
            .should_receive('__init__') \
            .and_return(None)
        roster = Roster(None)
        roster._squad_id = ''

        output = roster._pull_stats(None)

        assert not output
