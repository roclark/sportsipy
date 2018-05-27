from flexmock import flexmock
from mock import PropertyMock
from sportsreference.constants import (AWAY,
                                       HOME,
                                       LOSS,
                                       NEUTRAL,
                                       POST_SEASON,
                                       REGULAR_SEASON,
                                       WIN)
from sportsreference.nhl.constants import OVERTIME_LOSS, SHOOTOUT
from sportsreference.nhl.schedule import Game


YEAR = 2017


class TestNHLSchedule:
    def test_away_game_returns_away_location(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, YEAR)
        fake_location = PropertyMock(return_value='@')
        type(game)._location = fake_location

        assert game.location == AWAY

    def test_home_game_returns_home_location(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, YEAR)
        fake_location = PropertyMock(return_value='')
        type(game)._location = fake_location

        assert game.location == HOME

    def test_winning_result_returns_win(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, YEAR)
        fake_result = PropertyMock(return_value='W')
        type(game)._result = fake_result

        assert game.result == WIN

    def test_losing_result_in_overtime_returns_overtime_loss(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, YEAR)
        fake_result = PropertyMock(return_value='L')
        type(game)._result = fake_result
        fake_overtime = PropertyMock(return_value='OT')
        type(game)._overtime = fake_overtime

        assert game.result == OVERTIME_LOSS

    def test_losing_result_in_regulation_returns_loss(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, YEAR)
        fake_result = PropertyMock(return_value='L')
        type(game)._result = fake_result
        fake_overtime = PropertyMock(return_value='')
        type(game)._overtime = fake_overtime

        assert game.result == LOSS

    def test_overtime_returns_one(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, YEAR)
        fake_overtime = PropertyMock(return_value='OT')
        type(game)._overtime = fake_overtime

        assert game.overtime == 1

    def test_no_overtime_returns_zero(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, YEAR)
        fake_overtime = PropertyMock(return_value='')
        type(game)._overtime = fake_overtime

        assert game.overtime == 0

    def test_double_overtime_returns_two(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, YEAR)
        fake_overtime = PropertyMock(return_value='2OT')
        type(game)._overtime = fake_overtime

        assert game.overtime == 2

    def test_shootout_returns_shootout_constant(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, YEAR)
        fake_overtime = PropertyMock(return_value='SO')
        type(game)._overtime = fake_overtime

        assert game.overtime == SHOOTOUT

    def test_bad_overtime_returns_default_number(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, YEAR)
        fake_overtime = PropertyMock(return_value='BAD')
        type(game)._overtime = fake_overtime

        assert game.overtime == 0
