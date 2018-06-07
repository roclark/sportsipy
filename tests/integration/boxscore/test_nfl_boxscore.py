import mock
import os
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY
from sportsreference.nfl.constants import BOXSCORE_URL
from sportsreference.nfl.boxscore import Boxscore


MONTH = 10
YEAR = 2017

BOXSCORE = '201802040nwe'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nfl', filename)
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


class TestNFLBoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': 'Sunday Feb 4, 2018',
            'time': '6:30pm',
            'stadium': 'U.S. Bank Stadium',
            'attendance': 67612,
            'duration': '3:46',
            'winner': AWAY,
            'winning_name': 'Philadelphia Eagles',
            'winning_abbr': 'PHI',
            'losing_name': 'New England Patriots',
            'losing_abbr': 'NWE',
            'away_points': 41,
            'away_first_downs': 25,
            'away_rush_attempts': 27,
            'away_rush_yards': 164,
            'away_rush_touchdowns': 1,
            'away_pass_completions': 29,
            'away_pass_attempts': 44,
            'away_pass_yards': 374,
            'away_pass_touchdowns': 4,
            'away_interceptions': 1,
            'away_times_sacked': 0,
            'away_yards_lost_from_sacks': 0,
            'away_net_pass_yards': 374,
            'away_total_yards': 538,
            'away_fumbles': 0,
            'away_fumbles_lost': 0,
            'away_turnovers': 1,
            'away_penalties': 6,
            'away_yards_from_penalties': 35,
            'away_third_down_conversions': 10,
            'away_third_down_attempts': 16,
            'away_fourth_down_conversions': 2,
            'away_fourth_down_attempts': 2,
            'away_time_of_possession': '34:04',
            'home_points': 33,
            'home_first_downs': 29,
            'home_rush_attempts': 22,
            'home_rush_yards': 113,
            'home_rush_touchdowns': 1,
            'home_pass_completions': 28,
            'home_pass_attempts': 49,
            'home_pass_yards': 505,
            'home_pass_touchdowns': 3,
            'home_interceptions': 0,
            'home_times_sacked': 1,
            'home_yards_lost_from_sacks': 5,
            'home_net_pass_yards': 500,
            'home_total_yards': 613,
            'home_fumbles': 1,
            'home_fumbles_lost': 1,
            'home_turnovers': 1,
            'home_penalties': 1,
            'home_yards_from_penalties': 5,
            'home_third_down_conversions': 5,
            'home_third_down_attempts': 10,
            'home_fourth_down_conversions': 1,
            'home_fourth_down_attempts': 2,
            'home_time_of_possession': '25:56',
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_nfl_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value
