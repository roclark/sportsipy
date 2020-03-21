import mock
import pandas as pd
from os import path
from sportsreference.fb.roster import Roster


EXPECTED_NUM_PLAYERS = 34


def read_file(filename):
    filepath = path.join(path.dirname(__file__), 'fb', filename)
    return open('%s.html' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    return MockPQ(read_file('tottenham-hotspur-2019-2020'))


class TestFBRoster:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'name': 'Harry Kane',
            'player_id': '21a66f6a',
            'nationality': 'England',
            'position': 'FW',
            'age': 26,
            'matches_played': 25,
            'starts': 25,
            'minutes': 2230,
            'goals': 17,
            'assists': 2,
            'penalty_kicks': 4,
            'penalty_kick_attempts': 4,
            'yellow_cards': 3,
            'red_cards': 0,
            'goals_per_90': 0.69,
            'assists_per_90': 0.08,
            'goals_and_assists_per_90': 0.77,
            'goals_non_penalty_per_90': 0.52,
            'goals_and_assists_non_penalty_per_90': 0.61,
            'expected_goals': 11.5,
            'expected_goals_non_penalty': 8.4,
            'expected_assists': 2.4,
            'expected_goals_per_90': 0.46,
            'expected_assists_per_90': 0.1,
            'expected_goals_and_assists_per_90': 0.56,
            'expected_goals_non_penalty_per_90': 0.34,
            'expected_goals_and_assists_non_penalty_per_90': 0.44,
            'own_goals': 0,
            'goals_against': None,
            'own_goals_against': None,
            'goals_against_per_90': None,
            'shots_on_target_against': None,
            'saves': None,
            'save_percentage': None,
            'wins': None,
            'draws': None,
            'losses': None,
            'clean_sheets': None,
            'clean_sheet_percentage': None,
            'penalty_kicks_attempted': None,
            'penalty_kicks_allowed': None,
            'penalty_kicks_saved': None,
            'penalty_kicks_missed': None,
            'free_kick_goals_against': None,
            'corner_kick_goals_against': None,
            'post_shot_expected_goals': None,
            'post_shot_expected_goals_per_shot': None,
            'post_shot_expected_goals_minus_allowed': None,
            'launches_completed': None,
            'launches_attempted': None,
            'launch_completion_percentage': None,
            'keeper_passes_attempted': None,
            'throws_attempted': None,
            'launch_percentage': None,
            'average_keeper_pass_length': None,
            'goal_kicks_attempted': None,
            'goal_kick_launch_percentage': None,
            'average_goal_kick_length': None,
            'opponent_cross_attempts': None,
            'opponent_cross_stops': None,
            'opponent_cross_stop_percentage': None,
            'keeper_actions_outside_penalty_area': None,
            'keeper_actions_outside_penalty_area_per_90': None,
            'average_keeper_action_outside_penalty_distance': None,
            'shots': 74,
            'shots_on_target': 28,
            'free_kick_shots': 5,
            'shots_on_target_percentage': 37.8,
            'shots_per_90': 2.99,
            'shots_on_target_per_90': 1.13,
            'goals_per_shot': 0.18,
            'goals_per_shot_on_target': 0.46,
            'expected_goals_non_penalty_per_shot': 0.12,
            'goals_minus_expected': 5.5,
            'non_penalty_minus_expected_non_penalty': 4.6,
            'assists_minus_expected': -0.4,
            'key_passes': 22,
            'passes_completed': 363,
            'passes_attempted': 532,
            'pass_completion': 68.2,
            'short_passes_completed': 8,
            'short_passes_attempted': 38,
            'short_pass_completion': 21.1,
            'medium_passes_completed': 275,
            'medium_passes_attempted': 361,
            'medium_pass_completion': 76.2,
            'long_passes_completed': 80,
            'long_passes_attempted': 133,
            'long_pass_completion': 60.2,
            'left_foot_passes': 55,
            'right_foot_passes': 395,
            'free_kick_passes': 4,
            'through_balls': 7,
            'corner_kicks': 0,
            'throw_ins': 7,
            'final_third_passes': 46,
            'penalty_area_passes': 19,
            'penalty_area_crosses': 2,
            'minutes_per_match': 89,
            'minutes_played_percentage': 67.0,
            'nineties_played': 24.8,
            'minutes_per_start': 89,
            'subs': 0,
            'minutes_per_sub': None,
            'unused_sub': 0,
            'points_per_match': 1.56,
            'goals_scored_on_pitch': 52,
            'goals_against_on_pitch': 40,
            'goal_difference_on_pitch': 12,
            'goal_difference_on_pitch_per_90': 0.48,
            'net_difference_on_pitch_per_90': 0.57,
            'expected_goals_on_pitch': 37.4,
            'expected_goals_against_on_pitch': 30.4,
            'expected_goal_difference': 6.9,
            'expected_goal_difference_per_90': 0.28,
            'net_expected_goal_difference_per_90': 1.03,
            'soft_reds': 0,
            'fouls_committed': 30,
            'fouls_drawn': 39,
            'offsides': 16,
            'crosses': 24,
            'tackles_won': 9,
            'interceptions': 4,
            'penalty_kicks_won': 2,
            'penalty_kicks_conceded': 0,
            'successful_dribbles': 31,
            'attempted_dribbles': 62,
            'dribble_success_rate': 50.0,
            'players_dribbled_past': 36,
            'nutmegs': 2,
            'dribblers_tackled': 15,
            'dribblers_contested': 28,
            'tackle_percentage': 53.6,
            'times_dribbled_past': 13
        }
        self.keeper = {
            'name': 'Hugo Lloris',
            'player_id': '8f62b6ee',
            'nationality': 'France',
            'position': 'GK',
            'age': 32,
            'matches_played': 18,
            'starts': 18,
            'minutes': 1538,
            'goals': 0,
            'assists': 0,
            'penalty_kicks': 0,
            'penalty_kick_attempts': 0,
            'yellow_cards': 0,
            'red_cards': 0,
            'goals_per_90': 0.0,
            'assists_per_90': 0.0,
            'goals_and_assists_per_90': 0.0,
            'goals_non_penalty_per_90': 0.0,
            'goals_and_assists_non_penalty_per_90': 0.0,
            'expected_goals': 0.0,
            'expected_goals_non_penalty': 0.0,
            'expected_assists': 0.0,
            'expected_goals_per_90': 0.0,
            'expected_assists_per_90': 0.0,
            'expected_goals_and_assists_per_90': 0.0,
            'expected_goals_non_penalty_per_90': 0.0,
            'expected_goals_and_assists_non_penalty_per_90': 0.0,
            'own_goals': 0,
            'goals_against': 30,
            'own_goals_against': 1,
            'goals_against_per_90': 1.76,
            'shots_on_target_against': 93,
            'saves': 65,
            'save_percentage': .71,
            'wins': 7,
            'draws': 5,
            'losses': 6,
            'clean_sheets': 2,
            'clean_sheet_percentage': 11.1,
            'penalty_kicks_attempted': 4,
            'penalty_kicks_allowed': 3,
            'penalty_kicks_saved': 1,
            'penalty_kicks_missed': 0,
            'free_kick_goals_against': 0,
            'corner_kick_goals_against': 1,
            'post_shot_expected_goals': 27.5,
            'post_shot_expected_goals_per_shot': 0.34,
            'post_shot_expected_goals_minus_allowed': 1.5,
            'post_shot_expected_goals_minus_allowed_per_90': 0.1,
            'launches_completed': 86,
            'launches_attempted': 191,
            'launch_completion_percentage': 45.0,
            'keeper_passes_attempted': 321,
            'throws_attempted': 67,
            'launch_percentage': 41.4,
            'average_keeper_pass_length': 37.3,
            'goal_kicks_attempted': 107,
            'goal_kick_launch_percentage': 54.2,
            'average_goal_kick_length': 40.8,
            'opponent_cross_attempts': 88,
            'opponent_cross_stops': 9,
            'opponent_cross_stop_percentage': 10.2,
            'keeper_actions_outside_penalty_area': 4,
            'keeper_actions_outside_penalty_area_per_90': 0.27,
            'average_keeper_action_outside_penalty_distance': 12.0,
            'shots': 0,
            'shots_on_target': 0,
            'free_kick_shots': 0,
            'shots_on_target_percentage': None,
            'shots_per_90': 0.0,
            'shots_on_target_per_90': 0.0,
            'goals_per_shot': None,
            'goals_per_shot_on_target': None,
            'expected_goals_non_penalty_per_shot': None,
            'goals_minus_expected': 0.0,
            'non_penalty_minus_expected_non_penalty': 0.0,
            'assists_minus_expected': 0.0,
            'key_passes': 0,
            'passes_completed': 318,
            'passes_attempted': 428,
            'pass_completion': 74.3,
            'short_passes_completed': 2,
            'short_passes_attempted': 2,
            'short_pass_completion': 100.0,
            'medium_passes_completed': 162,
            'medium_passes_attempted': 163,
            'medium_pass_completion': 99.4,
            'long_passes_completed': 154,
            'long_passes_attempted': 263,
            'long_pass_completion': 58.6,
            'left_foot_passes': 240,
            'right_foot_passes': 96,
            'free_kick_passes': 25,
            'through_balls': 0,
            'corner_kicks': 0,
            'throw_ins': 0,
            'final_third_passes': 5,
            'penalty_area_passes': 0,
            'penalty_area_crosses': 0,
            'minutes_per_match': 85,
            'minutes_played_percentage': 39.1,
            'nineties_played': 17.1,
            'minutes_per_start': 85,
            'subs': 0,
            'minutes_per_sub': None,
            'unused_sub': 1,
            'points_per_match': 1.44,
            'goals_scored_on_pitch': 30,
            'goals_against_on_pitch': 30,
            'goal_difference_on_pitch': 0,
            'goal_difference_on_pitch_per_90': 0.0,
            'net_difference_on_pitch_per_90': -0.44,
            'expected_goals_on_pitch': 20.3,
            'expected_goals_against_on_pitch': 26.5,
            'expected_goal_difference': -6.1,
            'expected_goal_difference_per_90': -0.41,
            'net_expected_goal_difference_per_90': -0.59,
            'soft_reds': 0,
            'fouls_committed': 0,
            'fouls_drawn': 1,
            'offsides': 0,
            'crosses': 0,
            'tackles_won': 0,
            'interceptions': 0,
            'penalty_kicks_won': 0,
            'penalty_kicks_conceded': 0,
            'successful_dribbles': 0,
            'attempted_dribbles': 1,
            'dribble_success_rate': 0.0,
            'players_dribbled_past': 0,
            'nutmegs': 0,
            'dribblers_tackled': 0,
            'dribblers_contested': 0,
            'tackle_percentage': None,
            'times_dribbled_past': 0
        }

        self.roster = Roster('Tottenham Hotspur')

    def test_outfield_player_roster_returns_expected_stats(self):
        harry_kane = self.roster('Harry Kane')

        for attribute, value in self.results.items():
            assert getattr(harry_kane, attribute) == value

    def test_keeper_player_roster_returns_expected_stats(self):
        hugo_lloris = self.roster('Hugo Lloris')

        for attribute, value in self.keeper.items():
            assert getattr(hugo_lloris, attribute) == value

    def test_outfield_player_id_returns_expected_player(self):
        harry_kane = self.roster('21a66f6a')

        for attribute, value in self.results.items():
            assert getattr(harry_kane, attribute) == value

    def test_number_of_players_returns_expected(self):
        for count, player in enumerate(self.roster):
            pass

        assert count + 1 == EXPECTED_NUM_PLAYERS

    def test_roster_len_returns_expected_roster_size(self):
        assert len(self.roster) == EXPECTED_NUM_PLAYERS

    def test_fb_roster_dataframe_returns_dataframe(self):
        df = pd.DataFrame([self.results], index=['21a66f6a'])

        harry_kane = self.roster('Harry Kane')
        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected on above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, harry_kane.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty
