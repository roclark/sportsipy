import os
from flexmock import flexmock
from mocker import Mocker, MockerTestCase
from pyquery import PyQuery
from sportsreference import utils
from sportsreference.nba.constants import SEASON_PAGE_URL
from sportsreference.nba.teams import Teams


MONTH = 1
YEAR = 2017


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nba_stats', filename)
    return open('%s' % filepath, 'r').read()


class MockPQ:
    def __init__(self, html_contents):
        self.html_contents = html_contents

    def __call__(self, div):
        if div == 'div#all_team-stats-base':
            return read_file('%s_team.html' % YEAR)
        else:
            return read_file('%s_opponent.html' % YEAR)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNBAIntegration(MockerTestCase):
    def setUp(self):
        self.results = {
            'rank': 26,
            'abbreviation': 'DET',
            'name': 'Detroit Pistons',
            'games_played': 82,
            'minutes_played': 19805,
            'field_goals': 3269,
            'field_goal_attempts': 7282,
            'field_goal_percentage': .449,
            'three_point_field_goals': 631,
            'three_point_field_goal_attempts': 1915,
            'three_point_field_goal_percentage': .330,
            'two_point_field_goals': 2638,
            'two_point_field_goal_attempts': 5367,
            'two_point_field_goal_percentage': .492,
            'free_throws': 1140,
            'free_throw_attempts': 1586,
            'free_throw_percentage': .719,
            'offensive_rebounds': 908,
            'defensive_rebounds': 2838,
            'total_rebounds': 3746,
            'assists': 1732,
            'steals': 574,
            'blocks': 310,
            'turnovers': 973,
            'personal_fouls': 1467,
            'points': 8309,
            'opp_field_goals': 3144,
            'opp_field_goal_attempts': 6830,
            'opp_field_goal_percentage': .460,
            'opp_three_point_field_goals': 767,
            'opp_three_point_field_goal_attempts': 2098,
            'opp_three_point_field_goal_percentage': .366,
            'opp_two_point_field_goals': 2377,
            'opp_two_point_field_goal_attempts': 4732,
            'opp_two_point_field_goal_percentage': .502,
            'opp_free_throws': 1346,
            'opp_free_throw_attempts': 1726,
            'opp_free_throw_percentage': .780,
            'opp_offensive_rebounds': 656,
            'opp_defensive_rebounds': 2861,
            'opp_total_rebounds': 3517,
            'opp_assists': 1929,
            'opp_steals': 551,
            'opp_blocks': 339,
            'opp_turnovers': 1046,
            'opp_personal_fouls': 1434,
            'opp_points': 8401
        }
        self.abbreviations = [
            'BOS', 'CLE', 'TOR', 'WAS', 'ATL', 'MIL', 'IND', 'CHI', 'MIA',
            'DET', 'CHO', 'NYK', 'ORL', 'PHI', 'BRK', 'GSW', 'SAS', 'HOU',
            'LAC', 'UTA', 'OKC', 'MEM', 'POR', 'DEN', 'NOP', 'DAL', 'SAC',
            'MIN', 'LAL', 'PHO'
        ]
        html_contents = read_file('NBA_%s.html' % YEAR)

        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        mock_pyquery = self.mocker.replace(PyQuery)
        mock_pyquery(SEASON_PAGE_URL % YEAR)
        self.mocker.result(MockPQ(html_contents))
        self.mocker.replay()

        self.teams = Teams()

    def test_nba_integration_returns_correct_number_of_teams(self):
        assert len(self.teams) == len(self.abbreviations)

    def test_nba_integration_returns_correct_attributes_for_team(self):
        detroit = self.teams('DET')

        for attribute, value in self.results.items():
            assert getattr(detroit, attribute) == value

    def test_nba_integration_returns_correct_team_abbreviations(self):
        for team in self.teams:
            assert team.abbreviation in self.abbreviations
