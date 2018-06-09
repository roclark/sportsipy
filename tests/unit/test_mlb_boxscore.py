from flexmock import flexmock
from mock import PropertyMock
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.mlb.boxscore import Boxscore
from sportsreference.mlb.constants import DAY, NIGHT


class MockName:
    def __init__(self, name):
        self._name = name

    def text(self):
        return self._name


class TestMLBBoxscore:
    def test_night_game_returns_night(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_time_of_day = PropertyMock(return_value='night game on grass')
        type(boxscore)._time_of_day = fake_time_of_day

        assert boxscore.time_of_day == NIGHT

    def test_night_game_returns_night(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_time_of_day = PropertyMock(return_value='day game on grass')
        type(boxscore)._time_of_day = fake_time_of_day

        assert boxscore.time_of_day == DAY

    def test_away_team_wins(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_away_runs = PropertyMock(return_value=6)
        fake_home_runs = PropertyMock(return_value=3)
        type(boxscore)._away_runs = fake_away_runs
        type(boxscore)._home_runs = fake_home_runs

        assert boxscore.winner == AWAY

    def test_home_team_wins(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_away_runs = PropertyMock(return_value=3)
        fake_home_runs = PropertyMock(return_value=6)
        type(boxscore)._away_runs = fake_away_runs
        type(boxscore)._home_runs = fake_home_runs

        assert boxscore.winner == HOME

    def test_winning_name_is_home(self):
        expected_name = 'Home Name'

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_winner = PropertyMock(return_value=HOME)
        fake_home_name = PropertyMock(return_value=MockName(expected_name))
        type(boxscore).winner = fake_winner
        type(boxscore)._home_name = fake_home_name

        assert boxscore.winning_name == expected_name

    def test_winning_name_is_away(self):
        expected_name = 'Away Name'

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_name = PropertyMock(return_value=MockName(expected_name))
        type(boxscore).winner = fake_winner
        type(boxscore)._away_name = fake_away_name

        assert boxscore.winning_name == expected_name

    def test_winning_abbr_is_home(self):
        expected_name = 'HOME'

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        boxscore = Boxscore(None)
        fake_winner = PropertyMock(return_value=HOME)
        fake_home_abbr = PropertyMock(return_value=MockName(expected_name))
        type(boxscore).winner = fake_winner
        type(boxscore)._home_abbr = fake_home_abbr

        assert boxscore.winning_abbr == expected_name

    def test_winning_abbr_is_away(self):
        expected_name = 'AWAY'

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        boxscore = Boxscore(None)
        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_abbr = PropertyMock(return_value=MockName(expected_name))
        type(boxscore).winner = fake_winner
        type(boxscore)._away_abbr = fake_away_abbr

        assert boxscore.winning_abbr == expected_name

    def test_losing_name_is_home(self):
        expected_name = 'Home Name'

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_name = PropertyMock(return_value=MockName(expected_name))
        type(boxscore).winner = fake_winner
        type(boxscore)._home_name = fake_home_name

        assert boxscore.losing_name == expected_name

    def test_losing_name_is_away(self):
        expected_name = 'Away Name'

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_winner = PropertyMock(return_value=HOME)
        fake_away_name = PropertyMock(return_value=MockName(expected_name))
        type(boxscore).winner = fake_winner
        type(boxscore)._away_name = fake_away_name

        assert boxscore.losing_name == expected_name

    def test_losing_abbr_is_home(self):
        expected_name = 'HOME'

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        boxscore = Boxscore(None)
        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_abbr = PropertyMock(return_value=MockName(expected_name))
        type(boxscore).winner = fake_winner
        type(boxscore)._home_abbr = fake_home_abbr

        assert boxscore.losing_abbr == expected_name

    def test_losing_abbr_is_away(self):
        expected_name = 'AWAY'

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        boxscore = Boxscore(None)
        fake_winner = PropertyMock(return_value=HOME)
        fake_away_abbr = PropertyMock(return_value=MockName(expected_name))
        type(boxscore).winner = fake_winner
        type(boxscore)._away_abbr = fake_away_abbr

        assert boxscore.losing_abbr == expected_name
