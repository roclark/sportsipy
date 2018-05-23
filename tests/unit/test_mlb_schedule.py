from flexmock import flexmock
from mock import PropertyMock
from sportsreference.constants import (AWAY,
                                       HOME,
                                       LOSS,
                                       WIN)
from sportsreference.mlb.constants import DAY, NIGHT
from sportsreference.mlb.schedule import Game


class TestMLBSchedule:
    def test_away_game_returns_away_location(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_location = PropertyMock(return_value='@')
        type(game)._location = fake_location

        assert game.location == AWAY

    def test_home_game_returns_home_location(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_location = PropertyMock(return_value='')
        type(game)._location = fake_location

        assert game.location == HOME

    def test_winning_result_returns_win(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_result = PropertyMock(return_value='W')
        type(game)._result = fake_result

        assert game.result == WIN

    def test_losing_result_returns_loss(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_result = PropertyMock(return_value='L')
        type(game)._result = fake_result

        assert game.result == LOSS

    def test_regular_length_game_returns_9_innings(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_innings = PropertyMock(return_value='')
        type(game)._innings = fake_innings

        assert game.innings == 9

    def test_extra_innings_returns_total_innings(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_innings = PropertyMock(return_value='12')
        type(game)._innings = fake_innings

        assert game.innings == 12

    def test_games_behind_returns_zero_when_tied(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_games_behind = PropertyMock(return_value='Tied')
        type(game)._games_behind = fake_games_behind

        assert game.games_behind == 0.0

    def test_games_behind_returns_number_of_games_behind(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_games_behind = PropertyMock(return_value='1.5')
        type(game)._games_behind = fake_games_behind

        assert game.games_behind == 1.5

    def test_games_behind_returns_number_of_games_ahead(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_games_behind = PropertyMock(return_value='up 1.5')
        type(game)._games_behind = fake_games_behind

        assert game.games_behind == -1.5

        fake_games_behind = PropertyMock(return_value='up13.0')
        type(game)._games_behind = fake_games_behind

        assert game.games_behind == -13.0

    def test_no_save_returns_none(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_save = PropertyMock(return_value='')
        type(game)._save = fake_save

        assert game.save is None

    def test_save_returns_name(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_save = PropertyMock(return_value='Verlander')
        type(game)._save = fake_save

        assert game.save == 'Verlander'

    def test_day_game_returns_daytime(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_day = PropertyMock(return_value='D')
        type(game)._day_or_night = fake_day

        assert game.day_or_night == DAY

    def test_night_game_returns_nighttime(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None, None)
        fake_day = PropertyMock(return_value='N')
        type(game)._day_or_night = fake_day

        assert game.day_or_night == NIGHT
