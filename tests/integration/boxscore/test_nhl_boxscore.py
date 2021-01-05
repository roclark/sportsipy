import mock
import os
import pandas as pd
from datetime import datetime
from flexmock import flexmock
from sportsipy import utils
from sportsipy.constants import AWAY
from sportsipy.nhl.constants import BOXSCORE_URL, BOXSCORES_URL
from sportsipy.nhl.boxscore import Boxscore, Boxscores


MONTH = 10
YEAR = 2020

BOXSCORE = '202003040VAN'


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'nhl', filename)
    return open('%s' % filepath, 'r', encoding='utf8').read()


def mock_pyquery(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 200
            self.html_contents = html_contents
            self.text = html_contents

    if url == BOXSCORES_URL % (3, 4, YEAR):
        return MockPQ(read_file('boxscores-3-4-2020.html'))
    if url == BOXSCORES_URL % (3, 5, YEAR):
        return MockPQ(read_file('boxscores-3-5-2020.html'))
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
            'date': 'March 4, 2020',
            'time': '10:30 PM',
            'arena': 'Rogers Arena',
            'attendance': 17363,
            'duration': '2:30',
            'winner': AWAY,
            'winning_name': 'Arizona Coyotes',
            'winning_abbr': 'ARI',
            'losing_name': 'Vancouver Canucks',
            'losing_abbr': 'VAN',
            'away_goals': 4,
            'away_assists': 5,
            'away_points': 9,
            'away_penalties_in_minutes': 6,
            'away_even_strength_goals': 3,
            'away_power_play_goals': 1,
            'away_short_handed_goals': 0,
            'away_game_winning_goals': 1,
            'away_even_strength_assists': 5,
            'away_power_play_assists': 0,
            'away_short_handed_assists': 0,
            'away_shots_on_goal': 40,
            'away_shooting_percentage': 10.0,
            'away_saves': 36,
            'away_save_percentage': .947,
            'away_shutout': 0,
            'home_goals': 2,
            'home_assists': 3,
            'home_points': 5,
            'home_penalties_in_minutes': 6,
            'home_even_strength_goals': 1,
            'home_power_play_goals': 1,
            'home_short_handed_goals': 0,
            'home_game_winning_goals': 0,
            'home_even_strength_assists': 1,
            'home_power_play_assists': 2,
            'home_short_handed_assists': 0,
            'home_shots_on_goal': 38,
            'home_shooting_percentage': 5.3,
            'home_saves': 36,
            'home_save_percentage': .9,
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

    def test_nhl_boxscore_string_representation(self):
        expected = ('Boxscore for Arizona Coyotes at Vancouver Canucks '
                    '(March 4, 2020)')

        boxscore = Boxscore(BOXSCORE)

        assert boxscore.__repr__() == expected


class TestNHLBoxscores:
    def setup_method(self):
        self.expected = {
            '3-4-2020': [
                {'boxscore': '202003040CGY',
                 'away_name': 'Columbus Blue Jackets',
                 'away_abbr': 'CBJ',
                 'away_score': 2,
                 'home_name': 'Calgary Flames',
                 'home_abbr': 'CGY',
                 'home_score': 3,
                 'winning_name': 'Calgary Flames',
                 'winning_abbr': 'CGY',
                 'losing_name': 'Columbus Blue Jackets',
                 'losing_abbr': 'CBJ'},
                {'boxscore': '202003040COL',
                 'away_name': 'Anaheim Ducks',
                 'away_abbr': 'ANA',
                 'away_score': 4,
                 'home_name': 'Colorado Avalanche',
                 'home_abbr': 'COL',
                 'home_score': 3,
                 'winning_name': 'Anaheim Ducks',
                 'winning_abbr': 'ANA',
                 'losing_name': 'Colorado Avalanche',
                 'losing_abbr': 'COL'},
                {'boxscore': '202003040VAN',
                 'away_name': 'Arizona Coyotes',
                 'away_abbr': 'ARI',
                 'away_score': 4,
                 'home_name': 'Vancouver Canucks',
                 'home_abbr': 'VAN',
                 'home_score': 2,
                 'winning_name': 'Arizona Coyotes',
                 'winning_abbr': 'ARI',
                 'losing_name': 'Vancouver Canucks',
                 'losing_abbr': 'VAN'},
                {'boxscore': '202003040WSH',
                 'away_name': 'Philadelphia Flyers',
                 'away_abbr': 'PHI',
                 'away_score': 5,
                 'home_name': 'Washington Capitals',
                 'home_abbr': 'WSH',
                 'home_score': 2,
                 'winning_name': 'Philadelphia Flyers',
                 'winning_abbr': 'PHI',
                 'losing_name': 'Washington Capitals',
                 'losing_abbr': 'WSH'}
            ]
        }

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 3, 4)).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_invalid_end(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 3, 4), datetime(2020, 3, 3)).games

        assert result == self.expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_multiple_days(self, *args, **kwargs):
        expected = {
            '3-4-2020': [
                {'boxscore': '202003040CGY',
                 'away_name': 'Columbus Blue Jackets',
                 'away_abbr': 'CBJ',
                 'away_score': 2,
                 'home_name': 'Calgary Flames',
                 'home_abbr': 'CGY',
                 'home_score': 3,
                 'winning_name': 'Calgary Flames',
                 'winning_abbr': 'CGY',
                 'losing_name': 'Columbus Blue Jackets',
                 'losing_abbr': 'CBJ'},
                {'boxscore': '202003040COL',
                 'away_name': 'Anaheim Ducks',
                 'away_abbr': 'ANA',
                 'away_score': 4,
                 'home_name': 'Colorado Avalanche',
                 'home_abbr': 'COL',
                 'home_score': 3,
                 'winning_name': 'Anaheim Ducks',
                 'winning_abbr': 'ANA',
                 'losing_name': 'Colorado Avalanche',
                 'losing_abbr': 'COL'},
                {'boxscore': '202003040VAN',
                 'away_name': 'Arizona Coyotes',
                 'away_abbr': 'ARI',
                 'away_score': 4,
                 'home_name': 'Vancouver Canucks',
                 'home_abbr': 'VAN',
                 'home_score': 2,
                 'winning_name': 'Arizona Coyotes',
                 'winning_abbr': 'ARI',
                 'losing_name': 'Vancouver Canucks',
                 'losing_abbr': 'VAN'},
                {'boxscore': '202003040WSH',
                 'away_name': 'Philadelphia Flyers',
                 'away_abbr': 'PHI',
                 'away_score': 5,
                 'home_name': 'Washington Capitals',
                 'home_abbr': 'WSH',
                 'home_score': 2,
                 'winning_name': 'Philadelphia Flyers',
                 'winning_abbr': 'PHI',
                 'losing_name': 'Washington Capitals',
                 'losing_abbr': 'WSH'}
            ],
            '3-5-2020': [
                {'boxscore': '202003050BUF',
                 'away_name': 'Pittsburgh Penguins',
                 'away_abbr': 'PIT',
                 'away_score': 4,
                 'home_name': 'Buffalo Sabres',
                 'home_abbr': 'BUF',
                 'home_score': 2,
                 'winning_name': 'Pittsburgh Penguins',
                 'winning_abbr': 'PIT',
                 'losing_name': 'Buffalo Sabres',
                 'losing_abbr': 'BUF'},
                {'boxscore': '202003050CHI',
                 'away_name': 'Edmonton Oilers',
                 'away_abbr': 'EDM',
                 'away_score': 3,
                 'home_name': 'Chicago Blackhawks',
                 'home_abbr': 'CHI',
                 'home_score': 4,
                 'winning_name': 'Chicago Blackhawks',
                 'winning_abbr': 'CHI',
                 'losing_name': 'Edmonton Oilers',
                 'losing_abbr': 'EDM'},
                {'boxscore': '202003050FLA',
                 'away_name': 'Boston Bruins',
                 'away_abbr': 'BOS',
                 'away_score': 2,
                 'home_name': 'Florida Panthers',
                 'home_abbr': 'FLA',
                 'home_score': 1,
                 'winning_name': 'Boston Bruins',
                 'winning_abbr': 'BOS',
                 'losing_name': 'Florida Panthers',
                 'losing_abbr': 'FLA'},
                {'boxscore': '202003050LAK',
                 'away_name': 'Toronto Maple Leafs',
                 'away_abbr': 'TOR',
                 'away_score': 0,
                 'home_name': 'Los Angeles Kings',
                 'home_abbr': 'LAK',
                 'home_score': 1,
                 'winning_name': 'Los Angeles Kings',
                 'winning_abbr': 'LAK',
                 'losing_name': 'Toronto Maple Leafs',
                 'losing_abbr': 'TOR'},
                {'boxscore': '202003050NSH',
                 'away_name': 'Dallas Stars',
                 'away_abbr': 'DAL',
                 'away_score': 0,
                 'home_name': 'Nashville Predators',
                 'home_abbr': 'NSH',
                 'home_score': 2,
                 'winning_name': 'Nashville Predators',
                 'winning_abbr': 'NSH',
                 'losing_name': 'Dallas Stars',
                 'losing_abbr': 'DAL'},
                {'boxscore': '202003050NYR',
                 'away_name': 'Washington Capitals',
                 'away_abbr': 'WSH',
                 'away_score': 5,
                 'home_name': 'New York Rangers',
                 'home_abbr': 'NYR',
                 'home_score': 6,
                 'winning_name': 'New York Rangers',
                 'winning_abbr': 'NYR',
                 'losing_name': 'Washington Capitals',
                 'losing_abbr': 'WSH'},
                {'boxscore': '202003050OTT',
                 'away_name': 'New York Islanders',
                 'away_abbr': 'NYI',
                 'away_score': 3,
                 'home_name': 'Ottawa Senators',
                 'home_abbr': 'OTT',
                 'home_score': 4,
                 'winning_name': 'Ottawa Senators',
                 'winning_abbr': 'OTT',
                 'losing_name': 'New York Islanders',
                 'losing_abbr': 'NYI'},
                {'boxscore': '202003050PHI',
                 'away_name': 'Carolina Hurricanes',
                 'away_abbr': 'CAR',
                 'away_score': 1,
                 'home_name': 'Philadelphia Flyers',
                 'home_abbr': 'PHI',
                 'home_score': 4,
                 'winning_name': 'Philadelphia Flyers',
                 'winning_abbr': 'PHI',
                 'losing_name': 'Carolina Hurricanes',
                 'losing_abbr': 'CAR'},
                {'boxscore': '202003050SJS',
                 'away_name': 'Minnesota Wild',
                 'away_abbr': 'MIN',
                 'away_score': 3,
                 'home_name': 'San Jose Sharks',
                 'home_abbr': 'SJS',
                 'home_score': 2,
                 'winning_name': 'Minnesota Wild',
                 'winning_abbr': 'MIN',
                 'losing_name': 'San Jose Sharks',
                 'losing_abbr': 'SJS'},
                {'boxscore': '202003050TBL',
                 'away_name': 'Montreal Canadiens',
                 'away_abbr': 'MTL',
                 'away_score': 0,
                 'home_name': 'Tampa Bay Lightning',
                 'home_abbr': 'TBL',
                 'home_score': 4,
                 'winning_name': 'Tampa Bay Lightning',
                 'winning_abbr': 'TBL',
                 'losing_name': 'Montreal Canadiens',
                 'losing_abbr': 'MTL'}
            ]
        }
        result = Boxscores(datetime(2020, 3, 4), datetime(2020, 3, 5)).games

        assert result == expected

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_boxscores_search_string_representation(self, *args, **kwargs):
        result = Boxscores(datetime(2020, 3, 4))

        assert result.__repr__() == 'NHL games for 3-4-2020'
