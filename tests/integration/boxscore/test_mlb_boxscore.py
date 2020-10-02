import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsipy import utils
from sportsipy.constants import HOME
from sportsipy.mlb.constants import BOXSCORE_URL, BOXSCORES_URL, NIGHT
from sportsipy.mlb.boxscore import Boxscore, Boxscores


MONTH = 10
YEAR = 2020

BOXSCORE = 'ANA/ANA202008170'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'mlb', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    if url == BOXSCORES_URL % (YEAR, 8, 17):
        return MockPQ(read_file('boxscore-8-17-2020.html'))
    if url == BOXSCORES_URL % (YEAR, 8, 18):
        return MockPQ(read_file('boxscore-8-18-2020.html'))
    path = '%s.shtml' % BOXSCORE
    boxscore = read_file(path.replace('ANA/', ''))
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestMLBBoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': 'Monday, August 17, 2020',
            'time': '6:40 p.m. Local',
            'venue': 'Angel Stadium of Anaheim',
            'time_of_day': NIGHT,
            'duration': '3:12',
            'winner': HOME,
            'winning_name': 'Los Angeles Angels',
            'winning_abbr': 'LAA',
            'losing_name': 'San Francisco Giants',
            'losing_abbr': 'SFG',
            'away_at_bats': 35,
            'away_runs': 6,
            'away_hits': 10,
            'away_rbi': 6,
            'away_earned_runs': 6.0,
            'away_bases_on_balls': 1,
            'away_strikeouts': 5,
            'away_plate_appearances': 38,
            'away_batting_average': .286,
            'away_on_base_percentage': .316,
            'away_slugging_percentage': .457,
            'away_on_base_plus': .773,
            'away_pitches': 140,
            'away_strikes': 100,
            'away_win_probability_for_offensive_player': .283,
            'away_average_leverage_index': 1.15,
            'away_win_probability_added': .893,
            'away_win_probability_subtracted': -.608,
            'away_base_out_runs_added': 1.1,
            'away_putouts': 25,
            'away_assists': 5,
            'away_innings_pitched': 8.1,
            'away_home_runs': 2,
            'away_strikes_by_contact': 63,
            'away_strikes_swinging': 14,
            'away_strikes_looking': 23,
            'away_grounded_balls': 10,
            'away_fly_balls': 21,
            'away_line_drives': 10,
            'away_unknown_bat_type': 0,
            'away_game_score': 38,
            'away_inherited_runners': 0,
            'away_inherited_score': 0,
            'away_win_probability_by_pitcher': -.783,
            'away_average_leverage_index': 1.75,
            'away_base_out_runs_saved': -2.4,
            'home_at_bats': 35,
            'home_runs': 7,
            'home_hits': 12,
            'home_rbi': 7,
            'home_earned_runs': 7.56,
            'home_bases_on_balls': 2,
            'home_strikeouts': 10,
            'home_plate_appearances': 38,
            'home_batting_average': .343,
            'home_on_base_percentage': .368,
            'home_slugging_percentage': .600,
            'home_on_base_plus': .968,
            'home_pitches': 159,
            'home_strikes': 99,
            'home_win_probability_for_offensive_player': .784,
            'home_average_leverage_index': 1.75,
            'home_win_probability_added': 1.842,
            'home_win_probability_subtracted': -1.060,
            'home_base_out_runs_added': 2.4,
            'home_putouts': 27,
            'home_assists': 8,
            'home_innings_pitched': 9,
            'home_home_runs': 1,
            'home_strikes_by_contact': 50,
            'home_strikes_swinging': 14,
            'home_strikes_looking': 35,
            'home_grounded_balls': 7,
            'home_fly_balls': 19,
            'home_line_drives': 9,
            'home_unknown_bat_type': 0,
            'home_game_score': 42,
            'home_inherited_runners': 5,
            'home_inherited_score': 2,
            'home_win_probability_by_pitcher': -.283,
            'home_average_leverage_index': 1.15,
            'home_base_out_runs_saved': -1.1
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_mlb_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value
        assert getattr(self.boxscore, 'summary') == {
            'away': [2, 0, 0, 0, 1, 3, 0, 0, 0],
            'home': [0, 0, 2, 0, 3, 0, 0, 0, 2]
        }

    def test_invalid_url_yields_empty_class(self):
        flexmock(Boxscore) \
            .should_receive('_retrieve_html_page') \
            .and_return(None)

        boxscore = Boxscore(BOXSCORE)

        for key, value in boxscore.__dict__.items():
            if key == '_uri':
                continue
            assert value is None

    def test_mlb_boxscore_dataframe_returns_dataframe_of_all_values(self):
        df = pd.DataFrame([self.results], index=[BOXSCORE])

        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, self.boxscore.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_mlb_boxscore_player(self):
        boxscore = Boxscore(BOXSCORE)

        assert len(boxscore.home_players) == 15
        assert len(boxscore.away_players) == 15

        for player in boxscore.home_players:
            assert not player.dataframe.empty
        for player in boxscore.away_players:
            assert not player.dataframe.empty

    def test_mlb_boxscore_string_representation(self):
        expected = ('Boxscore for San Francisco Giants at '
                    'Los Angeles Angels (Monday, August 17, 2020)')

        boxscore = Boxscore(BOXSCORE)

        assert boxscore.__repr__() == expected


