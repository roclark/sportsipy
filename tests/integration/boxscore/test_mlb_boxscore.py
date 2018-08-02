import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY
from sportsreference.mlb.constants import BOXSCORE_URL, BOXSCORES_URL, NIGHT
from sportsreference.mlb.boxscore import Boxscore, Boxscores


MONTH = 10
YEAR = 2017

BOXSCORE = 'BOS/BOS201806070'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'mlb', filename)
    return open('%s' % filepath, 'r').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    if url == BOXSCORES_URL % (YEAR, 7, 17):
        return MockPQ(read_file('boxscore.html'))
    path = '%s.shtml' % BOXSCORE
    boxscore = read_file(path.replace('BOS/', ''))
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestMLBBoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': 'Thursday, June 7, 2018',
            'time': '7:10 p.m. ET',
            'attendance': 36556,
            'venue': 'Fenway Park',
            'time_of_day': NIGHT,
            'duration': '2:55',
            'winner': AWAY,
            'winning_name': 'Detroit Tigers',
            'winning_abbr': 'DET',
            'losing_name': 'Boston Red Sox',
            'losing_abbr': 'BOS',
            'away_at_bats': 37,
            'away_runs': 7,
            'away_hits': 10,
            'away_rbi': 7,
            'away_earned_runs': 7.0,
            'away_bases_on_balls': 3,
            'away_strikeouts': 11,
            'away_plate_appearances': 40,
            'away_batting_average': .270,
            'away_on_base_percentage': .325,
            'away_slugging_percentage': .486,
            'away_on_base_plus': .811,
            'away_pitches': 141,
            'away_strikes': 109,
            'away_win_probability_for_offensive_player': .315,
            'away_average_leverage_index': .46,
            'away_win_probability_added': .551,
            'away_win_probability_subtracted': -.236,
            'away_base_out_runs_added': 2.2,
            'away_putouts': 27,
            'away_assists': 9,
            'away_innings_pitched': 9,
            'away_home_runs': 1,
            'away_strikes_by_contact': 68,
            'away_strikes_swinging': 14,
            'away_strikes_looking': 27,
            'away_grounded_balls': 13,
            'away_fly_balls': 13,
            'away_line_drives': 6,
            'away_unknown_bat_type': 0,
            'away_game_score': 59,
            'away_inherited_runners': 1,
            'away_inherited_score': 0,
            'away_win_probability_by_pitcher': .184,
            'away_average_leverage_index': .71,
            'away_base_out_runs_saved': 2.8,
            'home_at_bats': 33,
            'home_runs': 2,
            'home_hits': 7,
            'home_rbi': 2,
            'home_earned_runs': 2.0,
            'home_bases_on_balls': 5,
            'home_strikeouts': 8,
            'home_plate_appearances': 38,
            'home_batting_average': .212,
            'home_on_base_percentage': .316,
            'home_slugging_percentage': .364,
            'home_on_base_plus': .679,
            'home_pitches': 157,
            'home_strikes': 83,
            'home_win_probability_for_offensive_player': -.184,
            'home_average_leverage_index': .71,
            'home_win_probability_added': .368,
            'home_win_probability_subtracted': -.552,
            'home_base_out_runs_added': -2.8,
            'home_putouts': 27,
            'home_assists': 9,
            'home_innings_pitched': 9,
            'home_home_runs': 1,
            'home_strikes_by_contact': 45,
            'home_strikes_swinging': 12,
            'home_strikes_looking': 26,
            'home_grounded_balls': 9,
            'home_fly_balls': 16,
            'home_line_drives': 7,
            'home_unknown_bat_type': 0,
            'home_game_score': 25,
            'home_inherited_runners': 0,
            'home_inherited_score': 0,
            'home_win_probability_by_pitcher': -.317,
            'home_average_leverage_index': .46,
            'home_base_out_runs_saved': -2.2
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_mlb_boxscore_returns_requested_boxscore(self):
        for attribute, value in self.results.items():
            assert getattr(self.boxscore, attribute) == value

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


class TestMLBBoxscores:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        expected = {
            'boxscores': [
                {'home_name': 'Atlanta Braves',
                 'home_abbr': 'ATL',
                 'boxscore': 'ATL/ATL201707170',
                 'away_name': 'Chicago Cubs',
                 'away_abbr': 'CHC'},
                {'home_name': 'Baltimore Orioles',
                 'home_abbr': 'BAL',
                 'boxscore': 'BAL/BAL201707170',
                 'away_name': 'Texas Rangers',
                 'away_abbr': 'TEX'},
                {'home_name': 'Boston Red Sox',
                 'home_abbr': 'BOS',
                 'boxscore': 'BOS/BOS201707170',
                 'away_name': 'Toronto Blue Jays',
                 'away_abbr': 'TOR'},
                {'home_name': 'Cincinnati Reds',
                 'home_abbr': 'CIN',
                 'boxscore': 'CIN/CIN201707170',
                 'away_name': 'Washington Nationals',
                 'away_abbr': 'WSN'},
                {'home_name': 'Colorado Rockies',
                 'home_abbr': 'COL',
                 'boxscore': 'COL/COL201707170',
                 'away_name': 'San Diego Padres',
                 'away_abbr': 'SDP'},
                {'home_name': 'Houston Astros',
                 'home_abbr': 'HOU',
                 'boxscore': 'HOU/HOU201707170',
                 'away_name': 'Seattle Mariners',
                 'away_abbr': 'SEA'},
                {'home_name': 'Kansas City Royals',
                 'home_abbr': 'KCR',
                 'boxscore': 'KCA/KCA201707170',
                 'away_name': 'Detroit Tigers',
                 'away_abbr': 'DET'},
                {'home_name': 'Miami Marlins',
                 'home_abbr': 'MIA',
                 'boxscore': 'MIA/MIA201707170',
                 'away_name': 'Philadelphia Phillies',
                 'away_abbr': 'PHI'},
                {'home_name': 'Minnesota Twins',
                 'home_abbr': 'MIN',
                 'boxscore': 'MIN/MIN201707170',
                 'away_name': 'New York Yankees',
                 'away_abbr': 'NYY'},
                {'home_name': 'New York Mets',
                 'home_abbr': 'NYM',
                 'boxscore': 'NYN/NYN201707170',
                 'away_name': 'St. Louis Cardinals',
                 'away_abbr': 'STL'},
                {'home_name': 'Oakland Athletics',
                 'home_abbr': 'OAK',
                 'boxscore': 'OAK/OAK201707170',
                 'away_name': 'Tampa Bay Rays',
                 'away_abbr': 'TBR'},
                {'home_name': 'Pittsburgh Pirates',
                 'home_abbr': 'PIT',
                 'boxscore': 'PIT/PIT201707170',
                 'away_name': 'Milwaukee Brewers',
                 'away_abbr': 'MIL'},
                {'home_name': 'San Francisco Giants',
                 'home_abbr': 'SFG',
                 'boxscore': 'SFN/SFN201707170',
                 'away_name': 'Cleveland Indians',
                 'away_abbr': 'CLE'}
            ]
        }

        result = Boxscores(datetime(2017, 7, 17)).games

        assert result == expected
