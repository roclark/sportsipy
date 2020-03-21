from mock import patch
from os import path
from sportsreference.fb.team import Team


def read_file(filename):
    filepath = path.join(path.dirname(__file__), 'fb_stats', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    contents = read_file('tottenham-hotspur-2019-2020.html')
    return MockPQ(contents)


class TestFBTeam:
    def setup_method(self):
        self.results = {
            'name': 'Tottenham Hotspur',
            'season': '2019-2020',
            'record': '11-8-10',
            'points': 41,
            'position': 8,
            'league': 'Premier League',
            'home_record': '8-2-4',
            'home_wins': 8,
            'home_draws': 2,
            'home_losses': 4,
            'home_games': 14,
            'home_points': 26,
            'away_record': '3-6-6',
            'away_wins': 3,
            'away_draws': 6,
            'away_losses': 6,
            'away_games': 15,
            'away_points': 15,
            'goals_scored': 47,
            'goals_against': 40,
            'goal_difference': 7,
            'expected_goals': 38.5,
            'expected_goals_against': 42.7,
            'expected_goal_difference': -4.2,
            'manager': 'José Mourinho',
            'country': 'England',
            'gender': 'Male'
        }

    @patch('requests.get', side_effect=mock_pyquery)
    def test_fb_team_returns_correct_attributes(self, *args, **kwargs):
        tottenham = Team('Tottenham Hotspur')

        for attribute, value in self.results.items():
            assert getattr(tottenham, attribute) == value