class TestMLBBoxscores:
    def setup_method(self):
        self.expected = {
            '8-17-2020': [
                {'home_name': 'Los Angeles Angels',
                 'home_abbr': 'LAA',
                 'home_score': 7,
                 'boxscore': 'ANA/ANA202008170',
                 'away_name': 'San Francisco Giants',
                 'away_abbr': 'SFG',
                 'away_score': 6,
                 'winning_name': 'Los Angeles Angels',
                 'winning_abbr': 'LAA',
                 'losing_name': 'San Francisco Giants',
                 'losing_abbr': 'SFG'},
                {'home_name': 'Arizona Diamondbacks',
                 'home_abbr': 'ARI',
                 'home_score': 4,
                 'boxscore': 'ARI/ARI202008170',
                 'away_name': 'Oakland Athletics',
                 'away_abbr': 'OAK',
                 'away_score': 3,
                 'winning_name': 'Arizona Diamondbacks',
                 'winning_abbr': 'ARI',
                 'losing_name': 'Oakland Athletics',
                 'losing_abbr': 'OAK'},
                {'home_name': 'Atlanta Braves',
                 'home_abbr': 'ATL',
                 'home_score': 7,
                 'boxscore': 'ATL/ATL202008170',
                 'away_name': 'Washington Nationals',
                 'away_abbr': 'WSN',
                 'away_score': 6,
                 'winning_name': 'Atlanta Braves',
                 'winning_abbr': 'ATL',
                 'losing_name': 'Washington Nationals',
                 'losing_abbr': 'WSN'},
                {'home_name': 'Baltimore Orioles',
                 'home_abbr': 'BAL',
                 'home_score': 2,
                 'boxscore': 'BAL/BAL202008170',
                 'away_name': 'Toronto Blue Jays',
                 'away_abbr': 'TOR',
                 'away_score': 7,
                 'winning_name': 'Toronto Blue Jays',
                 'winning_abbr': 'TOR',
                 'losing_name': 'Baltimore Orioles',
                 'losing_abbr': 'BAL'},
                {'home_name': 'Chicago White Sox',
                 'home_abbr': 'CHW',
                 'home_score': 7,
                 'boxscore': 'CHA/CHA202008170',
                 'away_name': 'Detroit Tigers',
                 'away_abbr': 'DET',
                 'away_score': 2,
                 'winning_name': 'Chicago White Sox',
                 'winning_abbr': 'CHW',
                 'losing_name': 'Detroit Tigers',
                 'losing_abbr': 'DET'},
                {'home_name': 'Chicago Cubs',
                 'home_abbr': 'CHC',
                 'home_score': 1,
                 'boxscore': 'CHN/CHN202008171',
                 'away_name': 'St. Louis Cardinals',
                 'away_abbr': 'STL',
                 'away_score': 3,
                 'winning_name': 'St. Louis Cardinals',
                 'winning_abbr': 'STL',
                 'losing_name': 'Chicago Cubs',
                 'losing_abbr': 'CHC'},
                {'home_name': 'Chicago Cubs',
                 'home_abbr': 'CHC',
                 'home_score': 5,
                 'boxscore': 'CHN/CHN202008172',
                 'away_name': 'St. Louis Cardinals',
                 'away_abbr': 'STL',
                 'away_score': 4,
                 'winning_name': 'Chicago Cubs',
                 'winning_abbr': 'CHC',
                 'losing_name': 'St. Louis Cardinals',
                 'losing_abbr': 'STL'},
                {'home_name': 'Houston Astros',
                 'home_abbr': 'HOU',
                 'home_score': 2,
                 'boxscore': 'HOU/HOU202008170',
                 'away_name': 'Colorado Rockies',
                 'away_abbr': 'COL',
                 'away_score': 1,
                 'winning_name': 'Houston Astros',
                 'winning_abbr': 'HOU',
                 'losing_name': 'Colorado Rockies',
                 'losing_abbr': 'COL'},
                {'home_name': 'Los Angeles Dodgers',
                 'home_abbr': 'LAD',
                 'home_score': 11,
                 'boxscore': 'LAN/LAN202008170',
                 'away_name': 'Seattle Mariners',
                 'away_abbr': 'SEA',
                 'away_score': 9,
                 'winning_name': 'Los Angeles Dodgers',
                 'winning_abbr': 'LAD',
                 'losing_name': 'Seattle Mariners',
                 'losing_abbr': 'SEA'},
                {'home_name': 'Miami Marlins',
                 'home_abbr': 'MIA',
                 'home_score': 4,
                 'boxscore': 'MIA/MIA202008170',
                 'away_name': 'New York Mets',
                 'away_abbr': 'NYM',
                 'away_score': 11,
                 'winning_name': 'New York Mets',
                 'winning_abbr': 'NYM',
                 'losing_name': 'Miami Marlins',
                 'losing_abbr': 'MIA'},
                {'home_name': 'Minnesota Twins',
                 'home_abbr': 'MIN',
                 'home_score': 4,
                 'boxscore': 'MIN/MIN202008170',
                 'away_name': 'Kansas City Royals',
                 'away_abbr': 'KCR',
                 'away_score': 1,
                 'winning_name': 'Minnesota Twins',
                 'winning_abbr': 'MIN',
                 'losing_name': 'Kansas City Royals',
                 'losing_abbr': 'KCR'},
                {'home_name': 'New York Yankees',
                 'home_abbr': 'NYY',
                 'home_score': 6,
                 'boxscore': 'NYA/NYA202008170',
                 'away_name': 'Boston Red Sox',
                 'away_abbr': 'BOS',
                 'away_score': 3,
                 'winning_name': 'New York Yankees',
                 'winning_abbr': 'NYY',
                 'losing_name': 'Boston Red Sox',
                 'losing_abbr': 'BOS'},
                {'home_name': 'Texas Rangers',
                 'home_abbr': 'TEX',
                 'home_score': 4,
                 'boxscore': 'TEX/TEX202008170',
                 'away_name': 'San Diego Padres',
                 'away_abbr': 'SDP',
                 'away_score': 14,
                 'winning_name': 'San Diego Padres',
                 'winning_abbr': 'SDP',
                 'losing_name': 'Texas Rangers',
                 'losing_abbr': 'TEX'}
            ]
        }

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 8, 17)).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_invalid_end(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 8, 17), datetime(2020, 8, 16)).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_multiple_days(self, *args, **kwargs):
        expected = {
            '8-17-2020': [
                {'home_name': 'Los Angeles Angels',
                 'home_abbr': 'LAA',
                 'home_score': 7,
                 'boxscore': 'ANA/ANA202008170',
                 'away_name': 'San Francisco Giants',
                 'away_abbr': 'SFG',
                 'away_score': 6,
                 'winning_name': 'Los Angeles Angels',
                 'winning_abbr': 'LAA',
                 'losing_name': 'San Francisco Giants',
                 'losing_abbr': 'SFG'},
                {'home_name': 'Arizona Diamondbacks',
                 'home_abbr': 'ARI',
                 'home_score': 4,
                 'boxscore': 'ARI/ARI202008170',
                 'away_name': 'Oakland Athletics',
                 'away_abbr': 'OAK',
                 'away_score': 3,
                 'winning_name': 'Arizona Diamondbacks',
                 'winning_abbr': 'ARI',
                 'losing_name': 'Oakland Athletics',
                 'losing_abbr': 'OAK'},
                {'home_name': 'Atlanta Braves',
                 'home_abbr': 'ATL',
                 'home_score': 7,
                 'boxscore': 'ATL/ATL202008170',
                 'away_name': 'Washington Nationals',
                 'away_abbr': 'WSN',
                 'away_score': 6,
                 'winning_name': 'Atlanta Braves',
                 'winning_abbr': 'ATL',
                 'losing_name': 'Washington Nationals',
                 'losing_abbr': 'WSN'},
                {'home_name': 'Baltimore Orioles',
                 'home_abbr': 'BAL',
                 'home_score': 2,
                 'boxscore': 'BAL/BAL202008170',
                 'away_name': 'Toronto Blue Jays',
                 'away_abbr': 'TOR',
                 'away_score': 7,
                 'winning_name': 'Toronto Blue Jays',
                 'winning_abbr': 'TOR',
                 'losing_name': 'Baltimore Orioles',
                 'losing_abbr': 'BAL'},
                {'home_name': 'Chicago White Sox',
                 'home_abbr': 'CHW',
                 'home_score': 7,
                 'boxscore': 'CHA/CHA202008170',
                 'away_name': 'Detroit Tigers',
                 'away_abbr': 'DET',
                 'away_score': 2,
                 'winning_name': 'Chicago White Sox',
                 'winning_abbr': 'CHW',
                 'losing_name': 'Detroit Tigers',
                 'losing_abbr': 'DET'},
                {'home_name': 'Chicago Cubs',
                 'home_abbr': 'CHC',
                 'home_score': 1,
                 'boxscore': 'CHN/CHN202008171',
                 'away_name': 'St. Louis Cardinals',
                 'away_abbr': 'STL',
                 'away_score': 3,
                 'winning_name': 'St. Louis Cardinals',
                 'winning_abbr': 'STL',
                 'losing_name': 'Chicago Cubs',
                 'losing_abbr': 'CHC'},
                {'home_name': 'Chicago Cubs',
                 'home_abbr': 'CHC',
                 'home_score': 5,
                 'boxscore': 'CHN/CHN202008172',
                 'away_name': 'St. Louis Cardinals',
                 'away_abbr': 'STL',
                 'away_score': 4,
                 'winning_name': 'Chicago Cubs',
                 'winning_abbr': 'CHC',
                 'losing_name': 'St. Louis Cardinals',
                 'losing_abbr': 'STL'},
                {'home_name': 'Houston Astros',
                 'home_abbr': 'HOU',
                 'home_score': 2,
                 'boxscore': 'HOU/HOU202008170',
                 'away_name': 'Colorado Rockies',
                 'away_abbr': 'COL',
                 'away_score': 1,
                 'winning_name': 'Houston Astros',
                 'winning_abbr': 'HOU',
                 'losing_name': 'Colorado Rockies',
                 'losing_abbr': 'COL'},
                {'home_name': 'Los Angeles Dodgers',
                 'home_abbr': 'LAD',
                 'home_score': 11,
                 'boxscore': 'LAN/LAN202008170',
                 'away_name': 'Seattle Mariners',
                 'away_abbr': 'SEA',
                 'away_score': 9,
                 'winning_name': 'Los Angeles Dodgers',
                 'winning_abbr': 'LAD',
                 'losing_name': 'Seattle Mariners',
                 'losing_abbr': 'SEA'},
                {'home_name': 'Miami Marlins',
                 'home_abbr': 'MIA',
                 'home_score': 4,
                 'boxscore': 'MIA/MIA202008170',
                 'away_name': 'New York Mets',
                 'away_abbr': 'NYM',
                 'away_score': 11,
                 'winning_name': 'New York Mets',
                 'winning_abbr': 'NYM',
                 'losing_name': 'Miami Marlins',
                 'losing_abbr': 'MIA'},
                {'home_name': 'Minnesota Twins',
                 'home_abbr': 'MIN',
                 'home_score': 4,
                 'boxscore': 'MIN/MIN202008170',
                 'away_name': 'Kansas City Royals',
                 'away_abbr': 'KCR',
                 'away_score': 1,
                 'winning_name': 'Minnesota Twins',
                 'winning_abbr': 'MIN',
                 'losing_name': 'Kansas City Royals',
                 'losing_abbr': 'KCR'},
                {'home_name': 'New York Yankees',
                 'home_abbr': 'NYY',
                 'home_score': 6,
                 'boxscore': 'NYA/NYA202008170',
                 'away_name': 'Boston Red Sox',
                 'away_abbr': 'BOS',
                 'away_score': 3,
                 'winning_name': 'New York Yankees',
                 'winning_abbr': 'NYY',
                 'losing_name': 'Boston Red Sox',
                 'losing_abbr': 'BOS'},
                {'home_name': 'Texas Rangers',
                 'home_abbr': 'TEX',
                 'home_score': 4,
                 'boxscore': 'TEX/TEX202008170',
                 'away_name': 'San Diego Padres',
                 'away_abbr': 'SDP',
                 'away_score': 14,
                 'winning_name': 'San Diego Padres',
                 'winning_abbr': 'SDP',
                 'losing_name': 'Texas Rangers',
                 'losing_abbr': 'TEX'}
            ],
            '8-18-2020': [
                {'boxscore': 'ANA/ANA202008180',
                 'away_name': 'San Francisco Giants',
                 'away_abbr': 'SFG',
                 'away_score': 8,
                 'home_name': 'Los Angeles Angels',
                 'home_abbr': 'LAA',
                 'home_score': 2,
                 'winning_name': 'San Francisco Giants',
                 'winning_abbr': 'SFG',
                 'losing_name': 'Los Angeles Angels',
                 'losing_abbr': 'LAA'},
                {'boxscore': 'ARI/ARI202008180',
                 'away_name': 'Oakland Athletics',
                 'away_abbr': 'OAK',
                 'away_score': 1,
                 'home_name': 'Arizona Diamondbacks',
                 'home_abbr': 'ARI',
                 'home_score': 10,
                 'winning_name': 'Arizona Diamondbacks',
                 'winning_abbr': 'ARI',
                 'losing_name': 'Oakland Athletics',
                 'losing_abbr': 'OAK'},
                {'boxscore': 'ATL/ATL202008180',
                 'away_name': 'Washington Nationals',
                 'away_abbr': 'WSN',
                 'away_score': 8,
                 'home_name': 'Atlanta Braves',
                 'home_abbr': 'ATL',
                 'home_score': 5,
                 'winning_name': 'Washington Nationals',
                 'winning_abbr': 'WSN',
                 'losing_name': 'Atlanta Braves',
                 'losing_abbr': 'ATL'},
                {'boxscore': 'BAL/BAL202008180',
                 'away_name': 'Toronto Blue Jays',
                 'away_abbr': 'TOR',
                 'away_score': 8,
                 'home_name': 'Baltimore Orioles',
                 'home_abbr': 'BAL',
                 'home_score': 7,
                 'winning_name': 'Toronto Blue Jays',
                 'winning_abbr': 'TOR',
                 'losing_name': 'Baltimore Orioles',
                 'losing_abbr': 'BAL'},
                {'boxscore': 'BOS/BOS202008180',
                 'away_name': 'Philadelphia Phillies',
                 'away_abbr': 'PHI',
                 'away_score': 13,
                 'home_name': 'Boston Red Sox',
                 'home_abbr': 'BOS',
                 'home_score': 6,
                 'winning_name': 'Philadelphia Phillies',
                 'winning_abbr': 'PHI',
                 'losing_name': 'Boston Red Sox',
                 'losing_abbr': 'BOS'},
                {'boxscore': 'CHA/CHA202008180',
                 'away_name': 'Detroit Tigers',
                 'away_abbr': 'DET',
                 'away_score': 4,
                 'home_name': 'Chicago White Sox',
                 'home_abbr': 'CHW',
                 'home_score': 10,
                 'winning_name': 'Chicago White Sox',
                 'winning_abbr': 'CHW',
                 'losing_name': 'Detroit Tigers',
                 'losing_abbr': 'DET'},
                {'boxscore': 'CHN/CHN202008180',
                 'away_name': 'St. Louis Cardinals',
                 'away_abbr': 'STL',
                 'away_score': 3,
                 'home_name': 'Chicago Cubs',
                 'home_abbr': 'CHC',
                 'home_score': 6,
                 'winning_name': 'Chicago Cubs',
                 'winning_abbr': 'CHC',
                 'losing_name': 'St. Louis Cardinals',
                 'losing_abbr': 'STL'},
                {'boxscore': 'HOU/HOU202008180',
                 'away_name': 'Colorado Rockies',
                 'away_abbr': 'COL',
                 'away_score': 1,
                 'home_name': 'Houston Astros',
                 'home_abbr': 'HOU',
                 'home_score': 2,
                 'winning_name': 'Houston Astros',
                 'winning_abbr': 'HOU',
                 'losing_name': 'Colorado Rockies',
                 'losing_abbr': 'COL'},
                {'boxscore': 'LAN/LAN202008180',
                 'away_name': 'Seattle Mariners',
                 'away_abbr': 'SEA',
                 'away_score': 1,
                 'home_name': 'Los Angeles Dodgers',
                 'home_abbr': 'LAD',
                 'home_score': 2,
                 'winning_name': 'Los Angeles Dodgers',
                 'winning_abbr': 'LAD',
                 'losing_name': 'Seattle Mariners',
                 'losing_abbr': 'SEA'},
                {'boxscore': 'MIA/MIA202008180',
                 'away_name': 'New York Mets',
                 'away_abbr': 'NYM',
                 'away_score': 8,
                 'home_name': 'Miami Marlins',
                 'home_abbr': 'MIA',
                 'home_score': 3,
                 'winning_name': 'New York Mets',
                 'winning_abbr': 'NYM',
                 'losing_name': 'Miami Marlins',
                 'losing_abbr': 'MIA'},
                {'boxscore': 'MIN/MIN202008180',
                 'away_name': 'Milwaukee Brewers',
                 'away_abbr': 'MIL',
                 'away_score': 3,
                 'home_name': 'Minnesota Twins',
                 'home_abbr': 'MIN',
                 'home_score': 4,
                 'winning_name': 'Minnesota Twins',
                 'winning_abbr': 'MIN',
                 'losing_name': 'Milwaukee Brewers',
                 'losing_abbr': 'MIL'},
                {'boxscore': 'NYA/NYA202008180',
                 'away_name': 'Tampa Bay Rays',
                 'away_abbr': 'TBR',
                 'away_score': 6,
                 'home_name': 'New York Yankees',
                 'home_abbr': 'NYY',
                 'home_score': 3,
                 'winning_name': 'Tampa Bay Rays',
                 'winning_abbr': 'TBR',
                 'losing_name': 'New York Yankees',
                 'losing_abbr': 'NYY'},
                {'boxscore': 'PIT/PIT202008180',
                 'away_name': 'Cleveland Indians',
                 'away_abbr': 'CLE',
                 'away_score': 6,
                 'home_name': 'Pittsburgh Pirates',
                 'home_abbr': 'PIT',
                 'home_score': 3,
                 'winning_name': 'Cleveland Indians',
                 'winning_abbr': 'CLE',
                 'losing_name': 'Pittsburgh Pirates',
                 'losing_abbr': 'PIT'},
                {'boxscore': 'TEX/TEX202008180',
                 'away_name': 'San Diego Padres',
                 'away_abbr': 'SDP',
                 'away_score': 6,
                 'home_name': 'Texas Rangers',
                 'home_abbr': 'TEX',
                 'home_score': 4,
                 'winning_name': 'San Diego Padres',
                 'winning_abbr': 'SDP',
                 'losing_name': 'Texas Rangers',
                 'losing_abbr': 'TEX'}
            ]
        }
        result = Boxscores(datetime(2020, 8, 17), datetime(2020, 8, 18)).games

        assert result == expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_string_representation(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 8, 17))

        assert result.__repr__() == 'MLB games for 8-17-2020'
