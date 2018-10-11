import mock
import os
import pandas as pd
import pytest
from flexmock import flexmock
from sportsreference import utils
from sportsreference.ncaaf.roster import Player, Roster
from sportsreference.ncaaf.teams import Team


def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), 'ncaaf', filename)
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
    if 'brycen-hopkins' in url:
        return MockPQ(read_file('brycen-hopkins-1'))
    if '2018-roster' in url:
        return MockPQ(read_file('2018-roster'))
    return MockPQ(read_file('david-blough-1'))


class TestNCAAFPlayer:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def setup_method(self, *args, **kwargs):
        self.results_career = {
            'adjusted_yards_per_attempt': 6.1,
            'assists_on_tackles': 1,
            'attempted_passes': 1118,
            'completed_passes': 669,
            'extra_points_made': 0,
            'field_goals_made': 0,
            'fumbles_forced': 0,
            'fumbles_recovered': 0,
            'fumbles_recovered_for_touchdown': None,
            'games': None,
            'height': '6-1',
            'interceptions': 0,
            'interceptions_returned_for_touchdown': 0,
            'interceptions_thrown': 34,
            'kickoff_return_touchdowns': 0,
            'name': 'David Blough',
            'other_touchdowns': None,
            'passes_defended': 0,
            'passing_completion': 59.8,
            'passing_touchdowns': 51,
            'passing_yards_per_attempt': 6.6,
            'player_id': 'david-blough-1',
            'plays_from_scrimmage': 222,
            'points': 72,
            'position': '',
            'punt_return_touchdowns': 0,
            'quarterback_rating': 124.0,
            'receiving_touchdowns': 0,
            'receiving_yards': 41,
            'receiving_yards_per_reception': 13.7,
            'receptions': 3,
            'rush_attempts': 219,
            'rush_touchdowns': 12,
            'rush_yards': 275,
            'rush_yards_per_attempt': 1.3,
            'rushing_and_receiving_touchdowns': 12,
            'sacks': 0.0,
            'safeties': None,
            'season': 'Career',
            'solo_tackles': 1,
            'tackles_for_loss': 0.0,
            'team_abbreviation': 'purdue',
            'total_tackles': 2,
            'total_touchdowns': 12,
            'two_point_conversions': None,
            'weight': 205,
            'yards_from_scrimmage': 316,
            'yards_from_scrimmage_per_play': 1.4,
            'yards_recovered_from_fumble': None,
            'yards_returned_from_interceptions': 0,
            'yards_returned_per_interception': None,
            'year': ''
        }

        self.results_2017 = {
            'adjusted_yards_per_attempt': 7.0,
            'assists_on_tackles': 1,
            'attempted_passes': 157,
            'completed_passes': 102,
            'extra_points_made': 0,
            'field_goals_made': 0,
            'fumbles_forced': 0,
            'fumbles_recovered': 0,
            'fumbles_recovered_for_touchdown': None,
            'games': 9,
            'height': '6-1',
            'interceptions': 0,
            'interceptions_returned_for_touchdown': 0,
            'interceptions_thrown': 4,
            'kickoff_return_touchdowns': 0,
            'name': 'David Blough',
            'other_touchdowns': None,
            'passes_defended': 0,
            'passing_completion': 65.0,
            'passing_touchdowns': 9,
            'passing_yards_per_attempt': 7.0,
            'player_id': 'david-blough-1',
            'plays_from_scrimmage': 43,
            'points': 12,
            'position': 'QB',
            'punt_return_touchdowns': 0,
            'quarterback_rating': 137.8,
            'receiving_touchdowns': 0,
            'receiving_yards': 24,
            'receiving_yards_per_reception': 24.0,
            'receptions': 1,
            'rush_attempts': 42,
            'rush_touchdowns': 2,
            'rush_yards': 103,
            'rush_yards_per_attempt': 2.5,
            'rushing_and_receiving_touchdowns': 2,
            'sacks': 0.0,
            'safeties': None,
            'season': '2017',
            'solo_tackles': 0,
            'tackles_for_loss': 0.0,
            'team_abbreviation': 'purdue',
            'total_tackles': 1,
            'total_touchdowns': 2,
            'two_point_conversions': None,
            'weight': 205,
            'yards_from_scrimmage': 127,
            'yards_from_scrimmage_per_play': 3.0,
            'yards_recovered_from_fumble': None,
            'yards_returned_from_interceptions': 0,
            'yards_returned_per_interception': None,
            'year': 'JR'
        }

        self.player = Player('david-blough-1')

    def test_ncaaf_player_returns_requested_career_stats(self):
        # Request the career stats
        player = self.player('')

        for attribute, value in self.results_career.items():
            assert getattr(player, attribute) == value

    def test_ncaaf_player_returns_requested_season_stats(self):
        # Request the 2017 stats
        player = self.player('2017')

        for attribute, value in self.results_2017.items():
            assert getattr(player, attribute) == value

    def test_dataframe_returns_dataframe(self):
        dataframe = [
            {'adjusted_yards_per_attempt': 4.8,
             'assists_on_tackles': 0,
             'attempted_passes': 293,
             'completed_passes': 169,
             'extra_points_made': 0,
             'field_goals_made': 0,
             'fumbles_forced': 0,
             'fumbles_recovered': 0,
             'fumbles_recovered_for_touchdown': None,
             'games': 10,
             'height': '6-1',
             'interceptions': 0,
             'interceptions_returned_for_touchdown': 0,
             'interceptions_thrown': 8,
             'kickoff_return_touchdowns': 0,
             'name': 'David Blough',
             'other_touchdowns': None,
             'passes_defended': 0,
             'passing_completion': 57.7,
             'passing_touchdowns': 10,
             'passing_yards_per_attempt': 5.4,
             'player_id': 'david-blough-1',
             'plays_from_scrimmage': 68,
             'points': 24,
             'position': 'QB',
             'punt_return_touchdowns': 0,
             'quarterback_rating': 108.6,
             'receiving_touchdowns': 0,
             'receiving_yards': 9,
             'receiving_yards_per_reception': 9.0,
             'receptions': 1,
             'rush_attempts': 67,
             'rush_touchdowns': 4,
             'rush_yards': 94,
             'rush_yards_per_attempt': 1.4,
             'rushing_and_receiving_touchdowns': 4,
             'sacks': 0.0,
             'safeties': None,
             'season': '2015',
             'solo_tackles': 0,
             'tackles_for_loss': 0.0,
             'team_abbreviation': 'purdue',
             'total_tackles': 0,
             'total_touchdowns': 4,
             'two_point_conversions': None,
             'weight': 205,
             'yards_from_scrimmage': 103,
             'yards_from_scrimmage_per_play': 1.5,
             'yards_recovered_from_fumble': None,
             'yards_returned_from_interceptions': 0,
             'yards_returned_per_interception': None,
             'year': 'FR'},
            {'adjusted_yards_per_attempt': 5.6,
             'assists_on_tackles': 0,
             'attempted_passes': 517,
             'completed_passes': 295,
             'extra_points_made': 0,
             'field_goals_made': 0,
             'fumbles_forced': 0,
             'fumbles_recovered': 0,
             'fumbles_recovered_for_touchdown': None,
             'games': 12,
             'height': '6-1',
             'interceptions': 0,
             'interceptions_returned_for_touchdown': 0,
             'interceptions_thrown': 21,
             'kickoff_return_touchdowns': 0,
             'name': 'David Blough',
             'other_touchdowns': None,
             'passes_defended': 0,
             'passing_completion': 57.1,
             'passing_touchdowns': 25,
             'passing_yards_per_attempt': 6.5,
             'player_id': 'david-blough-1',
             'plays_from_scrimmage': 81,
             'points': 24,
             'position': 'QB',
             'punt_return_touchdowns': 0,
             'quarterback_rating': 119.4,
             'receiving_touchdowns': 0,
             'receiving_yards': 8,
             'receiving_yards_per_reception': 8.0,
             'receptions': 1,
             'rush_attempts': 80,
             'rush_touchdowns': 4,
             'rush_yards': 13,
             'rush_yards_per_attempt': 0.2,
             'rushing_and_receiving_touchdowns': 4,
             'sacks': 0.0,
             'safeties': None,
             'season': '2016',
             'solo_tackles': 1,
             'tackles_for_loss': 0.0,
             'team_abbreviation': 'purdue',
             'total_tackles': 1,
             'total_touchdowns': 4,
             'two_point_conversions': None,
             'weight': 205,
             'yards_from_scrimmage': 21,
             'yards_from_scrimmage_per_play': 0.3,
             'yards_recovered_from_fumble': None,
             'yards_returned_from_interceptions': 0,
             'yards_returned_per_interception': None,
             'year': 'SO'},
            {'adjusted_yards_per_attempt': 7.0,
             'assists_on_tackles': 1,
             'attempted_passes': 157,
             'completed_passes': 102,
             'extra_points_made': 0,
             'field_goals_made': 0,
             'fumbles_forced': 0,
             'fumbles_recovered': 0,
             'fumbles_recovered_for_touchdown': None,
             'games': 9,
             'height': '6-1',
             'interceptions': 0,
             'interceptions_returned_for_touchdown': 0,
             'interceptions_thrown': 4,
             'kickoff_return_touchdowns': 0,
             'name': 'David Blough',
             'other_touchdowns': None,
             'passes_defended': 0,
             'passing_completion': 65.0,
             'passing_touchdowns': 9,
             'passing_yards_per_attempt': 7.0,
             'player_id': 'david-blough-1',
             'plays_from_scrimmage': 43,
             'points': 12,
             'position': 'QB',
             'punt_return_touchdowns': 0,
             'quarterback_rating': 137.8,
             'receiving_touchdowns': 0,
             'receiving_yards': 24,
             'receiving_yards_per_reception': 24.0,
             'receptions': 1,
             'rush_attempts': 42,
             'rush_touchdowns': 2,
             'rush_yards': 103,
             'rush_yards_per_attempt': 2.5,
             'rushing_and_receiving_touchdowns': 2,
             'sacks': 0.0,
             'safeties': None,
             'season': '2017',
             'solo_tackles': 0,
             'tackles_for_loss': 0.0,
             'team_abbreviation': 'purdue',
             'total_tackles': 1,
             'total_touchdowns': 2,
             'two_point_conversions': None,
             'weight': 205,
             'yards_from_scrimmage': 127,
             'yards_from_scrimmage_per_play': 3.0,
             'yards_recovered_from_fumble': None,
             'yards_returned_from_interceptions': 0,
             'yards_returned_per_interception': None,
             'year': 'JR'},
            {'adjusted_yards_per_attempt': 9.4,
             'assists_on_tackles': 0,
             'attempted_passes': 151,
             'completed_passes': 103,
             'extra_points_made': 0,
             'field_goals_made': 0,
             'fumbles_forced': 0,
             'fumbles_recovered': 0,
             'fumbles_recovered_for_touchdown': None,
             'games': 5,
             'height': '6-1',
             'interceptions': 0,
             'interceptions_returned_for_touchdown': 0,
             'interceptions_thrown': 1,
             'kickoff_return_touchdowns': 0,
             'name': 'David Blough',
             'other_touchdowns': None,
             'passes_defended': 0,
             'passing_completion': 68.2,
             'passing_touchdowns': 7,
             'passing_yards_per_attempt': 8.7,
             'player_id': 'david-blough-1',
             'plays_from_scrimmage': 30,
             'points': 12,
             'position': 'QB',
             'punt_return_touchdowns': 0,
             'quarterback_rating': 155.5,
             'receiving_touchdowns': 0,
             'receiving_yards': 0,
             'receiving_yards_per_reception': None,
             'receptions': 0,
             'rush_attempts': 30,
             'rush_touchdowns': 2,
             'rush_yards': 65,
             'rush_yards_per_attempt': 2.2,
             'rushing_and_receiving_touchdowns': 2,
             'sacks': 0.0,
             'safeties': None,
             'season': '2018',
             'solo_tackles': 0,
             'tackles_for_loss': 0.0,
             'team_abbreviation': 'purdue',
             'total_tackles': 0,
             'total_touchdowns': 2,
             'two_point_conversions': None,
             'weight': 205,
             'yards_from_scrimmage': 65,
             'yards_from_scrimmage_per_play': 2.2,
             'yards_recovered_from_fumble': None,
             'yards_returned_from_interceptions': 0,
             'yards_returned_per_interception': None,
             'year': 'SR'},
            {'adjusted_yards_per_attempt': 6.1,
             'assists_on_tackles': 1,
             'attempted_passes': 1118,
             'completed_passes': 669,
             'extra_points_made': 0,
             'field_goals_made': 0,
             'fumbles_forced': 0,
             'fumbles_recovered': 0,
             'fumbles_recovered_for_touchdown': None,
             'games': None,
             'height': '6-1',
             'interceptions': 0,
             'interceptions_returned_for_touchdown': 0,
             'interceptions_thrown': 34,
             'kickoff_return_touchdowns': 0,
             'name': 'David Blough',
             'other_touchdowns': None,
             'passes_defended': 0,
             'passing_completion': 59.8,
             'passing_touchdowns': 51,
             'passing_yards_per_attempt': 6.6,
             'player_id': 'david-blough-1',
             'plays_from_scrimmage': 222,
             'points': 72,
             'position': '',
             'punt_return_touchdowns': 0,
             'quarterback_rating': 124.0,
             'receiving_touchdowns': 0,
             'receiving_yards': 41,
             'receiving_yards_per_reception': 13.7,
             'receptions': 3,
             'rush_attempts': 219,
             'rush_touchdowns': 12,
             'rush_yards': 275,
             'rush_yards_per_attempt': 1.3,
             'rushing_and_receiving_touchdowns': 12,
             'sacks': 0.0,
             'safeties': None,
             'season': 'Career',
             'solo_tackles': 1,
             'tackles_for_loss': 0.0,
             'team_abbreviation': 'purdue',
             'total_tackles': 2,
             'total_touchdowns': 12,
             'two_point_conversions': None,
             'weight': 205,
             'yards_from_scrimmage': 316,
             'yards_from_scrimmage_per_play': 1.4,
             'yards_recovered_from_fumble': None,
             'yards_returned_from_interceptions': 0,
             'yards_returned_per_interception': None,
             'year': ''}
        ]
        indices = ['2015', '2016', '2017', '2018', 'Career']

        df = pd.DataFrame(dataframe, index=indices)
        player = self.player('')

        # Pandas doesn't natively allow comparisons of DataFrames.
        # Concatenating the two DataFrames (the one generated during the test
        # and the expected on above) and dropping duplicate rows leaves only
        # the rows that are unique between the two frames. This allows a quick
        # check of the DataFrame to see if it is empty - if so, all rows are
        # duplicates, and they are equal.
        frames = [df, player.dataframe]
        df1 = pd.concat(frames).drop_duplicates(keep=False)

    def test_ncaaf_tight_end_skips_passing_without_errors(self):
        player = Player('brycen-hopkins-1')

        assert player.name == 'Brycen Hopkins'
        assert player.dataframe is not None

    def test_ncaaf_404_returns_none_with_no_errors(self):
        player = Player('bad')

        assert player.name is None
        assert player.dataframe is None

    def test_ncaaf_404_returns_none_for_different_season(self):
        player = Player('bad')
        player = player('2017')

        assert player.name is None
        assert player.dataframe is None


class TestNCAAFRoster:
    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_roster_class_pulls_all_player_stats(self, *args, **kwargs):
        flexmock(utils) \
            .should_receive('_find_year_for_season') \
            .and_return('2018')
        roster = Roster('PURDUE')

        assert len(roster.players) == 2

        for player in roster.players:
            assert player.name in ['David Blough', 'Rondale Moore']

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_bad_url_raises_value_error(self, *args, **kwargs):
        with pytest.raises(ValueError):
            roster = Roster('BAD')

    @mock.patch('requests.get', side_effect=mock_pyquery)
    def test_roster_from_team_class(self, *args, **kwargs):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        team = Team(None, 1, '2018')
        mock_abbreviation = mock.PropertyMock(return_value='PURDUE')
        type(team)._abbreviation = mock_abbreviation

        assert len(team.roster.players) == 2

        for player in team.roster.players:
            assert player.name in ['David Blough', 'Rondale Moore']
        type(team)._abbreviation = None
