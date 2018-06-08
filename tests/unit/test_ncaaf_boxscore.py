from flexmock import flexmock
from mock import PropertyMock
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.ncaaf.boxscore import Boxscore


class MockName:
    def __init__(self, name):
        self._name = name

    def text(self):
        return self._name


class TestNCAAFBoxscore:
    def test_away_team_wins(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_away_points = PropertyMock(return_value=28)
        fake_home_points = PropertyMock(return_value=21)
        type(boxscore)._away_points = fake_away_points
        type(boxscore)._home_points = fake_home_points

        assert boxscore.winner == AWAY

    def test_home_team_wins(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_away_points = PropertyMock(return_value=21)
        fake_home_points = PropertyMock(return_value=28)
        type(boxscore)._away_points = fake_away_points
        type(boxscore)._home_points = fake_home_points

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
