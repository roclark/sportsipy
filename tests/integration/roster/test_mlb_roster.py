# coding=utf-8
import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsreference import utils
from sportsreference.mlb.roster import Player, Roster
from sportsreference.mlb.teams import Team


YEAR = 2017


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'mlb', filename)
    return open('%s.shtml' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents, status=200):
            self.url = url
            self.reason = 'Bad URL'  # Used when throwing HTTPErrors
            self.headers = {}  # Used when throwing HTTPErrors
            self.status_code = status
            self.html_contents = html_contents
            self.text = html_contents

    if 'BAD' in url:
        return MockPQ(None, 404)
    if 'HOU' in url:
        return MockPQ(read_file('2017'))
    if 'verlaju01' in url:
        return MockPQ(read_file('verlaju01'))
    return MockPQ(read_file('altuvjo01'))


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


class TestMLBPlayer:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results_career = {
            'assists': 2763,
            'at_bats': 4436,
            'bases_on_balls': 311,
            'batting_average': 0.317,
            'birth_date': '1990-05-06',
            'complete_games': 990,
            'defensive_chances': 4500,
            'defensive_runs_saved_above_average': -24,
            'defensive_runs_saved_above_average_per_innings': -3,
            'double_plays_turned': 623,
            'doubles': 271,
            'errors': 61,
            'fielding_percentage': 0.986,
            'games': 1105,
            'games_catcher': 0,
            'games_center_fielder': 0,
            'games_designated_hitter': 30,
            'games_first_baseman': 0,
            'games_in_batting_order': 1105,
            'games_in_defensive_lineup': 1070,
            'games_left_fielder': 0,
            'games_outfielder': 0,
            'games_pinch_hitter': 7,
            'games_pinch_runner': 4,
            'games_pitcher': 0,
            'games_right_fielder': 0,
            'games_second_baseman': 1070,
            'games_shortstop': 1,
            'games_started': 1059,
            'games_third_baseman': 0,
            'grounded_into_double_plays': 123,
            'height': '5-6',
            'hits': 1404,
            'home_runs': 96,
            'innings_played': 9269.0,
            'intentional_bases_on_balls': 38,
            'league_fielding_percentage': 0.984,
            'league_range_factor_per_game': 4.5,
            'league_range_factor_per_nine_innings': 4.53,
            'name': u'José Altuve',
            'nationality': 'Venezuela',
            'on_base_percentage': 0.364,
            'on_base_plus_slugging_percentage': 0.818,
            'on_base_plus_slugging_percentage_plus': 126,
            'plate_appearances': 4851,
            'player_id': 'altuvjo01',
            'position': '2B',
            'putouts': 1676,
            'range_factor_per_game': 4.15,
            'range_factor_per_nine_innings': 4.31,
            'runs': 635,
            'runs_batted_in': 457,
            'sacrifice_flies': 36,
            'sacrifice_hits': 24,
            'season': 'Career',
            'slugging_percentage': 0.454,
            'stolen_bases': 246,
            'team_abbreviation': 'HOU',
            'times_caught_stealing': 68,
            'times_hit_by_pitch': 44,
            'times_struck_out': 535,
            'total_bases': 2013,
            'total_fielding_runs_above_average': 23,
            'total_fielding_runs_above_average_per_innings': 3,
            'triples': 25,
            'weight': 165
        }

        self.results_2017 = {
            'assists': 351,
            'at_bats': 590,
            'bases_on_balls': 58,
            'batting_average': 0.346,
            'birth_date': '1990-05-06',
            'complete_games': 134,
            'defensive_chances': 562,
            'defensive_runs_saved_above_average': 3,
            'defensive_runs_saved_above_average_per_innings': 3,
            'double_plays_turned': 86,
            'doubles': 39,
            'errors': 10,
            'fielding_percentage': 0.982,
            'games': 153,
            'games_catcher': 0,
            'games_center_fielder': 0,
            'games_designated_hitter': 3,
            'games_first_baseman': 0,
            'games_in_batting_order': 153,
            'games_in_defensive_lineup': 149,
            'games_left_fielder': 0,
            'games_outfielder': 0,
            'games_pinch_hitter': 1,
            'games_pinch_runner': 1,
            'games_pitcher': 0,
            'games_right_fielder': 0,
            'games_second_baseman': 149,
            'games_shortstop': 0,
            'games_started': 148,
            'games_third_baseman': 0,
            'grounded_into_double_plays': 19,
            'height': '5-6',
            'hits': 204,
            'home_runs': 24,
            'innings_played': 1283.1,
            'intentional_bases_on_balls': 3,
            'league_fielding_percentage': 0.983,
            'league_range_factor_per_game': 4.3,
            'league_range_factor_per_nine_innings': 4.35,
            'name': u'José Altuve',
            'nationality': 'Venezuela',
            'on_base_percentage': 0.41,
            'on_base_plus_slugging_percentage': 0.957,
            'on_base_plus_slugging_percentage_plus': 162,
            'plate_appearances': 662,
            'player_id': 'altuvjo01',
            'position': '2B',
            'putouts': 201,
            'range_factor_per_game': 3.7,
            'range_factor_per_nine_innings': 3.87,
            'runs': 112,
            'runs_batted_in': 81,
            'sacrifice_flies': 4,
            'sacrifice_hits': 1,
            'season': '2017',
            'slugging_percentage': 0.547,
            'stolen_bases': 32,
            'team_abbreviation': 'HOU',
            'times_caught_stealing': 6,
            'times_hit_by_pitch': 9,
            'times_struck_out': 84,
            'total_bases': 323,
            'total_fielding_runs_above_average': 13,
            'total_fielding_runs_above_average_per_innings': 12,
            'triples': 4,
            'weight': 165,
            # Properties specific to pitchers
            'balks': None,
            'bases_on_balls_given': None,
            'bases_on_balls_given_per_nine_innings': None,
            'batters_faced': None,
            'batters_struckout_per_nine_innings': None,
            'earned_runs_allowed': None,
            'era': None,
            'era_plus': None,
            'fielding_independent_pitching': None,
            'games_finished': None,
            'hits_against_per_nine_innings': None,
            'hits_allowed': None,
            'home_runs_against_per_nine_innings': None,
            'home_runs_allowed': None,
            'intentional_bases_on_balls_given': None,
            'losses': None,
            'runs_allowed': None,
            'saves': None,
            'shutouts': None,
            'strikeouts': None,
            'strikeouts_thrown_per_walk': None,
            'times_hit_player': None,
            'whip': None,
            'wild_pitches': None,
            'win_percentage': None,
            'wins': None
        }

        self.player = Player('altuvjo01')

    def test_mlb_player_returns_requested_career_stats(self):
        # Request the career stats
        player = self.player('')

        for attribute, value in self.results_career.items():
            assert getattr(player, attribute) == value

    def test_mlb_player_returns_requested_player_season_stats(self):
        # Request the 2017 stats
        player = self.player('2017')

        for attribute, value in self.results_2017.items():
            assert getattr(player, attribute) == value

    def test_dataframe_returns_dataframe(self):
        dataframe = [
            {'assists': 2763,
             'at_bats': 4436,
             'bases_on_balls': 311,
             'batting_average': 0.317,
             'birth_date': '1990-05-06',
             'complete_games': 990,
             'defensive_chances': 4500,
             'defensive_runs_saved_above_average': -24,
             'defensive_runs_saved_above_average_per_innings': -3,
             'double_plays_turned': 623,
             'doubles': 271,
             'errors': 61,
             'fielding_percentage': 0.986,
             'games': 1105,
             'games_catcher': 0,
             'games_center_fielder': 0,
             'games_designated_hitter': 30,
             'games_first_baseman': 0,
             'games_in_batting_order': 1105,
             'games_in_defensive_lineup': 1070,
             'games_left_fielder': 0,
             'games_outfielder': 0,
             'games_pinch_hitter': 7,
             'games_pinch_runner': 4,
             'games_pitcher': 0,
             'games_right_fielder': 0,
             'games_second_baseman': 1070,
             'games_shortstop': 1,
             'games_started': 1059,
             'games_third_baseman': 0,
             'grounded_into_double_plays': 123,
             'height': '5-6',
             'hits': 1404,
             'home_runs': 96,
             'innings_played': 9269.0,
             'intentional_bases_on_balls': 38,
             'league_fielding_percentage': 0.984,
             'league_range_factor_per_game': 4.5,
             'league_range_factor_per_nine_innings': 4.53,
             'name': u'José Altuve',
             'nationality': 'Venezuela',
             'on_base_percentage': 0.364,
             'on_base_plus_slugging_percentage': 0.818,
             'on_base_plus_slugging_percentage_plus': 126,
             'plate_appearances': 4851,
             'player_id': 'altuvjo01',
             'position': '2B',
             'putouts': 1676,
             'range_factor_per_game': 4.15,
             'range_factor_per_nine_innings': 4.31,
             'runs': 635,
             'runs_batted_in': 457,
             'sacrifice_flies': 36,
             'sacrifice_hits': 24,
             'season': 'Career',
             'slugging_percentage': 0.454,
             'stolen_bases': 246,
             'team_abbreviation': 'HOU',
             'times_caught_stealing': 68,
             'times_hit_by_pitch': 44,
             'times_struck_out': 535,
             'total_bases': 2013,
             'total_fielding_runs_above_average': 23,
             'total_fielding_runs_above_average_per_innings': 3,
             'triples': 25,
             'weight': 165,
             # Properties specific to pitchers
             'balks': None,
             'bases_on_balls_given': None,
             'bases_on_balls_given_per_nine_innings': None,
             'batters_faced': None,
             'batters_struckout_per_nine_innings': None,
             'earned_runs_allowed': None,
             'era': None,
             'era_plus': None,
             'fielding_independent_pitching': None,
             'games_finished': None,
             'hits_against_per_nine_innings': None,
             'hits_allowed': None,
             'home_runs_against_per_nine_innings': None,
             'home_runs_allowed': None,
             'intentional_bases_on_balls_given': None,
             'losses': None,
             'runs_allowed': None,
             'saves': None,
             'shutouts': None,
             'strikeouts': None,
             'strikeouts_thrown_per_walk': None,
             'times_hit_player': None,
             'whip': None,
             'wild_pitches': None,
             'win_percentage': None,
             'wins': None},
            {'assists': 351,
             'at_bats': 590,
             'bases_on_balls': 58,
             'batting_average': 0.346,
             'birth_date': '1990-05-06',
             'complete_games': 134,
             'defensive_chances': 562,
             'defensive_runs_saved_above_average': 3,
             'defensive_runs_saved_above_average_per_innings': 3,
             'double_plays_turned': 86,
             'doubles': 39,
             'errors': 10,
             'fielding_percentage': 0.982,
             'games': 153,
             'games_catcher': 0,
             'games_center_fielder': 0,
             'games_designated_hitter': 3,
             'games_first_baseman': 0,
             'games_in_batting_order': 153,
             'games_in_defensive_lineup': 149,
             'games_left_fielder': 0,
             'games_outfielder': 0,
             'games_pinch_hitter': 1,
             'games_pinch_runner': 1,
             'games_pitcher': 0,
             'games_right_fielder': 0,
             'games_second_baseman': 149,
             'games_shortstop': 0,
             'games_started': 148,
             'games_third_baseman': 0,
             'grounded_into_double_plays': 19,
             'height': '5-6',
             'hits': 204,
             'home_runs': 24,
             'innings_played': 1283.1,
             'intentional_bases_on_balls': 3,
             'league_fielding_percentage': 0.983,
             'league_range_factor_per_game': 4.3,
             'league_range_factor_per_nine_innings': 4.35,
             'name': u'José Altuve',
             'nationality': 'Venezuela',
             'on_base_percentage': 0.41,
             'on_base_plus_slugging_percentage': 0.957,
             'on_base_plus_slugging_percentage_plus': 162,
             'plate_appearances': 662,
             'player_id': 'altuvjo01',
             'position': '2B',
             'putouts': 201,
             'range_factor_per_game': 3.7,
             'range_factor_per_nine_innings': 3.87,
             'runs': 112,
             'runs_batted_in': 81,
             'sacrifice_flies': 4,
             'sacrifice_hits': 1,
             'season': '2017',
             'slugging_percentage': 0.547,
             'stolen_bases': 32,
             'team_abbreviation': 'HOU',
             'times_caught_stealing': 6,
             'times_hit_by_pitch': 9,
             'times_struck_out': 84,
             'total_bases': 323,
             'total_fielding_runs_above_average': 13,
             'total_fielding_runs_above_average_per_innings': 12,
             'triples': 4,
             'weight': 165},
            {'assists': 361,
             'at_bats': 640,
             'bases_on_balls': 60,
             'batting_average': 0.338,
             'birth_date': '1990-05-06',
             'complete_games': 135,
             'defensive_chances': 574,
             'defensive_runs_saved_above_average': -2,
             'defensive_runs_saved_above_average_per_innings': -2,
             'double_plays_turned': 73,
             'doubles': 42,
             'errors': 7,
             'fielding_percentage': 0.988,
             'games': 161,
             'games_catcher': 0,
             'games_center_fielder': 0,
             'games_designated_hitter': 13,
             'games_first_baseman': 0,
             'games_in_batting_order': 161,
             'games_in_defensive_lineup': 148,
             'games_left_fielder': 0,
             'games_outfielder': 0,
             'games_pinch_hitter': 0,
             'games_pinch_runner': 1,
             'games_pitcher': 0,
             'games_right_fielder': 0,
             'games_second_baseman': 148,
             'games_shortstop': 1,
             'games_started': 147,
             'games_third_baseman': 0,
             'grounded_into_double_plays': 15,
             'height': '5-6',
             'hits': 216,
             'home_runs': 24,
             'innings_played': 1307.0,
             'intentional_bases_on_balls': 11,
             'league_fielding_percentage': 0.983,
             'league_range_factor_per_game': 4.44,
             'league_range_factor_per_nine_innings': 4.48,
             'name': u'José Altuve',
             'nationality': 'Venezuela',
             'on_base_percentage': 0.396,
             'on_base_plus_slugging_percentage': 0.928,
             'on_base_plus_slugging_percentage_plus': 155,
             'plate_appearances': 717,
             'player_id': 'altuvjo01',
             'position': '2B',
             'putouts': 206,
             'range_factor_per_game': 3.83,
             'range_factor_per_nine_innings': 3.9,
             'runs': 108,
             'runs_batted_in': 96,
             'sacrifice_flies': 7,
             'sacrifice_hits': 3,
             'season': '2016',
             'slugging_percentage': 0.531,
             'stolen_bases': 30,
             'team_abbreviation': 'HOU',
             'times_caught_stealing': 10,
             'times_hit_by_pitch': 7,
             'times_struck_out': 70,
             'total_bases': 340,
             'total_fielding_runs_above_average': 6,
             'total_fielding_runs_above_average_per_innings': 5,
             'triples': 5,
             'weight': 165,
             # Properties specific to pitchers
             'balks': None,
             'bases_on_balls_given': None,
             'bases_on_balls_given_per_nine_innings': None,
             'batters_faced': None,
             'batters_struckout_per_nine_innings': None,
             'earned_runs_allowed': None,
             'era': None,
             'era_plus': None,
             'fielding_independent_pitching': None,
             'games_finished': None,
             'hits_against_per_nine_innings': None,
             'hits_allowed': None,
             'home_runs_against_per_nine_innings': None,
             'home_runs_allowed': None,
             'intentional_bases_on_balls_given': None,
             'losses': None,
             'runs_allowed': None,
             'saves': None,
             'shutouts': None,
             'strikeouts': None,
             'strikeouts_thrown_per_walk': None,
             'times_hit_player': None,
             'whip': None,
             'wild_pitches': None,
             'win_percentage': None,
             'wins': None}
        ]
        indices = ['Career', '2017', '2016']

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

    def test_player_contract_returns_contract(self):
        contract = self.player.contract

        expected = {
            '2012': {
                'age': '22',
                'team': 'Houston Astros',
                'salary': '$483,000'
            },
            '2013': {
                'age': '23',
                'team': 'Houston Astros',
                'salary': '$505,700'
            },
            '2014': {
                'age': '24',
                'team': 'Houston Astros',
                'salary': '$1,250,000'
            },
            '2015': {
                'age': '25',
                'team': 'Houston Astros',
                'salary': '$2,500,000'
            },
            '2016': {
                'age': '26',
                'team': 'Houston Astros',
                'salary': '$3,500,000'
            },
            '2017': {
                'age': '27',
                'team': 'Houston Astros',
                'salary': '$4,500,000'
            },
            '2018': {
                'age': '28',
                'team': 'Houston Astros',
                'salary': '$9,000,000'
            },
            '2019': {
                'age': '29',
                'team': 'Houston Astros',
                'salary': '$9,500,000'
            },
            '2020': {
                'age': '30',
                'team': 'Houston Astros',
                'salary': '$29,000,000'
            },
            '2021': {
                'age': '31',
                'team': 'Houston Astros',
                'salary': '$29,000,000'
            },
            '2022': {
                'age': '32',
                'team': 'Houston Astros',
                'salary': '$29,000,000'
            },
            '2023': {
                'age': '33',
                'team': 'Houston Astros',
                'salary': '$29,000,000'
            },
            '2024': {
                'age': '34',
                'team': 'Houston Astros',
                'salary': '$29,000,000'
            }
            }

        assert contract == expected


