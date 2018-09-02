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
from sportsreference.nhl.schedule import Game, Schedule


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

    def test_bad_shots_on_goal_returns_default_number(self):
        fake_shots = PropertyMock(return_value='')
        type(self.game)._shots_on_goal = fake_shots

        assert self.game.shots_on_goal is None

    def test_bad_penalties_in_minutes_returns_default_number(self):
        fake_penalties = PropertyMock(return_value='')
        type(self.game)._penalties_in_minutes = fake_penalties

        assert self.game.penalties_in_minutes is None

    def test_bad_power_play_goals_returns_default_number(self):
        fake_power_play_goals = PropertyMock(return_value='')
        type(self.game)._power_play_goals = fake_power_play_goals

        assert self.game.power_play_goals is None

    def test_bad_power_play_opportunities_returns_default_number(self):
        fake_power_play_opps = PropertyMock(return_value='')
        type(self.game)._power_play_opportunities = fake_power_play_opps

        assert self.game.power_play_opportunities is None

    def test_bad_short_handed_goals_returns_default_number(self):
        fake_goals = PropertyMock(return_value='')
        type(self.game)._short_handed_goals = fake_goals

        assert self.game.short_handed_goals is None

    def test_bad_opp_shots_on_goal_returns_default_number(self):
        fake_shots = PropertyMock(return_value='')
        type(self.game)._opp_shots_on_goal = fake_shots

        assert self.game.opp_shots_on_goal is None

    def test_bad_opp_penalties_in_minutes_returns_default_number(self):
        fake_penalties = PropertyMock(return_value='')
        type(self.game)._opp_penalties_in_minutes = fake_penalties

        assert self.game.opp_penalties_in_minutes is None

    def test_bad_opp_power_play_goals_returns_default_number(self):
        fake_power_play_goals = PropertyMock(return_value='')
        type(self.game)._opp_power_play_goals = fake_power_play_goals

        assert self.game.opp_power_play_goals is None

    def test_bad_opp_power_play_opportunities_returns_default_number(self):
        fake_power_play_opps = PropertyMock(return_value='')
        type(self.game)._opp_power_play_opportunities = fake_power_play_opps

        assert self.game.opp_power_play_opportunities is None

    def test_bad_opp_short_handed_goals_returns_default_number(self):
        fake_goals = PropertyMock(return_value='')
        type(self.game)._opp_short_handed_goals = fake_goals

        assert self.game.opp_short_handed_goals is None

    def test_bad_penalties_in_minutes_returns_default_number(self):
        fake_penalties = PropertyMock(return_value='')
        type(self.game)._penalties_in_minutes = fake_penalties

        assert self.game.penalties_in_minutes is None

    def test_bad_power_play_goals_returns_default_number(self):
        fake_power_play_goals = PropertyMock(return_value='')
        type(self.game)._power_play_goals = fake_power_play_goals

        assert self.game.power_play_goals is None

    def test_bad_power_play_opportunities_returns_default_number(self):
        fake_power_play_opps = PropertyMock(return_value='')
        type(self.game)._power_play_opportunities = fake_power_play_opps

        assert self.game.power_play_opportunities is None

    def test_bad_corsi_for_returns_default_number(self):
        fake_corsi = PropertyMock(return_value='')
        type(self.game)._corsi_for = fake_corsi

        assert self.game.corsi_for is None

    def test_bad_corsi_against_returns_default_number(self):
        fake_corsi = PropertyMock(return_value='')
        type(self.game)._corsi_against = fake_corsi

        assert self.game.corsi_against is None

    def test_bad_corsi_for_percentage_returns_default_number(self):
        fake_corsi = PropertyMock(return_value='')
        type(self.game)._corsi_for_percentage = fake_corsi

        assert self.game.corsi_for_percentage is None

    def test_bad_fenwick_for_returns_default_number(self):
        fake_fenwick = PropertyMock(return_value='')
        type(self.game)._fenwick_for = fake_fenwick

        assert self.game.fenwick_for is None

    def test_bad_fenwick_against_returns_default_number(self):
        fake_fenwick = PropertyMock(return_value='')
        type(self.game)._fenwick_against = fake_fenwick

        assert self.game.fenwick_against is None

    def test_bad_fenwick_for_percentage_returns_default_number(self):
        fake_fenwick = PropertyMock(return_value='')
        type(self.game)._fenwick_for_percentage = fake_fenwick

        assert self.game.fenwick_for_percentage is None

    def test_bad_faceoff_wins_returns_default_number(self):
        fake_faceoff = PropertyMock(return_value='')
        type(self.game)._faceoff_wins = fake_faceoff

        assert self.game.faceoff_wins is None

    def test_bad_faceoff_losses_returns_default_number(self):
        fake_faceoff = PropertyMock(return_value='')
        type(self.game)._faceoff_losses = fake_faceoff

        assert self.game.faceoff_losses is None

    def test_bad_faceoff_win_percentage_returns_default_number(self):
        fake_faceoff = PropertyMock(return_value='')
        type(self.game)._faceoff_win_percentage = fake_faceoff

        assert self.game.faceoff_win_percentage is None

    def test_bad_offensive_zone_start_percentage_returns_default_number(self):
        fake_start = PropertyMock(return_value='')
        type(self.game)._offensive_zone_start_percentage = fake_start

        assert self.game.offensive_zone_start_percentage is None

    def test_bad_pdo_returns_default_number(self):
        fake_pdo = PropertyMock(return_value='')
        type(self.game)._pdo = fake_pdo

        assert self.game.pdo is None

    def test_empty_game_class_returns_dataframe_of_none(self):
        assert self.game._goals_scored is None
        assert self.game._goals_allowed is None
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
