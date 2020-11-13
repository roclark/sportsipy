import mock
import os
import pandas as pd
import pytest
from datetime import datetime
from flexmock import flexmock
from sportsipy import utils
from sportsipy.constants import AWAY, LOSS
from sportsipy.nhl.boxscore import Boxscore
from sportsipy.nhl.constants import SCHEDULE_URL
from sportsipy.nhl.schedule import Schedule


MONTH = 1
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 82


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nhl', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

        def __call__(self, div):
            return read_file('table.html')

    schedule = read_file('%s_gamelog.html' % YEAR)
    return MockPQ(schedule)


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


class TestNHLSchedule:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'game': 2,
            'boxscore_index': '201610150STL',
            'date': '2016-10-15',
            'datetime': datetime(2016, 10, 15),
            'location': AWAY,
            'opponent_abbr': 'STL',
            'opponent_name': 'St. Louis Blues',
            'goals_scored': 2,
            'goals_allowed': 3,
            'result': LOSS,
            'overtime': 0,
            'shots_on_goal': 35,
            'penalties_in_minutes': 8,
            'power_play_goals': 0,
            'power_play_opportunities': 2,
            'short_handed_goals': 0,
            'opp_shots_on_goal': 18,
            'opp_penalties_in_minutes': 4,
            'opp_power_play_goals': 1,
            'opp_power_play_opportunities': 5,
            'opp_short_handed_goals': 0,
            'corsi_for': 54,
            'corsi_against': 23,
            'corsi_for_percentage': 70.1,
            'fenwick_for': 41,
            'fenwick_against': 18,
            'fenwick_for_percentage': 69.5,
            'faceoff_wins': 29,
            'faceoff_losses': 18,
            'faceoff_win_percentage': 61.7,
            'offensive_zone_start_percentage': 55.2,
            'pdo': 92.4
        }
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)
        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))

        self.schedule = Schedule('NYR')

    def test_nhl_schedule_returns_correct_number_of_games(self):
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_nhl_schedule_returns_requested_match_from_index(self):
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nhl_schedule_returns_requested_match_from_date(self):
        match_two = self.schedule(datetime(2016, 10, 15))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nhl_schedule_dataframe_returns_dataframe(self):
        df = pd.DataFrame([self.results], index=['NYR'])

        match_two = self.schedule[1]
        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected one above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, match_two.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nhl_schedule_dataframe_extended_returns_dataframe(self):
        df = pd.DataFrame([{'key': 'value'}])

        result = self.schedule[1].dataframe_extended

        frames = [df, result]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nhl_schedule_all_dataframe_returns_dataframe(self):
        result = self.schedule.dataframe.drop_duplicates(keep=False)

        assert len(result) == NUM_GAMES_IN_SCHEDULE
        assert set(result.columns.values) == set(self.results.keys())

    def test_nhl_schedule_all_dataframe_extended_returns_dataframe(self):
        result = self.schedule.dataframe_extended

        assert len(result) == NUM_GAMES_IN_SCHEDULE

    def test_no_games_for_date_raises_value_error(self):
        with pytest.raises(ValueError):
            self.schedule(datetime.now())

    def test_empty_page_return_no_games(self):
        flexmock(utils) \
            .should_receive('_no_data_found') \
            .once()
        flexmock(utils) \
            .should_receive('_get_stats_table') \
            .and_return(None)

        schedule = Schedule('NYR')

        assert len(schedule) == 0

    def test_game_string_representation(self):
        game = self.schedule[0]

        assert game.__repr__() == '2016-10-13 - NYI'

    def test_schedule_string_representation(self):
        expected = """2016-10-13 - NYI
2016-10-15 - STL
2016-10-17 - SJS
2016-10-19 - DET
2016-10-22 - WSH
2016-10-23 - ARI
2016-10-26 - BOS
2016-10-28 - CAR
2016-10-30 - TBL
2016-11-01 - STL
2016-11-03 - EDM
2016-11-05 - BOS
2016-11-06 - WPG
2016-11-08 - VAN
2016-11-12 - CGY
2016-11-13 - EDM
2016-11-15 - VAN
2016-11-18 - CBJ
2016-11-20 - FLA
2016-11-21 - PIT
2016-11-23 - PIT
2016-11-25 - PHI
2016-11-27 - OTT
2016-11-29 - CAR
2016-12-01 - BUF
2016-12-03 - CAR
2016-12-06 - NYI
2016-12-08 - WPG
2016-12-09 - CHI
2016-12-11 - NJD
2016-12-13 - CHI
2016-12-15 - DAL
2016-12-17 - NSH
2016-12-18 - NJD
2016-12-20 - PIT
2016-12-23 - MIN
2016-12-27 - OTT
2016-12-29 - ARI
2016-12-31 - COL
2017-01-03 - BUF
2017-01-04 - PHI
2017-01-07 - CBJ
2017-01-13 - TOR
2017-01-14 - MTL
2017-01-17 - DAL
2017-01-19 - TOR
2017-01-22 - DET
2017-01-23 - LAK
2017-01-25 - PHI
2017-01-31 - CBJ
2017-02-02 - BUF
2017-02-05 - CGY
2017-02-07 - ANA
2017-02-09 - NSH
2017-02-11 - COL
2017-02-13 - CBJ
2017-02-16 - NYI
2017-02-19 - WSH
2017-02-21 - MTL
2017-02-23 - TOR
2017-02-25 - NJD
2017-02-26 - CBJ
2017-02-28 - WSH
2017-03-02 - BOS
2017-03-04 - MTL
2017-03-06 - TBL
2017-03-07 - FLA
2017-03-09 - CAR
2017-03-12 - DET
2017-03-13 - TBL
2017-03-17 - FLA
2017-03-18 - MIN
2017-03-21 - NJD
2017-03-22 - NYI
2017-03-25 - LAK
2017-03-26 - ANA
2017-03-28 - SJS
2017-03-31 - PIT
2017-04-02 - PHI
2017-04-05 - WSH
2017-04-08 - OTT
2017-04-09 - PIT"""

        assert self.schedule.__repr__() == expected


class TestNHLScheduleInvalidYear:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_default_year_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        results = {
            'game': 2,
            'boxscore_index': '201610150STL',
            'date': '2016-10-15',
            'datetime': datetime(2016, 10, 15),
            'location': AWAY,
            'opponent_abbr': 'STL',
            'opponent_name': 'St. Louis Blues',
            'goals_scored': 2,
            'goals_allowed': 3,
            'result': LOSS,
            'overtime': 0,
            'shots_on_goal': 35,
            'penalties_in_minutes': 8,
            'power_play_goals': 0,
            'power_play_opportunities': 2,
            'short_handed_goals': 0,
            'opp_shots_on_goal': 18,
            'opp_penalties_in_minutes': 4,
            'opp_power_play_goals': 1,
            'opp_power_play_opportunities': 5,
            'opp_short_handed_goals': 0,
            'corsi_for': 54,
            'corsi_against': 23,
            'corsi_for_percentage': 70.1,
            'fenwick_for': 41,
            'fenwick_against': 18,
            'fenwick_for_percentage': 69.5,
            'faceoff_wins': 29,
            'faceoff_losses': 18,
            'faceoff_win_percentage': 61.7,
            'offensive_zone_start_percentage': 55.2,
            'pdo': 92.4
        }
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2018)
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)
        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))
        schedule = Schedule('NYR')

        for attribute, value in results.items():
            assert getattr(schedule[1], attribute) == value
