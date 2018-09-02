from flexmock import flexmock
from mock import PropertyMock
from sportsreference.constants import (AWAY,
                                       HOME,
                                       LOSS,
                                       WIN)
from sportsreference.nba.schedule import Game, Schedule


class TestNBASchedule:
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

    def test_winning_result_returns_win(self):
        fake_result = PropertyMock(return_value='W')
        type(self.game)._result = fake_result

        assert self.game.result == WIN

    def test_losing_result_returns_loss(self):
        fake_result = PropertyMock(return_value='L')
        type(self.game)._result = fake_result

        assert self.game.result == LOSS

    def test_empty_game_class_returns_dataframe_of_none(self):
        assert self.game._points_allowed is None
        assert self.game._points_scored is None
        assert self.game.dataframe is None

    def test_no_dataframes_returns_none(self):
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)
        schedule = Schedule('DET')

        fake_game = flexmock(dataframe=None)
        fake_games = PropertyMock(return_value=fake_game)
        type(schedule).__iter__ = fake_games

        assert schedule.dataframe is None

    def test_no_dataframes_extended_returns_none(self):
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)
        schedule = Schedule('DET')

        fake_game = flexmock(dataframe_extended=None)
        fake_games = PropertyMock(return_value=fake_game)
        type(schedule).__iter__ = fake_games

        assert schedule.dataframe_extended is None
