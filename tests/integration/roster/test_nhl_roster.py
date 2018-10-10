import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsreference import utils
from sportsreference.nhl.roster import Player, Roster
from sportsreference.nhl.teams import Team


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nhl', filename)
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

    if 'BAD' in url or 'bad' in url:
        return MockPQ(None, 404)
    if 'zettehe01' in url:
        return MockPQ(read_file('zettehe01'))
    if '2018' in url:
        return MockPQ(read_file('2018'))
    return MockPQ(read_file('howarja02'))


class TestNHLPlayer:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.skater_results_career = {
            'adjusted_assists': 692,
            'adjusted_goals': 377,
            'adjusted_goals_against_average': None,
            'adjusted_goals_created': 394,
            'adjusted_points': 1069,
            'age': None,
            'assists': 623,
            'average_time_on_ice': '19:35',
            'blocks_at_even_strength': 267,
            'corsi_against': 10322.0,
            'corsi_for': None,
            'corsi_for_percentage': 55.1,
            'defensive_point_shares': 29.4,
            'defensive_zone_start_percentage': 45.5,
            'even_strength_assists': 379,
            'even_strength_goals': 228,
            'even_strength_goals_allowed': None,
            'even_strength_save_percentage': None,
            'even_strength_shots_faced': None,
            'faceoff_losses': 5602,
            'faceoff_percentage': 51.1,
            'faceoff_wins': 5863,
            'fenwick_against': 8123,
            'fenwick_for': 9757,
            'fenwick_for_percentage': 54.6,
            'game_winning_goals': 64,
            'games_played': 1082,
            'giveaways': 482,
            'goal_against_percentage_relative': None,
            'goalie_point_shares': None,
            'goals': 337,
            'goals_against': None,
            'goals_against_average': None,
            'goals_against_on_ice': 530,
            'goals_created': 348,
            'goals_for_on_ice': 633,
            'goals_saved_above_average': None,
            'height': '6-0',
            'hits_at_even_strength': 471,
            'league': 'NHL',
            'losses': None,
            'minutes': None,
            'name': 'Henrik Zetterberg',
            'offensive_point_shares': 79.9,
            'offensive_zone_start_percentage': 54.5,
            'pdo': 100.0,
            'penalties_in_minutes': 401,
            'player_id': 'zettehe01',
            'plus_minus': 160,
            'point_shares': 109.3,
            'points': 960,
            'power_play_assists': 235,
            'power_play_goals': 100,
            'power_play_goals_against_on_ice': 140,
            'power_play_goals_allowed': None,
            'power_play_goals_for_on_ice': 490,
            'power_play_save_percentage': None,
            'power_play_shots_faced': None,
            'quality_start_percentage': None,
            'quality_starts': None,
            'really_bad_starts': None,
            'relative_corsi_for_percentage': 3.3,
            'relative_fenwick_for_percentage': 3.1,
            'save_percentage': None,
            'save_percentage_on_ice': None,
            'saves': None,
            'season': 'Career',
            'shooting_percentage': 9.8,
            'shooting_percentage_on_ice': 8.8,
            'shootout_attempts': 47,
            'shootout_goals': 10,
            'shootout_misses': 37,
            'shootout_percentage': 21.3,
            'short_handed_assists': 9,
            'short_handed_goals': 9,
            'short_handed_goals_allowed': None,
            'short_handed_save_percentage': None,
            'short_handed_shots_faced': None,
            'shots_against': None,
            'shots_on_goal': 3455,
            'shutouts': None,
            'takeaways': 454,
            'team_abbreviation': None,
            'ties_plus_overtime_loss': None,
            'time_on_ice': 21186,
            'time_on_ice_even_strength': 12658.7,
            'total_goals_against_on_ice': 851,
            'total_goals_for_on_ice': 1362,
            'total_shots': 5408,
            'weight': 197,
            'wins': None
        }

        self.skater_results_2017 = {
            'adjusted_assists': 46,
            'adjusted_goals': 11,
            'adjusted_goals_against_average': None,
            'adjusted_goals_created': 19,
            'adjusted_points': 57,
            'age': 37,
            'assists': 45,
            'average_time_on_ice': '19:30',
            'blocks_at_even_strength': 34,
            'corsi_against': 1243.0,
            'corsi_for': None,
            'corsi_for_percentage': 50.6,
            'defensive_point_shares': 2.0,
            'defensive_zone_start_percentage': 45.2,
            'even_strength_assists': 28,
            'even_strength_goals': 10,
            'even_strength_goals_allowed': None,
            'even_strength_save_percentage': None,
            'even_strength_shots_faced': None,
            'faceoff_losses': 709,
            'faceoff_percentage': 48.4,
            'faceoff_wins': 666,
            'fenwick_against': 948,
            'fenwick_for': 975,
            'fenwick_for_percentage': 50.7,
            'game_winning_goals': 2,
            'games_played': 82,
            'giveaways': 57,
            'goal_against_percentage_relative': None,
            'goalie_point_shares': None,
            'goals': 11,
            'goals_against': None,
            'goals_against_average': None,
            'goals_against_on_ice': 52,
            'goals_created': 18,
            'goals_for_on_ice': 54,
            'goals_saved_above_average': None,
            'height': '6-0',
            'hits_at_even_strength': 49,
            'league': 'NHL',
            'losses': None,
            'minutes': None,
            'name': 'Henrik Zetterberg',
            'offensive_point_shares': 2.4,
            'offensive_zone_start_percentage': 54.8,
            'pdo': 99.9,
            'penalties_in_minutes': 14,
            'player_id': 'zettehe01',
            'plus_minus': 1,
            'point_shares': 4.4,
            'points': 56,
            'power_play_assists': 17,
            'power_play_goals': 1,
            'power_play_goals_against_on_ice': 0,
            'power_play_goals_allowed': None,
            'power_play_goals_for_on_ice': 25,
            'power_play_save_percentage': None,
            'power_play_shots_faced': None,
            'quality_start_percentage': None,
            'quality_starts': None,
            'really_bad_starts': None,
            'relative_corsi_for_percentage': 2.7,
            'relative_fenwick_for_percentage': 2.0,
            'save_percentage': None,
            'save_percentage_on_ice': None,
            'saves': None,
            'season': '2017-18',
            'shooting_percentage': 6.1,
            'shooting_percentage_on_ice': 7.6,
            'shootout_attempts': 3,
            'shootout_goals': 0,
            'shootout_misses': 3,
            'shootout_percentage': 0.0,
            'short_handed_assists': 0,
            'short_handed_goals': 0,
            'short_handed_goals_allowed': None,
            'short_handed_save_percentage': None,
            'short_handed_shots_faced': None,
            'shots_against': None,
            'shots_on_goal': 180,
            'shutouts': None,
            'takeaways': 51,
            'team_abbreviation': 'DET',
            'ties_plus_overtime_loss': None,
            'time_on_ice': 1599,
            'time_on_ice_even_strength': 1382.2,
            'total_goals_against_on_ice': 53,
            'total_goals_for_on_ice': 79,
            'total_shots': 332,
            'weight': 197,
            'wins': None
        }

        self.goalie_results_career = {
            'adjusted_assists': None,
            'adjusted_goals': None,
            'adjusted_goals_against_average': None,
            'adjusted_goals_created': None,
            'adjusted_points': None,
            'age': None,
            'assists': 8,
            'average_time_on_ice': None,
            'blocks_at_even_strength': None,
            'corsi_against': None,
            'corsi_for': None,
            'corsi_for_percentage': None,
            'defensive_point_shares': None,
            'defensive_zone_start_percentage': None,
            'even_strength_assists': None,
            'even_strength_goals': None,
            'even_strength_goals_allowed': 800,
            'even_strength_save_percentage': 0.922,
            'even_strength_shots_faced': 10295,
            'faceoff_losses': None,
            'faceoff_percentage': None,
            'faceoff_wins': None,
            'fenwick_against': None,
            'fenwick_for': None,
            'fenwick_for_percentage': None,
            'game_winning_goals': None,
            'games_played': None,
            'giveaways': None,
            'goal_against_percentage_relative': 97,
            'goalie_point_shares': 78.8,
            'goals': 0,
            'goals_against': 1091,
            'goals_against_average': 2.49,
            'goals_against_on_ice': None,
            'goals_created': None,
            'goals_for_on_ice': None,
            'goals_saved_above_average': None,
            'height': '6-1',
            'hits_at_even_strength': None,
            'league': 'NHL',
            'losses': 151,
            'minutes': 26332,
            'name': 'Jimmy Howard',
            'offensive_point_shares': None,
            'offensive_zone_start_percentage': None,
            'pdo': None,
            'penalties_in_minutes': 34,
            'player_id': 'howarja02',
            'plus_minus': None,
            'point_shares': None,
            'points': 8,
            'power_play_assists': None,
            'power_play_goals': None,
            'power_play_goals_against_on_ice': None,
            'power_play_goals_allowed': 26,
            'power_play_goals_for_on_ice': None,
            'power_play_save_percentage': 0.92,
            'power_play_shots_faced': 327,
            'quality_start_percentage': 0.544,
            'quality_starts': 239,
            'really_bad_starts': 61,
            'relative_corsi_for_percentage': None,
            'relative_fenwick_for_percentage': None,
            'save_percentage': 0.915,
            'save_percentage_on_ice': None,
            'saves': 11696,
            'season': 'Career',
            'shooting_percentage': None,
            'shooting_percentage_on_ice': None,
            'shootout_attempts': None,
            'shootout_goals': None,
            'shootout_misses': None,
            'shootout_percentage': None,
            'short_handed_assists': None,
            'short_handed_goals': None,
            'short_handed_goals_allowed': 249,
            'short_handed_save_percentage': 0.877,
            'short_handed_shots_faced': 2027,
            'shots_against': 12787,
            'shots_on_goal': None,
            'shutouts': 24,
            'takeaways': None,
            'team_abbreviation': None,
            'ties_plus_overtime_loss': 63,
            'time_on_ice': None,
            'time_on_ice_even_strength': None,
            'total_goals_against_on_ice': None,
            'total_goals_for_on_ice': None,
            'total_shots': None,
            'weight': 218,
            'wins': 221
        }

        self.goalie_results_2017 = {
            'adjusted_assists': None,
            'adjusted_goals': None,
            'adjusted_goals_against_average': None,
            'adjusted_goals_created': None,
            'adjusted_points': None,
            'age': 33,
            'assists': 1,
            'average_time_on_ice': None,
            'blocks_at_even_strength': None,
            'corsi_against': None,
            'corsi_for': None,
            'corsi_for_percentage': None,
            'defensive_point_shares': None,
            'defensive_zone_start_percentage': None,
            'even_strength_assists': None,
            'even_strength_goals': None,
            'even_strength_goals_allowed': 122,
            'even_strength_save_percentage': 0.916,
            'even_strength_shots_faced': 1455,
            'faceoff_losses': None,
            'faceoff_percentage': None,
            'faceoff_wins': None,
            'fenwick_against': None,
            'fenwick_for': None,
            'fenwick_for_percentage': None,
            'game_winning_goals': None,
            'games_played': None,
            'giveaways': None,
            'goal_against_percentage_relative': 103,
            'goalie_point_shares': 9.4,
            'goals': 0,
            'goals_against': 160,
            'goals_against_average': 2.85,
            'goals_against_on_ice': None,
            'goals_created': None,
            'goals_for_on_ice': None,
            'goals_saved_above_average': -4.65,
            'height': '6-1',
            'hits_at_even_strength': None,
            'league': 'NHL',
            'losses': 27,
            'minutes': 3368,
            'name': 'Jimmy Howard',
            'offensive_point_shares': None,
            'offensive_zone_start_percentage': None,
            'pdo': None,
            'penalties_in_minutes': 10,
            'player_id': 'howarja02',
            'plus_minus': None,
            'point_shares': None,
            'points': 1,
            'power_play_assists': None,
            'power_play_goals': None,
            'power_play_goals_against_on_ice': None,
            'power_play_goals_allowed': 2,
            'power_play_goals_for_on_ice': None,
            'power_play_save_percentage': 0.949,
            'power_play_shots_faced': 39,
            'quality_start_percentage': 0.491,
            'quality_starts': 28,
            'really_bad_starts': 6,
            'relative_corsi_for_percentage': None,
            'relative_fenwick_for_percentage': None,
            'save_percentage': 0.91,
            'save_percentage_on_ice': None,
            'saves': 1610,
            'season': '2017-18',
            'shooting_percentage': None,
            'shooting_percentage_on_ice': None,
            'shootout_attempts': None,
            'shootout_goals': None,
            'shootout_misses': None,
            'shootout_percentage': None,
            'short_handed_assists': None,
            'short_handed_goals': None,
            'short_handed_goals_allowed': 36,
            'short_handed_save_percentage': 0.869,
            'short_handed_shots_faced': 275,
            'shots_against': 1770,
            'shots_on_goal': None,
            'shutouts': 1,
            'takeaways': None,
            'team_abbreviation': 'DET',
            'ties_plus_overtime_loss': 9,
            'time_on_ice': None,
            'time_on_ice_even_strength': None,
            'total_goals_against_on_ice': None,
            'total_goals_for_on_ice': None,
            'total_shots': None,
            'weight': 218,
            'wins': 22
        }

        self.skater = Player('zettehe01')
        self.goalie = Player('howarja02')

    def test_nhl_skater_returns_requested_career_stats(self):
        # Request the career stats
        player = self.skater('')

        for attribute, value in self.skater_results_career.items():
            assert getattr(player, attribute) == value

    def test_nhl_skater_returns_player_season_stats(self):
        # Request the 2017 stats
        player = self.skater('2017-18')

        for attribute, value in self.skater_results_2017.items():
            assert getattr(player, attribute) == value

    def test_nhl_goalie_returns_requested_career_stats(self):
        # Request the career stats
        player = self.goalie('')

        for attribute, value in self.goalie_results_career.items():
            assert getattr(player, attribute) == value

    def test_nhl_goalie_returns_player_season_stats(self):
        # Request the 2017 stats
        player = self.goalie('2017-18')

        for attribute, value in self.goalie_results_2017.items():
            assert getattr(player, attribute) == value

    def test_dataframe_returns_dataframe(self):
        dataframe = [
            {'adjusted_assists': 46,
             'adjusted_goals': 11,
             'adjusted_goals_against_average': None,
             'adjusted_goals_created': 19,
             'adjusted_points': 57,
             'age': 37,
             'assists': 45,
             'average_time_on_ice': '19:30',
             'blocks_at_even_strength': 34,
             'corsi_against': 1243.0,
             'corsi_for': None,
             'corsi_for_percentage': 50.6,
             'defensive_point_shares': 2.0,
             'defensive_zone_start_percentage': 45.2,
             'even_strength_assists': 28,
             'even_strength_goals': 10,
             'even_strength_goals_allowed': None,
             'even_strength_save_percentage': None,
             'even_strength_shots_faced': None,
             'faceoff_losses': 709,
             'faceoff_percentage': 48.4,
             'faceoff_wins': 666,
             'fenwick_against': 948,
             'fenwick_for': 975,
             'fenwick_for_percentage': 50.7,
             'game_winning_goals': 2,
             'games_played': 82,
             'giveaways': 57,
             'goal_against_percentage_relative': None,
             'goalie_point_shares': None,
             'goals': 11,
             'goals_against': None,
             'goals_against_average': None,
             'goals_against_on_ice': 52,
             'goals_created': 18,
             'goals_for_on_ice': 54,
             'goals_saved_above_average': None,
             'height': '6-0',
             'hits_at_even_strength': 49,
             'league': 'NHL',
             'losses': None,
             'minutes': None,
             'name': 'Henrik Zetterberg',
             'offensive_point_shares': 2.4,
             'offensive_zone_start_percentage': 54.8,
             'pdo': 99.9,
             'penalties_in_minutes': 14,
             'player_id': 'zettehe01',
             'plus_minus': 1,
             'point_shares': 4.4,
             'points': 56,
             'power_play_assists': 17,
             'power_play_goals': 1,
             'power_play_goals_against_on_ice': 0,
             'power_play_goals_allowed': None,
             'power_play_goals_for_on_ice': 25,
             'power_play_save_percentage': None,
             'power_play_shots_faced': None,
             'quality_start_percentage': None,
             'quality_starts': None,
             'really_bad_starts': None,
             'relative_corsi_for_percentage': 2.7,
             'relative_fenwick_for_percentage': 2.0,
             'save_percentage': None,
             'save_percentage_on_ice': None,
             'saves': None,
             'season': '2017-18',
             'shooting_percentage': 6.1,
             'shooting_percentage_on_ice': 7.6,
             'shootout_attempts': 3,
             'shootout_goals': 0,
             'shootout_misses': 3,
             'shootout_percentage': 0.0,
             'short_handed_assists': 0,
             'short_handed_goals': 0,
             'short_handed_goals_allowed': None,
             'short_handed_save_percentage': None,
             'short_handed_shots_faced': None,
             'shots_against': None,
             'shots_on_goal': 180,
             'shutouts': None,
             'takeaways': 51,
             'team_abbreviation': 'DET',
             'ties_plus_overtime_loss': None,
             'time_on_ice': 1599,
             'time_on_ice_even_strength': 1382.2,
             'total_goals_against_on_ice': 53,
             'total_goals_for_on_ice': 79,
             'total_shots': 332,
             'weight': 197,
             'wins': None},
            {'adjusted_assists': 692,
             'adjusted_goals': 377,
             'adjusted_goals_against_average': None,
             'adjusted_goals_created': 394,
             'adjusted_points': 1069,
             'age': None,
             'assists': 623,
             'average_time_on_ice': '19:35',
             'blocks_at_even_strength': 267,
             'corsi_against': 10322.0,
             'corsi_for': None,
             'corsi_for_percentage': 55.1,
             'defensive_point_shares': 29.4,
             'defensive_zone_start_percentage': 45.5,
             'even_strength_assists': 379,
             'even_strength_goals': 228,
             'even_strength_goals_allowed': None,
             'even_strength_save_percentage': None,
             'even_strength_shots_faced': None,
             'faceoff_losses': 5602,
             'faceoff_percentage': 51.1,
             'faceoff_wins': 5863,
             'fenwick_against': 8123,
             'fenwick_for': 9757,
             'fenwick_for_percentage': 54.6,
             'game_winning_goals': 64,
             'games_played': 1082,
             'giveaways': 482,
             'goal_against_percentage_relative': None,
             'goalie_point_shares': None,
             'goals': 337,
             'goals_against': None,
             'goals_against_average': None,
             'goals_against_on_ice': 530,
             'goals_created': 348,
             'goals_for_on_ice': 633,
             'goals_saved_above_average': None,
             'height': '6-0',
             'hits_at_even_strength': 471,
             'league': 'NHL',
             'losses': None,
             'minutes': None,
             'name': 'Henrik Zetterberg',
             'offensive_point_shares': 79.9,
             'offensive_zone_start_percentage': 54.5,
             'pdo': 100.0,
             'penalties_in_minutes': 401,
             'player_id': 'zettehe01',
             'plus_minus': 160,
             'point_shares': 109.3,
             'points': 960,
             'power_play_assists': 235,
             'power_play_goals': 100,
             'power_play_goals_against_on_ice': 140,
             'power_play_goals_allowed': None,
             'power_play_goals_for_on_ice': 490,
             'power_play_save_percentage': None,
             'power_play_shots_faced': None,
             'quality_start_percentage': None,
             'quality_starts': None,
             'really_bad_starts': None,
             'relative_corsi_for_percentage': 3.3,
             'relative_fenwick_for_percentage': 3.1,
             'save_percentage': None,
             'save_percentage_on_ice': None,
             'saves': None,
             'season': 'Career',
             'shooting_percentage': 9.8,
             'shooting_percentage_on_ice': 8.8,
             'shootout_attempts': 47,
             'shootout_goals': 10,
             'shootout_misses': 37,
             'shootout_percentage': 21.3,
             'short_handed_assists': 9,
             'short_handed_goals': 9,
             'short_handed_goals_allowed': None,
             'short_handed_save_percentage': None,
             'short_handed_shots_faced': None,
             'shots_against': None,
             'shots_on_goal': 3455,
             'shutouts': None,
             'takeaways': 454,
             'team_abbreviation': None,
             'ties_plus_overtime_loss': None,
             'time_on_ice': 21186,
             'time_on_ice_even_strength': 12658.7,
             'total_goals_against_on_ice': 851,
             'total_goals_for_on_ice': 1362,
             'total_shots': 5408,
             'weight': 197,
             'wins': None}
        ]
        indices = ['2017', 'Career']

        df = pd.DataFrame(dataframe, index=indices)
        player = self.skater('')

        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected on above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, player.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

    def test_nhl_404_returns_none_with_no_errors(self):
        player = Player('bad')

        assert player.name is None
        assert player.dataframe is None

    def test_nhl_404_returns_none_for_different_season(self):
        player = Player('bad')

        assert player.name is None
        assert player.dataframe is None


class TestNHLRoster:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_roster_class_pulls_all_player_stats(self, *args, **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return('2018')
        roster = Roster('DET')

        assert len(roster.players) == 2

        for player in roster.players:
            assert player.name in ['Jimmy Howard', 'Henrik Zetterberg']

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_bad_url_raises_value_error(self, *args, **kwargs):
        with pytest.raises(ValueError):
            roster = Roster('bad')

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_roster_from_team_class(self, *args, **kwargs):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        team = Team(None, 1, '2018')
        mock_abbreviation = mock.PropertyMock(return_value='DET')
        type(team)._abbreviation = mock_abbreviation

        assert len(team.roster.players) == 2

        for player in team.roster.players:
            assert player.name in ['Jimmy Howard', 'Henrik Zetterberg']
        type(team)._abbreviation = None
