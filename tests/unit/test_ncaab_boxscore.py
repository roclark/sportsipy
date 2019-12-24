from flexmock import flexmock
from mock import patch, PropertyMock
from pyquery import PyQuery as pq
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.ncaab.boxscore import Boxscore, Boxscores


class MockBoxscore:
    def __init__(self, name):
        self._name = name

    def __call__(self, scheme):
        return self._name


class MockName:
    def __init__(self, name):
        self._name = name

    def __str__(self):
        return self._name

    def text(self):
        return self._name.replace('<a>cbb/schools</a>', '')


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


class TestNCAABBoxscore:
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

    def test_winning_name_di_is_home(self):
        expected_name = 'Home Name'
        test_name = '<a>cbb/schools</a>Home Name'

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
        test_name = '<a>cbb/schools</a>Away Name'

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
        expected_name = 'Home'
        test_name = '<a>cbb/schools</a>HOME'

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
        test_name = '<a>cbb/schools</a>AWAY'

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
        test_name = '<a>cbb/schools</a>Home Name'

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
        test_name = '<a>cbb/schools</a>Away Name'

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
        test_name = '<a>cbb/schools</a>HOME'

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
        test_name = '<a>cbb/schools</a>AWAY'

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

    def test_invalid_away_record_returns_default_wins(self):
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(self.boxscore)._away_record = fake_record

        assert self.boxscore.away_wins == 0

    def test_invalid_away_record_returns_default_losses(self):
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(self.boxscore)._away_record = fake_record

        assert self.boxscore.away_losses == 0

    def test_invalid_home_record_returns_default_wins(self):
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(self.boxscore)._home_record = fake_record

        assert self.boxscore.home_wins == 0

    def test_invalid_home_record_returns_default_losses(self):
        fake_record = PropertyMock(return_value='Purdue (1)')
        type(self.boxscore)._home_record = fake_record

        assert self.boxscore.home_losses == 0

    def test_game_summary_with_no_scores_returns_none(self):
        result = Boxscore(None)._parse_summary(pq(
            """<table id="line-score">
    <tbody>
        <tr>
            <td class="right"></td>
            <td class="right"></td>
        </tr>
        <tr>
            <td class="right"></td>
            <td class="right"></td>
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

    def test_parsing_name_for_non_di_school(self):
        name = 'Away name'
        boxscore = MockBoxscore(name)

        result = self.boxscore._parse_name('away_name', boxscore)

        assert result == name

    def test_no_home_free_throw_percentage_returns_default(self):
        fake_percentage = PropertyMock(return_value='')
        type(self.boxscore)._home_free_throw_percentage = fake_percentage

        assert self.boxscore.home_free_throw_percentage is None

    def test_no_away_free_throw_percentage_returns_default(self):
        fake_percentage = PropertyMock(return_value='')
        type(self.boxscore)._away_free_throw_percentage = fake_percentage

        assert self.boxscore.away_free_throw_percentage is None

    def test_empty_boxscore_class_returns_dataframe_of_none(self):
        fake_points = PropertyMock(return_value=None)
        type(self.boxscore)._home_points = fake_points
        type(self.boxscore)._away_points = fake_points

        assert self.boxscore._home_points is None
        assert self.boxscore._away_points is None
        assert self.boxscore.dataframe is None

    def test_away_win_percentage_no_games_played_returns_default(self):
        fake_games = PropertyMock(return_value=0)
        type(self.boxscore).away_wins = fake_games
        type(self.boxscore).away_losses = fake_games

        assert self.boxscore.away_wins == 0
        assert self.boxscore.away_losses == 0
        assert self.boxscore.away_win_percentage == 0.0

    def test_home_win_percentage_no_games_played_returns_default(self):
        fake_games = PropertyMock(return_value=0)
        type(self.boxscore).home_wins = fake_games
        type(self.boxscore).home_losses = fake_games

        assert self.boxscore.home_wins == 0
        assert self.boxscore.home_losses == 0
        assert self.boxscore.home_win_percentage == 0.0

    def test_ranking_with_no_boxscores(self):
        ranking = self.boxscore._parse_ranking('home_ranking',
                                               MockBoxscore(''))

        assert ranking is None

    def test_ncaab_game_info(self):
        fields = {
            'date': 'November 9, 2018',
            'location': 'WVU Coliseum, Morgantown, West Virginia'
        }

        mock_field = """November 9, 2018
WVU Coliseum, Morgantown, West Virginia
Logos via Sports Logos.net / About logos
"""

        m = MockBoxscoreData(MockField(mock_field))

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert value == result

    def test_ncaab_partial_game_info(self):
        fields = {
            'date': 'November 9, 2018',
            'location': None
        }

        mock_field = """November 9, 2018
Logos via Sports Logos.net / About logos"""

        m = MockBoxscoreData(MockField(mock_field))

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert value == result


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
<tr class="loser">
    <td><a href="/cbb/schools/south-dakota/2019.html">South Dakota</a></td>
    <td class="right"></td>
    <td class="right gamelink">
    </td>
</tr>
<tr class="loser">
    <td><a href="/cbb/schools/kansas/2019.html">Kansas</a>\
<span class='pollrank'>&nbsp;(1)&nbsp;</span></td>
    <td class="right"></td>
    <td class="right">&nbsp;
    </td>
</tr>
</tbody>
</table>""")
        games = self.boxscores._extract_game_info([mock_html])

        assert games == [
            {
                'home_name': 'Kansas',
                'home_abbr': 'kansas',
                'away_name': 'South Dakota',
                'away_abbr': 'south-dakota',
                'boxscore': '',
                'non_di': False,
                'top_25': True,
                'home_score': None,
                'home_rank': 1,
                'away_score': None,
                'away_rank': None,
                'winning_name': None,
                'winning_abbr': None,
                'losing_name': None,
                'losing_abbr': None
            }
        ]
