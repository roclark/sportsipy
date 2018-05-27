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
    def test_away_game_returns_away_location(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_location = PropertyMock(return_value='@')
        type(game)._location = fake_location

        assert game.location == AWAY

    def test_home_game_returns_home_location(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_location = PropertyMock(return_value='')
        type(game)._location = fake_location

        assert game.location == HOME

    def test_neutral_game_returns_neutral_location(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_location = PropertyMock(return_value='N')
        type(game)._location = fake_location

        assert game.location == NEUTRAL

    def test_winning_result_returns_win(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_result = PropertyMock(return_value='W')
        type(game)._result = fake_result

        assert game.result == WIN

    def test_losing_result_returns_loss(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_result = PropertyMock(return_value='L')
        type(game)._result = fake_result

        assert game.result == LOSS

    def test_overtime_returns_overtime(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_overtime = PropertyMock(return_value='OT')
        type(game)._overtime = fake_overtime

        assert game.overtime

    def test_no_overtime_returns_none(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_overtime = PropertyMock(return_value='')
        type(game)._overtime = fake_overtime

        assert not game.overtime

    def test_bye_week_returns_true(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_name = PropertyMock(return_value='Bye Week')
        type(game)._opponent_name = fake_name

        assert game.bye

    def test_non_bye_week_returns_false(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_name = PropertyMock(return_value='Jacksonville Jaguars')
        type(game)._opponent_name = fake_name

        assert not game.bye

    def test_no_turnovers_returns_zero(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_turnovers = PropertyMock(return_value='')
        type(game)._turnovers = fake_turnovers

        assert game.turnovers == 0

    def test_nonzero_turnover_returns_nonzero_number(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_turnovers = PropertyMock(return_value='1')
        type(game)._turnovers = fake_turnovers

        assert game.turnovers == 1

    def test_no_turnovers_forced_returns_zero(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_turnovers = PropertyMock(return_value='')
        type(game)._turnovers_forced = fake_turnovers

        assert game.turnovers_forced == 0

    def test_nonzero_turnovers_forced_returns_nonzero_number(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)
        fake_turnovers = PropertyMock(return_value='1')
        type(game)._turnovers_forced = fake_turnovers

        assert game.turnovers_forced == 1

    def test_regular_season_type(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, REGULAR_SEASON, YEAR)

        assert game.type == REGULAR_SEASON

    def test_playoff_type(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, POST_SEASON, YEAR)

        assert game.type == POST_SEASON
