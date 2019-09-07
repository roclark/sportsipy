from datetime import datetime
from flexmock import flexmock
from mock import PropertyMock
from pyquery import PyQuery as pq
from sportsreference import utils
from sportsreference.constants import (AWAY,
                                       CONFERENCE_TOURNAMENT,
                                       HOME,
                                       LOSS,
                                       NEUTRAL,
                                       NON_DI,
                                       REGULAR_SEASON,
                                       WIN)
from sportsreference.ncaab.constants import (CBI_TOURNAMENT,
                                             CIT_TOURNAMENT,
                                             NCAA_TOURNAMENT,
                                             NIT_TOURNAMENT)
from sportsreference.ncaab.schedule import Game, Schedule


class TestNCAABSchedule:
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

    def test_regular_season_game_type(self):
        fake_type = PropertyMock(return_value='REG')
        type(self.game)._type = fake_type

        assert self.game.type == REGULAR_SEASON

    def test_conference_tournament_game_type(self):
        fake_type = PropertyMock(return_value='CTOURN')
        type(self.game)._type = fake_type

        assert self.game.type == CONFERENCE_TOURNAMENT

    def test_ncaa_tournament_game_type(self):
        fake_type = PropertyMock(return_value='NCAA')
        type(self.game)._type = fake_type

        assert self.game.type == NCAA_TOURNAMENT

    def test_nit_tournament_game_type(self):
        fake_type = PropertyMock(return_value='NIT')
        type(self.game)._type = fake_type

        assert self.game.type == NIT_TOURNAMENT

    def test_cbi_tournament_game_type(self):
        fake_type = PropertyMock(return_value='CBI')
        type(self.game)._type = fake_type

        assert self.game.type == CBI_TOURNAMENT

    def test_cit_tournament_game_type(self):
        fake_type = PropertyMock(return_value='CIT')
        type(self.game)._type = fake_type

        assert self.game.type == CIT_TOURNAMENT

    def test_team_with_rank_returns_rank(self):
        fake_name = PropertyMock(return_value='Purdue (3)')
        type(self.game)._opponent_name = fake_name

        assert self.game.opponent_rank == 3

    def test_team_with_no_rank_returns_none(self):
        fake_name = PropertyMock(return_value='Kansas State')
        type(self.game)._opponent_name = fake_name

        assert self.game.opponent_rank is None

    def test_overtimes_returns_number_of_overtimes(self):
        fake_overtime = PropertyMock(return_value='OT')
        type(self.game)._overtimes = fake_overtime

        assert self.game.overtimes == 1

    def test_multiple_overtimes_returns_number_of_overtimes(self):
        fake_overtime = PropertyMock(return_value='2OT')
        type(self.game)._overtimes = fake_overtime

        assert self.game.overtimes == 2

    def test_no_overtime_returns_zero(self):
        fake_overtime = PropertyMock(return_value='')
        type(self.game)._overtimes = fake_overtime

        assert self.game.overtimes == 0

    def test_bad_overtime_defaults_to_zero(self):
        fake_overtime = PropertyMock(return_value='BAD')
        type(self.game)._overtimes = fake_overtime

        assert self.game.overtimes == 0

    def test_none_time_defaults_to_set_time_in_datetime(self):
        fake_date = PropertyMock(return_value='Thu, Dec 13, 2018')
        fake_time = PropertyMock(return_value=None)
        type(self.game)._date = fake_date
        type(self.game)._time = fake_time

        assert self.game.datetime == datetime(2018, 12, 13, 0, 0)

    def test_blank_time_defaults_to_set_time_in_datetime(self):
        fake_date = PropertyMock(return_value='Thu, Dec 13, 2018')
        fake_time = PropertyMock(return_value='')
        type(self.game)._date = fake_date
        type(self.game)._time = fake_time

        assert self.game.datetime == datetime(2018, 12, 13, 0, 0)

    def test_empty_schedule_class_returns_dataframe_of_none(self):
        fake_points = PropertyMock(return_value=None)
        type(self.game)._home_points = fake_points
        type(self.game)._away_points = fake_points

        assert self.game._home_points is None
        assert self.game._away_points is None
        assert self.game.dataframe is None

    def test_empty_schedule_class_returns_dataframe_extended_of_none(self):
        fake_points = PropertyMock(return_value=None)
        type(self.game)._home_points = fake_points
        type(self.game)._away_points = fake_points

        assert self.game._home_points is None
        assert self.game._away_points is None
        assert self.game.dataframe_extended is None

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


class TestNCAABScheduleNames:
    def test_non_major_school_returns_name_for_abbreviation(self):
        text = ('<td class="left " data-stat="opp_name">'
                'City College of New York</td>')
        game_data = pq(text)

        game = Game(game_data)

        assert game.opponent_abbr == 'City College of New York'

    def test_non_major_school_returns_non_dI_for_conference(self):
        game_data = pq('<td class="left " data-stat="conf_abbr"></td>')

        game = Game(game_data)

        assert game.opponent_conference == NON_DI
