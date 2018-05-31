from flexmock import flexmock
from mock import PropertyMock
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.ncaab.boxscore import Boxscore


class MockName:
    def __init__(self, name):
        self._name = name

    def text(self):
        return self._name


class TestNCAABBoxscore:
    def test_away_team_wins(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_away_points = PropertyMock(return_value=75)
        fake_home_points = PropertyMock(return_value=70)
        type(boxscore)._away_points = fake_away_points
        type(boxscore)._home_points = fake_home_points

        assert boxscore.winner == AWAY

    def test_home_team_wins(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_away_points = PropertyMock(return_value=70)
        fake_home_points = PropertyMock(return_value=75)
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

    def test_invalid_away_record_returns_default_wins(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(boxscore)._away_record = fake_record

        assert boxscore.away_wins == 0

    def test_invalid_away_record_returns_default_losses(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(boxscore)._away_record = fake_record

        assert boxscore.away_losses == 0

    def test_invalid_home_record_returns_default_wins(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(boxscore)._home_record = fake_record

        assert boxscore.home_wins == 0

    def test_invalid_home_record_returns_default_losses(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(boxscore)._home_record = fake_record

        assert boxscore.home_losses == 0