class TestMLBPitcher:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results_career = {
            'assists': 278,
            'at_bats': 48,
            'bases_on_balls': 0,
            'batting_average': 0.104,
            'birth_date': '1983-02-20',
            'complete_games': 24,
            'defensive_chances': 465,
            'defensive_runs_saved_above_average': 31,
            'defensive_runs_saved_above_average_per_innings': 2,
            'double_plays_turned': 28,
            'doubles': 0,
            'errors': 33,
            'fielding_percentage': 0.929,
            'games': 23,
            'games_catcher': 0,
            'games_center_fielder': 0,
            'games_designated_hitter': 0,
            'games_first_baseman': 0,
            'games_in_batting_order': 23,
            'games_in_defensive_lineup': 417,
            'games_left_fielder': 0,
            'games_outfielder': 0,
            'games_pinch_hitter': 0,
            'games_pinch_runner': 0,
            'games_pitcher': 417,
            'games_right_fielder': 0,
            'games_second_baseman': 0,
            'games_shortstop': 0,
            'games_started': 417,
            'games_third_baseman': 0,
            'grounded_into_double_plays': 1,
            'height': '6-5',
            'hits': 5,
            'home_runs': 0,
            'innings_played': 2747.0,
            'intentional_bases_on_balls': 0,
            'league_fielding_percentage': 0.953,
            'league_range_factor_per_game': 1.5,
            'league_range_factor_per_nine_innings': 1.51,
            'name': 'Justin Verlander',
            'nationality': 'United States of America',
            'on_base_percentage': 0.104,
            'on_base_plus_slugging_percentage': 0.208,
            'on_base_plus_slugging_percentage_plus': -43,
            'plate_appearances': 58,
            'player_id': 'verlaju01',
            'position': 'P',
            'putouts': 154,
            'range_factor_per_game': 1.04,
            'range_factor_per_nine_innings': 1.42,
            'runs': 2,
            'runs_batted_in': 1,
            'sacrifice_flies': 0,
            'sacrifice_hits': 10,
            'season': 'Career',
            'slugging_percentage': 0.104,
            'stolen_bases': 0,
            'team_abbreviation': 'HOU',
            'times_caught_stealing': 0,
            'times_hit_by_pitch': 0,
            'times_struck_out': 23,
            'total_bases': 5,
            'total_fielding_runs_above_average': None,
            'total_fielding_runs_above_average_per_innings': None,
            'triples': 0,
            'weight': 225,
            'balks': 19,
            'bases_on_balls_given': 807,
            'bases_on_balls_given_per_nine_innings': 2.6,
            'batters_faced': 11305,
            'batters_struckout_per_nine_innings': 8.8,
            'earned_runs_allowed': 1039,
            'era': 3.4,
            'era_plus': 125.0,
            'fielding_independent_pitching': 3.43,
            'games_finished': 0,
            'hits_against_per_nine_innings': 7.8,
            'hits_allowed': 2394,
            'home_runs_against_per_nine_innings': 0.9,
            'home_runs_allowed': 272,
            'intentional_bases_on_balls_given': 27,
            'losses': 123,
            'runs_allowed': 1124,
            'saves': 0,
            'shutouts': 8,
            'strikeouts': 2685,
            'strikeouts_thrown_per_walk': 3.33,
            'times_hit_player': 91,
            'whip': 1.165,
            'wild_pitches': 82,
            'win_percentage': 0.624,
            'wins': 204
        }

        self.results_2017 = {
            'assists': 13,
            'at_bats': 6,
            'bases_on_balls': 0,
            'batting_average': 0.167,
            'birth_date': '1983-02-20',
            'complete_games': 0,
            'defensive_chances': 24,
            'defensive_runs_saved_above_average': 0,
            'defensive_runs_saved_above_average_per_innings': 0,
            'double_plays_turned': 1,
            'doubles': 0,
            'errors': 1,
            'fielding_percentage': 0.958,
            'games': 2,
            'games_catcher': 0,
            'games_center_fielder': 0,
            'games_designated_hitter': 0,
            'games_first_baseman': 0,
            'games_in_batting_order': 2,
            'games_in_defensive_lineup': 28,
            'games_left_fielder': 0,
            'games_outfielder': 0,
            'games_pinch_hitter': 0,
            'games_pinch_runner': 0,
            'games_pitcher': 28,
            'games_right_fielder': 0,
            'games_second_baseman': 0,
            'games_shortstop': 0,
            'games_started': 33,
            'games_third_baseman': 0,
            'grounded_into_double_plays': 0,
            'height': '6-5',
            'hits': 1,
            'home_runs': 0,
            'innings_played': 206.0,
            'intentional_bases_on_balls': 0,
            'league_fielding_percentage': 0.948,
            'league_range_factor_per_game': 1.32,
            'league_range_factor_per_nine_innings': 1.33,
            'name': 'Justin Verlander',
            'nationality': 'United States of America',
            'on_base_percentage': 0.167,
            'on_base_plus_slugging_percentage': 0.333,
            'on_base_plus_slugging_percentage_plus': -10,
            'plate_appearances': 6,
            'player_id': 'verlaju01',
            'position': 'P',
            'putouts': 10,
            'range_factor_per_game': 0.7,
            'range_factor_per_nine_innings': 1.0,
            'runs': 0,
            'runs_batted_in': 1,
            'sacrifice_flies': 0,
            'sacrifice_hits': 0,
            'season': '2017',
            'slugging_percentage': 0.167,
            'stolen_bases': 0,
            'team_abbreviation': 'HOU',
            'times_caught_stealing': 0,
            'times_hit_by_pitch': 0,
            'times_struck_out': 4,
            'total_bases': 1,
            'total_fielding_runs_above_average': None,
            'total_fielding_runs_above_average_per_innings': None,
            'triples': 0,
            'weight': 225,
            'balks': 0,
            'bases_on_balls_given': 72,
            'bases_on_balls_given_per_nine_innings': 3.1,
            'batters_faced': 849,
            'batters_struckout_per_nine_innings': 9.6,
            'earned_runs_allowed': 77,
            'era': 3.36,
            'era_plus': 131.0,
            'fielding_independent_pitching': 3.84,
            'games_finished': 0,
            'hits_against_per_nine_innings': 7.4,
            'hits_allowed': 170,
            'home_runs_against_per_nine_innings': 1.2,
            'home_runs_allowed': 27,
            'intentional_bases_on_balls_given': 4,
            'losses': 8,
            'runs_allowed': 80,
            'saves': 0,
            'shutouts': 0,
            'strikeouts': 219,
            'strikeouts_thrown_per_walk': 3.04,
            'times_hit_player': 4,
            'whip': 1.175,
            'wild_pitches': 5,
            'win_percentage': 0.652,
            'wins': 15
        }

        self.player = Player('verlaju01')

    def test_mlb_player_returns_requested_career_stats(self):
        # Request the career stats
        player = self.player('')

        for attribute, value in self.results_career.items():
            assert getattr(player, attribute) == value

    def test_mlb_player_returns_requested_player_season_stats(self):
        # Request the 2017 stats
        player = self.player('2017')

        for attribute, value in self.results_2017.items():
            assert getattr(player, attribute) == value

    def test_dataframe_returns_dataframe(self):
        dataframe = [
            {'assists': 278,
             'at_bats': 48,
             'bases_on_balls': 0,
             'batting_average': 0.104,
             'birth_date': '1983-02-20',
             'complete_games': 24,
             'defensive_chances': 465,
             'defensive_runs_saved_above_average': 31,
             'defensive_runs_saved_above_average_per_innings': 2,
             'double_plays_turned': 28,
             'doubles': 0,
             'errors': 33,
             'fielding_percentage': 0.929,
             'games': 23,
             'games_catcher': 0,
             'games_center_fielder': 0,
             'games_designated_hitter': 0,
             'games_first_baseman': 0,
             'games_in_batting_order': 23,
             'games_in_defensive_lineup': 417,
             'games_left_fielder': 0,
             'games_outfielder': 0,
             'games_pinch_hitter': 0,
             'games_pinch_runner': 0,
             'games_pitcher': 417,
             'games_right_fielder': 0,
             'games_second_baseman': 0,
             'games_shortstop': 0,
             'games_started': 417,
             'games_third_baseman': 0,
             'grounded_into_double_plays': 1,
             'height': '6-5',
             'hits': 5,
             'home_runs': 0,
             'innings_played': 2747.0,
             'intentional_bases_on_balls': 0,
             'league_fielding_percentage': 0.953,
             'league_range_factor_per_game': 1.5,
             'league_range_factor_per_nine_innings': 1.51,
             'name': 'Justin Verlander',
             'nationality': 'United States of America',
             'on_base_percentage': 0.104,
             'on_base_plus_slugging_percentage': 0.208,
             'on_base_plus_slugging_percentage_plus': -43,
             'plate_appearances': 58,
             'player_id': 'verlaju01',
             'position': 'P',
             'putouts': 154,
             'range_factor_per_game': 1.04,
             'range_factor_per_nine_innings': 1.42,
             'runs': 2,
             'runs_batted_in': 1,
             'sacrifice_flies': 0,
             'sacrifice_hits': 10,
             'season': 'Career',
             'slugging_percentage': 0.104,
             'stolen_bases': 0,
             'team_abbreviation': 'HOU',
             'times_caught_stealing': 0,
             'times_hit_by_pitch': 0,
             'times_struck_out': 23,
             'total_bases': 5,
             'total_fielding_runs_above_average': None,
             'total_fielding_runs_above_average_per_innings': None,
             'triples': 0,
             'weight': 225,
             'balks': 19,
             'bases_on_balls_given': 807,
             'bases_on_balls_given_per_nine_innings': 2.6,
             'batters_faced': 11305,
             'batters_struckout_per_nine_innings': 8.8,
             'earned_runs_allowed': 1039,
             'era': 3.4,
             'era_plus': 125.0,
             'fielding_independent_pitching': 3.43,
             'games_finished': 0,
             'hits_against_per_nine_innings': 7.8,
             'hits_allowed': 2394,
             'home_runs_against_per_nine_innings': 0.9,
             'home_runs_allowed': 272,
             'intentional_bases_on_balls_given': 27,
             'losses': 123,
             'runs_allowed': 1124,
             'saves': 0,
             'shutouts': 8,
             'strikeouts': 2685,
             'strikeouts_thrown_per_walk': 3.33,
             'times_hit_player': 91,
             'whip': 1.165,
             'wild_pitches': 82,
             'win_percentage': 0.624,
             'wins': 204},
            {'assists': 13,
             'at_bats': 6,
             'bases_on_balls': 0,
             'batting_average': 0.167,
             'birth_date': '1983-02-20',
             'complete_games': 0,
             'defensive_chances': 24,
             'defensive_runs_saved_above_average': 0,
             'defensive_runs_saved_above_average_per_innings': 0,
             'double_plays_turned': 1,
             'doubles': 0,
             'errors': 1,
             'fielding_percentage': 0.958,
             'games': 2,
             'games_catcher': 0,
             'games_center_fielder': 0,
             'games_designated_hitter': 0,
             'games_first_baseman': 0,
             'games_in_batting_order': 2,
             'games_in_defensive_lineup': 28,
             'games_left_fielder': 0,
             'games_outfielder': 0,
             'games_pinch_hitter': 0,
             'games_pinch_runner': 0,
             'games_pitcher': 28,
             'games_right_fielder': 0,
             'games_second_baseman': 0,
             'games_shortstop': 0,
             'games_started': 33,
             'games_third_baseman': 0,
             'grounded_into_double_plays': 0,
             'height': '6-5',
             'hits': 1,
             'home_runs': 0,
             'innings_played': 206.0,
             'intentional_bases_on_balls': 0,
             'league_fielding_percentage': 0.948,
             'league_range_factor_per_game': 1.32,
             'league_range_factor_per_nine_innings': 1.33,
             'name': 'Justin Verlander',
             'nationality': 'United States of America',
             'on_base_percentage': 0.167,
             'on_base_plus_slugging_percentage': 0.333,
             'on_base_plus_slugging_percentage_plus': -10,
             'plate_appearances': 6,
             'player_id': 'verlaju01',
             'position': 'P',
             'putouts': 10,
             'range_factor_per_game': 0.7,
             'range_factor_per_nine_innings': 1.0,
             'runs': 0,
             'runs_batted_in': 1,
             'sacrifice_flies': 0,
             'sacrifice_hits': 0,
             'season': '2017',
             'slugging_percentage': 0.167,
             'stolen_bases': 0,
             'team_abbreviation': 'HOU',
             'times_caught_stealing': 0,
             'times_hit_by_pitch': 0,
             'times_struck_out': 4,
             'total_bases': 1,
             'total_fielding_runs_above_average': None,
             'total_fielding_runs_above_average_per_innings': None,
             'triples': 0,
             'weight': 225,
             'balks': 0,
             'bases_on_balls_given': 72,
             'bases_on_balls_given_per_nine_innings': 3.1,
             'batters_faced': 849,
             'batters_struckout_per_nine_innings': 9.6,
             'earned_runs_allowed': 77,
             'era': 3.36,
             'era_plus': 131.0,
             'fielding_independent_pitching': 3.84,
             'games_finished': 0,
             'hits_against_per_nine_innings': 7.4,
             'hits_allowed': 170,
             'home_runs_against_per_nine_innings': 1.2,
             'home_runs_allowed': 27,
             'intentional_bases_on_balls_given': 4,
             'losses': 8,
             'runs_allowed': 80,
             'saves': 0,
             'shutouts': 0,
             'strikeouts': 219,
             'strikeouts_thrown_per_walk': 3.04,
             'times_hit_player': 4,
             'whip': 1.175,
             'wild_pitches': 5,
             'win_percentage': 0.652,
             'wins': 15},
            {'assists': 29,
             'at_bats': 5,
             'bases_on_balls': 0,
             'batting_average': 0.2,
             'birth_date': '1983-02-20',
             'complete_games': 2,
             'defensive_chances': 37,
             'defensive_runs_saved_above_average': 5,
             'defensive_runs_saved_above_average_per_innings': 4,
             'double_plays_turned': 2,
             'doubles': 0,
             'errors': 1,
             'fielding_percentage': 0.973,
             'games': 2,
             'games_catcher': 0,
             'games_center_fielder': 0,
             'games_designated_hitter': 0,
             'games_first_baseman': 0,
             'games_in_batting_order': 2,
             'games_in_defensive_lineup': 34,
             'games_left_fielder': 0,
             'games_outfielder': 0,
             'games_pinch_hitter': 0,
             'games_pinch_runner': 0,
             'games_pitcher': 34,
             'games_right_fielder': 0,
             'games_second_baseman': 0,
             'games_shortstop': 0,
             'games_started': 34,
             'games_third_baseman': 0,
             'grounded_into_double_plays': 0,
             'height': '6-5',
             'hits': 1,
             'home_runs': 0,
             'innings_played': 227.2,
             'intentional_bases_on_balls': 0,
             'league_fielding_percentage': 0.95,
             'league_range_factor_per_game': 1.39,
             'league_range_factor_per_nine_innings': 1.41,
             'name': 'Justin Verlander',
             'nationality': 'United States of America',
             'on_base_percentage': 0.2,
             'on_base_plus_slugging_percentage': 0.4,
             'on_base_plus_slugging_percentage_plus': 9,
             'plate_appearances': 5,
             'player_id': 'verlaju01',
             'position': 'P',
             'putouts': 7,
             'range_factor_per_game': 1.06,
             'range_factor_per_nine_innings': 1.42,
             'runs': 1,
             'runs_batted_in': 0,
             'sacrifice_flies': 0,
             'sacrifice_hits': 0,
             'season': '2016',
             'slugging_percentage': 0.2,
             'stolen_bases': 0,
             'team_abbreviation': 'HOU',
             'times_caught_stealing': 0,
             'times_hit_by_pitch': 0,
             'times_struck_out': 2,
             'total_bases': 1,
             'total_fielding_runs_above_average': None,
             'total_fielding_runs_above_average_per_innings': None,
             'triples': 0,
             'weight': 225,
             'balks': 0,
             'bases_on_balls_given': 57,
             'bases_on_balls_given_per_nine_innings': 2.3,
             'batters_faced': 903,
             'batters_struckout_per_nine_innings': 10.0,
             'earned_runs_allowed': 77,
             'era': 3.04,
             'era_plus': 140.0,
             'fielding_independent_pitching': 3.48,
             'games_finished': 0,
             'hits_against_per_nine_innings': 6.8,
             'hits_allowed': 171,
             'home_runs_against_per_nine_innings': 1.2,
             'home_runs_allowed': 30,
             'intentional_bases_on_balls_given': 1,
             'losses': 9,
             'runs_allowed': 81,
             'saves': 0,
             'shutouts': 0,
             'strikeouts': 254,
             'strikeouts_thrown_per_walk': 4.46,
             'times_hit_player': 8,
             'whip': 1.001,
             'wild_pitches': 6,
             'win_percentage': 0.64,
             'wins': 16}
        ]
        indices = ['Career', '2017', '2016']

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

    def test_player_contract_returns_contract(self):
        contract = self.player.contract

        expected = {
            '2006': {
                'age': '23',
                'team': 'Detroit Tigers',
                'salary': '$980,000'
            },
            '2007': {
                'age': '24',
                'team': 'Detroit Tigers',
                'salary': '$1,030,000'
            },
            '2008': {
                'age': '25',
                'team': 'Detroit Tigers',
                'salary': '$1,130,000'
            },
            '2009': {
                'age': '26',
                'team': 'Detroit Tigers',
                'salary': '$3,675,000'
            },
            '2010': {
                'age': '27',
                'team': 'Detroit Tigers',
                'salary': '$6,850,000'
            },
            '2011': {
                'age': '28',
                'team': 'Detroit Tigers',
                'salary': '$12,850,000'
            },
            '2012': {
                'age': '29',
                'team': 'Detroit Tigers',
                'salary': '$20,000,000'
            },
            '2013': {
                'age': '30',
                'team': 'Detroit Tigers',
                'salary': '$20,000,000'
            },
            '2014': {
                'age': '31',
                'team': 'Detroit Tigers',
                'salary': '$20,000,000'
            },
            '2015': {
                'age': '32',
                'team': 'Detroit Tigers',
                'salary': '$28,000,000'
            },
            '2016': {
                'age': '33',
                'team': 'Detroit Tigers',
                'salary': '$28,000,000'
            },
            '2017': {
                'age': '34',
                'team': 'Houston Astros',
                'salary': '$28,000,000'
            },
            '2018': {
                'age': '35',
                'team': 'Houston Astros',
                'salary': '$28,000,000'
            },
            '2019': {
                'age': '36',
                'team': 'Houston Astros',
                'salary': '$28,000,000'
            }
            }

        assert contract == expected

    def test_correct_initial_index_found(self):
        seasons = ['2017', None, '2018']
        mock_season = mock.PropertyMock(return_value=seasons)
        player = Player('verlaju01')
        type(player)._season = mock_season

        result = player._find_initial_index()

        assert player._index == 1


