import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsreference import utils
from sportsreference.constants import AWAY
from sportsreference.nhl.constants import BOXSCORE_URL, BOXSCORES_URL
from sportsreference.nhl.boxscore import Boxscore, Boxscores


MONTH = 10
YEAR = 2017

BOXSCORE = '201806070VEG'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nhl', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    if url == BOXSCORES_URL % (2, 4, YEAR):
        return MockPQ(read_file('boxscores-2-4-2017.html'))
    if url == BOXSCORES_URL % (2, 5, YEAR):
        return MockPQ(read_file('boxscores-2-5-2017.html'))
    boxscore = read_file('%s.html' % BOXSCORE)
    return MockPQ(boxscore)


class MockDateTime:
    def __init__(self, year, month):
        self.year = year
        self.month = month


class TestNHLBoxscore:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results = {
            'date': 'June 7, 2018',
            'time': '8:00 PM',
            'arena': 'T-Mobile Arena',
            'attendance': 18529,
            'duration': '2:45',
            'winner': AWAY,
            'winning_name': 'Washington Capitals',
            'winning_abbr': 'WSH',
            'losing_name': 'Vegas Golden Knights',
            'losing_abbr': 'VEG',
            'away_goals': 4,
            'away_assists': 7,
            'away_points': 11,
            'away_penalties_in_minutes': 8,
            'away_even_strength_goals': 3,
            'away_power_play_goals': 1,
            'away_short_handed_goals': 0,
            'away_game_winning_goals': 1,
            'away_even_strength_assists': 5,
            'away_power_play_assists': 2,
            'away_short_handed_assists': 0,
            'away_shots_on_goal': 33,
            'away_shooting_percentage': 12.1,
            'away_saves': 28,
            'away_save_percentage': .903,
            'away_shutout': 0,
            'home_goals': 3,
            'home_assists': 6,
            'home_points': 9,
            'home_penalties_in_minutes': 12,
            'home_even_strength_goals': 2,
            'home_power_play_goals': 1,
            'home_short_handed_goals': 0,
            'home_game_winning_goals': 0,
            'home_even_strength_assists': 4,
            'home_power_play_assists': 2,
            'home_short_handed_assists': 0,
            'home_shots_on_goal': 31,
            'home_shooting_percentage': 9.7,
            'home_saves': 29,
            'home_save_percentage': .879,
            'home_shutout': 0
        }

        flexmock(utils) \
            .should_receive('_todays_date') \
            .and_return(MockDateTime(YEAR, MONTH))

        self.boxscore = Boxscore(BOXSCORE)

    def test_nhl_boxscore_returns_requested_boxscore(self):
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

    def test_nhl_boxscore_dataframe_returns_dataframe_of_all_values(self):
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

    def test_nhl_boxscore_player(self):
        boxscore = Boxscore(BOXSCORE)

        assert len(boxscore.home_players) == 19
        assert len(boxscore.away_players) == 19

        for player in boxscore.home_players:
            assert not player.dataframe.empty
        for player in boxscore.away_players:
            assert not player.dataframe.empty


