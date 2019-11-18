from flexmock import flexmock
from mock import PropertyMock
from sportsreference.constants import (AWAY,
                                       HOME,
                                       LOSS,
                                       TIE,
                                       NEUTRAL,
                                       POST_SEASON,
                                       REGULAR_SEASON,
                                       WIN)
from sportsreference.nfl.constants import (CONF_CHAMPIONSHIP,
                                           DIVISION,
                                           SUPER_BOWL,
                                           WILD_CARD)
from sportsreference.nfl.schedule import Game, Schedule


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

    def test_tied_result_returns_tie(self):
        fake_result = PropertyMock(return_value='T')
        type(self.game)._result = fake_result

        assert self.game.result == TIE

    def test_no_result_returns_none(self):
        fake_result = PropertyMock(return_value='')
        type(self.game)._result = fake_result

        assert self.game.result is None

    def test_overtime_returns_overtime(self):
        fake_overtime = PropertyMock(return_value='OT')
        type(self.game)._overtime = fake_overtime

        assert self.game.overtime

    def test_no_overtime_returns_none(self):
        fake_overtime = PropertyMock(return_value='')
        type(self.game)._overtime = fake_overtime

        assert not self.game.overtime

    def test_regular_season_type(self):
        assert self.game.type == REGULAR_SEASON

    def test_playoff_type(self):
        game = Game(None, POST_SEASON, YEAR)

        assert game.type == POST_SEASON

    def test_wild_card_game_returns_wild_card(self):
        fake_week = PropertyMock(return_value='Wild Card')
        type(self.game)._week = fake_week

        assert self.game.week == WILD_CARD

    def test_division_playoff_game_returns_division(self):
        fake_week = PropertyMock(return_value='Division')
        type(self.game)._week = fake_week

        assert self.game.week == DIVISION

    def test_conference_championship_returns_division(self):
        fake_week = PropertyMock(return_value='Conf. Champ.')
        type(self.game)._week = fake_week

        assert self.game.week == CONF_CHAMPIONSHIP

    def test_super_bowl_returns_super_bowl(self):
        fake_week = PropertyMock(return_value='SuperBowl')
        type(self.game)._week = fake_week

        assert self.game.week == SUPER_BOWL

    def test_empty_game_class_returns_dataframe_of_none(self):
        assert self.game._points_scored is None
        assert self.game._points_allowed is None
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
