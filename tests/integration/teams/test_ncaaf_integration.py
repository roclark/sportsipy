import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsreference import utils
from sportsreference.ncaaf.constants import (OFFENSIVE_STATS_URL,
                                             SEASON_PAGE_URL)
from sportsreference.ncaaf.teams import Teams


MONTH = 9
YEAR = 2017


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaaf_stats', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if div == 'table#offense':
                return read_file('%s-team-offense_offense.html' % YEAR)
            else:
                return read_file('%s-standings_standings.html' % YEAR)

    offensive_contents = read_file('%s-team-offense.html' % YEAR)
    standings_contents = read_file('%s-standings.html' % YEAR)
    if url == OFFENSIVE_STATS_URL % YEAR:
        return MockPQ(offensive_contents)
    elif url == SEASON_PAGE_URL % YEAR:
        return MockPQ(standings_contents)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNCAAFIntegration:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'abbreviation': 'PURDUE',
            'name': 'Purdue',
            'games': 13,
            'wins': 7,
            'losses': 6,
            'win_percentage': .538,
            'conference_wins': 4,
            'conference_losses': 5,
            'conference_win_percentage': .444,
            'points_per_game': 25.2,
            'points_against_per_game': 20.5,
            'strength_of_schedule': 6.21,
            'simple_rating_system': 9.74,
            'pass_completions': 22.5,
            'pass_attempts': 37.8,
            'pass_completion_percentage': 59.5,
            'pass_yards': 251.5,
            'interceptions': 0.8,
            'pass_touchdowns': 2.1,
            'rush_attempts': 34.4,
            'rush_yards': 151.5,
            'rush_yards_per_attempt': 4.4,
            'rush_touchdowns': 0.9,
            'plays': 72.2,
            'yards': 403.1,
            'turnovers': 1.3,
            'fumbles_lost': 0.5,
            'yards_per_play': 5.6,
            'pass_first_downs': 11.1,
            'rush_first_downs': 8.8,
            'first_downs_from_penalties': 1.8,
            'first_downs': 21.7,
            'penalties': 5.9,
            'yards_from_penalties': 50.6
        }
        self.schools = [
            'UCF', 'Memphis', 'Oklahoma', 'Oklahoma State', 'Arizona',
            'Ohio State', 'Penn State', 'Florida Atlantic', 'Ohio',
            'South Florida', 'Louisville', 'Arkansas State', 'SMU',
            'Missouri', 'Alabama', 'Toledo', 'Washington', 'Oregon',
            'North Texas', 'Georgia', 'Wake Forest', 'West Virginia',
            'Texas Tech', 'Notre Dame', 'Auburn', 'Louisiana-Monroe',
            'Western Michigan', 'Wisconsin', 'Texas Christian',
            'Appalachian State', 'Colorado State', 'Clemson',
            'Ole Miss', 'Texas A&M', 'USC', 'Boise State',
            'UCLA', 'Stanford', 'Kansas State', 'North Carolina State',
            'Mississippi State', 'Arizona State', 'Troy', 'Air Force',
            'San Diego State', 'Army', 'Massachusetts',
            'Louisiana Tech', 'Navy', 'Washington State', 'Utah State',
            'Texas', 'Utah', 'New Mexico State', 'Tulsa', 'Iowa State',
            'Northwestern', 'Southern Mississippi', 'Miami (FL)',
            'Northern Illinois', 'Arkansas', 'Nevada-Las Vegas',
            'Buffalo', 'Central Michigan', 'Houston', 'Iowa',
            'Louisiana', 'Nevada', 'Virginia Tech', 'Georgia Tech',
            'California', 'Florida State', 'UAB', 'Tulane', 'Syracuse',
            'LSU', 'Fresno State', 'Indiana', 'Marshall', 'Duke',
            'Colorado', 'Eastern Michigan', 'North Carolina',
            'Nebraska', 'Boston College', 'Florida International',
            'Kentucky', 'Middle Tennessee State', 'Western Kentucky',
            'Bowling Green State', 'Michigan', 'Purdue', 'Temple',
            'East Carolina', 'Vanderbilt', 'Michigan State',
            'Miami (OH)', 'Baylor', 'South Carolina', 'Maryland',
            'Pitt', 'Coastal Carolina', 'Connecticut', 'UTSA',
            'Wyoming', 'Hawaii', 'Virginia', 'Akron', 'Florida',
            'Minnesota', 'Cincinnati', 'Idaho', 'Georgia Southern',
            'New Mexico', 'Old Dominion', 'Oregon State',
            'Georgia State', 'South Alabama', 'Tennessee', 'Kansas',
            'Rutgers', 'Ball State', 'Texas State', 'Brigham Young',
            'Rice', 'San Jose State', 'Illinois', 'Charlotte',
            'Kent State', 'UTEP'
        ]
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.teams = Teams()

    def test_ncaaf_integration_returns_correct_number_of_teams(self):
        assert len(self.teams) == len(self.schools)

    def test_ncaaf_integration_returns_correct_attributes_for_team(self):
        purdue = self.teams('PURDUE')

        for attribute, value in self.results.items():
            assert getattr(purdue, attribute) == value

    def test_ncaaf_integration_returns_correct_team_abbreviations(self):
        for team in self.teams:
            assert team.name in self.schools

    def test_ncaaf_integration_dataframe_returns_dataframe(self):
        df = pd.DataFrame([self.results], index=['PURDUE'])

        purdue = self.teams('PURDUE')
        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, purdue.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_ncaaf_integration_all_teams_dataframe_returns_dataframe(self):
        result = self.teams.dataframes.drop_duplicates(keep=False)

        assert len(result) == len(self.schools)
        assert set(result.columns.values) == set(self.results.keys())

    def test_ncaaf_invalid_team_name_raises_value_error(self):
        with pytest.raises(ValueError):
            self.teams('INVALID_NAME')
