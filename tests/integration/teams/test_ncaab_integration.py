import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsipy import utils
from sportsipy.ncaab.conferences import Conferences
from sportsipy.ncaab.constants import (ADVANCED_OPPONENT_STATS_URL,
                                       ADVANCED_STATS_URL,
                                       BASIC_OPPONENT_STATS_URL,
                                       BASIC_STATS_URL)
from sportsipy.ncaab.teams import Team, Teams


MONTH = 1
YEAR = 2018


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaab_stats', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


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


class TestNCAABIntegration:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'conference': 'big-ten',
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
            'two_point_field_goals': 680,
            'two_point_field_goal_attempts': 1257,
            'two_point_field_goal_percentage': .541,
            'free_throws': 555,
            'free_throw_attempts': 747,
            'free_throw_percentage': .743,
            'offensive_rebounds': 311,
            'defensive_rebounds': 984,
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
            'opp_two_point_field_goals': 656,
            'opp_two_point_field_goal_attempts': 1442,
            'opp_two_point_field_goal_percentage': .455,
            'opp_free_throws': 366,
            'opp_free_throw_attempts': 531,
            'opp_free_throw_percentage': .689,
            'opp_offensive_rebounds': 376,
            'opp_defensive_rebounds': 828,
            'opp_total_rebounds': 1204,
            'opp_assists': 443,
            'opp_steals': 190,
            'opp_blocks': 94,
            'opp_turnovers': 448,
            'opp_personal_fouls': 688,
            'pace': 68.2,
            'offensive_rating': 117.5,
            'net_rating': 21.5,
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

        team_conference = {'kansas': 'big-12',
                           'texas-tech': 'big-12',
                           'west-virginia': 'big-12',
                           'kansas-state': 'big-12',
                           'texas-christian': 'big-12',
                           'oklahoma-state': 'big-12',
                           'oklahoma': 'big-12',
                           'baylor': 'big-12',
                           'texas': 'big-12',
                           'iowa-state': 'big-12',
                           'xavier': 'big-east',
                           'villanova': 'big-east',
                           'seton-hall': 'big-east',
                           'creighton': 'big-east',
                           'providence': 'big-east',
                           'butler': 'big-east',
                           'marquette': 'big-east',
                           'georgetown': 'big-east',
                           'st-johns-ny': 'big-east',
                           'depaul': 'big-east',
                           'virginia': 'acc',
                           'duke': 'acc',
                           'clemson': 'acc',
                           'north-carolina': 'acc',
                           'miami-fl': 'acc',
                           'north-carolina-state': 'acc',
                           'virginia-tech': 'acc',
                           'florida-state': 'acc',
                           'louisville': 'acc',
                           'syracuse': 'acc',
                           'notre-dame': 'acc',
                           'boston-college': 'acc',
                           'georgia-tech': 'acc',
                           'wake-forest': 'acc',
                           'pittsburgh': 'acc',
                           'michigan-state': 'big-ten',
                           'purdue': 'big-ten',
                           'ohio-state': 'big-ten',
                           'michigan': 'big-ten',
                           'nebraska': 'big-ten',
                           'penn-state': 'big-ten',
                           'indiana': 'big-ten',
                           'maryland': 'big-ten',
                           'wisconsin': 'big-ten',
                           'northwestern': 'big-ten',
                           'minnesota': 'big-ten',
                           'illinois': 'big-ten',
                           'iowa': 'big-ten',
                           'rutgers': 'big-ten',
                           'auburn': 'sec',
                           'tennessee': 'sec',
                           'florida': 'sec',
                           'kentucky': 'sec',
                           'arkansas': 'sec',
                           'missouri': 'sec',
                           'mississippi-state': 'sec',
                           'texas-am': 'sec',
                           'alabama': 'sec',
                           'louisiana-state': 'sec',
                           'georgia': 'sec',
                           'south-carolina': 'sec',
                           'vanderbilt': 'sec',
                           'mississippi': 'sec',
                           'arizona': 'pac-12',
                           'southern-california': 'pac-12',
                           'utah': 'pac-12',
                           'ucla': 'pac-12',
                           'stanford': 'pac-12',
                           'oregon': 'pac-12',
                           'washington': 'pac-12',
                           'arizona-state': 'pac-12',
                           'colorado': 'pac-12',
                           'oregon-state': 'pac-12',
                           'washington-state': 'pac-12',
                           'california': 'pac-12',
                           'cincinnati': 'aac',
                           'houston': 'aac',
                           'wichita-state': 'aac',
                           'tulsa': 'aac',
                           'memphis': 'aac',
                           'central-florida': 'aac',
                           'temple': 'aac',
                           'connecticut': 'aac',
                           'southern-methodist': 'aac',
                           'tulane': 'aac',
                           'east-carolina': 'aac',
                           'south-florida': 'aac',
                           'nevada': 'mwc',
                           'boise-state': 'mwc',
                           'new-mexico': 'mwc',
                           'san-diego-state': 'mwc',
                           'fresno-state': 'mwc',
                           'wyoming': 'mwc',
                           'nevada-las-vegas': 'mwc',
                           'utah-state': 'mwc',
                           'air-force': 'mwc',
                           'colorado-state': 'mwc',
                           'san-jose-state': 'mwc',
                           'loyola-il': 'mvc',
                           'southern-illinois': 'mvc',
                           'illinois-state': 'mvc',
                           'drake': 'mvc',
                           'bradley': 'mvc',
                           'indiana-state': 'mvc',
                           'missouri-state': 'mvc',
                           'evansville': 'mvc',
                           'northern-iowa': 'mvc',
                           'valparaiso': 'mvc',
                           'rhode-island': 'atlantic-10',
                           'st-bonaventure': 'atlantic-10',
                           'davidson': 'atlantic-10',
                           'saint-josephs': 'atlantic-10',
                           'virginia-commonwealth': 'atlantic-10',
                           'saint-louis': 'atlantic-10',
                           'george-mason': 'atlantic-10',
                           'richmond': 'atlantic-10',
                           'dayton': 'atlantic-10',
                           'duquesne': 'atlantic-10',
                           'george-washington': 'atlantic-10',
                           'la-salle': 'atlantic-10',
                           'massachusetts': 'atlantic-10',
                           'fordham': 'atlantic-10',
                           'gonzaga': 'wcc',
                           'saint-marys-ca': 'wcc',
                           'brigham-young': 'wcc',
                           'san-diego': 'wcc',
                           'san-francisco': 'wcc',
                           'pacific': 'wcc',
                           'santa-clara': 'wcc',
                           'loyola-marymount': 'wcc',
                           'portland': 'wcc',
                           'pepperdine': 'wcc',
                           'middle-tennessee': 'cusa',
                           'old-dominion': 'cusa',
                           'western-kentucky': 'cusa',
                           'marshall': 'cusa',
                           'texas-san-antonio': 'cusa',
                           'alabama-birmingham': 'cusa',
                           'north-texas': 'cusa',
                           'florida-international': 'cusa',
                           'louisiana-tech': 'cusa',
                           'southern-mississippi': 'cusa',
                           'florida-atlantic': 'cusa',
                           'texas-el-paso': 'cusa',
                           'rice': 'cusa',
                           'charlotte': 'cusa',
                           'buffalo': 'mac',
                           'kent-state': 'mac',
                           'miami-oh': 'mac',
                           'bowling-green-state': 'mac',
                           'ohio': 'mac',
                           'akron': 'mac',
                           'toledo': 'mac',
                           'eastern-michigan': 'mac',
                           'ball-state': 'mac',
                           'western-michigan': 'mac',
                           'central-michigan': 'mac',
                           'northern-illinois': 'mac',
                           'south-dakota-state': 'summit',
                           'south-dakota': 'summit',
                           'denver': 'summit',
                           'ipfw': 'summit',
                           'north-dakota-state': 'summit',
                           'oral-roberts': 'summit',
                           'nebraska-omaha': 'summit',
                           'western-illinois': 'summit',
                           'louisiana-lafayette': 'sun-belt',
                           'georgia-state': 'sun-belt',
                           'georgia-southern': 'sun-belt',
                           'texas-arlington': 'sun-belt',
                           'louisiana-monroe': 'sun-belt',
                           'troy': 'sun-belt',
                           'appalachian-state': 'sun-belt',
                           'coastal-carolina': 'sun-belt',
                           'texas-state': 'sun-belt',
                           'south-alabama': 'sun-belt',
                           'arkansas-state': 'sun-belt',
                           'arkansas-little-rock': 'sun-belt',
                           'college-of-charleston': 'colonial',
                           'northeastern': 'colonial',
                           'hofstra': 'colonial',
                           'william-mary': 'colonial',
                           'towson': 'colonial',
                           'north-carolina-wilmington': 'colonial',
                           'elon': 'colonial',
                           'delaware': 'colonial',
                           'drexel': 'colonial',
                           'james-madison': 'colonial',
                           'montana': 'big-sky',
                           'idaho': 'big-sky',
                           'weber-state': 'big-sky',
                           'eastern-washington': 'big-sky',
                           'northern-colorado': 'big-sky',
                           'portland-state': 'big-sky',
                           'idaho-state': 'big-sky',
                           'montana-state': 'big-sky',
                           'north-dakota': 'big-sky',
                           'southern-utah': 'big-sky',
                           'sacramento-state': 'big-sky',
                           'northern-arizona': 'big-sky',
                           'new-mexico-state': 'wac',
                           'utah-valley': 'wac',
                           'grand-canyon': 'wac',
                           'seattle': 'wac',
                           'texas-pan-american': 'wac',
                           'cal-state-bakersfield': 'wac',
                           'missouri-kansas-city': 'wac',
                           'chicago-state': 'wac',
                           'california-davis': 'big-west',
                           'california-santa-barbara': 'big-west',
                           'california-irvine': 'big-west',
                           'cal-state-fullerton': 'big-west',
                           'long-beach-state': 'big-west',
                           'hawaii': 'big-west',
                           'cal-poly': 'big-west',
                           'california-riverside': 'big-west',
                           'cal-state-northridge': 'big-west',
                           'pennsylvania': 'ivy',
                           'harvard': 'ivy',
                           'yale': 'ivy',
                           'cornell': 'ivy',
                           'princeton': 'ivy',
                           'columbia': 'ivy',
                           'brown': 'ivy',
                           'dartmouth': 'ivy',
                           'rider': 'maac',
                           'canisius': 'maac',
                           'niagara': 'maac',
                           'iona': 'maac',
                           'fairfield': 'maac',
                           'manhattan': 'maac',
                           'quinnipiac': 'maac',
                           'monmouth': 'maac',
                           'saint-peters': 'maac',
                           'siena': 'maac',
                           'marist': 'maac',
                           'north-carolina-greensboro': 'southern',
                           'east-tennessee-state': 'southern',
                           'furman': 'southern',
                           'wofford': 'southern',
                           'mercer': 'southern',
                           'western-carolina': 'southern',
                           'samford': 'southern',
                           'citadel': 'southern',
                           'virginia-military-institute': 'southern',
                           'chattanooga': 'southern',
                           'murray-state': 'ovc',
                           'belmont': 'ovc',
                           'austin-peay': 'ovc',
                           'jacksonville-state': 'ovc',
                           'tennessee-tech': 'ovc',
                           'tennessee-state': 'ovc',
                           'southeast-missouri-state': 'ovc',
                           'eastern-illinois': 'ovc',
                           'eastern-kentucky': 'ovc',
                           'tennessee-martin': 'ovc',
                           'southern-illinois-edwardsville': 'ovc',
                           'morehead-state': 'ovc',
                           'vermont': 'america-east',
                           'maryland-baltimore-county': 'america-east',
                           'hartford': 'america-east',
                           'albany-ny': 'america-east',
                           'stony-brook': 'america-east',
                           'massachusetts-lowell': 'america-east',
                           'new-hampshire': 'america-east',
                           'maine': 'america-east',
                           'binghamton': 'america-east',
                           'northern-kentucky': 'horizon',
                           'wright-state': 'horizon',
                           'illinois-chicago': 'horizon',
                           'oakland': 'horizon',
                           'milwaukee': 'horizon',
                           'iupui': 'horizon',
                           'green-bay': 'horizon',
                           'cleveland-state': 'horizon',
                           'youngstown-state': 'horizon',
                           'detroit-mercy': 'horizon',
                           'north-carolina-asheville': 'big-south',
                           'radford': 'big-south',
                           'winthrop': 'big-south',
                           'campbell': 'big-south',
                           'liberty': 'big-south',
                           'charleston-southern': 'big-south',
                           'high-point': 'big-south',
                           'gardner-webb': 'big-south',
                           'presbyterian': 'big-south',
                           'longwood': 'big-south',
                           'bucknell': 'patriot',
                           'colgate': 'patriot',
                           'navy': 'patriot',
                           'lehigh': 'patriot',
                           'boston-university': 'patriot',
                           'holy-cross': 'patriot',
                           'lafayette': 'patriot',
                           'army': 'patriot',
                           'loyola-md': 'patriot',
                           'american': 'patriot',
                           'florida-gulf-coast': 'atlantic-sun',
                           'lipscomb': 'atlantic-sun',
                           'jacksonville': 'atlantic-sun',
                           'njit': 'atlantic-sun',
                           'north-florida': 'atlantic-sun',
                           'kennesaw-state': 'atlantic-sun',
                           'stetson': 'atlantic-sun',
                           'south-carolina-upstate': 'atlantic-sun',
                           'nicholls-state': 'southland',
                           'southeastern-louisiana': 'southland',
                           'stephen-f-austin': 'southland',
                           'sam-houston-state': 'southland',
                           'lamar': 'southland',
                           'new-orleans': 'southland',
                           'central-arkansas': 'southland',
                           'abilene-christian': 'southland',
                           'mcneese-state': 'southland',
                           'texas-am-corpus-christi': 'southland',
                           'incarnate-word': 'southland',
                           'houston-baptist': 'southland',
                           'northwestern-state': 'southland',
                           'wagner': 'northeast',
                           'saint-francis-pa': 'northeast',
                           'mount-st-marys': 'northeast',
                           'long-island-university': 'northeast',
                           'st-francis-ny': 'northeast',
                           'robert-morris': 'northeast',
                           'fairleigh-dickinson': 'northeast',
                           'central-connecticut-state': 'northeast',
                           'sacred-heart': 'northeast',
                           'bryant': 'northeast',
                           'grambling': 'swac',
                           'prairie-view': 'swac',
                           'texas-southern': 'swac',
                           'arkansas-pine-bluff': 'swac',
                           'southern': 'swac',
                           'jackson-state': 'swac',
                           'alabama-state': 'swac',
                           'alcorn-state': 'swac',
                           'mississippi-valley-state': 'swac',
                           'alabama-am': 'swac',
                           'bethune-cookman': 'meac',
                           'savannah-state': 'meac',
                           'hampton': 'meac',
                           'north-carolina-at': 'meac',
                           'norfolk-state': 'meac',
                           'north-carolina-central': 'meac',
                           'morgan-state': 'meac',
                           'howard': 'meac',
                           'florida-am': 'meac',
                           'south-carolina-state': 'meac',
                           'coppin-state': 'meac',
                           'maryland-eastern-shore': 'meac',
                           'delaware-state': 'meac'}
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

    def test_ncaab_empty_page_returns_no_teams(self):
        flexmock(utils) \
            .should_receive('_no_data_found') \
            .once()
        flexmock(utils) \
            .should_receive('_get_stats_table') \
            .and_return(None)

        teams = Teams()

        assert len(teams) == 0

    def test_ncaab_no_conference_info_skips_team(self):
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))
        flexmock(Conferences) \
            .should_receive('team_conference') \
            .and_return({})
        flexmock(Conferences) \
            .should_receive('_find_conferences') \
            .and_return(None)

        teams = Teams()

        assert len(teams) == 0

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_pulling_team_directly(self, *args, **kwargs):
        purdue = Team('PURDUE')

        for attribute, value in self.results.items():
            assert getattr(purdue, attribute) == value

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_team_string_representation(self, *args, **kwargs):
        purdue = Team('PURDUE')

        assert purdue.__repr__() == 'Purdue (PURDUE) - 2018'

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_teams_string_representation(self, *args, **kwargs):
        expected = """Abilene Christian (ABILENE-CHRISTIAN)
Air Force (AIR-FORCE)
Akron (AKRON)
Alabama A&M (ALABAMA-AM)
Alabama-Birmingham (ALABAMA-BIRMINGHAM)
Alabama State (ALABAMA-STATE)
Alabama (ALABAMA)
Albany (NY) (ALBANY-NY)
Alcorn State (ALCORN-STATE)
American (AMERICAN)
Appalachian State (APPALACHIAN-STATE)
Arizona State (ARIZONA-STATE)
Arizona (ARIZONA)
Little Rock (ARKANSAS-LITTLE-ROCK)
Arkansas-Pine Bluff (ARKANSAS-PINE-BLUFF)
Arkansas State (ARKANSAS-STATE)
Arkansas (ARKANSAS)
Army (ARMY)
Auburn (AUBURN)
Austin Peay (AUSTIN-PEAY)
Ball State (BALL-STATE)
Baylor (BAYLOR)
Belmont (BELMONT)
Bethune-Cookman (BETHUNE-COOKMAN)
Binghamton (BINGHAMTON)
Boise State (BOISE-STATE)
Boston College (BOSTON-COLLEGE)
Boston University (BOSTON-UNIVERSITY)
Bowling Green State (BOWLING-GREEN-STATE)
Bradley (BRADLEY)
Brigham Young (BRIGHAM-YOUNG)
Brown (BROWN)
Bryant (BRYANT)
Bucknell (BUCKNELL)
Buffalo (BUFFALO)
Butler (BUTLER)
Cal Poly (CAL-POLY)
Cal State Bakersfield (CAL-STATE-BAKERSFIELD)
Cal State Fullerton (CAL-STATE-FULLERTON)
Cal State Northridge (CAL-STATE-NORTHRIDGE)
UC-Davis (CALIFORNIA-DAVIS)
UC-Irvine (CALIFORNIA-IRVINE)
UC-Riverside (CALIFORNIA-RIVERSIDE)
UC-Santa Barbara (CALIFORNIA-SANTA-BARBARA)
University of California (CALIFORNIA)
Campbell (CAMPBELL)
Canisius (CANISIUS)
Central Arkansas (CENTRAL-ARKANSAS)
Central Connecticut State (CENTRAL-CONNECTICUT-STATE)
Central Florida (CENTRAL-FLORIDA)
Central Michigan (CENTRAL-MICHIGAN)
Charleston Southern (CHARLESTON-SOUTHERN)
Charlotte (CHARLOTTE)
Chattanooga (CHATTANOOGA)
Chicago State (CHICAGO-STATE)
Cincinnati (CINCINNATI)
Citadel (CITADEL)
Clemson (CLEMSON)
Cleveland State (CLEVELAND-STATE)
Coastal Carolina (COASTAL-CAROLINA)
Colgate (COLGATE)
College of Charleston (COLLEGE-OF-CHARLESTON)
Colorado State (COLORADO-STATE)
Colorado (COLORADO)
Columbia (COLUMBIA)
Connecticut (CONNECTICUT)
Coppin State (COPPIN-STATE)
Cornell (CORNELL)
Creighton (CREIGHTON)
Dartmouth (DARTMOUTH)
Davidson (DAVIDSON)
Dayton (DAYTON)
Delaware State (DELAWARE-STATE)
Delaware (DELAWARE)
Denver (DENVER)
DePaul (DEPAUL)
Detroit Mercy (DETROIT-MERCY)
Drake (DRAKE)
Drexel (DREXEL)
Duke (DUKE)
Duquesne (DUQUESNE)
East Carolina (EAST-CAROLINA)
East Tennessee State (EAST-TENNESSEE-STATE)
Eastern Illinois (EASTERN-ILLINOIS)
Eastern Kentucky (EASTERN-KENTUCKY)
Eastern Michigan (EASTERN-MICHIGAN)
Eastern Washington (EASTERN-WASHINGTON)
Elon (ELON)
Evansville (EVANSVILLE)
Fairfield (FAIRFIELD)
Fairleigh Dickinson (FAIRLEIGH-DICKINSON)
Florida A&M (FLORIDA-AM)
Florida Atlantic (FLORIDA-ATLANTIC)
Florida Gulf Coast (FLORIDA-GULF-COAST)
Florida International (FLORIDA-INTERNATIONAL)
Florida State (FLORIDA-STATE)
Florida (FLORIDA)
Fordham (FORDHAM)
Fresno State (FRESNO-STATE)
Furman (FURMAN)
Gardner-Webb (GARDNER-WEBB)
George Mason (GEORGE-MASON)
George Washington (GEORGE-WASHINGTON)
Georgetown (GEORGETOWN)
Georgia Southern (GEORGIA-SOUTHERN)
Georgia State (GEORGIA-STATE)
Georgia Tech (GEORGIA-TECH)
Georgia (GEORGIA)
Gonzaga (GONZAGA)
Grambling (GRAMBLING)
Grand Canyon (GRAND-CANYON)
Green Bay (GREEN-BAY)
Hampton (HAMPTON)
Hartford (HARTFORD)
Harvard (HARVARD)
Hawaii (HAWAII)
High Point (HIGH-POINT)
Hofstra (HOFSTRA)
Holy Cross (HOLY-CROSS)
Houston Baptist (HOUSTON-BAPTIST)
Houston (HOUSTON)
Howard (HOWARD)
Idaho State (IDAHO-STATE)
Idaho (IDAHO)
Illinois-Chicago (ILLINOIS-CHICAGO)
Illinois State (ILLINOIS-STATE)
Illinois (ILLINOIS)
Incarnate Word (INCARNATE-WORD)
Indiana State (INDIANA-STATE)
Indiana (INDIANA)
Iona (IONA)
Iowa State (IOWA-STATE)
Iowa (IOWA)
Fort Wayne (IPFW)
IUPUI (IUPUI)
Jackson State (JACKSON-STATE)
Jacksonville State (JACKSONVILLE-STATE)
Jacksonville (JACKSONVILLE)
James Madison (JAMES-MADISON)
Kansas State (KANSAS-STATE)
Kansas (KANSAS)
Kennesaw State (KENNESAW-STATE)
Kent State (KENT-STATE)
Kentucky (KENTUCKY)
La Salle (LA-SALLE)
Lafayette (LAFAYETTE)
Lamar (LAMAR)
Lehigh (LEHIGH)
Liberty (LIBERTY)
Lipscomb (LIPSCOMB)
Long Beach State (LONG-BEACH-STATE)
Long Island University (LONG-ISLAND-UNIVERSITY)
Longwood (LONGWOOD)
Louisiana (LOUISIANA-LAFAYETTE)
Louisiana-Monroe (LOUISIANA-MONROE)
Louisiana State (LOUISIANA-STATE)
Louisiana Tech (LOUISIANA-TECH)
Louisville (LOUISVILLE)
Loyola (IL) (LOYOLA-IL)
Loyola Marymount (LOYOLA-MARYMOUNT)
Loyola (MD) (LOYOLA-MD)
Maine (MAINE)
Manhattan (MANHATTAN)
Marist (MARIST)
Marquette (MARQUETTE)
Marshall (MARSHALL)
Maryland-Baltimore County (MARYLAND-BALTIMORE-COUNTY)
Maryland-Eastern Shore (MARYLAND-EASTERN-SHORE)
Maryland (MARYLAND)
Massachusetts-Lowell (MASSACHUSETTS-LOWELL)
Massachusetts (MASSACHUSETTS)
McNeese State (MCNEESE-STATE)
Memphis (MEMPHIS)
Mercer (MERCER)
Miami (FL) (MIAMI-FL)
Miami (OH) (MIAMI-OH)
Michigan State (MICHIGAN-STATE)
Michigan (MICHIGAN)
Middle Tennessee (MIDDLE-TENNESSEE)
Milwaukee (MILWAUKEE)
Minnesota (MINNESOTA)
Mississippi State (MISSISSIPPI-STATE)
Mississippi Valley State (MISSISSIPPI-VALLEY-STATE)
Mississippi (MISSISSIPPI)
Missouri-Kansas City (MISSOURI-KANSAS-CITY)
Missouri State (MISSOURI-STATE)
Missouri (MISSOURI)
Monmouth (MONMOUTH)
Montana State (MONTANA-STATE)
Montana (MONTANA)
Morehead State (MOREHEAD-STATE)
Morgan State (MORGAN-STATE)
Mount St. Mary's (MOUNT-ST-MARYS)
Murray State (MURRAY-STATE)
Navy (NAVY)
Omaha (NEBRASKA-OMAHA)
Nebraska (NEBRASKA)
Nevada-Las Vegas (NEVADA-LAS-VEGAS)
Nevada (NEVADA)
New Hampshire (NEW-HAMPSHIRE)
New Mexico State (NEW-MEXICO-STATE)
New Mexico (NEW-MEXICO)
New Orleans (NEW-ORLEANS)
Niagara (NIAGARA)
Nicholls State (NICHOLLS-STATE)
NJIT (NJIT)
Norfolk State (NORFOLK-STATE)
North Carolina-Asheville (NORTH-CAROLINA-ASHEVILLE)
North Carolina A&T (NORTH-CAROLINA-AT)
North Carolina Central (NORTH-CAROLINA-CENTRAL)
North Carolina-Greensboro (NORTH-CAROLINA-GREENSBORO)
North Carolina State (NORTH-CAROLINA-STATE)
North Carolina-Wilmington (NORTH-CAROLINA-WILMINGTON)
North Carolina (NORTH-CAROLINA)
North Dakota State (NORTH-DAKOTA-STATE)
North Dakota (NORTH-DAKOTA)
North Florida (NORTH-FLORIDA)
North Texas (NORTH-TEXAS)
Northeastern (NORTHEASTERN)
Northern Arizona (NORTHERN-ARIZONA)
Northern Colorado (NORTHERN-COLORADO)
Northern Illinois (NORTHERN-ILLINOIS)
Northern Iowa (NORTHERN-IOWA)
Northern Kentucky (NORTHERN-KENTUCKY)
Northwestern State (NORTHWESTERN-STATE)
Northwestern (NORTHWESTERN)
Notre Dame (NOTRE-DAME)
Oakland (OAKLAND)
Ohio State (OHIO-STATE)
Ohio (OHIO)
Oklahoma State (OKLAHOMA-STATE)
Oklahoma (OKLAHOMA)
Old Dominion (OLD-DOMINION)
Oral Roberts (ORAL-ROBERTS)
Oregon State (OREGON-STATE)
Oregon (OREGON)
Pacific (PACIFIC)
Penn State (PENN-STATE)
Pennsylvania (PENNSYLVANIA)
Pepperdine (PEPPERDINE)
Pittsburgh (PITTSBURGH)
Portland State (PORTLAND-STATE)
Portland (PORTLAND)
Prairie View (PRAIRIE-VIEW)
Presbyterian (PRESBYTERIAN)
Princeton (PRINCETON)
Providence (PROVIDENCE)
Purdue (PURDUE)
Quinnipiac (QUINNIPIAC)
Radford (RADFORD)
Rhode Island (RHODE-ISLAND)
Rice (RICE)
Richmond (RICHMOND)
Rider (RIDER)
Robert Morris (ROBERT-MORRIS)
Rutgers (RUTGERS)
Sacramento State (SACRAMENTO-STATE)
Sacred Heart (SACRED-HEART)
Saint Francis (PA) (SAINT-FRANCIS-PA)
Saint Joseph's (SAINT-JOSEPHS)
Saint Louis (SAINT-LOUIS)
Saint Mary's (CA) (SAINT-MARYS-CA)
Saint Peter's (SAINT-PETERS)
Sam Houston State (SAM-HOUSTON-STATE)
Samford (SAMFORD)
San Diego State (SAN-DIEGO-STATE)
San Diego (SAN-DIEGO)
San Francisco (SAN-FRANCISCO)
San Jose State (SAN-JOSE-STATE)
Santa Clara (SANTA-CLARA)
Savannah State (SAVANNAH-STATE)
Seattle (SEATTLE)
Seton Hall (SETON-HALL)
Siena (SIENA)
South Alabama (SOUTH-ALABAMA)
South Carolina State (SOUTH-CAROLINA-STATE)
South Carolina Upstate (SOUTH-CAROLINA-UPSTATE)
South Carolina (SOUTH-CAROLINA)
South Dakota State (SOUTH-DAKOTA-STATE)
South Dakota (SOUTH-DAKOTA)
South Florida (SOUTH-FLORIDA)
Southeast Missouri State (SOUTHEAST-MISSOURI-STATE)
Southeastern Louisiana (SOUTHEASTERN-LOUISIANA)
Southern California (SOUTHERN-CALIFORNIA)
SIU Edwardsville (SOUTHERN-ILLINOIS-EDWARDSVILLE)
Southern Illinois (SOUTHERN-ILLINOIS)
Southern Methodist (SOUTHERN-METHODIST)
Southern Mississippi (SOUTHERN-MISSISSIPPI)
Southern Utah (SOUTHERN-UTAH)
Southern (SOUTHERN)
St. Bonaventure (ST-BONAVENTURE)
St. Francis (NY) (ST-FRANCIS-NY)
St. John's (NY) (ST-JOHNS-NY)
Stanford (STANFORD)
Stephen F. Austin (STEPHEN-F-AUSTIN)
Stetson (STETSON)
Stony Brook (STONY-BROOK)
Syracuse (SYRACUSE)
Temple (TEMPLE)
Tennessee-Martin (TENNESSEE-MARTIN)
Tennessee State (TENNESSEE-STATE)
Tennessee Tech (TENNESSEE-TECH)
Tennessee (TENNESSEE)
Texas A&M-Corpus Christi (TEXAS-AM-CORPUS-CHRISTI)
Texas A&M (TEXAS-AM)
Texas-Arlington (TEXAS-ARLINGTON)
Texas Christian (TEXAS-CHRISTIAN)
Texas-El Paso (TEXAS-EL-PASO)
Texas-Rio Grande Valley (TEXAS-PAN-AMERICAN)
Texas-San Antonio (TEXAS-SAN-ANTONIO)
Texas Southern (TEXAS-SOUTHERN)
Texas State (TEXAS-STATE)
Texas Tech (TEXAS-TECH)
Texas (TEXAS)
Toledo (TOLEDO)
Towson (TOWSON)
Troy (TROY)
Tulane (TULANE)
Tulsa (TULSA)
UCLA (UCLA)
Utah State (UTAH-STATE)
Utah Valley (UTAH-VALLEY)
Utah (UTAH)
Valparaiso (VALPARAISO)
Vanderbilt (VANDERBILT)
Vermont (VERMONT)
Villanova (VILLANOVA)
Virginia Commonwealth (VIRGINIA-COMMONWEALTH)
VMI (VIRGINIA-MILITARY-INSTITUTE)
Virginia Tech (VIRGINIA-TECH)
Virginia (VIRGINIA)
Wagner (WAGNER)
Wake Forest (WAKE-FOREST)
Washington State (WASHINGTON-STATE)
Washington (WASHINGTON)
Weber State (WEBER-STATE)
West Virginia (WEST-VIRGINIA)
Western Carolina (WESTERN-CAROLINA)
Western Illinois (WESTERN-ILLINOIS)
Western Kentucky (WESTERN-KENTUCKY)
Western Michigan (WESTERN-MICHIGAN)
Wichita State (WICHITA-STATE)
William & Mary (WILLIAM-MARY)
Winthrop (WINTHROP)
Wisconsin (WISCONSIN)
Wofford (WOFFORD)
Wright State (WRIGHT-STATE)
Wyoming (WYOMING)
Xavier (XAVIER)
Yale (YALE)
Youngstown State (YOUNGSTOWN-STATE)"""

        teams = Teams()

        assert teams.__repr__() == expected


