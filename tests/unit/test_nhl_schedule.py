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
    def setup_method(self, *args, **kwargs):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        self.game = Game(None, YEAR)

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

    def test_losing_result_in_overtime_returns_overtime_loss(self):
        fake_result = PropertyMock(return_value='L')
        type(self.game)._result = fake_result
        fake_overtime = PropertyMock(return_value='OT')
        type(self.game)._overtime = fake_overtime

        assert self.game.result == OVERTIME_LOSS

    def test_losing_result_in_regulation_returns_loss(self):
        fake_result = PropertyMock(return_value='L')
        type(self.game)._result = fake_result
        fake_overtime = PropertyMock(return_value='')
        type(self.game)._overtime = fake_overtime

        assert self.game.result == LOSS

    def test_overtime_returns_one(self):
        fake_overtime = PropertyMock(return_value='OT')
        type(self.game)._overtime = fake_overtime

        assert self.game.overtime == 1

    def test_no_overtime_returns_zero(self):
        fake_overtime = PropertyMock(return_value='')
        type(self.game)._overtime = fake_overtime

        assert self.game.overtime == 0

    def test_double_overtime_returns_two(self):
        fake_overtime = PropertyMock(return_value='2OT')
        type(self.game)._overtime = fake_overtime

        assert self.game.overtime == 2

    def test_shootout_returns_shootout_constant(self):
        fake_overtime = PropertyMock(return_value='SO')
        type(self.game)._overtime = fake_overtime

        assert self.game.overtime == SHOOTOUT

    def test_bad_overtime_returns_default_number(self):
        fake_overtime = PropertyMock(return_value='BAD')
        type(self.game)._overtime = fake_overtime

        assert self.game.overtime == 0
