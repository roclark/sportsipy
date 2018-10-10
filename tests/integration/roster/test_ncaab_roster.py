import mock
import os
import pandas as pd
import pytest
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.ncaab.roster import Player, Roster
from sportsreference.ncaab.teams import Team


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaab', filename)
    return open('%s.html' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents, status=200):
            self.url = url
            self.reason = 'Bad URL'  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = status
            self.html_contents = html_contents
            self.text = html_contents

    if 'purdue' in url:
        return MockPQ(read_file('2018'))
    if 'isaac-haas-1' in url:
        return MockPQ(read_file('isaac-haas-1'))
    if 'vince-edwards-2' in url:
        return MockPQ(read_file('vince-edwards-2'))
    if 'bad' in url:
        return MockPQ(None, 404)
    return MockPQ(read_file('carsen-edwards-1'))


class TestNCAABPlayer:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results_career = {
            'assist_percentage': 17.3,
            'assists': 166,
            'block_percentage': 0.6,
            'blocks': 11,
            'box_plus_minus': 6.1,
            'conference': '',
            'defensive_box_plus_minus': 1.9,
            'defensive_rebound_percentage': 11.8,
            'defensive_rebounds': 206,
            'defensive_win_shares': 3.5,
            'effective_field_goal_percentage': 0.515,
            'field_goal_attempts': 835,
            'field_goal_percentage': 0.428,
            'field_goals': 357,
            'free_throw_attempt_rate': 0.279,
            'free_throw_attempts': 233,
            'free_throw_percentage': 0.798,
            'free_throws': 186,
            'games_played': 72,
            'games_started': 58,
            'height': '6-1',
            'minutes_played': 1905,
            'name': 'Carsen Edwards',
            'offensive_box_plus_minus': 4.2,
            'offensive_rebound_percentage': 1.8,
            'offensive_rebounds': 27,
            'offensive_win_shares': 4.4,
            'personal_fouls': 133,
            'player_efficiency_rating': 19.9,
            'points': 1046,
            'points_produced': 961,
            'position': 'Guard',
            'season': 'Career',
            'steal_percentage': 2.4,
            'steals': 78,
            'team_abbreviation': 'purdue',
            'three_point_attempt_rate': 0.459,
            'three_point_attempts': 383,
            'three_point_percentage': 0.381,
            'three_pointers': 146,
            'total_rebound_percentage': 7.2,
            'total_rebounds': 233,
            'true_shooting_percentage': 0.553,
            'turnover_percentage': 11.9,
            'turnovers': 128,
            'two_point_attempts': 452,
            'two_point_percentage': 0.467,
            'two_pointers': 211,
            'usage_percentage': 28.9,
            'weight': 190,
            'win_shares': 8.0,
            'win_shares_per_40_minutes': 0.167
        }

        self.results_2018 = {
            'assist_percentage': 19.5,
            'assists': 104,
            'block_percentage': 0.8,
            'blocks': 8,
            'box_plus_minus': 9.0,
            'conference': 'big-ten',
            'defensive_box_plus_minus': 1.5,
            'defensive_rebound_percentage': 12.9,
            'defensive_rebounds': 129,
            'defensive_win_shares': 2.0,
            'effective_field_goal_percentage': 0.555,
            'field_goal_attempts': 500,
            'field_goal_percentage': 0.458,
            'field_goals': 229,
            'free_throw_attempt_rate': 0.318,
            'free_throw_attempts': 159,
            'free_throw_percentage': 0.824,
            'free_throws': 131,
            'games_played': 37,
            'games_started': 37,
            'height': '6-1',
            'minutes_played': 1092,
            'name': 'Carsen Edwards',
            'offensive_box_plus_minus': 7.6,
            'offensive_rebound_percentage': 1.5,
            'offensive_rebounds': 13,
            'offensive_win_shares': 4.0,
            'personal_fouls': 65,
            'player_efficiency_rating': 25.4,
            'points': 686,
            'points_produced': 626,
            'position': 'Guard',
            'season': '2017-18',
            'steal_percentage': 2.3,
            'steals': 42,
            'team_abbreviation': 'purdue',
            'three_point_attempt_rate': 0.478,
            'three_point_attempts': 239,
            'three_point_percentage': 0.406,
            'three_pointers': 97,
            'total_rebound_percentage': 7.7,
            'total_rebounds': 142,
            'true_shooting_percentage': 0.596,
            'turnover_percentage': 10.0,
            'turnovers': 64,
            'two_point_attempts': 261,
            'two_point_percentage': 0.506,
            'two_pointers': 132,
            'usage_percentage': 30.5,
            'weight': 190,
            'win_shares': 6.1,
            'win_shares_per_40_minutes': 0.223
        }

        self.player = Player('carsen-edwards-1')

    def test_ncaab_player_returns_requested_player_career_stats(self):
        # Request the career stats
        player = self.player('')

        for attribute, value in self.results_career.items():
            assert getattr(player, attribute) == value

    def test_ncaab_player_returns_requested_player_season_stats(self):
        # Request the 2017-18 stats
        player = self.player('2017-18')

        for attribute, value in self.results_2018.items():
            assert getattr(player, attribute) == value

    def test_correct_initial_index_found(self):
        seasons = ['2017-18', 'Career', '2016-17']
        mock_season = mock.PropertyMock(return_value=seasons)
        player = Player('carsen-edwards-1')
        type(player)._season = mock_season

        result = player._find_initial_index()

        assert player._index == 1

    def test_dataframe_returns_dataframe(self):
        dataframe = [
            {'assist_percentage': 17.3,
             'assists': 166,
             'block_percentage': 0.6,
             'blocks': 11,
             'box_plus_minus': 6.1,
             'conference': '',
             'defensive_box_plus_minus': 1.9,
             'defensive_rebound_percentage': 11.8,
             'defensive_rebounds': 206,
             'defensive_win_shares': 3.5,
             'effective_field_goal_percentage': 0.515,
             'field_goal_attempts': 835,
             'field_goal_percentage': 0.428,
             'field_goals': 357,
             'free_throw_attempt_rate': 0.279,
             'free_throw_attempts': 233,
             'free_throw_percentage': 0.798,
             'free_throws': 186,
             'games_played': 72,
             'games_started': 58,
             'height': '6-1',
             'minutes_played': 1905,
             'offensive_box_plus_minus': 4.2,
             'offensive_rebound_percentage': 1.8,
             'offensive_rebounds': 27,
             'offensive_win_shares': 4.4,
             'personal_fouls': 133,
             'player_efficiency_rating': 19.9,
             'player_id': 'carsen-edwards-1',
             'points': 1046,
             'points_produced': 961,
             'position': 'Guard',
             'steal_percentage': 2.4,
             'steals': 78,
             'team_abbreviation': 'purdue',
             'three_point_attempt_rate': 0.459,
             'three_point_attempts': 383,
             'three_point_percentage': 0.381,
             'three_pointers': 146,
             'total_rebound_percentage': 7.2,
             'total_rebounds': 233,
             'true_shooting_percentage': 0.553,
             'turnover_percentage': 11.9,
             'turnovers': 128,
             'two_point_attempts': 452,
             'two_point_percentage': 0.467,
             'two_pointers': 211,
             'usage_percentage': 28.9,
             'weight': 190,
             'win_shares': 8.0,
             'win_shares_per_40_minutes': 0.167},
            {'assist_percentage': 14.3,
             'assists': 62,
             'block_percentage': 0.4,
             'blocks': 3,
             'box_plus_minus': 2.1,
             'conference': 'big-ten',
             'defensive_box_plus_minus': 2.4,
             'defensive_rebound_percentage': 10.4,
             'defensive_rebounds': 77,
             'defensive_win_shares': 1.5,
             'effective_field_goal_percentage': 0.455,
             'field_goal_attempts': 335,
             'field_goal_percentage': 0.382,
             'field_goals': 128,
             'free_throw_attempt_rate': 0.221,
             'free_throw_attempts': 74,
             'free_throw_percentage': 0.743,
             'free_throws': 55,
             'games_played': 35,
             'games_started': 21,
             'height': '6-1',
             'minutes_played': 813,
             'offensive_box_plus_minus': -0.3,
             'offensive_rebound_percentage': 2.2,
             'offensive_rebounds': 14,
             'offensive_win_shares': 0.4,
             'personal_fouls': 68,
             'player_efficiency_rating': 12.5,
             'player_id': 'carsen-edwards-1',
             'points': 360,
             'points_produced': 335,
             'position': 'Guard',
             'steal_percentage': 2.5,
             'steals': 36,
             'team_abbreviation': 'purdue',
             'three_point_attempt_rate': 0.43,
             'three_point_attempts': 144,
             'three_point_percentage': 0.34,
             'three_pointers': 49,
             'total_rebound_percentage': 6.6,
             'total_rebounds': 91,
             'true_shooting_percentage': 0.486,
             'turnover_percentage': 14.7,
             'turnovers': 64,
             'two_point_attempts': 191,
             'two_point_percentage': 0.414,
             'two_pointers': 79,
             'usage_percentage': 26.8,
             'weight': 190,
             'win_shares': 1.9,
             'win_shares_per_40_minutes': 0.092},
            {'assist_percentage': 19.5,
             'assists': 104,
             'block_percentage': 0.8,
             'blocks': 8,
             'box_plus_minus': 9.0,
             'conference': 'big-ten',
             'defensive_box_plus_minus': 1.5,
             'defensive_rebound_percentage': 12.9,
             'defensive_rebounds': 129,
             'defensive_win_shares': 2.0,
             'effective_field_goal_percentage': 0.555,
             'field_goal_attempts': 500,
             'field_goal_percentage': 0.458,
             'field_goals': 229,
             'free_throw_attempt_rate': 0.318,
             'free_throw_attempts': 159,
             'free_throw_percentage': 0.824,
             'free_throws': 131,
             'games_played': 37,
             'games_started': 37,
             'height': '6-1',
             'minutes_played': 1092,
             'offensive_box_plus_minus': 7.6,
             'offensive_rebound_percentage': 1.5,
             'offensive_rebounds': 13,
             'offensive_win_shares': 4.0,
             'personal_fouls': 65,
             'player_efficiency_rating': 25.4,
             'player_id': 'carsen-edwards-1',
             'points': 686,
             'points_produced': 626,
             'position': 'Guard',
             'steal_percentage': 2.3,
             'steals': 42,
             'team_abbreviation': 'purdue',
             'three_point_attempt_rate': 0.478,
             'three_point_attempts': 239,
             'three_point_percentage': 0.406,
             'three_pointers': 97,
             'total_rebound_percentage': 7.7,
             'total_rebounds': 142,
             'true_shooting_percentage': 0.596,
             'turnover_percentage': 10.0,
             'turnovers': 64,
             'two_point_attempts': 261,
             'two_point_percentage': 0.506,
             'two_pointers': 132,
             'usage_percentage': 30.5,
             'weight': 190,
             'win_shares': 6.1,
             'win_shares_per_40_minutes': 0.223}
        ]
        indices = ['Career', '2016-17', '2017-18']

        df = pd.DataFrame(dataframe, index=indices)
        player = self.player('')

        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, player.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)


class TestNCAABRoster:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_roster_class_pulls_all_player_stats(self, *args, **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return('2018')
        roster = Roster('PURDUE')

        assert len(roster.players) == 3

        for player in roster.players:
            assert player.name in ['Carsen Edwards', 'Isaac Haas',
                                   'Vince Edwards']

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_bad_url_raises_value_error(self, *args, **kwargs):
        with pytest.raises(ValueError):
            roster = Roster('BAD')

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_roster_from_team_class(self, *args, **kwargs):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        team = Team(None, 1, '2018')
        mock_abbreviation = mock.PropertyMock(return_value='PURDUE')
        type(team)._abbreviation = mock_abbreviation

        assert len(team.roster.players) == 3

        for player in team.roster.players:
            assert player.name in ['Carsen Edwards', 'Isaac Haas',
                                   'Vince Edwards']
        type(team)._abbreviation = None
