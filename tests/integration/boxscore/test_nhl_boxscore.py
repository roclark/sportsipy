import mock
import os
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY
from sportsreference.nhl.constants import BOXSCORE_URL
from sportsreference.nhl.boxscore import Boxscore


MONTH = 10
YEAR = 2017

BOXSCORE = '201806070VEG'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nhl', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNHLBoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': 'June 7, 2018',
            'time': '8:00 PM',
            'arena': 'T-Mobile Arena',
            'attendance': 18529,
            'duration': '2:45',
            'winner': AWAY,
            'winning_name': 'Washington Capitals',
            'winning_abbr': 'WSH',
            'losing_name': 'Vegas Golden Knights',
            'losing_abbr': 'VEG',
            'away_goals': 4,
            'away_assists': 7,
            'away_points': 11,
            'away_penalties_in_minutes': 8,
            'away_even_strength_goals': 3,
            'away_power_play_goals': 1,
            'away_short_handed_goals': 0,
            'away_game_winning_goals': 1,
            'away_even_strength_assists': 5,
            'away_power_play_assists': 2,
            'away_short_handed_assists': 0,
            'away_shots_on_goal': 33,
            'away_shooting_percentage': 12.1,
            'away_saves': 28,
            'away_save_percentage': .903,
            'away_shutout': 0,
            'home_goals': 3,
            'home_assists': 6,
            'home_points': 9,
            'home_penalties_in_minutes': 12,
            'home_even_strength_goals': 2,
            'home_power_play_goals': 1,
            'home_short_handed_goals': 0,
            'home_game_winning_goals': 0,
            'home_even_strength_assists': 4,
            'home_power_play_assists': 2,
            'home_short_handed_assists': 0,
            'home_shots_on_goal': 31,
            'home_shooting_percentage': 9.7,
            'home_saves': 29,
            'home_save_percentage': .879,
            'home_shutout': 0
        }

        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_nhl_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value

    def test_invalid_url_yields_empty_class(self):
        flexmock(Boxscore) \
            .should_receive('_retrieve_html_page') \
            .and_return(None)

        boxscore = Boxscore(BOXSCORE)

        for key, value in boxscore.__dict__.items():
            assert value is None
