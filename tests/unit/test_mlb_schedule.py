import pytest
from datetime import datetime
from flexmock import flexmock
from mock import PropertyMock
from sportsreference.constants import (AWAY,
                                       HOME,
                                       LOSS,
                                       WIN)
from sportsreference.mlb.constants import DAY, NIGHT
from sportsreference.mlb.schedule import Game, Schedule


class TestMLBSchedule:
    def setup_method(self, *args, **kwargs):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        self.game = Game(None, None)

    def test_double_header_returns_second_game(self):
        fake_date = PropertyMock(return_value='Sunday, May 14 (2)')
        fake_year = PropertyMock(return_value='2017')
        type(self.game)._date = fake_date
        type(self.game)._year = fake_year

        assert self.game.datetime == datetime(2017, 5, 14)
        assert self.game.game_number_for_day == 2

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

    def test_regular_length_game_returns_9_innings(self):
        fake_innings = PropertyMock(return_value='')
        type(self.game)._innings = fake_innings

        assert self.game.innings == 9

    def test_extra_innings_returns_total_innings(self):
        fake_innings = PropertyMock(return_value='12')
        type(self.game)._innings = fake_innings

        assert self.game.innings == 12

    def test_games_behind_returns_zero_when_tied(self):
        fake_games_behind = PropertyMock(return_value='Tied')
        type(self.game)._games_behind = fake_games_behind

        assert self.game.games_behind == 0.0

    def test_games_behind_returns_number_of_games_behind(self):
        fake_games_behind = PropertyMock(return_value='1.5')
        type(self.game)._games_behind = fake_games_behind

        assert self.game.games_behind == 1.5

    def test_games_behind_returns_number_of_games_ahead(self):
        fake_games_behind = PropertyMock(return_value='up 1.5')
        type(self.game)._games_behind = fake_games_behind

        assert self.game.games_behind == -1.5

        fake_games_behind = PropertyMock(return_value='up13.0')
        type(self.game)._games_behind = fake_games_behind

        assert self.game.games_behind == -13.0

    def test_no_save_returns_none(self):
        fake_save = PropertyMock(return_value='')
        type(self.game)._save = fake_save

        assert self.game.save is None

    def test_save_returns_name(self):
        fake_save = PropertyMock(return_value='Verlander')
        type(self.game)._save = fake_save

        assert self.game.save == 'Verlander'

    def test_day_game_returns_daytime(self):
        fake_day = PropertyMock(return_value='D')
        type(self.game)._day_or_night = fake_day

        assert self.game.day_or_night == DAY

    def test_night_game_returns_nighttime(self):
        fake_day = PropertyMock(return_value='N')
        type(self.game)._day_or_night = fake_day

        assert self.game.day_or_night == NIGHT

    def test_empty_game_class_returns_dataframe_of_none(self):
        assert self.game._runs_allowed is None
        assert self.game._runs_scored is None
        assert self.game.dataframe is None

    def test_empty_boxscore_class_returns_dataframe_of_none(self):
        assert self.game._runs_allowed is None
        assert self.game._runs_scored is None
        assert self.game.dataframe_extended is None

    def test_invalid_dataframe_not_included_with_schedule_dataframes(self):
        # If a DataFrame is not valid, it should not be included with the
        # dataframes property. If no dataframes are present, the DataFrame
        # should return the default value of None.
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)
        schedule = Schedule('HOU')

        fake_game = flexmock(_runs_scored=None, _runs_allowed=None)
        fake_games = PropertyMock(return_value=fake_game)
        type(schedule).__iter__ = fake_games

        assert schedule.dataframe is None

    def test_no_dataframes_extended_returns_none(self):
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)
        schedule = Schedule('HOU')

        fake_game = flexmock(dataframe_extended=None)
        fake_games = PropertyMock(return_value=fake_game)
        type(schedule).__iter__ = fake_games

        assert schedule.dataframe_extended is None

    def test_bad_games_up_returns_default(self):
        fake_games_up = PropertyMock(return_value='up BAD')
        type(self.game)._games_behind = fake_games_up

        assert self.game.games_behind is None

    def test_bad_games_ahead_returns_default(self):
        fake_games_up = PropertyMock(return_value='BAD')
        type(self.game)._games_behind = fake_games_up

        assert self.game.games_behind is None
