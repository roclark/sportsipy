import pytest
from flexmock import flexmock
from mock import patch, PropertyMock
from pyquery import PyQuery as pq
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.ncaaf.boxscore import Boxscore, Boxscores
from sportsreference.ncaaf.player import AbstractPlayer


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

    def __str__(self):
        return self._name

    def text(self):
        return self._name.replace('<a>cfb/schools</a>', '')


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 404
            self.html_contents = html_contents
            self.text = html_contents

    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class TestNCAAFBoxscore:
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

    def test_winning_name_di_is_home(self):
        expected_name = 'Home Name'
        test_name = '<a>cfb/schools</a>Home Name'

        fake_winner = PropertyMock(return_value=HOME)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_non_di_is_home(self):
        expected_name = 'Home Name'
        test_name = 'Home Name'

        fake_winner = PropertyMock(return_value=HOME)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_di_is_away(self):
        expected_name = 'Away Name'
        test_name = '<a>cfb/schools</a>Away Name'

        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.winning_name == expected_name

    def test_winning_name_non_di_is_away(self):
        expected_name = 'Away Name'
        test_name = 'Away Name'

        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.winning_name == expected_name

    def test_winning_abbr_di_is_home(self):
        expected_name = 'HOME'
        test_name = '<a>cfb/schools</a>HOME'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=HOME)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_non_di_is_home(self):
        expected_name = 'HOME'
        test_name = 'HOME'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=HOME)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_di_is_away(self):
        expected_name = 'AWAY'
        test_name = '<a>cfb/schools</a>AWAY'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.winning_abbr == expected_name

    def test_winning_abbr_non_di_is_away(self):
        expected_name = 'AWAY'
        test_name = 'AWAY'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=AWAY)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.winning_abbr == expected_name

    def test_losing_name_di_is_home(self):
        expected_name = 'Home Name'
        test_name = '<a>cfb/schools</a>Home Name'

        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_non_di_is_home(self):
        expected_name = 'Home Name'
        test_name = 'Home Name'

        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_di_is_away(self):
        expected_name = 'Away Name'
        test_name = '<a>cfb/schools</a>Away Name'

        fake_winner = PropertyMock(return_value=HOME)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.losing_name == expected_name

    def test_losing_name_non_di_is_away(self):
        expected_name = 'Away Name'
        test_name = 'Away Name'

        fake_winner = PropertyMock(return_value=HOME)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.losing_name == expected_name

    def test_losing_abbr_di_is_home(self):
        expected_name = 'HOME'
        test_name = '<a>cfb/schools</a>HOME'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_non_di_is_home(self):
        expected_name = 'HOME'
        test_name = 'HOME'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=AWAY)
        fake_home_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._home_name = fake_home_name

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_di_is_away(self):
        expected_name = 'AWAY'
        test_name = '<a>cfb/schools</a>AWAY'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=HOME)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.losing_abbr == expected_name

    def test_losing_abbr_non_di_is_away(self):
        expected_name = 'AWAY'
        test_name = 'AWAY'

        flexmock(utils) \
            .should_receive('_parse_abbreviation') \
            .and_return(expected_name)

        fake_winner = PropertyMock(return_value=HOME)
        fake_away_name = PropertyMock(return_value=MockName(test_name))
        type(self.boxscore).winner = fake_winner
        type(self.boxscore)._away_name = fake_away_name

        assert self.boxscore.losing_abbr == expected_name

    def test_game_summary_with_no_scores_returns_none(self):
        result = Boxscore(None)._parse_summary(pq(
            """<table class="linescore nohover stats_table no_freeze">
    <tbody>
        <tr>
            <td class="center"></td>
            <td class="center"></td>
        </tr>
        <tr>
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

    def test_invalid_url_returns_none(self):
        result = Boxscore(None)._retrieve_html_page('')

        assert result is None

    def test_game_information_regular_game(self):
        fields = ['date', 'time', 'stadium']
        fields = {
            'date': 'Saturday Nov 25, 2017',
            'time': '12:00 PM ET',
            'stadium': 'Ross-Ade Stadium - West Lafayette, Indiana'
        }

        mock_field = """Saturday Nov 25, 2017
12:00 PM ET
Ross-Ade Stadium - West Lafayette, Indiana
Logos via Sports Logos.net / About logos
"""
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_game_information_championship_game(self):
        fields = ['date', 'time', 'stadium']
        fields = {
            'date': 'Saturday Dec 2, 2017',
            'time': '8:00 PM ET',
            'stadium': 'Lucas Oil Stadium - Indianapolis, Indiana'
        }

        mock_field = """Big Ten Conference Championship
Saturday Dec 2, 2017
8:00 PM ET
Lucas Oil Stadium - Indianapolis, Indiana
Logos via Sports Logos.net / About logos
"""
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_somewhat_limited_game_information(self):
        fields = ['date', 'time', 'stadium']
        fields = {
            'date': 'Friday Nov 24, 2017',
            'time': '',
            'stadium': ''
        }

        mock_field = """Friday Nov 24, 2017
Logos via Sports Logos.net / About logos
"""
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_limited_game_information(self):
        fields = ['date', 'time', 'stadium']
        fields = {
            'date': 'Friday Nov 24, 2017',
            'time': '',
            'stadium': ''
        }

        mock_field = 'Friday Nov 24, 2017'
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_limited_game_information_championship(self):
        fields = ['date', 'time', 'stadium']
        fields = {
            'date': 'Saturday Dec 2, 2017',
            'time': '',
            'stadium': ''
        }

        mock_field = """Big Ten Conference Championship
Saturday Dec 2, 2017
Logos via Sports Logos.net / About logos
"""
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_no_game_information_championship(self):
        fields = ['date', 'time', 'stadium']
        fields = {
            'date': '',
            'time': '',
            'stadium': ''
        }

        mock_field = """Big Ten Conference Championship
Logos via Sports Logos.net / About logos
"""
        m = MockBoxscoreData(MockField(mock_field))

        self.boxscore._parse_game_date_and_location(m)
        for field, value in fields.items():
            assert getattr(self.boxscore, field) == value

    def test_empty_boxscore_class_returns_dataframe_of_none(self):
        fake_points = PropertyMock(return_value=None)
        type(self.boxscore)._home_points = fake_points
        type(self.boxscore)._away_points = fake_points

        assert self.boxscore._home_points is None
        assert self.boxscore._away_points is None
        assert self.boxscore.dataframe is None

    def test_empty_attribute_returns_none(self):
        fake_rushes = PropertyMock(return_value=None)
        type(self.boxscore)._away_rush_attempts = fake_rushes

        assert self.boxscore.away_rush_attempts is None

    def test_non_int_value_returns_none(self):
        fake_rushes = PropertyMock(return_value='bad')
        type(self.boxscore)._away_rush_attempts = fake_rushes

        assert self.boxscore.away_rush_attempts is None

    @patch('requests.get', side_effect=mock_pyquery)
    def test_attempted_passes_has_deprecation_warning(self, *args, **kwargs):
        flexmock(AbstractPlayer) \
            .should_receive('__init__') \
            .and_return(None)
        mock_passes = PropertyMock(return_value=[32])
        mock_index = PropertyMock(return_value=0)
        player = AbstractPlayer(None, None, None)
        type(player)._pass_attempts = mock_passes
        type(player)._index = mock_index

        with pytest.deprecated_call():
            result = player.attempted_passes

            assert result == 32


class TestNCAABBoxscores:
    @patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        flexmock(Boxscores) \
            .should_receive('_find_games') \
            .and_return(None)
        self.boxscores = Boxscores(None)

    def test_boxscore_with_no_score_returns_none(self):
        mock_html = pq("""<table class="teams">
<tbody>
<tr class="date"><td colspan=3>Armed Forces Bowl</td></tr>

<tr class="">
    <td><a href="/cfb/schools/army/2018.html">Army</a>\
<span class='pollrank'>&nbsp;(22)&nbsp;</span></td>
    <td class="right"></td>
    <td class="right gamelink">
        <a href="/cfb/boxscores/2018-12-22-army.html">Preview</a>
    </td>
</tr>
<tr class="">
    <td><a href="/cfb/schools/houston/2018.html">Houston</a></td>
    <td class="right"></td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                'home_name': 'Houston',
                'home_abbr': 'houston',
                'away_name': 'Army',
                'away_abbr': 'army',
                'boxscore': '2018-12-22-army',
                'non_di': False,
                'top_25': True,
                'home_score': None,
                'home_rank': None,
                'away_score': None,
                'away_rank': 22,
                'winning_name': None,
                'winning_abbr': None,
                'losing_name': None,
                'losing_abbr': None
            }
        ]
