from flexmock import flexmock
from mock import PropertyMock
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.nhl.boxscore import Boxscore


class MockName:
    def __init__(self, name):
        self._name = name

    def text(self):
        return self._name


class TestNHLBoxscore:
    def test_away_team_wins(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_away_goals = PropertyMock(return_value=4)
        fake_home_goals = PropertyMock(return_value=3)
        type(boxscore)._away_goals = fake_away_goals
        type(boxscore)._home_goals = fake_home_goals

        assert boxscore.winner == AWAY

    def test_home_team_wins(self):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_away_goals = PropertyMock(return_value=3)
        fake_home_goals = PropertyMock(return_value=4)
        type(boxscore)._away_goals = fake_away_goals
        type(boxscore)._home_goals = fake_home_goals

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

    def test_invalid_away_game_winning_goals_returns_default(self):
        goals = ['0', '1', 'bad']

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_goals = PropertyMock(return_value=goals)
        fake_num_skaters = PropertyMock(return_value=3)
        type(boxscore)._away_game_winning_goals = fake_goals
        type(boxscore)._away_skaters = fake_num_skaters

        assert boxscore.away_game_winning_goals == 1

    def test_invalid_away_even_strength_assists_returns_default(self):
        assists = ['0', '1', 'bad']

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=3)
        type(boxscore)._away_even_strength_assists = fake_assists
        type(boxscore)._away_skaters = fake_num_skaters

        assert boxscore.away_even_strength_assists == 1

    def test_invalid_home_even_strength_assists_returns_default(self):
        assists = ['0', '1', 'bad']

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=0)
        type(boxscore)._home_even_strength_assists = fake_assists
        type(boxscore)._away_skaters = fake_num_skaters

        assert boxscore.home_even_strength_assists == 1

    def test_invalid_away_power_play_assists_returns_default(self):
        assists = ['0', '1', 'bad']

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=3)
        type(boxscore)._away_power_play_assists = fake_assists
        type(boxscore)._away_skaters = fake_num_skaters

        assert boxscore.away_power_play_assists == 1

    def test_invalid_home_power_play_assits_returns_default(self):
        assists = ['0', '1', 'bad']

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=0)
        type(boxscore)._home_power_play_assists = fake_assists
        type(boxscore)._away_skaters = fake_num_skaters

        assert boxscore.home_power_play_assists == 1

    def test_invalid_away_short_handed_assists_returns_default(self):
        assists = ['0', '1', 'bad']

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=3)
        type(boxscore)._away_short_handed_assists = fake_assists
        type(boxscore)._away_skaters = fake_num_skaters

        assert boxscore.away_short_handed_assists == 1

    def test_invalid_home_short_handed_assits_returns_default(self):
        assists = ['0', '1', 'bad']

        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        boxscore = Boxscore(None)
        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=0)
        type(boxscore)._home_short_handed_assists = fake_assists
        type(boxscore)._away_skaters = fake_num_skaters

        assert boxscore.home_short_handed_assists == 1
