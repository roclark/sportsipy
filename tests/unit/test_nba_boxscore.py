from flexmock import flexmock
from mock import patch, PropertyMock
from pyquery import PyQuery as pq
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.nba.boxscore import Boxscore, Boxscores


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

    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class TestNBABoxscore:
    @patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        self.boxscore = Boxscore(None)

    def test_away_team_wins(self):
        fake_away_points = PropertyMock(return_value=75)
        fake_home_points = PropertyMock(return_value=70)
        type(self.boxscore)._away_points = fake_away_points
        type(self.boxscore)._home_points = fake_home_points

        assert self.boxscore.winner == AWAY

    def test_home_team_wins(self):
        fake_away_points = PropertyMock(return_value=70)
        fake_home_points = PropertyMock(return_value=75)
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

    def test_invalid_away_record_returns_default_wins(self):
        fake_record = PropertyMock(return_value='Golden State Warriors 1')
        type(self.boxscore)._away_record = fake_record

        assert self.boxscore.away_wins == 0

    def test_invalid_away_record_returns_default_losses(self):
        fake_record = PropertyMock(return_value='Golden State Warriors 1')
        type(self.boxscore)._away_record = fake_record

        assert self.boxscore.away_losses == 0

    def test_invalid_home_record_returns_default_wins(self):
        fake_record = PropertyMock(return_value='Golden State Warriors 1')
        type(self.boxscore)._home_record = fake_record

        assert self.boxscore.home_wins == 0

    def test_invalid_home_record_returns_default_losses(self):
        fake_record = PropertyMock(return_value='Golden State Warriors 1')
        type(self.boxscore)._home_record = fake_record

        assert self.boxscore.home_losses == 0

    def test_invalid_url_returns_none(self):
        result = Boxscore(None)._retrieve_html_page('')

        assert result is None

    def test_no_class_information_returns_dataframe_of_none(self):
        mock_points = PropertyMock(return_value=None)
        type(self.boxscore)._away_points = mock_points
        type(self.boxscore)._home_points = mock_points

        assert self.boxscore.dataframe is None

    def test_nba_game_info(self):
        fields = {
            'date': '7:30 PM, November 9, 2018',
            'location': 'State Farm Arena, Atlanta, Georgia'
        }

        mock_field = """7:30 PM, November 9, 2018
State Farm Arena, Atlanta, Georgia
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert value == result

    def test_nba_partial_game_info(self):
        fields = {
            'date': '7:30 PM, November 9, 2018',
            'location': None
        }

        mock_field = """7:30 PM, November 9, 2018
Logos via Sports Logos.net / About logos"""

        m = MockBoxscoreData(MockField(mock_field))

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert value == result


class TestNBABoxscores:
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
            <td class="right">84</td>
            <td class="right gamelink">
            </td>
    </tr>
    <tr class="winner">
            <td><a href="/teams/IND/2017.html">Indiana</a></td>
            <td class="right">105</td>
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
            <td><a href="/teams/DET/2017.html">Detroit</a></td>
            <td class="right">84</td>
            <td class="right gamelink">
                    <a href="/boxscores/201702040IND.html">Final</a>
            </td>
    </tr>
    <tr class="winner">
            <td class="right">105</td>
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
            <td><a href="/teams/DET/2017.html">Detroit</a></td>
            <td class="right gamelink">
                    <a href="/boxscores/201702040IND.html">Final</a>
            </td>
    </tr>
    <tr class="loser">
            <td><a href="/teams/IND/2017.html">Indiana</a></td>
            <td class="right">&nbsp;
            </td>
    </tr>
    </tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                'home_name': 'Indiana',
                'home_abbr': 'IND',
                'away_name': 'Detroit',
                'away_abbr': 'DET',
                'boxscore': '201702040IND',
                'winning_name': None,
                'winning_abbr': None,
                'losing_name': None,
                'losing_abbr': None,
                'home_score': None,
                'away_score': None
            }
        ]
