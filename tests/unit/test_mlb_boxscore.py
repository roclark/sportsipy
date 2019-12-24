from flexmock import flexmock
from mock import patch, PropertyMock
from pyquery import PyQuery as pq
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.mlb.boxscore import Boxscore, Boxscores
from sportsreference.mlb.constants import DAY, NIGHT
from urllib.error import HTTPError


class MockName:
    def __init__(self, name):
        self._name = name

    def text(self):
        return self._name


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


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents
            self.url = url
            self.reason = '404'
            self.headers = None

    return MockPQ(None)


class TestMLBBoxscore:
    @patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        self.boxscore = Boxscore(None)

    def test_away_team_wins(self):
        fake_away_runs = PropertyMock(return_value=6)
        fake_home_runs = PropertyMock(return_value=3)
        type(self.boxscore)._away_runs = fake_away_runs
        type(self.boxscore)._home_runs = fake_home_runs

        assert self.boxscore.winner == AWAY

    def test_home_team_wins(self):
        fake_away_runs = PropertyMock(return_value=3)
        fake_home_runs = PropertyMock(return_value=6)
        type(self.boxscore)._away_runs = fake_away_runs
        type(self.boxscore)._home_runs = fake_home_runs

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

    def test_game_summary_with_no_scores_returns_none(self):
        result = Boxscore(None)._parse_summary(pq(
            """<table class="linescore nohover stats_table no_freeze">
    <tbody>
        <tr>
            <td class="center"></td>
            <td class="center"></td>
            <td class="center"></td>
            <td class="center"></td>
        </tr>
        <tr>
            <td class="center"></td>
            <td class="center"></td>
            <td class="center"></td>
            <td class="center"></td>
        </tr>
    </tbody>
</table>"""
        ))

        assert result == {
            'away': [None],
            'home': [None]
        }

    @patch('requests.get', side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        result = Boxscore(None)._retrieve_html_page('')

        assert result is None

    def test_mlb_game_info(self):
        fields = {
            'attendance': 26340,
            'date': 'Monday, July 9, 2018',
            'time': '4:05 p.m. ET',
            'venue': 'Oriole Park at Camden Yards',
            'duration': '2:55',
            'time_of_day': 'Night'
        }

        mock_field = """Monday, July 9, 2018
Start Time: 4:05 p.m. ET
Attendance: 26,340
Venue: Oriole Park at Camden Yards
Game Duration: 2:55
Night Game, on grass
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_mlb_first_game_double_header_info(self):
        fields = {
            'attendance': None,
            'date': 'Monday, July 9, 2018',
            'time': '4:05 p.m. ET',
            'venue': 'Oriole Park at Camden Yards',
            'duration': '2:55',
            'time_of_day': 'Night'
        }

        mock_field = """Monday, July 9, 2018
Start Time: 4:05 p.m. ET
Venue: Oriole Park at Camden Yards
Game Duration: 2:55
Night Game, on grass
First game of doubleheader
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_mlb_second_game_double_header_info(self):
        fields = {
            'attendance': 26340,
            'date': 'Monday, July 9, 2018',
            'attendance': 26340,
            'venue': 'Oriole Park at Camden Yards',
            'duration': '3:13',
            'time_of_day': 'Night'
        }

        mock_field = """Monday, July 9, 2018
Attendance: 26,340
Venue: Oriole Park at Camden Yards
Game Duration: 3:13
Night Game, on grass
Second game of doubleheader
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_mlb_limited_game_info(self):
        fields = {
            'attendance': 19043,
            'date': 'Sunday, June 28, 1970',
            'time': None,
            'venue': 'Robert F. Kennedy Stadium',
            'duration': '3:43',
            'time_of_day': 'Day'
        }

        mock_field = """Sunday, June 28, 1970
Attendance: 19,043
Venue: Robert F. Kennedy Stadium
Game Duration: 3:43
Day Game, on grass
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_invalid_away_inherited_runners_returns_default(self):
        mock_runners = PropertyMock(return_value='')
        type(self.boxscore)._away_inherited_runners = mock_runners

        assert self.boxscore.away_inherited_runners is None

    def test_invalid_away_inherited_score_returns_default(self):
        mock_score = PropertyMock(return_value='')
        type(self.boxscore)._away_inherited_score = mock_score

        assert self.boxscore.away_inherited_score is None

    def test_invalid_home_inherited_runners_returns_default(self):
        mock_runners = PropertyMock(return_value='')
        type(self.boxscore)._home_inherited_runners = mock_runners

        assert self.boxscore.home_inherited_runners is None

    def test_invalid_home_inherited_score_returns_default(self):
        mock_score = PropertyMock(return_value='')
        type(self.boxscore)._home_inherited_score = mock_score

        assert self.boxscore.home_inherited_score is None

    def test_no_class_information_returns_dataframe_of_none(self):
        mock_runs = PropertyMock(return_value=None)
        type(self.boxscore)._away_runs = mock_runs
        type(self.boxscore)._home_runs = mock_runs

        assert self.boxscore.dataframe is None

    def test_attendance_with_empty_string(self):
        fake_attendance = PropertyMock(return_value='')
        type(self.boxscore)._attendance = fake_attendance

        assert self.boxscore.attendance is None

    def test_night_game_returns_night(self):
        fake_time_of_day = PropertyMock(return_value='night game on grass')
        type(self.boxscore)._time_of_day = fake_time_of_day

        assert self.boxscore.time_of_day == NIGHT

    def test_night_game_returns_night(self):
        fake_time_of_day = PropertyMock(return_value='day game on grass')
        type(self.boxscore)._time_of_day = fake_time_of_day

        assert self.boxscore.time_of_day == DAY


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
    <td><a href="/teams/BAL/2017.shtml">Baltimore Orioles</a></td>
    <td class="right">3</td>
    <td class="right">
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
    <td><a href="/teams/TEX/2017.shtml">Texas Rangers</a></td>
    <td class="right">1</td>
    <td class="right gamelink">
        <a href="/boxes/BAL/BAL201707170.shtml">Final</a>
    </td>
</tr>
<tr class="winner">
    <td class="right">3</td>
    <td class="right">
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
    <td><a href="/teams/TEX/2017.shtml">Texas Rangers</a></td>
    <td class="right gamelink">
        <a href="/boxes/BAL/BAL201707170.shtml">Final</a>
    </td>
</tr>
<tr class="loser">
    <td><a href="/teams/BAL/2017.shtml">Baltimore Orioles</a></td>
    <td class="right">
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                'away_abbr': 'TEX',
                'away_name': 'Texas Rangers',
                'away_score': None,
                'boxscore': 'BAL/BAL201707170',
                'home_abbr': 'BAL',
                'home_name': 'Baltimore Orioles',
                'home_score': None,
                'losing_abbr': None,
                'losing_name': None,
                'winning_abbr': None,
                'winning_name': None
            }
        ]
