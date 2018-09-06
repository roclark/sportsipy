from flexmock import flexmock
from mock import patch, PropertyMock
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.ncaaf.boxscore import Boxscore


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

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert result == value

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

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert result == value

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

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert result == value

    def test_limited_game_information(self):
        fields = ['date', 'time', 'stadium']
        fields = {
            'date': 'Friday Nov 24, 2017',
            'time': '',
            'stadium': ''
        }

        mock_field = 'Friday Nov 24, 2017'
        m = MockBoxscoreData(MockField(mock_field))

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert result == value

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

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert result == value

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

        for field, value in fields.items():
            result = self.boxscore._parse_game_date_and_location(field, m)
            assert result == value

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