class TestNCAABIntegrationInvalidYear:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_pyquery)
    def test_invalid_default_year_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        team_conference = {'kansas': 'big-12',
                           'texas-tech': 'big-12',
                           'west-virginia': 'big-12',
                           'kansas-state': 'big-12',
                           'texas-christian': 'big-12',
                           'oklahoma-state': 'big-12',
                           'oklahoma': 'big-12',
                           'baylor': 'big-12',
                           'texas': 'big-12',
                           'iowa-state': 'big-12',
                           'xavier': 'big-east',
                           'villanova': 'big-east',
                           'seton-hall': 'big-east',
                           'creighton': 'big-east',
                           'providence': 'big-east',
                           'butler': 'big-east',
                           'marquette': 'big-east',
                           'georgetown': 'big-east',
                           'st-johns-ny': 'big-east',
                           'depaul': 'big-east',
                           'virginia': 'acc',
                           'duke': 'acc',
                           'clemson': 'acc',
                           'north-carolina': 'acc',
                           'miami-fl': 'acc',
                           'north-carolina-state': 'acc',
                           'virginia-tech': 'acc',
                           'florida-state': 'acc',
                           'louisville': 'acc',
                           'syracuse': 'acc',
                           'notre-dame': 'acc',
                           'boston-college': 'acc',
                           'georgia-tech': 'acc',
                           'wake-forest': 'acc',
                           'pittsburgh': 'acc',
                           'michigan-state': 'big-ten',
                           'purdue': 'big-ten',
                           'ohio-state': 'big-ten',
                           'michigan': 'big-ten',
                           'nebraska': 'big-ten',
                           'penn-state': 'big-ten',
                           'indiana': 'big-ten',
                           'maryland': 'big-ten',
                           'wisconsin': 'big-ten',
                           'northwestern': 'big-ten',
                           'minnesota': 'big-ten',
                           'illinois': 'big-ten',
                           'iowa': 'big-ten',
                           'rutgers': 'big-ten',
                           'auburn': 'sec',
                           'tennessee': 'sec',
                           'florida': 'sec',
                           'kentucky': 'sec',
                           'arkansas': 'sec',
                           'missouri': 'sec',
                           'mississippi-state': 'sec',
                           'texas-am': 'sec',
                           'alabama': 'sec',
                           'louisiana-state': 'sec',
                           'georgia': 'sec',
                           'south-carolina': 'sec',
                           'vanderbilt': 'sec',
                           'mississippi': 'sec',
                           'arizona': 'pac-12',
                           'southern-california': 'pac-12',
                           'utah': 'pac-12',
                           'ucla': 'pac-12',
                           'stanford': 'pac-12',
                           'oregon': 'pac-12',
                           'washington': 'pac-12',
                           'arizona-state': 'pac-12',
                           'colorado': 'pac-12',
                           'oregon-state': 'pac-12',
                           'washington-state': 'pac-12',
                           'california': 'pac-12',
                           'cincinnati': 'aac',
                           'houston': 'aac',
                           'wichita-state': 'aac',
                           'tulsa': 'aac',
                           'memphis': 'aac',
                           'central-florida': 'aac',
                           'temple': 'aac',
                           'connecticut': 'aac',
                           'southern-methodist': 'aac',
                           'tulane': 'aac',
                           'east-carolina': 'aac',
                           'south-florida': 'aac',
                           'nevada': 'mwc',
                           'boise-state': 'mwc',
                           'new-mexico': 'mwc',
                           'san-diego-state': 'mwc',
                           'fresno-state': 'mwc',
                           'wyoming': 'mwc',
                           'nevada-las-vegas': 'mwc',
                           'utah-state': 'mwc',
                           'air-force': 'mwc',
                           'colorado-state': 'mwc',
                           'san-jose-state': 'mwc',
                           'loyola-il': 'mvc',
                           'southern-illinois': 'mvc',
                           'illinois-state': 'mvc',
                           'drake': 'mvc',
                           'bradley': 'mvc',
                           'indiana-state': 'mvc',
                           'missouri-state': 'mvc',
                           'evansville': 'mvc',
                           'northern-iowa': 'mvc',
                           'valparaiso': 'mvc',
                           'rhode-island': 'atlantic-10',
                           'st-bonaventure': 'atlantic-10',
                           'davidson': 'atlantic-10',
                           'saint-josephs': 'atlantic-10',
                           'virginia-commonwealth': 'atlantic-10',
                           'saint-louis': 'atlantic-10',
                           'george-mason': 'atlantic-10',
                           'richmond': 'atlantic-10',
                           'dayton': 'atlantic-10',
                           'duquesne': 'atlantic-10',
                           'george-washington': 'atlantic-10',
                           'la-salle': 'atlantic-10',
                           'massachusetts': 'atlantic-10',
                           'fordham': 'atlantic-10',
                           'gonzaga': 'wcc',
                           'saint-marys-ca': 'wcc',
                           'brigham-young': 'wcc',
                           'san-diego': 'wcc',
                           'san-francisco': 'wcc',
                           'pacific': 'wcc',
                           'santa-clara': 'wcc',
                           'loyola-marymount': 'wcc',
                           'portland': 'wcc',
                           'pepperdine': 'wcc',
                           'middle-tennessee': 'cusa',
                           'old-dominion': 'cusa',
                           'western-kentucky': 'cusa',
                           'marshall': 'cusa',
                           'texas-san-antonio': 'cusa',
                           'alabama-birmingham': 'cusa',
                           'north-texas': 'cusa',
                           'florida-international': 'cusa',
                           'louisiana-tech': 'cusa',
                           'southern-mississippi': 'cusa',
                           'florida-atlantic': 'cusa',
                           'texas-el-paso': 'cusa',
                           'rice': 'cusa',
                           'charlotte': 'cusa',
                           'buffalo': 'mac',
                           'kent-state': 'mac',
                           'miami-oh': 'mac',
                           'bowling-green-state': 'mac',
                           'ohio': 'mac',
                           'akron': 'mac',
                           'toledo': 'mac',
                           'eastern-michigan': 'mac',
                           'ball-state': 'mac',
                           'western-michigan': 'mac',
                           'central-michigan': 'mac',
                           'northern-illinois': 'mac',
                           'south-dakota-state': 'summit',
                           'south-dakota': 'summit',
                           'denver': 'summit',
                           'ipfw': 'summit',
                           'north-dakota-state': 'summit',
                           'oral-roberts': 'summit',
                           'nebraska-omaha': 'summit',
                           'western-illinois': 'summit',
                           'louisiana-lafayette': 'sun-belt',
                           'georgia-state': 'sun-belt',
                           'georgia-southern': 'sun-belt',
                           'texas-arlington': 'sun-belt',
                           'louisiana-monroe': 'sun-belt',
                           'troy': 'sun-belt',
                           'appalachian-state': 'sun-belt',
                           'coastal-carolina': 'sun-belt',
                           'texas-state': 'sun-belt',
                           'south-alabama': 'sun-belt',
                           'arkansas-state': 'sun-belt',
                           'arkansas-little-rock': 'sun-belt',
                           'college-of-charleston': 'colonial',
                           'northeastern': 'colonial',
                           'hofstra': 'colonial',
                           'william-mary': 'colonial',
                           'towson': 'colonial',
                           'north-carolina-wilmington': 'colonial',
                           'elon': 'colonial',
                           'delaware': 'colonial',
                           'drexel': 'colonial',
                           'james-madison': 'colonial',
                           'montana': 'big-sky',
                           'idaho': 'big-sky',
                           'weber-state': 'big-sky',
                           'eastern-washington': 'big-sky',
                           'northern-colorado': 'big-sky',
                           'portland-state': 'big-sky',
                           'idaho-state': 'big-sky',
                           'montana-state': 'big-sky',
                           'north-dakota': 'big-sky',
                           'southern-utah': 'big-sky',
                           'sacramento-state': 'big-sky',
                           'northern-arizona': 'big-sky',
                           'new-mexico-state': 'wac',
                           'utah-valley': 'wac',
                           'grand-canyon': 'wac',
                           'seattle': 'wac',
                           'texas-pan-american': 'wac',
                           'cal-state-bakersfield': 'wac',
                           'missouri-kansas-city': 'wac',
                           'chicago-state': 'wac',
                           'california-davis': 'big-west',
                           'california-santa-barbara': 'big-west',
                           'california-irvine': 'big-west',
                           'cal-state-fullerton': 'big-west',
                           'long-beach-state': 'big-west',
                           'hawaii': 'big-west',
                           'cal-poly': 'big-west',
                           'california-riverside': 'big-west',
                           'cal-state-northridge': 'big-west',
                           'pennsylvania': 'ivy',
                           'harvard': 'ivy',
                           'yale': 'ivy',
                           'cornell': 'ivy',
                           'princeton': 'ivy',
                           'columbia': 'ivy',
                           'brown': 'ivy',
                           'dartmouth': 'ivy',
                           'rider': 'maac',
                           'canisius': 'maac',
                           'niagara': 'maac',
                           'iona': 'maac',
                           'fairfield': 'maac',
                           'manhattan': 'maac',
                           'quinnipiac': 'maac',
                           'monmouth': 'maac',
                           'saint-peters': 'maac',
                           'siena': 'maac',
                           'marist': 'maac',
                           'north-carolina-greensboro': 'southern',
                           'east-tennessee-state': 'southern',
                           'furman': 'southern',
                           'wofford': 'southern',
                           'mercer': 'southern',
                           'western-carolina': 'southern',
                           'samford': 'southern',
                           'citadel': 'southern',
                           'virginia-military-institute': 'southern',
                           'chattanooga': 'southern',
                           'murray-state': 'ovc',
                           'belmont': 'ovc',
                           'austin-peay': 'ovc',
                           'jacksonville-state': 'ovc',
                           'tennessee-tech': 'ovc',
                           'tennessee-state': 'ovc',
                           'southeast-missouri-state': 'ovc',
                           'eastern-illinois': 'ovc',
                           'eastern-kentucky': 'ovc',
                           'tennessee-martin': 'ovc',
                           'southern-illinois-edwardsville': 'ovc',
                           'morehead-state': 'ovc',
                           'vermont': 'america-east',
                           'maryland-baltimore-county': 'america-east',
                           'hartford': 'america-east',
                           'albany-ny': 'america-east',
                           'stony-brook': 'america-east',
                           'massachusetts-lowell': 'america-east',
                           'new-hampshire': 'america-east',
                           'maine': 'america-east',
                           'binghamton': 'america-east',
                           'northern-kentucky': 'horizon',
                           'wright-state': 'horizon',
                           'illinois-chicago': 'horizon',
                           'oakland': 'horizon',
                           'milwaukee': 'horizon',
                           'iupui': 'horizon',
                           'green-bay': 'horizon',
                           'cleveland-state': 'horizon',
                           'youngstown-state': 'horizon',
                           'detroit-mercy': 'horizon',
                           'north-carolina-asheville': 'big-south',
                           'radford': 'big-south',
                           'winthrop': 'big-south',
                           'campbell': 'big-south',
                           'liberty': 'big-south',
                           'charleston-southern': 'big-south',
                           'high-point': 'big-south',
                           'gardner-webb': 'big-south',
                           'presbyterian': 'big-south',
                           'longwood': 'big-south',
                           'bucknell': 'patriot',
                           'colgate': 'patriot',
                           'navy': 'patriot',
                           'lehigh': 'patriot',
                           'boston-university': 'patriot',
                           'holy-cross': 'patriot',
                           'lafayette': 'patriot',
                           'army': 'patriot',
                           'loyola-md': 'patriot',
                           'american': 'patriot',
                           'florida-gulf-coast': 'atlantic-sun',
                           'lipscomb': 'atlantic-sun',
                           'jacksonville': 'atlantic-sun',
                           'njit': 'atlantic-sun',
                           'north-florida': 'atlantic-sun',
                           'kennesaw-state': 'atlantic-sun',
                           'stetson': 'atlantic-sun',
                           'south-carolina-upstate': 'atlantic-sun',
                           'nicholls-state': 'southland',
                           'southeastern-louisiana': 'southland',
                           'stephen-f-austin': 'southland',
                           'sam-houston-state': 'southland',
                           'lamar': 'southland',
                           'new-orleans': 'southland',
                           'central-arkansas': 'southland',
                           'abilene-christian': 'southland',
                           'mcneese-state': 'southland',
                           'texas-am-corpus-christi': 'southland',
                           'incarnate-word': 'southland',
                           'houston-baptist': 'southland',
                           'northwestern-state': 'southland',
                           'wagner': 'northeast',
                           'saint-francis-pa': 'northeast',
                           'mount-st-marys': 'northeast',
                           'long-island-university': 'northeast',
                           'st-francis-ny': 'northeast',
                           'robert-morris': 'northeast',
                           'fairleigh-dickinson': 'northeast',
                           'central-connecticut-state': 'northeast',
                           'sacred-heart': 'northeast',
                           'bryant': 'northeast',
                           'grambling': 'swac',
                           'prairie-view': 'swac',
                           'texas-southern': 'swac',
                           'arkansas-pine-bluff': 'swac',
                           'southern': 'swac',
                           'jackson-state': 'swac',
                           'alabama-state': 'swac',
                           'alcorn-state': 'swac',
                           'mississippi-valley-state': 'swac',
                           'alabama-am': 'swac',
                           'bethune-cookman': 'meac',
                           'savannah-state': 'meac',
                           'hampton': 'meac',
                           'north-carolina-at': 'meac',
                           'norfolk-state': 'meac',
                           'north-carolina-central': 'meac',
                           'morgan-state': 'meac',
                           'howard': 'meac',
                           'florida-am': 'meac',
                           'south-carolina-state': 'meac',
                           'coppin-state': 'meac',
                           'maryland-eastern-shore': 'meac',
                           'delaware-state': 'meac'}
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2019)
        flexmock(Conferences) \
            .should_receive('_find_conferences') \
            .and_return(None)
        flexmock(Conferences) \
            .should_receive('team_conference') \
            .and_return(team_conference)

        teams = Teams()

        for team in teams:
            assert team._year == '2018'
