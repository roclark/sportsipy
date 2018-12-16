from flexmock import flexmock
from mock import patch, PropertyMock
from pyquery import PyQuery as pq
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.nhl.boxscore import Boxscore, Boxscores


class MockField:
    def __init__(self, field):
        self._field = field

    def text(self):
        return self._field


class MockBoxscoreData:
    def __init__(self, fields):
        self._fields = fields

    def __call__(self, field):
        return self

    def items(self):
        return [self._fields]


class MockName:
    def __init__(self, name):
        self._name = name

    def text(self):
        return self._name


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class TestNHLBoxscore:
    @patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        self.boxscore = Boxscore(None)

    def test_away_team_wins(self):
        fake_away_goals = PropertyMock(return_value=4)
        fake_home_goals = PropertyMock(return_value=3)
        type(self.boxscore)._away_goals = fake_away_goals
        type(self.boxscore)._home_goals = fake_home_goals

        assert self.boxscore.winner == AWAY

    def test_home_team_wins(self):
        fake_away_goals = PropertyMock(return_value=3)
        fake_home_goals = PropertyMock(return_value=4)
        type(self.boxscore)._away_goals = fake_away_goals
        type(self.boxscore)._home_goals = fake_home_goals

        assert self.boxscore.winner == HOME

    def test_winning_name_is_home(self):
        expected_name = 'Home Name'

        fake_winner = PropertyMock(return_value=HOME)
        fake_home_name = PropertyMock(return_value=MockName(expected_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_is_away(self):
        expected_name = 'Away Name'

        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_name = PropertyMock(return_value=MockName(expected_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.winning_name == expected_name

    def test_winning_abbr_is_home(self):
        expected_name = 'HOME'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=HOME)
        fake_home_abbr = PropertyMock(return_value=MockName(expected_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_abbr = fake_home_abbr

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_is_away(self):
        expected_name = 'AWAY'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_abbr = PropertyMock(return_value=MockName(expected_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_abbr = fake_away_abbr

        assert self.boxscore.winning_abbr == expected_name

    def test_losing_name_is_home(self):
        expected_name = 'Home Name'

        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_name = PropertyMock(return_value=MockName(expected_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_is_away(self):
        expected_name = 'Away Name'

        fake_winner = PropertyMock(return_value=HOME)
        fake_away_name = PropertyMock(return_value=MockName(expected_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.losing_name == expected_name

    def test_losing_abbr_is_home(self):
        expected_name = 'HOME'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_abbr = PropertyMock(return_value=MockName(expected_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_abbr = fake_home_abbr

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_is_away(self):
        expected_name = 'AWAY'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=HOME)
        fake_away_abbr = PropertyMock(return_value=MockName(expected_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_abbr = fake_away_abbr

        assert self.boxscore.losing_abbr == expected_name

    def test_invalid_away_game_winning_goals_returns_default(self):
        goals = ['0', '1', 'bad']

        fake_goals = PropertyMock(return_value=goals)
        fake_num_skaters = PropertyMock(return_value=3)
        fake_num_goalies = PropertyMock(return_value=0)
        type(self.boxscore)._away_game_winning_goals = fake_goals
        type(self.boxscore)._away_skaters = fake_num_skaters
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.away_game_winning_goals == 1

    def test_invalid_away_even_strength_assists_returns_default(self):
        assists = ['0', '1', 'bad']

        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=3)
        fake_num_goalies = PropertyMock(return_value=0)
        type(self.boxscore)._away_even_strength_assists = fake_assists
        type(self.boxscore)._away_skaters = fake_num_skaters
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.away_even_strength_assists == 1

    def test_invalid_home_even_strength_assists_returns_default(self):
        assists = ['0', '1', 'bad']

        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=0)
        fake_num_goalies = PropertyMock(return_value=0)
        type(self.boxscore)._home_even_strength_assists = fake_assists
        type(self.boxscore)._away_skaters = fake_num_skaters
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.home_even_strength_assists == 1

    def test_invalid_away_power_play_assists_returns_default(self):
        assists = ['0', '1', 'bad']

        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=3)
        fake_num_goalies = PropertyMock(return_value=0)
        type(self.boxscore)._away_power_play_assists = fake_assists
        type(self.boxscore)._away_skaters = fake_num_skaters
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.away_power_play_assists == 1

    def test_invalid_home_power_play_assits_returns_default(self):
        assists = ['0', '1', 'bad']

        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=0)
        fake_num_goalies = PropertyMock(return_value=0)
        type(self.boxscore)._home_power_play_assists = fake_assists
        type(self.boxscore)._away_skaters = fake_num_skaters
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.home_power_play_assists == 1

    def test_invalid_away_short_handed_assists_returns_default(self):
        assists = ['0', '1', 'bad']

        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=3)
        fake_num_goalies = PropertyMock(return_value=0)
        type(self.boxscore)._away_short_handed_assists = fake_assists
        type(self.boxscore)._away_skaters = fake_num_skaters
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.away_short_handed_assists == 1

    def test_invalid_home_short_handed_assits_returns_default(self):
        assists = ['0', '1', 'bad']

        fake_assists = PropertyMock(return_value=assists)
        fake_num_skaters = PropertyMock(return_value=0)
        fake_num_goalies = PropertyMock(return_value=0)
        type(self.boxscore)._home_short_handed_assists = fake_assists
        type(self.boxscore)._away_skaters = fake_num_skaters
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.home_short_handed_assists == 1

    def test_invalid_url_returns_none(self):
        result = Boxscore(None)._retrieve_html_page('')

        assert result is None

    def test_regular_season_information(self):
        fields = {
            'date': 'October 5, 2017',
            'playoff_round': None,
            'time': '7:00 PM',
            'attendance': 17565,
            'arena': 'TD Garden',
            'duration': '2:39'
        }

        mock_field = """October 5, 2017, 7:00 PM
Attendance: 17,565
Arena: TD Garden
Game Duration: 2:39
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_playoffs_information(self):
        fields = {
            'date': 'June 7, 2018',
            'playoff_round': 'Stanley Cup Final',
            'time': '8:00 PM',
            'attendance': 18529,
            'arena': 'T-Mobile Arena',
            'duration': '2:45'
        }

        mock_field = """June 7, 2018, 8:00 PM
Stanley Cup Final
Attendance: 18,529
Arena: T-Mobile Arena
Game Duration: 2:45
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_no_game_information(self):
        fields = {
            'date': '',
            'playoff_round': None,
            'time': None,
            'attendance': None,
            'arena': None,
            'duration': None
        }

        mock_field = '\n'

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_limited_game_information(self):
        fields = {
            'date': 'June 7, 2018',
            'playoff_round': 'Stanley Cup Final',
            'time': None,
            'attendance': None,
            'arena': 'T-Mobile Arena',
            'duration': None
        }

        mock_field = """June 7, 2018
Stanley Cup Final
Arena: T-Mobile Arena
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_away_shutout_single_goalies(self):
        shutout = ['1', '0']

        fake_shutout = PropertyMock(return_value=shutout)
        fake_num_goalies = PropertyMock(return_value=1)
        type(self.boxscore)._away_shutout = fake_shutout
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.away_shutout == 1

    def test_away_shutout_multiple_goalies(self):
        shutout = ['0', '1', '0']

        fake_shutout = PropertyMock(return_value=shutout)
        fake_num_goalies = PropertyMock(return_value=2)
        type(self.boxscore)._away_shutout = fake_shutout
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.away_shutout == 1

    def test_away_shutout_multiple_goalies_empty_field(self):
        shutout = ['', '1', '0']

        fake_shutout = PropertyMock(return_value=shutout)
        fake_num_goalies = PropertyMock(return_value=2)
        type(self.boxscore)._away_shutout = fake_shutout
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.away_shutout == 1

    def test_home_shutout_single_goalies(self):
        shutout = ['0', '1']

        fake_shutout = PropertyMock(return_value=shutout)
        fake_num_goalies = PropertyMock(return_value=1)
        type(self.boxscore)._home_shutout = fake_shutout
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.home_shutout == 1

    def test_home_shutout_multiple_goalies(self):
        shutout = ['0', '0', '1']

        fake_shutout = PropertyMock(return_value=shutout)
        fake_num_goalies = PropertyMock(return_value=1)
        type(self.boxscore)._home_shutout = fake_shutout
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.home_shutout == 1

    def test_home_shutout_multiple_goalies_empty_field(self):
        shutout = ['0', '', '1']

        fake_shutout = PropertyMock(return_value=shutout)
        fake_num_goalies = PropertyMock(return_value=1)
        type(self.boxscore)._home_shutout = fake_shutout
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.home_shutout == 1

    def test_away_saves_single_goalies(self):
        saves = ['29', '30']

        fake_saves = PropertyMock(return_value=saves)
        fake_num_goalies = PropertyMock(return_value=1)
        type(self.boxscore)._away_saves = fake_saves
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.away_saves == 29

    def test_away_saves_multiple_goalies_empty_field(self):
        saves = ['29', '3', '30']

        fake_saves = PropertyMock(return_value=saves)
        fake_num_goalies = PropertyMock(return_value=2)
        type(self.boxscore)._away_saves = fake_saves
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.away_saves == 32

    def test_away_saves_multiple_goalies_empty_field(self):
        saves = ['29', '', '30']

        fake_saves = PropertyMock(return_value=saves)
        fake_num_goalies = PropertyMock(return_value=2)
        type(self.boxscore)._away_saves = fake_saves
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.away_saves == 29

    def test_home_saves_single_goalies(self):
        saves = ['29', '30']

        fake_saves = PropertyMock(return_value=saves)
        fake_num_goalies = PropertyMock(return_value=1)
        type(self.boxscore)._home_saves = fake_saves
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.home_saves == 30

    def test_home_saves_multiple_goalies_empty_field(self):
        saves = ['29', '3', '30']

        fake_saves = PropertyMock(return_value=saves)
        fake_num_goalies = PropertyMock(return_value=1)
        type(self.boxscore)._home_saves = fake_saves
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.home_saves == 33

    def test_home_saves_multiple_goalies_empty_field(self):
        saves = ['29', '30', '']

        fake_saves = PropertyMock(return_value=saves)
        fake_num_goalies = PropertyMock(return_value=1)
        type(self.boxscore)._home_saves = fake_saves
        type(self.boxscore)._away_goalies = fake_num_goalies

        assert self.boxscore.home_saves == 30

    def test_away_save_percentage(self):
        fake_saves = PropertyMock(return_value=30)
        fake_shots_on_goal = PropertyMock(return_value=33)
        type(self.boxscore).away_saves = fake_saves
        type(self.boxscore).home_shots_on_goal = fake_shots_on_goal

        assert self.boxscore.away_save_percentage == 0.909

    def test_away_save_percentage_zero_shots(self):
        fake_saves = PropertyMock(return_value=0)
        fake_shots_on_goal = PropertyMock(return_value=0)
        type(self.boxscore).away_saves = fake_saves
        type(self.boxscore).home_shots_on_goal = fake_shots_on_goal

        assert self.boxscore.away_save_percentage == 0.0

    def test_home_save_percentage(self):
        fake_saves = PropertyMock(return_value=30)
        fake_shots_on_goal = PropertyMock(return_value=33)
        type(self.boxscore).home_saves = fake_saves
        type(self.boxscore).away_shots_on_goal = fake_shots_on_goal

        assert self.boxscore.home_save_percentage == 0.909

    def test_home_save_percentage_zero_shots(self):
        fake_saves = PropertyMock(return_value=0)
        fake_shots_on_goal = PropertyMock(return_value=0)
        type(self.boxscore).home_saves = fake_saves
        type(self.boxscore).away_shots_on_goal = fake_shots_on_goal

        assert self.boxscore.home_save_percentage == 0.0

    def test_no_class_information_returns_dataframe_of_none(self):
        mock_goals = PropertyMock(return_value=None)
        type(self.boxscore)._away_goals = mock_goals
        type(self.boxscore)._home_goals = mock_goals

        assert self.boxscore.dataframe is None


class TestMLBBoxscores:
    @patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        flexmock(Boxscores) \
            .should_receive('_find_games') \
            .and_return(None)
        self.boxscores = Boxscores(None)

    def test_improper_loser_boxscore_format_skips_game(self):
        flexmock(Boxscores) \
            .should_receive('_get_team_details') \
            .and_return((None, None, None, None, None, None))
        mock_html = pq("""<table class="teams">
<tbody>
<tr class="loser">
    <td class="right">1</td>
    <td class="right gamelink">
    </td>
</tr>
<tr class="winner">
    <td><a href="/teams/DET/2019.html">Detroit Red Wings</a></td>
    <td class="right">3</td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert len(games) == 0

    def test_improper_winner_boxscore_format_skips_game(self):
        flexmock(Boxscores) \
            .should_receive('_get_team_details') \
            .and_return((None, None, None, None, None, None))
        mock_html = pq("""<table class="teams">
<tbody>
<tr class="loser">
    <td><a href="/teams/LAK/2019.html">Los Angeles Kings</a></td>
    <td class="right">1</td>
    <td class="right gamelink">
        <a href="/boxscores/201812100DET.html">Final</a>
    </td>
</tr>
<tr class="winner">
    <td class="right">3</td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert len(games) == 0

    def test_boxscore_with_no_score_returns_none(self):
        mock_html = pq("""<table class="teams">
<tbody>
<tr class="loser">
    <td><a href="/teams/LAK/2019.html">Los Angeles Kings</a></td>
    <td class="right gamelink">
        <a href="/boxscores/201812100DET.html">Final</a>
    </td>
</tr>
<tr class="loser">
    <td><a href="/teams/DET/2019.html">Detroit Red Wings</a></td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                'away_abbr': 'LAK',
                'away_name': 'Los Angeles Kings',
                'away_score': None,
                'boxscore': '201812100DET',
                'home_abbr': 'DET',
                'home_name': 'Detroit Red Wings',
                'home_score': None,
                'losing_abbr': None,
                'losing_name': None,
                'winning_abbr': None,
                'winning_name': None
            }
        ]
