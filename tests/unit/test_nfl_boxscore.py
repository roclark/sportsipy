from flexmock import flexmock
from mock import patch, PropertyMock
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.nfl.boxscore import Boxscore


class MockName:
    def __init__(self, name):
        self._name = name

    def text(self):
        return self._name


def mock_pyquery(url, status_code=404):
    class MockPQ:
        def __init__(self, html_contents, status_code=404):
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

    if url == '404':
        return MockPQ('404 error', 200)
    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


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
        result = Boxscore(None)._retrieve_html_page('')

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