class TestNHLBoxscores:
    def setup_method(self):
        self.expected = {
            '2-4-2017': [
                {'boxscore': '201702040BOS',
                 'away_name': 'Toronto Maple Leafs',
                 'away_abbr': 'TOR',
                 'away_score': 6,
                 'home_name': 'Boston Bruins',
                 'home_abbr': 'BOS',
                 'home_score': 5,
                 'winning_name': 'Toronto Maple Leafs',
                 'winning_abbr': 'TOR',
                 'losing_name': 'Boston Bruins',
                 'losing_abbr': 'BOS'},
                {'boxscore': '201702040BUF',
                 'away_name': 'Ottawa Senators',
                 'away_abbr': 'OTT',
                 'away_score': 0,
                 'home_name': 'Buffalo Sabres',
                 'home_abbr': 'BUF',
                 'home_score': 4,
                 'winning_name': 'Buffalo Sabres',
                 'winning_abbr': 'BUF',
                 'losing_name': 'Ottawa Senators',
                 'losing_abbr': 'OTT'},
                {'boxscore': '201702040CBJ',
                 'away_name': 'New Jersey Devils',
                 'away_abbr': 'NJD',
                 'away_score': 5,
                 'home_name': 'Columbus Blue Jackets',
                 'home_abbr': 'CBJ',
                 'home_score': 1,
                 'winning_name': 'New Jersey Devils',
                 'winning_abbr': 'NJD',
                 'losing_name': 'Columbus Blue Jackets',
                 'losing_abbr': 'CBJ'},
                {'boxscore': '201702040COL',
                 'away_name': 'Winnipeg Jets',
                 'away_abbr': 'WPG',
                 'away_score': 2,
                 'home_name': 'Colorado Avalanche',
                 'home_abbr': 'COL',
                 'home_score': 5,
                 'winning_name': 'Colorado Avalanche',
                 'winning_abbr': 'COL',
                 'losing_name': 'Winnipeg Jets',
                 'losing_abbr': 'WPG'},
                {'boxscore': '201702040DAL',
                 'away_name': 'Chicago Blackhawks',
                 'away_abbr': 'CHI',
                 'away_score': 5,
                 'home_name': 'Dallas Stars',
                 'home_abbr': 'DAL',
                 'home_score': 3,
                 'winning_name': 'Chicago Blackhawks',
                 'winning_abbr': 'CHI',
                 'losing_name': 'Dallas Stars',
                 'losing_abbr': 'DAL'},
                {'boxscore': '201702040MTL',
                 'away_name': 'Washington Capitals',
                 'away_abbr': 'WSH',
                 'away_score': 3,
                 'home_name': 'Montreal Canadiens',
                 'home_abbr': 'MTL',
                 'home_score': 2,
                 'winning_name': 'Washington Capitals',
                 'winning_abbr': 'WSH',
                 'losing_name': 'Montreal Canadiens',
                 'losing_abbr': 'MTL'},
                {'boxscore': '201702040NSH',
                 'away_name': 'Detroit Red Wings',
                 'away_abbr': 'DET',
                 'away_score': 1,
                 'home_name': 'Nashville Predators',
                 'home_abbr': 'NSH',
                 'home_score': 0,
                 'winning_name': 'Detroit Red Wings',
                 'winning_abbr': 'DET',
                 'losing_name': 'Nashville Predators',
                 'losing_abbr': 'NSH'},
                {'boxscore': '201702040NYI',
                 'away_name': 'Carolina Hurricanes',
                 'away_abbr': 'CAR',
                 'away_score': 5,
                 'home_name': 'New York Islanders',
                 'home_abbr': 'NYI',
                 'home_score': 4,
                 'winning_name': 'Carolina Hurricanes',
                 'winning_abbr': 'CAR',
                 'losing_name': 'New York Islanders',
                 'losing_abbr': 'NYI'},
                {'boxscore': '201702040PHI',
                 'away_name': 'Los Angeles Kings',
                 'away_abbr': 'LAK',
                 'away_score': 1,
                 'home_name': 'Philadelphia Flyers',
                 'home_abbr': 'PHI',
                 'home_score': 0,
                 'winning_name': 'Los Angeles Kings',
                 'winning_abbr': 'LAK',
                 'losing_name': 'Philadelphia Flyers',
                 'losing_abbr': 'PHI'},
                {'boxscore': '201702040SJS',
                 'away_name': 'Arizona Coyotes',
                 'away_abbr': 'ARI',
                 'away_score': 3,
                 'home_name': 'San Jose Sharks',
                 'home_abbr': 'SJS',
                 'home_score': 2,
                 'winning_name': 'Arizona Coyotes',
                 'winning_abbr': 'ARI',
                 'losing_name': 'San Jose Sharks',
                 'losing_abbr': 'SJS'},
                {'boxscore': '201702040STL',
                 'away_name': 'Pittsburgh Penguins',
                 'away_abbr': 'PIT',
                 'away_score': 4,
                 'home_name': 'St. Louis Blues',
                 'home_abbr': 'STL',
                 'home_score': 1,
                 'winning_name': 'Pittsburgh Penguins',
                 'winning_abbr': 'PIT',
                 'losing_name': 'St. Louis Blues',
                 'losing_abbr': 'STL'},
                {'boxscore': '201702040TBL',
                 'away_name': 'Anaheim Ducks',
                 'away_abbr': 'ANA',
                 'away_score': 2,
                 'home_name': 'Tampa Bay Lightning',
                 'home_abbr': 'TBL',
                 'home_score': 3,
                 'winning_name': 'Tampa Bay Lightning',
                 'winning_abbr': 'TBL',
                 'losing_name': 'Anaheim Ducks',
                 'losing_abbr': 'ANA'},
                {'boxscore': '201702040VAN',
                 'away_name': 'Minnesota Wild',
                 'away_abbr': 'MIN',
                 'away_score': 6,
                 'home_name': 'Vancouver Canucks',
                 'home_abbr': 'VAN',
                 'home_score': 3,
                 'winning_name': 'Minnesota Wild',
                 'winning_abbr': 'MIN',
                 'losing_name': 'Vancouver Canucks',
                 'losing_abbr': 'VAN'}
            ]
        }

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        result = Boxscores(datetime(2017, 2, 4)).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_invalid_end(self, *args, **kwargs):
        result = Boxscores(datetime(2017, 2, 4), datetime(2017, 2, 3)).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_multiple_days(self, *args, **kwargs):
        expected = {
            '2-4-2017': [
                {'boxscore': '201702040BOS',
                 'away_name': 'Toronto Maple Leafs',
                 'away_abbr': 'TOR',
                 'away_score': 6,
                 'home_name': 'Boston Bruins',
                 'home_abbr': 'BOS',
                 'home_score': 5,
                 'winning_name': 'Toronto Maple Leafs',
                 'winning_abbr': 'TOR',
                 'losing_name': 'Boston Bruins',
                 'losing_abbr': 'BOS'},
                {'boxscore': '201702040BUF',
                 'away_name': 'Ottawa Senators',
                 'away_abbr': 'OTT',
                 'away_score': 0,
                 'home_name': 'Buffalo Sabres',
                 'home_abbr': 'BUF',
                 'home_score': 4,
                 'winning_name': 'Buffalo Sabres',
                 'winning_abbr': 'BUF',
                 'losing_name': 'Ottawa Senators',
                 'losing_abbr': 'OTT'},
                {'boxscore': '201702040CBJ',
                 'away_name': 'New Jersey Devils',
                 'away_abbr': 'NJD',
                 'away_score': 5,
                 'home_name': 'Columbus Blue Jackets',
                 'home_abbr': 'CBJ',
                 'home_score': 1,
                 'winning_name': 'New Jersey Devils',
                 'winning_abbr': 'NJD',
                 'losing_name': 'Columbus Blue Jackets',
                 'losing_abbr': 'CBJ'},
                {'boxscore': '201702040COL',
                 'away_name': 'Winnipeg Jets',
                 'away_abbr': 'WPG',
                 'away_score': 2,
                 'home_name': 'Colorado Avalanche',
                 'home_abbr': 'COL',
                 'home_score': 5,
                 'winning_name': 'Colorado Avalanche',
                 'winning_abbr': 'COL',
                 'losing_name': 'Winnipeg Jets',
                 'losing_abbr': 'WPG'},
                {'boxscore': '201702040DAL',
                 'away_name': 'Chicago Blackhawks',
                 'away_abbr': 'CHI',
                 'away_score': 5,
                 'home_name': 'Dallas Stars',
                 'home_abbr': 'DAL',
                 'home_score': 3,
                 'winning_name': 'Chicago Blackhawks',
                 'winning_abbr': 'CHI',
                 'losing_name': 'Dallas Stars',
                 'losing_abbr': 'DAL'},
                {'boxscore': '201702040MTL',
                 'away_name': 'Washington Capitals',
                 'away_abbr': 'WSH',
                 'away_score': 3,
                 'home_name': 'Montreal Canadiens',
                 'home_abbr': 'MTL',
                 'home_score': 2,
                 'winning_name': 'Washington Capitals',
                 'winning_abbr': 'WSH',
                 'losing_name': 'Montreal Canadiens',
                 'losing_abbr': 'MTL'},
                {'boxscore': '201702040NSH',
                 'away_name': 'Detroit Red Wings',
                 'away_abbr': 'DET',
                 'away_score': 1,
                 'home_name': 'Nashville Predators',
                 'home_abbr': 'NSH',
                 'home_score': 0,
                 'winning_name': 'Detroit Red Wings',
                 'winning_abbr': 'DET',
                 'losing_name': 'Nashville Predators',
                 'losing_abbr': 'NSH'},
                {'boxscore': '201702040NYI',
                 'away_name': 'Carolina Hurricanes',
                 'away_abbr': 'CAR',
                 'away_score': 5,
                 'home_name': 'New York Islanders',
                 'home_abbr': 'NYI',
                 'home_score': 4,
                 'winning_name': 'Carolina Hurricanes',
                 'winning_abbr': 'CAR',
                 'losing_name': 'New York Islanders',
                 'losing_abbr': 'NYI'},
                {'boxscore': '201702040PHI',
                 'away_name': 'Los Angeles Kings',
                 'away_abbr': 'LAK',
                 'away_score': 1,
                 'home_name': 'Philadelphia Flyers',
                 'home_abbr': 'PHI',
                 'home_score': 0,
                 'winning_name': 'Los Angeles Kings',
                 'winning_abbr': 'LAK',
                 'losing_name': 'Philadelphia Flyers',
                 'losing_abbr': 'PHI'},
                {'boxscore': '201702040SJS',
                 'away_name': 'Arizona Coyotes',
                 'away_abbr': 'ARI',
                 'away_score': 3,
                 'home_name': 'San Jose Sharks',
                 'home_abbr': 'SJS',
                 'home_score': 2,
                 'winning_name': 'Arizona Coyotes',
                 'winning_abbr': 'ARI',
                 'losing_name': 'San Jose Sharks',
                 'losing_abbr': 'SJS'},
                {'boxscore': '201702040STL',
                 'away_name': 'Pittsburgh Penguins',
                 'away_abbr': 'PIT',
                 'away_score': 4,
                 'home_name': 'St. Louis Blues',
                 'home_abbr': 'STL',
                 'home_score': 1,
                 'winning_name': 'Pittsburgh Penguins',
                 'winning_abbr': 'PIT',
                 'losing_name': 'St. Louis Blues',
                 'losing_abbr': 'STL'},
                {'boxscore': '201702040TBL',
                 'away_name': 'Anaheim Ducks',
                 'away_abbr': 'ANA',
                 'away_score': 2,
                 'home_name': 'Tampa Bay Lightning',
                 'home_abbr': 'TBL',
                 'home_score': 3,
                 'winning_name': 'Tampa Bay Lightning',
                 'winning_abbr': 'TBL',
                 'losing_name': 'Anaheim Ducks',
                 'losing_abbr': 'ANA'},
                {'boxscore': '201702040VAN',
                 'away_name': 'Minnesota Wild',
                 'away_abbr': 'MIN',
                 'away_score': 6,
                 'home_name': 'Vancouver Canucks',
                 'home_abbr': 'VAN',
                 'home_score': 3,
                 'winning_name': 'Minnesota Wild',
                 'winning_abbr': 'MIN',
                 'losing_name': 'Vancouver Canucks',
                 'losing_abbr': 'VAN'}
            ],
            '2-5-2017': [
                {'boxscore': '201702050MTL',
                 'away_name': 'Edmonton Oilers',
                 'away_abbr': 'EDM',
                 'away_score': 1,
                 'home_name': 'Montreal Canadiens',
                 'home_abbr': 'MTL',
                 'home_score': 0,
                 'winning_name': 'Edmonton Oilers',
                 'winning_abbr': 'EDM',
                 'losing_name': 'Montreal Canadiens',
                 'losing_abbr': 'MTL'},
                {'boxscore': '201702050NYR',
                 'away_name': 'Calgary Flames',
                 'away_abbr': 'CGY',
                 'away_score': 3,
                 'home_name': 'New York Rangers',
                 'home_abbr': 'NYR',
                 'home_score': 4,
                 'winning_name': 'New York Rangers',
                 'winning_abbr': 'NYR',
                 'losing_name': 'Calgary Flames',
                 'losing_abbr': 'CGY'},
                {'boxscore': '201702050WSH',
                 'away_name': 'Los Angeles Kings',
                 'away_abbr': 'LAK',
                 'away_score': 0,
                 'home_name': 'Washington Capitals',
                 'home_abbr': 'WSH',
                 'home_score': 5,
                 'winning_name': 'Washington Capitals',
                 'winning_abbr': 'WSH',
                 'losing_name': 'Los Angeles Kings',
                 'losing_abbr': 'LAK'}
            ]
        }
        result = Boxscores(datetime(2017, 2, 4), datetime(2017, 2, 5)).games

        assert result == expected
