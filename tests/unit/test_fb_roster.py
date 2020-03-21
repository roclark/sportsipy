import pytest
from flexmock import flexmock
from pyquery import PyQuery as pq
from sportsreference.fb.roster import SquadPlayer, Roster


class MockSquadPlayer:
    def __init__(self, name=None, player_id=None):
        self.name = name
        self.player_id = player_id

    def __call__(self, obj):
        return pq('<tr></tr>')


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
