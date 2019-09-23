import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsreference import utils
from sportsreference.ncaaf.conferences import Conferences
from sportsreference.ncaaf.constants import (OFFENSIVE_STATS_URL,
                                             DEFENSIVE_STATS_URL,
                                             SEASON_PAGE_URL)
from sportsreference.ncaaf.teams import Teams


MONTH = 9
YEAR = 2017


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaaf_stats', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if div == 'table#offense':
                return read_file('%s-team-offense_offense.html' % YEAR)
            elif div == 'table#defense':
                return read_file('%s-team-defense_defense.html' % YEAR)
            else:
                return read_file('%s-standings_standings.html' % YEAR)

    offensive_contents = read_file('%s-team-offense.html' % YEAR)
    defensive_contents = read_file('%s-team-defense.html' % YEAR)
    standings_contents = read_file('%s-standings.html' % YEAR)
    if url == OFFENSIVE_STATS_URL % YEAR:
        return MockPQ(offensive_contents)
    elif url == DEFENSIVE_STATS_URL % YEAR:
        return MockPQ(defensive_contents)
    elif url == SEASON_PAGE_URL % YEAR:
        return MockPQ(standings_contents)


def mock_request(url):
    class MockRequest:
        def __init__(self, html_contents, status_code=200):
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents

    if str(YEAR) in url:
        return MockRequest('good')
    else:
        return MockRequest('bad', status_code=404)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNCAAFIntegration:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'conference': 'big-ten',
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
            'yards_from_penalties': 50.6,
            'opponents_pass_completions': 19.1,
            'opponents_pass_attempts': 33.6,
            'opponents_pass_completion_percentage': 56.8,
            'opponents_pass_yards': 242.5,
            'opponents_interceptions': 0.8,
            'opponents_pass_touchdowns': 1.6,
            'opponents_rush_attempts': 37.4,
            'opponents_rush_yards': 133.2,
            'opponents_rush_yards_per_attempt': 3.6,
            'opponents_rush_touchdowns': 0.8,
            'opponents_plays': 71.0,
            'opponents_yards': 375.8,
            'opponents_turnovers': 1.6,
            'opponents_fumbles_lost': 0.8,
            'opponents_yards_per_play': 5.3,
            'opponents_pass_first_downs': 10.6,
            'opponents_rush_first_downs': 6.8,
            'opponents_first_downs_from_penalties': 1.8,
            'opponents_first_downs': 19.2,
            'opponents_penalties': 6.9,
            'opponents_yards_from_penalties': 59.8
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

        team_conference = {'florida-state': 'acc',
                           'boston-college': 'acc',
                           'clemson': 'acc',
                           'north-carolina-state': 'acc',
                           'syracuse': 'acc',
                           'wake-forest': 'acc',
                           'louisville': 'acc',
                           'virginia-tech': 'acc',
                           'duke': 'acc',
                           'georgia-tech': 'acc',
                           'pittsburgh': 'acc',
                           'virginia': 'acc',
                           'miami-fl': 'acc',
                           'north-carolina': 'acc',
                           'florida': 'sec',
                           'georgia': 'sec',
                           'kentucky': 'sec',
                           'missouri': 'sec',
                           'south-carolina': 'sec',
                           'vanderbilt': 'sec',
                           'tennessee': 'sec',
                           'alabama': 'sec',
                           'arkansas': 'sec',
                           'auburn': 'sec',
                           'louisiana-state': 'sec',
                           'mississippi-state': 'sec',
                           'mississippi': 'sec',
                           'texas-am': 'sec',
                           'buffalo': 'mac',
                           'ohio': 'mac',
                           'bowling-green-state': 'mac',
                           'kent-state': 'mac',
                           'miami-oh': 'mac',
                           'akron': 'mac',
                           'ball-state': 'mac',
                           'eastern-michigan': 'mac',
                           'toledo': 'mac',
                           'central-michigan': 'mac',
                           'northern-illinois': 'mac',
                           'western-michigan': 'mac',
                           'georgia-southern': 'sun-belt',
                           'appalachian-state': 'sun-belt',
                           'coastal-carolina': 'sun-belt',
                           'arkansas-state': 'sun-belt',
                           'georgia-state': 'sun-belt',
                           'louisiana-lafayette': 'sun-belt',
                           'louisiana-monroe': 'sun-belt',
                           'south-alabama': 'sun-belt',
                           'texas-state': 'sun-belt',
                           'troy': 'sun-belt',
                           'idaho': 'sun-belt',
                           'baylor': 'big-12',
                           'kansas-state': 'big-12',
                           'oklahoma': 'big-12',
                           'oklahoma-state': 'big-12',
                           'texas-christian': 'big-12',
                           'west-virginia': 'big-12',
                           'kansas': 'big-12',
                           'texas': 'big-12',
                           'texas-tech': 'big-12',
                           'iowa-state': 'big-12',
                           'colorado-state': 'mwc',
                           'air-force': 'mwc',
                           'boise-state': 'mwc',
                           'new-mexico': 'mwc',
                           'wyoming': 'mwc',
                           'utah-state': 'mwc',
                           'hawaii': 'mwc',
                           'fresno-state': 'mwc',
                           'nevada': 'mwc',
                           'nevada-las-vegas': 'mwc',
                           'san-diego-state': 'mwc',
                           'san-jose-state': 'mwc',
                           'california': 'pac-12',
                           'oregon': 'pac-12',
                           'stanford': 'pac-12',
                           'washington-state': 'pac-12',
                           'oregon-state': 'pac-12',
                           'washington': 'pac-12',
                           'arizona-state': 'pac-12',
                           'colorado': 'pac-12',
                           'southern-california': 'pac-12',
                           'utah': 'pac-12',
                           'arizona': 'pac-12',
                           'ucla': 'pac-12',
                           'central-florida': 'american',
                           'connecticut': 'american',
                           'cincinnati': 'american',
                           'south-florida': 'american',
                           'east-carolina': 'american',
                           'temple': 'american',
                           'houston': 'american',
                           'memphis': 'american',
                           'tulsa': 'american',
                           'navy': 'american',
                           'southern-methodist': 'american',
                           'tulane': 'american',
                           'charlotte': 'cusa',
                           'marshall': 'cusa',
                           'florida-atlantic': 'cusa',
                           'florida-international': 'cusa',
                           'middle-tennessee-state': 'cusa',
                           'old-dominion': 'cusa',
                           'western-kentucky': 'cusa',
                           'louisiana-tech': 'cusa',
                           'north-texas': 'cusa',
                           'southern-mississippi': 'cusa',
                           'alabama-birmingham': 'cusa',
                           'rice': 'cusa',
                           'texas-el-paso': 'cusa',
                           'texas-san-antonio': 'cusa',
                           'liberty': 'independent',
                           'massachusetts': 'independent',
                           'new-mexico-state': 'independent',
                           'brigham-young': 'independent',
                           'notre-dame': 'independent',
                           'army': 'independent',
                           'indiana': 'big-ten',
                           'maryland': 'big-ten',
                           'michigan-state': 'big-ten',
                           'ohio-state': 'big-ten',
                           'penn-state': 'big-ten',
                           'rutgers': 'big-ten',
                           'michigan': 'big-ten',
                           'northwestern': 'big-ten',
                           'purdue': 'big-ten',
                           'illinois': 'big-ten',
                           'iowa': 'big-ten',
                           'minnesota': 'big-ten',
                           'wisconsin': 'big-ten',
                           'nebraska': 'big-ten'}
        self.team_conference = team_conference

        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))
        flexmock(Conferences) \
            .should_receive('_find_conferences') \
            .and_return(None)
        flexmock(Conferences) \
            .should_receive('team_conference') \
            .and_return(team_conference)

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

    def test_ncaaf_empty_page_returns_no_teams(self):
        flexmock(utils) \
            .should_receive('_no_data_found') \
            .once()
        flexmock(utils) \
            .should_receive('_get_stats_table') \
            .and_return(None)

        teams = Teams()

        assert len(teams) == 0


