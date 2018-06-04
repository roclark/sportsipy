from flexmock import flexmock
from mock import PropertyMock
from sportsreference.constants import (AWAY,
                                       HOME,
                                       LOSS,
                                       NEUTRAL,
                                       POST_SEASON,
                                       REGULAR_SEASON,
                                       WIN)
from sportsreference.nfl.schedule import Game


YEAR = 2017


class TestNFLSchedule:
    def setup_method(self, *args, **kwargs):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        self.game = Game(None, REGULAR_SEASON, YEAR)

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

    def test_overtime_returns_overtime(self):
        fake_overtime = PropertyMock(return_value='OT')
        type(self.game)._overtime = fake_overtime

        assert self.game.overtime

    def test_no_overtime_returns_none(self):
        fake_overtime = PropertyMock(return_value='')
        type(self.game)._overtime = fake_overtime

        assert not self.game.overtime

    def test_bye_week_returns_true(self):
        fake_name = PropertyMock(return_value='Bye Week')
        type(self.game)._opponent_name = fake_name

        assert self.game.bye

    def test_non_bye_week_returns_false(self):
        fake_name = PropertyMock(return_value='Jacksonville Jaguars')
        type(self.game)._opponent_name = fake_name

        assert not self.game.bye

    def test_no_turnovers_returns_zero(self):
        fake_turnovers = PropertyMock(return_value='')
        type(self.game)._turnovers = fake_turnovers

        assert self.game.turnovers == 0

    def test_nonzero_turnover_returns_nonzero_number(self):
        fake_turnovers = PropertyMock(return_value='1')
        type(self.game)._turnovers = fake_turnovers

        assert self.game.turnovers == 1

    def test_no_turnovers_forced_returns_zero(self):
        fake_turnovers = PropertyMock(return_value='')
        type(self.game)._turnovers_forced = fake_turnovers

        assert self.game.turnovers_forced == 0

    def test_nonzero_turnovers_forced_returns_nonzero_number(self):
        fake_turnovers = PropertyMock(return_value='1')
        type(self.game)._turnovers_forced = fake_turnovers

        assert self.game.turnovers_forced == 1

    def test_regular_season_type(self):
        assert self.game.type == REGULAR_SEASON

    def test_playoff_type(self):
        game = Game(None, POST_SEASON, YEAR)

        assert game.type == POST_SEASON
