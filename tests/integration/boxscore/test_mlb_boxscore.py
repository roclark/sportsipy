import mock
import os
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY
from sportsreference.mlb.constants import BOXSCORE_URL, NIGHT
from sportsreference.mlb.boxscore import Boxscore


MONTH = 10
YEAR = 2017

BOXSCORE = 'BOS/BOS201806070'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'mlb', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    path = '%s.shtml' % BOXSCORE
    boxscore = read_file(path.replace('BOS/', ''))
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestMLBBoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': 'Thursday, June 7, 2018',
            'time': '7:10 p.m. ET',
            'attendance': 36556,
            'venue': 'Fenway Park',
            'time_of_day': NIGHT,
            'duration': '2:55',
            'winner': AWAY,
            'winning_name': 'Detroit Tigers',
            'winning_abbr': 'DET',
            'losing_name': 'Boston Red Sox',
            'losing_abbr': 'BOS',
            'away_at_bats': 37,
            'away_runs': 7,
            'away_hits': 10,
            'away_rbi': 7,
            'away_earned_runs': 7.0,
            'away_bases_on_balls': 3,
            'away_strikeouts': 11,
            'away_plate_appearances': 40,
            'away_batting_average': .270,
            'away_on_base_percentage': .325,
            'away_slugging_percentage': .486,
            'away_on_base_plus': .811,
            'away_pitches': 141,
            'away_strikes': 109,
            'away_win_probability_for_offensive_player': .315,
            'away_average_leverage_index': .46,
            'away_win_probability_added': .551,
            'away_win_probability_subtracted': -.236,
            'away_base_out_runs_added': 2.2,
            'away_putouts': 27,
            'away_assists': 9,
            'away_innings_pitched': 9,
            'away_home_runs': 1,
            'away_strikes_by_contact': 68,
            'away_strikes_swinging': 14,
            'away_strikes_looking': 27,
            'away_grounded_balls': 13,
            'away_fly_balls': 13,
            'away_line_drives': 6,
            'away_unknown_bat_type': 0,
            'away_game_score': 59,
            'away_inherited_runners': 1,
            'away_inherited_score': 0,
            'away_win_probability_by_pitcher': .184,
            'away_average_leverage_index': .71,
            'away_base_out_runs_saved': 2.8,
            'home_at_bats': 33,
            'home_runs': 2,
            'home_hits': 7,
            'home_rbi': 2,
            'home_earned_runs': 2.0,
            'home_bases_on_balls': 5,
            'home_strikeouts': 8,
            'home_plate_appearances': 38,
            'home_batting_average': .212,
            'home_on_base_percentage': .316,
            'home_slugging_percentage': .364,
            'home_on_base_plus': .679,
            'home_pitches': 157,
            'home_strikes': 83,
            'home_win_probability_for_offensive_player': -.184,
            'home_average_leverage_index': .71,
            'home_win_probability_added': .368,
            'home_win_probability_subtracted': -.552,
            'home_base_out_runs_added': -2.8,
            'home_putouts': 27,
            'home_assists': 9,
            'home_innings_pitched': 9,
            'home_home_runs': 1,
            'home_strikes_by_contact': 45,
            'home_strikes_swinging': 12,
            'home_strikes_looking': 26,
            'home_grounded_balls': 9,
            'home_fly_balls': 16,
            'home_line_drives': 7,
            'home_unknown_bat_type': 0,
            'home_game_score': 25,
            'home_inherited_runners': 0,
            'home_inherited_score': 0,
            'home_win_probability_by_pitcher': -.317,
            'home_average_leverage_index': .46,
            'home_base_out_runs_saved': -2.2
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_mlb_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value

    def test_invalid_url_yields_empty_class(self):
        flexmock(Boxscore) \
            .should_receive('_retrieve_html_page') \
            .and_return(None)

        boxscore = Boxscore(BOXSCORE)

        for key, value in boxscore.__dict__.items():
            assert value is None
