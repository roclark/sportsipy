import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsipy import utils
from sportsipy.mlb.constants import STANDINGS_URL, TEAM_STATS_URL
from sportsipy.mlb.teams import Team, Teams


MONTH = 4
YEAR = 2021


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'mlb_stats', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            if div == 'div#all_teams_standard_batting':
                return read_file('%s_batting.html' % YEAR)
            elif div == 'div#all_teams_standard_pitching':
                return read_file('%s_pitching.html' % YEAR)
            else:
                return read_file('%s_overall.html' % YEAR)

    html_contents = read_file('%s-standings.html' % YEAR)
    team_stats = read_file('%s.html' % YEAR)

    if url == STANDINGS_URL % YEAR:
        return MockPQ(html_contents)
    elif url == TEAM_STATS_URL % YEAR:
        return MockPQ(team_stats)


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


class TestMLBIntegration:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'rank': 5,
            'abbreviation': 'HOU',
            'name': 'Houston Astros',
            'league': None,
            'games': 123,
            'wins': 73,
            'losses': 50,
            'win_percentage': .594,
            'streak': 'W 3',
            'runs': 5.4,
            'runs_against': 3.9,
            'run_difference': 1.5,
            'strength_of_schedule': -0.1,
            'simple_rating_system': 1.5,
            'pythagorean_win_loss': '79-44',
            'luck': -6,
            'interleague_record': '6-8',
            'home_record': '39-23',
            'home_wins': 39,
            'home_losses': 23,
            'away_record': '34-27',
            'away_wins': 34,
            'away_losses': 27,
            'extra_inning_record': '5-6',
            'extra_inning_wins': 5,
            'extra_inning_losses': 6,
            'single_run_record': '12-14',
            'single_run_wins': 12,
            'single_run_losses': 14,
            'record_vs_right_handed_pitchers': '45-30',
            'wins_vs_right_handed_pitchers': 45,
            'losses_vs_right_handed_pitchers': 30,
            'record_vs_left_handed_pitchers': '28-20',
            'wins_vs_left_handed_pitchers': 28,
            'losses_vs_left_handed_pitchers': 20,
            'record_vs_teams_over_500': '39-25',
            'wins_vs_teams_over_500': 39,
            'losses_vs_teams_over_500': 25,
            'record_vs_teams_under_500': '34-25',
            'wins_vs_teams_under_500': 34,
            'losses_vs_teams_under_500': 25,
            'last_ten_games_record': '6-4',
            'wins_last_ten_games': 6,
            'losses_last_ten_games': 4,
            'last_twenty_games_record': '10-10',
            'wins_last_twenty_games': 10,
            'losses_last_twenty_games': 10,
            'last_thirty_games_record': '17-13',
            'wins_last_thirty_games': 17,
            'losses_last_thirty_games': 13,
            'number_players_used': 48,
            'average_batter_age': 29.0,
            'plate_appearances': 4757,
            'at_bats': 4220,
            'total_runs': 669,
            'hits': 1132,
            'doubles': 233,
            'triples': 10,
            'home_runs': 163,
            'runs_batted_in': 643,
            'stolen_bases': 43,
            'times_caught_stealing': 13,
            'bases_on_balls': 433,
            'times_struck_out': 929,
            'batting_average': .268,
            'on_base_percentage': .340,
            'slugging_percentage': .444,
            'on_base_plus_slugging_percentage': .784,
            'on_base_plus_slugging_percentage_plus': 115,
            'total_bases': 1874,
            'grounded_into_double_plays': 107,
            'times_hit_by_pitch': 49,
            'sacrifice_hits': 6,
            'sacrifice_flies': 48,
            'intentional_bases_on_balls': 19,
            'runners_left_on_base': 842,
            'number_of_pitchers': 29,
            'average_pitcher_age': 28.8,
            'runs_allowed_per_game': 3.92,
            'earned_runs_against': 3.61,
            'games_finished': 121,
            'complete_games': 2,
            'shutouts': 6,
            'complete_game_shutouts': 0,
            'saves': 26,
            'innings_pitched': 1094.0,
            'hits_allowed': 917,
            'home_runs_against': 144,
            'bases_on_walks_given': 404,
            'strikeouts': 1121,
            'hit_pitcher': 49,
            'balks': 1,
            'wild_pitches': 59,
            'batters_faced': 4578,
            'earned_runs_against_plus': 119,
            'fielding_independent_pitching': 4.09,
            'whip': 1.207,
            'hits_per_nine_innings': 7.5,
            'home_runs_per_nine_innings': 1.2,
            'bases_on_walks_given_per_nine_innings': 3.3,
            'strikeouts_per_nine_innings': 9.2,
            'strikeouts_per_base_on_balls': 2.77,
            'opposing_runners_left_on_base': 814
        }
        self.abbreviations = [
            'NYY', 'BOS', 'ATL', 'LAA', 'HOU', 'MIL', 'PHI', 'ARI', 'STL',
            'PIT', 'SEA', 'WSN', 'CHC', 'COL', 'NYM', 'TOR', 'CLE', 'SFG',
            'OAK', 'MIN', 'DET', 'TBR', 'LAD', 'TEX', 'SDP', 'MIA', 'CIN',
            'KCR', 'BAL', 'CHW'
        ]

        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_mlb_integration_returns_correct_number_of_teams(self, *args,
                                                             **kwargs):
        teams = Teams()

        assert len(teams) == len(self.abbreviations)

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_mlb_integration_returns_correct_attributes_for_team(self,
                                                                 *args,
                                                                 **kwargs):
        teams = Teams()

        houston = teams('HOU')

        for attribute, value in self.results.items():
            assert getattr(houston, attribute) == value

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_mlb_integration_returns_correct_team_abbreviations(self,
                                                                *args,
                                                                **kwargs):
        teams = Teams()

        for team in teams:
            assert team.abbreviation in self.abbreviations

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_mlb_integration_dataframe_returns_dataframe(self, *args,
                                                         **kwargs):
        teams = Teams()
        df = pd.DataFrame([self.results], index=['HOU'])

        houston = teams('HOU')
        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, houston.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_mlb_integration_all_teams_dataframe_returns_dataframe(self,
                                                                   *args,
                                                                   **kwargs):
        teams = Teams()
        result = teams.dataframes.drop_duplicates(keep=False)

        assert len(result) == len(self.abbreviations)
        assert set(result.columns.values) == set(self.results.keys())

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_pulling_team_directly(self, *args, **kwargs):
        hou = Team('HOU')

        for attribute, value in self.results.items():
            assert getattr(hou, attribute) == value

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_mlb_invalid_team_name_raises_value_error(self, *args, **kwargs):
        teams = Teams()

        with pytest.raises(ValueError):
            teams('INVALID_NAME')

    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_mlb_invalid_default_year_reverts_to_previous_year(self,
                                                               *args,
                                                               **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2022)

        teams = Teams()

        for team in teams:
            assert team._year == '2021'

    def test_mlb_empty_page_returns_no_teams(self):
        flexmock(utils) \
            .should_receive('_no_data_found') \
            .once()
        flexmock(utils) \
            .should_receive('_get_stats_table') \
            .and_return(None)

        teams = Teams()

        assert len(teams) == 0

    def test_mlb_team_string_representation(self):
        hou = Team('HOU')

        assert hou.__repr__() == 'Houston Astros (HOU) - 2021'

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_mlb_teams_string_representation(self, *args, **kwargs):
        expected = """San Francisco Giants (SFG)
Los Angeles Dodgers (LAD)
Tampa Bay Rays (TBR)
Milwaukee Brewers (MIL)
Houston Astros (HOU)
Chicago White Sox (CHW)
New York Yankees (NYY)
Oakland Athletics (OAK)
Boston Red Sox (BOS)
Atlanta Braves (ATL)
Cincinnati Reds (CIN)
San Diego Padres (SDP)
Seattle Mariners (SEA)
Toronto Blue Jays (TOR)
St. Louis Cardinals (STL)
Philadelphia Phillies (PHI)
Los Angeles Angels (LAA)
Cleveland Indians (CLE)
New York Mets (NYM)
Detroit Tigers (DET)
Colorado Rockies (COL)
Kansas City Royals (KCR)
Minnesota Twins (MIN)
Washington Nationals (WSN)
Chicago Cubs (CHC)
Miami Marlins (MIA)
Pittsburgh Pirates (PIT)
Texas Rangers (TEX)
Arizona Diamondbacks (ARI)
Baltimore Orioles (BAL)"""

        teams = Teams()

        assert teams.__repr__() == expected