class TestNCAAFIntegrationInvalidYear:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_default_year_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        team_conference = {'florida-state': 'acc',
                           'boston-college': 'acc',
                           'clemson': 'acc',
                           'north-carolina-state': 'acc',
                           'syracuse': 'acc',
                           'wake-forest': 'acc',
                           'louisville': 'acc',
                           'virginia-tech': 'acc',
                           'duke': 'acc',
                           'georgia-tech': 'acc',
                           'pittsburgh': 'acc',
                           'virginia': 'acc',
                           'miami-fl': 'acc',
                           'north-carolina': 'acc',
                           'florida': 'sec',
                           'georgia': 'sec',
                           'kentucky': 'sec',
                           'missouri': 'sec',
                           'south-carolina': 'sec',
                           'vanderbilt': 'sec',
                           'tennessee': 'sec',
                           'alabama': 'sec',
                           'arkansas': 'sec',
                           'auburn': 'sec',
                           'louisiana-state': 'sec',
                           'mississippi-state': 'sec',
                           'mississippi': 'sec',
                           'texas-am': 'sec',
                           'buffalo': 'mac',
                           'ohio': 'mac',
                           'bowling-green-state': 'mac',
                           'kent-state': 'mac',
                           'miami-oh': 'mac',
                           'akron': 'mac',
                           'ball-state': 'mac',
                           'eastern-michigan': 'mac',
                           'toledo': 'mac',
                           'central-michigan': 'mac',
                           'northern-illinois': 'mac',
                           'western-michigan': 'mac',
                           'georgia-southern': 'sun-belt',
                           'appalachian-state': 'sun-belt',
                           'coastal-carolina': 'sun-belt',
                           'arkansas-state': 'sun-belt',
                           'georgia-state': 'sun-belt',
                           'louisiana-lafayette': 'sun-belt',
                           'louisiana-monroe': 'sun-belt',
                           'south-alabama': 'sun-belt',
                           'texas-state': 'sun-belt',
                           'troy': 'sun-belt',
                           'idaho': 'sun-belt',
                           'baylor': 'big-12',
                           'kansas-state': 'big-12',
                           'oklahoma': 'big-12',
                           'oklahoma-state': 'big-12',
                           'texas-christian': 'big-12',
                           'west-virginia': 'big-12',
                           'kansas': 'big-12',
                           'texas': 'big-12',
                           'texas-tech': 'big-12',
                           'iowa-state': 'big-12',
                           'colorado-state': 'mwc',
                           'air-force': 'mwc',
                           'boise-state': 'mwc',
                           'new-mexico': 'mwc',
                           'wyoming': 'mwc',
                           'utah-state': 'mwc',
                           'hawaii': 'mwc',
                           'fresno-state': 'mwc',
                           'nevada': 'mwc',
                           'nevada-las-vegas': 'mwc',
                           'san-diego-state': 'mwc',
                           'san-jose-state': 'mwc',
                           'california': 'pac-12',
                           'oregon': 'pac-12',
                           'stanford': 'pac-12',
                           'washington-state': 'pac-12',
                           'oregon-state': 'pac-12',
                           'washington': 'pac-12',
                           'arizona-state': 'pac-12',
                           'colorado': 'pac-12',
                           'southern-california': 'pac-12',
                           'utah': 'pac-12',
                           'arizona': 'pac-12',
                           'ucla': 'pac-12',
                           'central-florida': 'american',
                           'connecticut': 'american',
                           'cincinnati': 'american',
                           'south-florida': 'american',
                           'east-carolina': 'american',
                           'temple': 'american',
                           'houston': 'american',
                           'memphis': 'american',
                           'tulsa': 'american',
                           'navy': 'american',
                           'southern-methodist': 'american',
                           'tulane': 'american',
                           'charlotte': 'cusa',
                           'marshall': 'cusa',
                           'florida-atlantic': 'cusa',
                           'florida-international': 'cusa',
                           'middle-tennessee-state': 'cusa',
                           'old-dominion': 'cusa',
                           'western-kentucky': 'cusa',
                           'louisiana-tech': 'cusa',
                           'north-texas': 'cusa',
                           'southern-mississippi': 'cusa',
                           'alabama-birmingham': 'cusa',
                           'rice': 'cusa',
                           'texas-el-paso': 'cusa',
                           'texas-san-antonio': 'cusa',
                           'liberty': 'independent',
                           'massachusetts': 'independent',
                           'new-mexico-state': 'independent',
                           'brigham-young': 'independent',
                           'notre-dame': 'independent',
                           'army': 'independent',
                           'indiana': 'big-ten',
                           'maryland': 'big-ten',
                           'michigan-state': 'big-ten',
                           'ohio-state': 'big-ten',
                           'penn-state': 'big-ten',
                           'rutgers': 'big-ten',
                           'michigan': 'big-ten',
                           'northwestern': 'big-ten',
                           'purdue': 'big-ten',
                           'illinois': 'big-ten',
                           'iowa': 'big-ten',
                           'minnesota': 'big-ten',
                           'wisconsin': 'big-ten',
                           'nebraska': 'big-ten'}

        flexmock(Conferences) \
            .should_receive('_find_conferences') \
            .and_return(None)
        flexmock(Conferences) \
            .should_receive('team_conference') \
            .and_return(team_conference)
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2018)

        teams = Teams()

        for team in teams:
            assert team._year == '2017'


