import pytest
from datetime import datetime
from flexmock import flexmock
from mock import PropertyMock
from pyquery import PyQuery as pq
from sportsreference import utils
from sportsreference.constants import (AWAY,
                                       HOME,
                                       LOSS,
                                       NEUTRAL,
                                       NON_DI,
                                       REGULAR_SEASON,
                                       WIN)
from sportsreference.ncaaf.schedule import Game, Schedule


class TestNCAAFSchedule:
    def setup_method(self, *args, **kwargs):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        self.game = Game(None)

    def test_away_game_returns_away_location(self):
        fake_location = PropertyMock(return_value='@')
        type(self.game)._location = fake_location

        assert self.game.location == AWAY

    def test_home_game_returns_home_location(self):
        fake_location = PropertyMock(return_value='')
        type(self.game)._location = fake_location

        assert self.game.location == HOME

    def test_neutral_game_returns_neutral_location(self):
        fake_location = PropertyMock(return_value='N')
        type(self.game)._location = fake_location

        assert self.game.location == NEUTRAL

    def test_winning_result_returns_win(self):
        fake_result = PropertyMock(return_value='W')
        type(self.game)._result = fake_result

        assert self.game.result == WIN

    def test_losing_result_returns_loss(self):
        fake_result = PropertyMock(return_value='L')
        type(self.game)._result = fake_result

        assert self.game.result == LOSS

    def test_team_with_rank_returns_rank(self):
        fake_name = PropertyMock(return_value='(1) Alabama')
        type(self.game)._rank = fake_name

        assert self.game.rank == 1

    def test_team_with_no_rank_returns_none(self):
        fake_name = PropertyMock(return_value='Missouri')
        type(self.game)._rank = fake_name

        assert self.game.rank is None

    def test_opponent_with_rank_returns_rank(self):
        fake_name = PropertyMock(return_value='(1) Alabama')
        type(self.game)._opponent_name = fake_name

        assert self.game.opponent_rank == 1

    def test_opponent_with_no_rank_returns_none(self):
        fake_name = PropertyMock(return_value='Missouri')
        type(self.game)._opponent_name = fake_name

        assert self.game.opponent_rank is None

    def test_datetime_with_no_time(self):
        fake_date = PropertyMock(return_value='Aug 31, 2017')
        fake_time = PropertyMock(return_value='')
        type(self.game)._date = fake_date
        type(self.game)._time = fake_time

        assert self.game.datetime == datetime(2017, 8, 31)

    def test_empty_game_class_returns_dataframe_of_none(self):
        assert self.game._points_for is None
        assert self.game._points_against is None
        assert self.game.dataframe is None

    def test_no_dataframes_returns_none(self):
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)
        schedule = Schedule('PURDUE')

        fake_game = flexmock(dataframe=None)
        fake_games = PropertyMock(return_value=fake_game)
        type(schedule).__iter__ = fake_games

        assert schedule.dataframe is None

    def test_no_dataframes_extended_returns_none(self):
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)
        schedule = Schedule('PURDUE')

        fake_game = flexmock(dataframe_extended=None)
        fake_games = PropertyMock(return_value=fake_game)
        type(schedule).__iter__ = fake_games

        assert schedule.dataframe_extended is None


class TestNCAAFScheduleNames:
    def test_non_major_school_returns_name_for_abbreviation(self):
        text = '<td class="left " data-stat="opp_name">Citadel</td>'
        game_data = pq(text)

        flexmock(utils) \
            .should_receive('_parse_field') \
            .and_return(None)

        game = Game(game_data)

        assert game.opponent_abbr == 'Citadel'

    def test_non_major_school_returns_non_dI_for_conference(self):
        text = '<td class="left " data-stat="conf_abbr">Non-Major</td>'
        game_data = pq(text)

        game = Game(game_data)

        assert game.opponent_conference == NON_DI