class TestMLBRoster:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_roster_class_pulls_all_player_stats(self, *args, **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return('2017')
        roster = Roster('HOU')

        assert len(roster.players) == 3

        for player in roster.players:
            assert player.name in [u'José Altuve', 'Justin Verlander',
                                   'Charlie Morton']

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
        mock_abbreviation = mock.PropertyMock(return_value='HOU')
        type(team)._abbreviation = mock_abbreviation

        assert len(team.roster.players) == 3

        for player in team.roster.players:
            assert player.name in [u'José Altuve', 'Justin Verlander',
                                   'Charlie Morton']
        type(team)._abbreviation = None

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_roster_class_with_slim_parameter(self, *args, **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return('2018')
        roster = Roster('HOU', slim=True)

        assert len(roster.players) == 3
        assert roster.players == {
            'altuvjo01': 'Jose Altuve',
            'verlaju01': 'Justin Verlander',
            'mortoch02': 'Charlie Morton'
        }

    @mock.patch('requests.head', side_effect=mock_request)
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_mlb_invalid_default_year_reverts_to_previous_year(self,
                                                               *args,
                                                               **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2018)

        roster = Roster('HOU')

        assert len(roster.players) == 3

        for player in roster.players:
            assert player.name in [u'José Altuve', 'Justin Verlander',
                                   'Charlie Morton']