class TestNCAAFIntegrationInvalidConference:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_conference_returns_none(self, *args, **kwargs):
        team_conference = {'florida-state': 'acc',
                           'boston-college': 'acc',
                           'clemson': 'acc',
                           'north-carolina-state': 'acc',
                           'syracuse': 'acc',
                           'wake-forest': 'acc',
                           'louisville': 'acc',
                           'virginia-tech': 'acc',
                           'duke': 'acc',
                           'georgia-tech': 'acc',
                           'pittsburgh': 'acc',
                           'virginia': 'acc',
                           'miami-fl': 'acc',
                           'north-carolina': 'acc',
                           'florida': 'sec',
                           'georgia': 'sec',
                           'kentucky': 'sec',
                           'missouri': 'sec',
                           'south-carolina': 'sec',
                           'vanderbilt': 'sec',
                           'tennessee': 'sec',
                           'alabama': 'sec',
                           'arkansas': 'sec',
                           'auburn': 'sec',
                           'louisiana-state': 'sec',
                           'mississippi-state': 'sec',
                           'mississippi': 'sec',
                           'texas-am': 'sec',
                           'buffalo': 'mac',
                           'ohio': 'mac',
                           'bowling-green-state': 'mac',
                           'kent-state': 'mac',
                           'miami-oh': 'mac',
                           'akron': 'mac',
                           'ball-state': 'mac',
                           'eastern-michigan': 'mac',
                           'toledo': 'mac',
                           'central-michigan': 'mac',
                           'northern-illinois': 'mac',
                           'western-michigan': 'mac',
                           'georgia-southern': 'sun-belt',
                           'appalachian-state': 'sun-belt',
                           'coastal-carolina': 'sun-belt',
                           'arkansas-state': 'sun-belt',
                           'georgia-state': 'sun-belt',
                           'louisiana-lafayette': 'sun-belt',
                           'louisiana-monroe': 'sun-belt',
                           'south-alabama': 'sun-belt',
                           'texas-state': 'sun-belt',
                           'troy': 'sun-belt',
                           'idaho': 'sun-belt',
                           'baylor': 'big-12',
                           'kansas-state': 'big-12',
                           'oklahoma': 'big-12',
                           'oklahoma-state': 'big-12',
                           'texas-christian': 'big-12',
                           'west-virginia': 'big-12',
                           'kansas': 'big-12',
                           'texas': 'big-12',
                           'texas-tech': 'big-12',
                           'iowa-state': 'big-12',
                           'colorado-state': 'mwc',
                           'air-force': 'mwc',
                           'boise-state': 'mwc',
                           'new-mexico': 'mwc',
                           'wyoming': 'mwc',
                           'utah-state': 'mwc',
                           'hawaii': 'mwc',
                           'fresno-state': 'mwc',
                           'nevada': 'mwc',
                           'nevada-las-vegas': 'mwc',
                           'san-diego-state': 'mwc',
                           'san-jose-state': 'mwc',
                           'california': 'pac-12',
                           'oregon': 'pac-12',
                           'stanford': 'pac-12',
                           'washington-state': 'pac-12',
                           'oregon-state': 'pac-12',
                           'washington': 'pac-12',
                           'arizona-state': 'pac-12',
                           'colorado': 'pac-12',
                           'southern-california': 'pac-12',
                           'utah': 'pac-12',
                           'arizona': 'pac-12',
                           'ucla': 'pac-12',
                           'central-florida': 'american',
                           'connecticut': 'american',
                           'cincinnati': 'american',
                           'south-florida': 'american',
                           'east-carolina': 'american',
                           'temple': 'american',
                           'houston': 'american',
                           'memphis': 'american',
                           'tulsa': 'american',
                           'navy': 'american',
                           'southern-methodist': 'american',
                           'tulane': 'american',
                           'charlotte': 'cusa',
                           'marshall': 'cusa',
                           'florida-atlantic': 'cusa',
                           'florida-international': 'cusa',
                           'middle-tennessee-state': 'cusa',
                           'old-dominion': 'cusa',
                           'western-kentucky': 'cusa',
                           'louisiana-tech': 'cusa',
                           'north-texas': 'cusa',
                           'southern-mississippi': 'cusa',
                           'alabama-birmingham': 'cusa',
                           'rice': 'cusa',
                           'texas-el-paso': 'cusa',
                           'texas-san-antonio': 'cusa',
                           'liberty': 'independent',
                           'massachusetts': 'independent',
                           'new-mexico-state': 'independent',
                           'brigham-young': 'independent',
                           'notre-dame': 'independent',
                           'army': 'independent'}

        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))
        flexmock(Conferences) \
            .should_receive('_find_conferences') \
            .and_return(None)
        flexmock(Conferences) \
            .should_receive('team_conference') \
            .and_return(team_conference)

        big_ten_schools = ['indiana', 'maryland', 'michigan-state',
                           'ohio-state', 'penn-state', 'rutgers', 'michigan',
                           'northwestern', 'purdue', 'illinois', 'iowa',
                           'minnesota', 'wisconsin', 'nebraska']

        teams = Teams()

        for team in big_ten_schools:
            assert teams(team).conference is None
