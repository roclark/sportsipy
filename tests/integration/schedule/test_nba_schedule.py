import mock
import os
import pandas as pd
import pytest
from datetime import datetime
from flexmock import flexmock
from sportsipy import utils
from sportsipy.constants import AWAY, WIN
from sportsipy.nba.boxscore import Boxscore
from sportsipy.nba.constants import SCHEDULE_URL
from sportsipy.nba.schedule import Schedule


MONTH = 1
YEAR = 2017

NUM_GAMES_IN_SCHEDULE = 99


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nba', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents, status_code=200):
            self.status_code = status_code
            self.html_contents = html_contents
            self.text = html_contents
            self.url = url
            self.reason = 'Invalid'
            self.headers = {}

        def __call__(self, div):
            if 'playoff' in div:
                return read_file('playoff.html')
            return read_file('table.html')

    schedule = read_file('%s_games.html' % YEAR)
    if '2021' in url:
        return MockPQ(schedule, status_code=404)
    if '2020' in url:
        return MockPQ(schedule)
    else:
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


class TestNBASchedule:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'game': 2,
            'boxscore_index': '201610280NOP',
            'date': 'Fri, Oct 28, 2016',
            'time': '9:30p',
            'datetime': datetime(2016, 10, 28),
            'location': AWAY,
            'opponent_abbr': 'NOP',
            'opponent_name': 'New Orleans Pelicans',
            'result': WIN,
            'playoffs': False,
            'points_scored': 122,
            'points_allowed': 114,
            'wins': 1,
            'losses': 1,
            'streak': 'W 1'
        }
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)
        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))
        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.schedule = Schedule('GSW')

    def test_nba_schedule_returns_correct_number_of_games(self):
        assert len(self.schedule) == NUM_GAMES_IN_SCHEDULE

    def test_nba_schedule_returns_requested_match_from_index(self):
        match_two = self.schedule[1]

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nba_schedule_returns_requested_match_from_date(self):
        match_two = self.schedule(datetime(2016, 10, 28))

        for attribute, value in self.results.items():
            assert getattr(match_two, attribute) == value

    def test_nba_schedule_dataframe_returns_dataframe(self):
        df = pd.DataFrame([self.results], index=['PHO'])

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

    def test_nba_schedule_dataframe_extended_returns_dataframe(self):
        df = pd.DataFrame([{'key': 'value'}])

        result = self.schedule[1].dataframe_extended

        frames = [df, result]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

        assert df1.empty

    def test_nba_schedule_all_dataframe_returns_dataframe(self):
        result = self.schedule.dataframe.drop_duplicates(keep=False)

        assert len(result) == NUM_GAMES_IN_SCHEDULE
        assert set(result.columns.values) == set(self.results.keys())

    def test_nba_schedule_all_dataframe_extended_returns_dataframe(self):
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

        schedule = Schedule('GSW')

        assert len(schedule) == 0

    def test_game_string_representation(self):
        game = self.schedule[0]

        assert game.__repr__() == 'Tue, Oct 25, 2016 - SAS'

    def test_schedule_string_representation(self):
        expected = """Tue, Oct 25, 2016 - SAS
Fri, Oct 28, 2016 - NOP
Sun, Oct 30, 2016 - PHO
Tue, Nov 1, 2016 - POR
Thu, Nov 3, 2016 - OKC
Fri, Nov 4, 2016 - LAL
Mon, Nov 7, 2016 - NOP
Wed, Nov 9, 2016 - DAL
Thu, Nov 10, 2016 - DEN
Sun, Nov 13, 2016 - PHO
Wed, Nov 16, 2016 - TOR
Fri, Nov 18, 2016 - BOS
Sat, Nov 19, 2016 - MIL
Mon, Nov 21, 2016 - IND
Wed, Nov 23, 2016 - LAL
Fri, Nov 25, 2016 - LAL
Sat, Nov 26, 2016 - MIN
Mon, Nov 28, 2016 - ATL
Thu, Dec 1, 2016 - HOU
Sat, Dec 3, 2016 - PHO
Mon, Dec 5, 2016 - IND
Wed, Dec 7, 2016 - LAC
Thu, Dec 8, 2016 - UTA
Sat, Dec 10, 2016 - MEM
Sun, Dec 11, 2016 - MIN
Tue, Dec 13, 2016 - NOP
Thu, Dec 15, 2016 - NYK
Sat, Dec 17, 2016 - POR
Tue, Dec 20, 2016 - UTA
Thu, Dec 22, 2016 - BRK
Fri, Dec 23, 2016 - DET
Sun, Dec 25, 2016 - CLE
Wed, Dec 28, 2016 - TOR
Fri, Dec 30, 2016 - DAL
Mon, Jan 2, 2017 - DEN
Wed, Jan 4, 2017 - POR
Fri, Jan 6, 2017 - MEM
Sun, Jan 8, 2017 - SAC
Tue, Jan 10, 2017 - MIA
Thu, Jan 12, 2017 - DET
Mon, Jan 16, 2017 - CLE
Wed, Jan 18, 2017 - OKC
Fri, Jan 20, 2017 - HOU
Sun, Jan 22, 2017 - ORL
Mon, Jan 23, 2017 - MIA
Wed, Jan 25, 2017 - CHO
Sat, Jan 28, 2017 - LAC
Sun, Jan 29, 2017 - POR
Wed, Feb 1, 2017 - CHO
Thu, Feb 2, 2017 - LAC
Sat, Feb 4, 2017 - SAC
Wed, Feb 8, 2017 - CHI
Fri, Feb 10, 2017 - MEM
Sat, Feb 11, 2017 - OKC
Mon, Feb 13, 2017 - DEN
Wed, Feb 15, 2017 - SAC
Thu, Feb 23, 2017 - LAC
Sat, Feb 25, 2017 - BRK
Mon, Feb 27, 2017 - PHI
Tue, Feb 28, 2017 - WAS
Thu, Mar 2, 2017 - CHI
Sun, Mar 5, 2017 - NYK
Mon, Mar 6, 2017 - ATL
Wed, Mar 8, 2017 - BOS
Fri, Mar 10, 2017 - MIN
Sat, Mar 11, 2017 - SAS
Tue, Mar 14, 2017 - PHI
Thu, Mar 16, 2017 - ORL
Sat, Mar 18, 2017 - MIL
Mon, Mar 20, 2017 - OKC
Tue, Mar 21, 2017 - DAL
Fri, Mar 24, 2017 - SAC
Sun, Mar 26, 2017 - MEM
Tue, Mar 28, 2017 - HOU
Wed, Mar 29, 2017 - SAS
Fri, Mar 31, 2017 - HOU
Sun, Apr 2, 2017 - WAS
Tue, Apr 4, 2017 - MIN
Wed, Apr 5, 2017 - PHO
Sat, Apr 8, 2017 - NOP
Mon, Apr 10, 2017 - UTA
Wed, Apr 12, 2017 - LAL
Sun, Apr 16, 2017 - POR
Wed, Apr 19, 2017 - POR
Sat, Apr 22, 2017 - POR
Mon, Apr 24, 2017 - POR
Tue, May 2, 2017 - UTA
Thu, May 4, 2017 - UTA
Sat, May 6, 2017 - UTA
Mon, May 8, 2017 - UTA
Sun, May 14, 2017 - SAS
Tue, May 16, 2017 - SAS
Sat, May 20, 2017 - SAS
Mon, May 22, 2017 - SAS
Thu, Jun 1, 2017 - CLE
Sun, Jun 4, 2017 - CLE
Wed, Jun 7, 2017 - CLE
Fri, Jun 9, 2017 - CLE
Mon, Jun 12, 2017 - CLE"""

        assert self.schedule.__repr__() == expected


class TestNBAScheduleInvalidError:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_default_year_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        results = {
            'game': 2,
            'boxscore_index': '201610280NOP',
            'date': 'Fri, Oct 28, 2016',
            'time': '9:30p',
            'datetime': datetime(2016, 10, 28),
            'location': AWAY,
            'opponent_abbr': 'NOP',
            'opponent_name': 'New Orleans Pelicans',
            'result': WIN,
            'points_scored': 122,
            'points_allowed': 114,
            'wins': 1,
            'losses': 1,
            'streak': 'W 1'
        }
        flexmock(Boxscore) \
            .should_receive('_parse_game_data') \
            .and_return(None)
        flexmock(Boxscore) \
            .should_receive('dataframe') \
            .and_return(pd.DataFrame([{'key': 'value'}]))
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2018)

        schedule = Schedule('GSW')

        for attribute, value in results.items():
            assert getattr(schedule[1], attribute) == value

    @mock.patch('requests.get', side_effect=mock_pyquery)
    @mock.patch('requests.head', side_effect=mock_request)
    def test_invalid_2020_default_reverts_to_previous_year(self,
                                                           *args,
                                                           **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return(2021)

        schedule = Schedule('2017')

        assert 'Tue, Oct 25, 2016' in str(schedule)
