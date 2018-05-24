from flexmock import flexmock
from mock import PropertyMock
from sportsreference.constants import (AWAY,
                                       HOME,
                                       LOSS,
                                       WIN)
from sportsreference.nba.schedule import Game


class TestNBASchedule:
    def test_away_game_returns_away_location(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_location = PropertyMock(return_value='@')
        type(game)._location = fake_location

        assert game.location == AWAY

    def test_home_game_returns_home_location(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_location = PropertyMock(return_value='')
        type(game)._location = fake_location

        assert game.location == HOME

    def test_winning_result_returns_win(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_result = PropertyMock(return_value='W')
        type(game)._result = fake_result

        assert game.result == WIN

    def test_losing_result_returns_loss(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_result = PropertyMock(return_value='L')
        type(game)._result = fake_result

        assert game.result == LOSS

    def test_overtime_returns_overtime(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_overtime = PropertyMock(return_value='OT')
        type(game)._overtime = fake_overtime

        assert game.overtime == 1

    def test_no_overtime_returns_none(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_overtime = PropertyMock(return_value='')
        type(game)._overtime = fake_overtime

        assert game.overtime is None
