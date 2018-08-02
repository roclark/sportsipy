import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import HOME
from sportsreference.ncaab.constants import BOXSCORES_URL, SCHEDULE_URL
from sportsreference.ncaab.boxscore import Boxscore, Boxscores


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

    if url == BOXSCORES_URL % (MONTH, 11, YEAR):
        return MockPQ(read_file('boxscores.html'))
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


class TestNCAABBoxscores:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        expected = {
            'boxscores': [
                {'home_name': 'Buffalo',
                 'away_abbr': 'canisius',
                 'home_abbr': 'buffalo',
                 'boxscore': '2017-11-11-13-buffalo',
                 'away_name': 'Canisius',
                 'non_di': False},
                {'home_name': 'Fairfield',
                 'away_abbr': 'pennsylvania',
                 'home_abbr': 'fairfield',
                 'boxscore': '2017-11-11-13-fairfield',
                 'away_name': 'Penn',
                 'non_di': False},
                {'home_name': 'Florida Gulf Coast',
                 'away_abbr': 'illinois-state',
                 'home_abbr': 'florida-gulf-coast',
                 'boxscore': '2017-11-11-13-florida-gulf-coast',
                 'away_name': 'Illinois State',
                 'non_di': False},
                {'home_name': 'Bradley',
                 'away_abbr': 'iupui',
                 'home_abbr': 'bradley',
                 'boxscore': '2017-11-11-14-bradley',
                 'away_name': 'IUPUI',
                 'non_di': False},
                {'home_name': 'Ohio',
                 'away_abbr': 'alabama-am',
                 'home_abbr': 'ohio',
                 'boxscore': '2017-11-11-14-ohio',
                 'away_name': 'Alabama A&M',
                 'non_di': False},
                {'home_name': 'Quinnipiac',
                 'away_abbr': 'dartmouth',
                 'home_abbr': 'quinnipiac',
                 'boxscore': '2017-11-11-14-quinnipiac',
                 'away_name': 'Dartmouth',
                 'non_di': False},
                {'home_name': 'Western Michigan',
                 'away_abbr': 'Siena Heights',
                 'home_abbr': 'western-michigan',
                 'boxscore': '2017-11-11-14-western-michigan',
                 'away_name': 'Siena Heights',
                 'non_di': True},
                {'home_name': 'Appalachian State',
                 'away_abbr': 'Toccoa Falls',
                 'home_abbr': 'appalachian-state',
                 'boxscore': '2017-11-11-15-appalachian-state',
                 'away_name': 'Toccoa Falls',
                 'non_di': True},
                {'home_name': 'Brown',
                 'away_abbr': 'Johnson & Wales (RI)',
                 'home_abbr': 'brown',
                 'boxscore': '2017-11-11-15-brown',
                 'away_name': 'Johnson & Wales (RI)',
                 'non_di': True},
                {'home_name': 'Drake',
                 'away_abbr': 'Coe',
                 'home_abbr': 'drake',
                 'boxscore': '2017-11-11-15-drake',
                 'away_name': 'Coe',
                 'non_di': True},
                {'home_name': 'La Salle',
                 'away_abbr': 'saint-peters',
                 'home_abbr': 'la-salle',
                 'boxscore': '2017-11-11-15-la-salle',
                 'away_name': 'St. Peter\'s',
                 'non_di': False},
                {'home_name': 'Longwood',
                 'away_abbr': 'stephen-f-austin',
                 'home_abbr': 'longwood',
                 'boxscore': '2017-11-11-15-longwood',
                 'away_name': 'Stephen F. Austin',
                 'non_di': False},
                {'home_name': 'Little Rock',
                 'away_abbr': 'Ouachita',
                 'home_abbr': 'arkansas-little-rock',
                 'boxscore': '2017-11-11-16-arkansas-little-rock',
                 'away_name': 'Ouachita',
                 'non_di': True},
                {'home_name': 'UCSB',
                 'away_abbr': 'north-dakota-state',
                 'home_abbr': 'california-santa-barbara',
                 'boxscore': '2017-11-11-16-california-santa-barbara',
                 'away_name': 'North Dakota State',
                 'non_di': False},
                {'home_name': 'DePaul',
                 'away_abbr': 'notre-dame',
                 'home_abbr': 'depaul',
                 'boxscore': '2017-11-11-16-depaul',
                 'away_name': 'Notre Dame',
                 'non_di': False},
                {'home_name': 'Duquesne',
                 'away_abbr': 'st-francis-ny',
                 'home_abbr': 'duquesne',
                 'boxscore': '2017-11-11-17-duquesne',
                 'away_name': 'St. Francis (NY)',
                 'non_di': False},
                {'home_name': 'NJIT',
                 'away_abbr': 'wagner',
                 'home_abbr': 'njit',
                 'boxscore': '2017-11-11-18-njit',
                 'away_name': 'Wagner',
                 'non_di': False},
                {'home_name': 'Akron',
                 'away_abbr': 'cleveland-state',
                 'home_abbr': 'akron',
                 'boxscore': '2017-11-11-19-akron',
                 'away_name': 'Cleveland State',
                 'non_di': False},
                {'home_name': 'Duke',
                 'away_abbr': 'utah-valley',
                 'home_abbr': 'duke',
                 'boxscore': '2017-11-11-19-duke',
                 'away_name': 'Utah Valley',
                 'non_di': False},
                {'home_name': 'Elon',
                 'away_abbr': 'Peace',
                 'home_abbr': 'elon',
                 'boxscore': '2017-11-11-19-elon',
                 'away_name': 'Peace',
                 'non_di': True},
                {'home_name': 'Marist',
                 'away_abbr': 'lehigh',
                 'home_abbr': 'marist',
                 'boxscore': '2017-11-11-19-marist',
                 'away_name': 'Lehigh',
                 'non_di': False},
                {'home_name': 'Michigan',
                 'away_abbr': 'north-florida',
                 'home_abbr': 'michigan',
                 'boxscore': '2017-11-11-19-michigan',
                 'away_name': 'North Florida',
                 'non_di': False},
                {'home_name': 'North Carolina-Wilmington',
                 'away_abbr': 'North Carolina Wesleyan',
                 'home_abbr': 'north-carolina-wilmington',
                 'boxscore': '2017-11-11-19-north-carolina-wilmington',
                 'away_name': 'North Carolina Wesleyan',
                 'non_di': True},
                {'home_name': 'Presbyterian',
                 'away_abbr': 'Johnson University',
                 'home_abbr': 'presbyterian',
                 'boxscore': '2017-11-11-19-presbyterian',
                 'away_name': 'Johnson University',
                 'non_di': True},
                {'home_name': 'Sam Houston State',
                 'away_abbr': 'Texas-Tyler',
                 'home_abbr': 'sam-houston-state',
                 'boxscore': '2017-11-11-19-sam-houston-state',
                 'away_name': 'Texas-Tyler',
                 'non_di': True},
                {'home_name': 'South Dakota',
                 'away_abbr': 'Mayville State',
                 'home_abbr': 'south-dakota',
                 'boxscore': '2017-11-11-19-south-dakota',
                 'away_name': 'Mayville State',
                 'non_di': True},
                {'home_name': 'Toledo',
                 'away_abbr': 'saint-josephs',
                 'home_abbr': 'toledo',
                 'boxscore': '2017-11-11-19-toledo',
                 'away_name': 'St. Joseph\'s',
                 'non_di': False},
                {'home_name': 'Nebraska',
                 'away_abbr': 'eastern-illinois',
                 'home_abbr': 'nebraska',
                 'boxscore': '2017-11-11-20-nebraska',
                 'away_name': 'Eastern Illinois',
                 'non_di': False},
                {'home_name': 'Saint Mary\'s (CA)',
                 'away_abbr': 'saint-francis-pa',
                 'home_abbr': 'saint-marys-ca',
                 'boxscore': '2017-11-11-20-saint-marys-ca',
                 'away_name': 'Saint Francis (PA)',
                 'non_di': False},
                {'home_name': 'Texas-Arlington',
                 'away_abbr': 'loyola-marymount',
                 'home_abbr': 'texas-arlington',
                 'boxscore': '2017-11-11-20-texas-arlington',
                 'away_name': 'Loyola Marymount',
                 'non_di': False},
                {'home_name': 'Western Illinois',
                 'away_abbr': 'Saint Mary\'s (MN)',
                 'home_abbr': 'western-illinois',
                 'boxscore': '2017-11-11-20-western-illinois',
                 'away_name': 'Saint Mary\'s (MN)',
                 'non_di': True},
                {'home_name': 'BYU',
                 'away_abbr': 'mississippi-valley-state',
                 'home_abbr': 'brigham-young',
                 'boxscore': '2017-11-11-21-brigham-young',
                 'away_name': 'Mississippi Valley State',
                 'non_di': False},
                {'home_name': 'Kent State',
                 'away_abbr': 'youngstown-state',
                 'home_abbr': 'kent-state',
                 'boxscore': '2017-11-11-21-kent-state',
                 'away_name': 'Youngstown State',
                 'non_di': False},
                {'home_name': 'New Mexico',
                 'away_abbr': 'Northern New Mexico',
                 'home_abbr': 'new-mexico',
                 'boxscore': '2017-11-11-21-new-mexico',
                 'away_name': 'Northern New Mexico',
                 'non_di': True},
                {'home_name': 'UNLV',
                 'away_abbr': 'florida-am',
                 'home_abbr': 'nevada-las-vegas',
                 'boxscore': '2017-11-11-22-nevada-las-vegas',
                 'away_name': 'Florida A&M',
                 'non_di': False},
                {'home_name': 'Portland',
                 'away_abbr': 'portland-state',
                 'home_abbr': 'portland',
                 'boxscore': '2017-11-11-22-portland',
                 'away_name': 'Portland State',
                 'non_di': False},
            ]
        }

        result = Boxscores(datetime(2017, 11, 11)).games

        assert result == expected
