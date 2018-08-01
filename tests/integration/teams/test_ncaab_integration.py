import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsreference import utils
from sportsreference.ncaab.constants import (ADVANCED_OPPONENT_STATS_URL,
                                             ADVANCED_STATS_URL,
                                             BASIC_OPPONENT_STATS_URL,
                                             BASIC_STATS_URL)
from sportsreference.ncaab.teams import Teams


MONTH = 1
YEAR = 2018


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaab_stats', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if div == 'table#basic_school_stats':
                return read_file('%s-school-stats-table.html' % YEAR)
            elif div == 'table#basic_opp_stats':
                return read_file('%s-opponent-stats-table.html' % YEAR)
            elif div == 'table#adv_school_stats':
                return read_file('%s-advanced-school-stats-table.html' % YEAR)
            else:
                return read_file('%s-advanced-opponent-stats-table.html'
                                 % YEAR)

    basic_contents = read_file('%s-school-stats.html' % YEAR)
    opp_contents = read_file('%s-opponent-stats.html' % YEAR)
    adv_contents = read_file('%s-advanced-school-stats.html' % YEAR)
    adv_opp_contents = read_file('%s-advanced-opponent-stats.html' % YEAR)
    if url == BASIC_STATS_URL % YEAR:
        return MockPQ(basic_contents)
    elif url == BASIC_OPPONENT_STATS_URL % YEAR:
        return MockPQ(opp_contents)
    elif url == ADVANCED_STATS_URL % YEAR:
        return MockPQ(adv_contents)
    elif url == ADVANCED_OPPONENT_STATS_URL % YEAR:
        return MockPQ(adv_opp_contents)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNCAABIntegration:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'abbreviation': 'PURDUE',
            'name': 'Purdue',
            'games_played': 37,
            'wins': 30,
            'losses': 7,
            'win_percentage': .811,
            'simple_rating_system': 23.41,
            'strength_of_schedule': 8.74,
            'conference_wins': 15,
            'conference_losses': 3,
            'home_wins': 16,
            'home_losses': 1,
            'away_wins': 8,
            'away_losses': 2,
            'points': 2974,
            'opp_points': 2431,
            'minutes_played': 1485,
            'field_goals': 1033,
            'field_goal_attempts': 2097,
            'field_goal_percentage': .493,
            'three_point_field_goals': 353,
            'three_point_field_goal_attempts': 840,
            'three_point_field_goal_percentage': .420,
            'free_throws': 555,
            'free_throw_attempts': 747,
            'free_throw_percentage': .743,
            'offensive_rebounds': 311,
            'total_rebounds': 1295,
            'assists': 598,
            'steals': 211,
            'blocks': 180,
            'turnovers': 399,
            'personal_fouls': 580,
            'opp_field_goals': 907,
            'opp_field_goal_attempts': 2197,
            'opp_field_goal_percentage': .413,
            'opp_three_point_field_goals': 251,
            'opp_three_point_field_goal_attempts': 755,
            'opp_three_point_field_goal_percentage': .332,
            'opp_free_throws': 366,
            'opp_free_throw_attempts': 531,
            'opp_free_throw_percentage': .689,
            'opp_offensive_rebounds': 376,
            'opp_total_rebounds': 1204,
            'opp_assists': 443,
            'opp_steals': 190,
            'opp_blocks': 94,
            'opp_turnovers': 448,
            'opp_personal_fouls': 688,
            'pace': 68.2,
            'offensive_rating': 117.5,
            'free_throw_attempt_rate': .356,
            'three_point_attempt_rate': .401,
            'true_shooting_percentage': .606,
            'total_rebound_percentage': 51.8,
            'assist_percentage': 57.9,
            'steal_percentage': 8.3,
            'block_percentage': 12.5,
            'effective_field_goal_percentage': .577,
            'turnover_percentage': 14.0,
            'offensive_rebound_percentage': 27.3,
            'free_throws_per_field_goal_attempt': .265,
            'opp_offensive_rating': 96.0,
            'opp_free_throw_attempt_rate': .242,
            'opp_three_point_attempt_rate': .344,
            'opp_true_shooting_percentage': .496,
            'opp_total_rebound_percentage': 48.2,
            'opp_assist_percentage': 48.8,
            'opp_steal_percentage': 7.5,
            'opp_block_percentage': 7.5,
            'opp_effective_field_goal_percentage': .470,
            'opp_turnover_percentage': 15.5,
            'opp_offensive_rebound_percentage': 27.6,
            'opp_free_throws_per_field_goal_attempt': .167
        }
        self.abbreviations = [
            'ABILENE-CHRISTIAN', 'AIR-FORCE', 'AKRON', 'ALABAMA-AM',
            'ALABAMA-BIRMINGHAM', 'ALABAMA-STATE', 'ALABAMA', 'ALBANY-NY',
            'ALCORN-STATE', 'AMERICAN', 'APPALACHIAN-STATE', 'ARIZONA-STATE',
            'ARIZONA', 'ARKANSAS-LITTLE-ROCK', 'ARKANSAS-PINE-BLUFF',
            'ARKANSAS-STATE', 'ARKANSAS', 'ARMY', 'AUBURN', 'AUSTIN-PEAY',
            'BALL-STATE', 'BAYLOR', 'BELMONT', 'BETHUNE-COOKMAN', 'BINGHAMTON',
            'BOISE-STATE', 'BOSTON-COLLEGE', 'BOSTON-UNIVERSITY',
            'BOWLING-GREEN-STATE', 'BRADLEY', 'BRIGHAM-YOUNG', 'BROWN',
            'BRYANT', 'BUCKNELL', 'BUFFALO', 'BUTLER', 'CAL-POLY',
            'CAL-STATE-BAKERSFIELD', 'CAL-STATE-FULLERTON',
            'CAL-STATE-NORTHRIDGE', 'CALIFORNIA-DAVIS', 'CALIFORNIA-IRVINE',
            'CALIFORNIA-RIVERSIDE', 'CALIFORNIA-SANTA-BARBARA', 'CALIFORNIA',
            'CAMPBELL', 'CANISIUS', 'CENTRAL-ARKANSAS',
            'CENTRAL-CONNECTICUT-STATE', 'CENTRAL-FLORIDA', 'CENTRAL-MICHIGAN',
            'CHARLESTON-SOUTHERN', 'CHARLOTTE', 'CHATTANOOGA', 'CHICAGO-STATE',
            'CINCINNATI', 'CITADEL', 'CLEMSON', 'CLEVELAND-STATE',
            'COASTAL-CAROLINA', 'COLGATE', 'COLLEGE-OF-CHARLESTON',
            'COLORADO-STATE', 'COLORADO', 'COLUMBIA', 'CONNECTICUT',
            'COPPIN-STATE', 'CORNELL', 'CREIGHTON', 'DARTMOUTH', 'DAVIDSON',
            'DAYTON', 'DELAWARE-STATE', 'DELAWARE', 'DENVER', 'DEPAUL',
            'DETROIT-MERCY', 'DRAKE', 'DREXEL', 'DUKE', 'DUQUESNE',
            'EAST-CAROLINA', 'EAST-TENNESSEE-STATE', 'EASTERN-ILLINOIS',
            'EASTERN-KENTUCKY', 'EASTERN-MICHIGAN', 'EASTERN-WASHINGTON',
            'ELON', 'EVANSVILLE', 'FAIRFIELD', 'FAIRLEIGH-DICKINSON',
            'FLORIDA-AM', 'FLORIDA-ATLANTIC', 'FLORIDA-GULF-COAST',
            'FLORIDA-INTERNATIONAL', 'FLORIDA-STATE', 'FLORIDA', 'FORDHAM',
            'FRESNO-STATE', 'FURMAN', 'GARDNER-WEBB', 'GEORGE-MASON',
            'GEORGE-WASHINGTON', 'GEORGETOWN', 'GEORGIA-SOUTHERN',
            'GEORGIA-STATE', 'GEORGIA-TECH', 'GEORGIA', 'GONZAGA', 'GRAMBLING',
            'GRAND-CANYON', 'GREEN-BAY', 'HAMPTON', 'HARTFORD', 'HARVARD',
            'HAWAII', 'HIGH-POINT', 'HOFSTRA', 'HOLY-CROSS', 'HOUSTON-BAPTIST',
            'HOUSTON', 'HOWARD', 'IDAHO-STATE', 'IDAHO', 'ILLINOIS-CHICAGO',
            'ILLINOIS-STATE', 'ILLINOIS', 'INCARNATE-WORD', 'INDIANA-STATE',
            'INDIANA', 'IONA', 'IOWA-STATE', 'IOWA', 'IPFW', 'IUPUI',
            'JACKSON-STATE', 'JACKSONVILLE-STATE', 'JACKSONVILLE',
            'JAMES-MADISON', 'KANSAS-STATE', 'KANSAS', 'KENNESAW-STATE',
            'KENT-STATE', 'KENTUCKY', 'LA-SALLE', 'LAFAYETTE', 'LAMAR',
            'LEHIGH', 'LIBERTY', 'LIPSCOMB', 'LONG-BEACH-STATE',
            'LONG-ISLAND-UNIVERSITY', 'LONGWOOD', 'LOUISIANA-LAFAYETTE',
            'LOUISIANA-MONROE', 'LOUISIANA-STATE', 'LOUISIANA-TECH',
            'LOUISVILLE', 'LOYOLA-IL', 'LOYOLA-MARYMOUNT', 'LOYOLA-MD',
            'MAINE', 'MANHATTAN', 'MARIST', 'MARQUETTE', 'MARSHALL',
            'MARYLAND-BALTIMORE-COUNTY', 'MARYLAND-EASTERN-SHORE', 'MARYLAND',
            'MASSACHUSETTS-LOWELL', 'MASSACHUSETTS', 'MCNEESE-STATE',
            'MEMPHIS', 'MERCER', 'MIAMI-FL', 'MIAMI-OH', 'MICHIGAN-STATE',
            'MICHIGAN', 'MIDDLE-TENNESSEE', 'MILWAUKEE', 'MINNESOTA',
            'MISSISSIPPI-STATE', 'MISSISSIPPI-VALLEY-STATE', 'MISSISSIPPI',
            'MISSOURI-KANSAS-CITY', 'MISSOURI-STATE', 'MISSOURI', 'MONMOUTH',
            'MONTANA-STATE', 'MONTANA', 'MOREHEAD-STATE', 'MORGAN-STATE',
            'MOUNT-ST-MARYS', 'MURRAY-STATE', 'NAVY', 'NEBRASKA-OMAHA',
            'NEBRASKA', 'NEVADA-LAS-VEGAS', 'NEVADA', 'NEW-HAMPSHIRE',
            'NEW-MEXICO-STATE', 'NEW-MEXICO', 'NEW-ORLEANS', 'NIAGARA',
            'NICHOLLS-STATE', 'NJIT', 'NORFOLK-STATE',
            'NORTH-CAROLINA-ASHEVILLE', 'NORTH-CAROLINA-AT',
            'NORTH-CAROLINA-CENTRAL', 'NORTH-CAROLINA-GREENSBORO',
            'NORTH-CAROLINA-STATE', 'NORTH-CAROLINA-WILMINGTON',
            'NORTH-CAROLINA', 'NORTH-DAKOTA-STATE', 'NORTH-DAKOTA',
            'NORTH-FLORIDA', 'NORTH-TEXAS', 'NORTHEASTERN', 'NORTHERN-ARIZONA',
            'NORTHERN-COLORADO', 'NORTHERN-ILLINOIS', 'NORTHERN-IOWA',
            'NORTHERN-KENTUCKY', 'NORTHWESTERN-STATE', 'NORTHWESTERN',
            'NOTRE-DAME', 'OAKLAND', 'OHIO-STATE', 'OHIO', 'OKLAHOMA-STATE',
            'OKLAHOMA', 'OLD-DOMINION', 'ORAL-ROBERTS', 'OREGON-STATE',
            'OREGON', 'PACIFIC', 'PENN-STATE', 'PENNSYLVANIA', 'PEPPERDINE',
            'PITTSBURGH', 'PORTLAND-STATE', 'PORTLAND', 'PRAIRIE-VIEW',
            'PRESBYTERIAN', 'PRINCETON', 'PROVIDENCE', 'PURDUE', 'QUINNIPIAC',
            'RADFORD', 'RHODE-ISLAND', 'RICE', 'RICHMOND', 'RIDER',
            'ROBERT-MORRIS', 'RUTGERS', 'SACRAMENTO-STATE', 'SACRED-HEART',
            'SAINT-FRANCIS-PA', 'SAINT-JOSEPHS', 'SAINT-LOUIS',
            'SAINT-MARYS-CA', 'SAINT-PETERS', 'SAM-HOUSTON-STATE', 'SAMFORD',
            'SAN-DIEGO-STATE', 'SAN-DIEGO', 'SAN-FRANCISCO', 'SAN-JOSE-STATE',
            'SANTA-CLARA', 'SAVANNAH-STATE', 'SEATTLE', 'SETON-HALL', 'SIENA',
            'SOUTH-ALABAMA', 'SOUTH-CAROLINA-STATE', 'SOUTH-CAROLINA-UPSTATE',
            'SOUTH-CAROLINA', 'SOUTH-DAKOTA-STATE', 'SOUTH-DAKOTA',
            'SOUTH-FLORIDA', 'SOUTHEAST-MISSOURI-STATE',
            'SOUTHEASTERN-LOUISIANA', 'SOUTHERN-CALIFORNIA',
            'SOUTHERN-ILLINOIS-EDWARDSVILLE', 'SOUTHERN-ILLINOIS',
            'SOUTHERN-METHODIST', 'SOUTHERN-MISSISSIPPI', 'SOUTHERN-UTAH',
            'SOUTHERN', 'ST-BONAVENTURE', 'ST-FRANCIS-NY', 'ST-JOHNS-NY',
            'STANFORD', 'STEPHEN-F-AUSTIN', 'STETSON', 'STONY-BROOK',
            'SYRACUSE', 'TEMPLE', 'TENNESSEE-MARTIN', 'TENNESSEE-STATE',
            'TENNESSEE-TECH', 'TENNESSEE', 'TEXAS-AM-CORPUS-CHRISTI',
            'TEXAS-AM', 'TEXAS-ARLINGTON', 'TEXAS-CHRISTIAN', 'TEXAS-EL-PASO',
            'TEXAS-PAN-AMERICAN', 'TEXAS-SAN-ANTONIO', 'TEXAS-SOUTHERN',
            'TEXAS-STATE', 'TEXAS-TECH', 'TEXAS', 'TOLEDO', 'TOWSON', 'TROY',
            'TULANE', 'TULSA', 'UCLA', 'UTAH-STATE', 'UTAH-VALLEY', 'UTAH',
            'VALPARAISO', 'VANDERBILT', 'VERMONT', 'VILLANOVA',
            'VIRGINIA-COMMONWEALTH', 'VIRGINIA-MILITARY-INSTITUTE',
            'VIRGINIA-TECH', 'VIRGINIA', 'WAGNER', 'WAKE-FOREST',
            'WASHINGTON-STATE', 'WASHINGTON', 'WEBER-STATE', 'WEST-VIRGINIA',
            'WESTERN-CAROLINA', 'WESTERN-ILLINOIS', 'WESTERN-KENTUCKY',
            'WESTERN-MICHIGAN', 'WICHITA-STATE', 'WILLIAM-MARY', 'WINTHROP',
            'WISCONSIN', 'WOFFORD', 'WRIGHT-STATE', 'WYOMING', 'XAVIER',
            'YALE', 'YOUNGSTOWN-STATE'
        ]

        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.teams = Teams()

    def test_ncaab_integration_returns_correct_number_of_teams(self):
        assert len(self.teams) == len(self.abbreviations)

    def test_ncaab_integration_returns_correct_attributes_for_team(self):
        purdue = self.teams('PURDUE')

        for attribute, value in self.results.items():
            assert getattr(purdue, attribute) == value

    def test_ncaab_integration_returns_correct_team_abbreviations(self):
        for team in self.teams:
            assert team.abbreviation in self.abbreviations

    def test_ncaab_integration_dataframe_returns_dataframe(self):
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

    def test_ncaab_integration_all_teams_dataframe_returns_dataframe(self):
        result = self.teams.dataframes.drop_duplicates(keep=False)

        assert len(result) == len(self.abbreviations)
        assert set(result.columns.values) == set(self.results.keys())

    def test_ncaab_invalid_team_name_raises_value_error(self):
        with pytest.raises(ValueError):
            self.teams('INVALID_NAME')
