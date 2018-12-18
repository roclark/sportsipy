from flexmock import flexmock
from mock import patch, PropertyMock
from pyquery import PyQuery as pq
from os.path import dirname, join
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.nfl.boxscore import Boxscore, Boxscores


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


def read_file(filename):
    filepath = join(dirname(__file__), 'nfl', filename)
    return open(filepath, 'r').read()


def mock_pyquery(url, status_code=404):
    class MockPQ:
        def __init__(self, html_contents, status_code=404):
            self.url = url
            self.reason = 'Bad URL'  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

    if url == '404':
        return MockPQ('404 error', 200)
    if 'bad' in url:
        return MockPQ(None)
    return MockPQ(read_file('%s.htm' % url))


class TestNFLBoxscore:
    @patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        self.boxscore = Boxscore(None)

    def test_away_team_wins(self):
        fake_away_points = PropertyMock(return_value=28)
        fake_home_points = PropertyMock(return_value=21)
        type(self.boxscore)._away_points = fake_away_points
        type(self.boxscore)._home_points = fake_home_points

        assert self.boxscore.winner == AWAY

    def test_home_team_wins(self):
        fake_away_points = PropertyMock(return_value=21)
        fake_home_points = PropertyMock(return_value=28)
        type(self.boxscore)._away_points = fake_away_points
        type(self.boxscore)._home_points = fake_home_points

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

    @patch('requests.get', side_effect=mock_pyquery)
    def test_invalid_url_returns_none(self, *args, **kwargs):
        result = Boxscore(None)._retrieve_html_page('bad')

        assert result is None

    def test_url_404_page_returns_none(self):
        result = Boxscore(None)._retrieve_html_page('404')

        assert result is None

    def test_no_class_information_returns_dataframe_of_none(self):
        mock_points = PropertyMock(return_value=None)
        type(self.boxscore)._home_points = mock_points
        type(self.boxscore)._away_points = mock_points

        assert self.boxscore.dataframe is None

    def test_empty_attribute_returns_none(self):
        fake_rushes = PropertyMock(return_value=None)
        type(self.boxscore)._away_rush_attempts = fake_rushes

        assert self.boxscore.away_rush_attempts is None

    def test_non_int_value_returns_none(self):
        fake_rushes = PropertyMock(return_value='bad')
        type(self.boxscore)._away_rush_attempts = fake_rushes

        assert self.boxscore.away_rush_attempts is None

    def test_nfl_game_information(self):
        fields = {
            'attendance': 62881,
            'date': 'Thursday Nov 8, 2018',
            'duration': '2:49',
            'stadium': 'Heinz Field',
            'time': '8:20pm'
        }

        mock_field = """Thursday Nov 8, 2018
Start Time: 8:20pm
Stadium: Heinz Field
Attendance: 62,881
Time of Game: 2:49
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_nfl_game_limited_information(self):
        fields = {
            'attendance': 22000,
            'date': 'Sunday Sep 8, 1940',
            'duration': None,
            'stadium': 'Forbes Field',
            'time': None
        }

        mock_field = """Sunday Sep 8, 1940
Stadium: Forbes Field
Attendance: 22,000
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value


class TestNFLBoxscores:
    @patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        flexmock(Boxscores) \
            .should_receive('_find_games') \
            .and_return(None)
        self.boxscores = Boxscores(None, None)

    def test_improper_loser_boxscore_format_skips_game(self):
        flexmock(Boxscores) \
            .should_receive('_get_team_details') \
            .and_return((None, None, None, None, None, None))
        mock_html = pq("""<table class="teams">
<tbody>
<tr class="date"><td colspan=3>Dec 9, 2018</td></tr>

<tr class="winner">
    <td><a href="/teams/nyj/2018.htm">New York Jets</a></td>
    <td class="right">27</td>
    <td class="right gamelink">
        <a href="/boxscores/201812090buf.htm">Final</a>
    </td>
</tr>
<tr class="loser">
    <td class="right">23</td>
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
<tr class="date"><td colspan=3>Dec 9, 2018</td></tr>

<tr class="winner">
    <td class="right">27</td>
    <td class="right gamelink">
    </td>
</tr>
<tr class="loser">
    <td><a href="/teams/buf/2018.htm">Buffalo Bills</a></td>
    <td class="right">23</td>
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
<tr class="date"><td colspan=3>Dec 9, 2018</td></tr>

<tr class="loser">
    <td><a href="/teams/nyj/2018.htm">New York Jets</a></td>
    <td class="right gamelink">
        <a href="/boxscores/201812090buf.htm">Final</a>
    </td>
</tr>
<tr class="loser">
    <td><a href="/teams/buf/2018.htm">Buffalo Bills</a></td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                'home_name': 'Buffalo Bills',
                'home_abbr': 'buf',
                'away_name': 'New York Jets',
                'away_abbr': 'nyj',
                'boxscore': '201812090buf',
                'winning_name': None,
                'winning_abbr': None,
                'losing_name': None,
                'losing_abbr': None,
                'home_score': None,
                'away_score': None
            }
        ]
