import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import HOME
from sportsreference.ncaab.constants import SCHEDULE_URL
from sportsreference.ncaab.boxscore import Boxscore


MONTH = 11
YEAR = 2017

BOXSCORE = '2017-11-24-21-purdue'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaab', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file('table.html')

    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNCAABBoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': 'November 24, 2017',
            'location': 'Imperial Arena at Atlantis Resort, Paradise Island',
            'winner': HOME,
            'winning_name': 'Purdue',
            'winning_abbr': 'PURDUE',
            'losing_name': 'Arizona',
            'losing_abbr': 'ARIZONA',
            'pace': 71.8,
            'away_wins': 3,
            'away_losses': 3,
            'away_minutes_played': 200,
            'away_field_goals': 25,
            'away_field_goal_attempts': 59,
            'away_field_goal_percentage': .424,
            'away_two_point_field_goals': 22,
            'away_two_point_field_goal_attempts': 42,
            'away_two_point_field_goal_percentage': .524,
            'away_three_point_field_goals': 3,
            'away_three_point_field_goal_attempts': 17,
            'away_three_point_field_goal_percentage': .176,
            'away_free_throws': 11,
            'away_free_throw_attempts': 16,
            'away_free_throw_percentage': .688,
            'away_offensive_rebounds': 6,
            'away_defensive_rebounds': 16,
            'away_total_rebounds': 22,
            'away_assists': 13,
            'away_steals': 4,
            'away_blocks': 3,
            'away_turnovers': 11,
            'away_personal_fouls': 20,
            'away_points': 64,
            'away_true_shooting_percentage': .480,
            'away_effective_field_goal_percentage': .449,
            'away_three_point_attempt_rate': .288,
            'away_free_throw_attempt_rate': .271,
            'away_offensive_rebound_percentage': 18.8,
            'away_defensive_rebound_percentage': 72.7,
            'away_total_rebound_percentage': 40.7,
            'away_assist_percentage': 52.0,
            'away_steal_percentage': 5.6,
            'away_block_percentage': 9.4,
            'away_turnover_percentage': 14.3,
            'away_offensive_rating': 88.9,
            'away_defensive_rating': 123.6,
            'home_wins': 5,
            'home_losses': 2,
            'home_minutes_played': 200,
            'home_field_goals': 31,
            'home_field_goal_attempts': 54,
            'home_field_goal_percentage': .574,
            'home_two_point_field_goals': 20,
            'home_two_point_field_goal_attempts': 32,
            'home_two_point_field_goal_percentage': .625,
            'home_three_point_field_goals': 11,
            'home_three_point_field_goal_attempts': 22,
            'home_three_point_field_goal_percentage': .500,
            'home_free_throws': 16,
            'home_free_throw_attempts': 21,
            'home_free_throw_percentage': .762,
            'home_offensive_rebounds': 6,
            'home_defensive_rebounds': 26,
            'home_total_rebounds': 32,
            'home_assists': 19,
            'home_steals': 6,
            'home_blocks': 7,
            'home_turnovers': 14,
            'home_personal_fouls': 19,
            'home_points': 89,
            'home_true_shooting_percentage': .696,
            'home_effective_field_goal_percentage': .676,
            'home_three_point_attempt_rate': .407,
            'home_free_throw_attempt_rate': .389,
            'home_offensive_rebound_percentage': 27.3,
            'home_defensive_rebound_percentage': 81.3,
            'home_total_rebound_percentage': 59.3,
            'home_assist_percentage': 61.3,
            'home_steal_percentage': 8.3,
            'home_block_percentage': 16.7,
            'home_turnover_percentage': 18.1,
            'home_offensive_rating': 123.6,
            'home_defensive_rating': 88.9
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore('2017-11-24-21-purdue')

    def test_ncaab_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value

    def test_invalid_url_yields_empty_class(self):
        flexmock(Boxscore) \
            .should_receive('_retrieve_html_page') \
            .and_return(None)

        boxscore = Boxscore(BOXSCORE)

        for key, value in boxscore.__dict__.items():
            if key == '_uri':
                continue
            assert value is None

    def test_ncaab_boxscore_dataframe_returns_dataframe_of_all_values(self):
        df = pd.DataFrame([self.results], index=[BOXSCORE])

        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, self.boxscore.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty
