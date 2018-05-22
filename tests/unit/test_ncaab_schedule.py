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
                                             NCAA_TOURNAMENT,
                                             NIT_TOURNAMENT)
from sportsreference.ncaab.schedule import Game


class TestNCAABSchedule:
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

    def test_neutral_game_returns_neutral_location(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_location = PropertyMock(return_value='N')
        type(game)._location = fake_location

        assert game.location == NEUTRAL

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

    def test_regular_season_game_type(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_type = PropertyMock(return_value='REG')
        type(game)._type = fake_type

        assert game.type == REGULAR_SEASON

    def test_conference_tournament_game_type(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_type = PropertyMock(return_value='CTOURN')
        type(game)._type = fake_type

        assert game.type == CONFERENCE_TOURNAMENT

    def test_ncaa_tournament_game_type(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_type = PropertyMock(return_value='NCAA')
        type(game)._type = fake_type

        assert game.type == NCAA_TOURNAMENT

    def test_nit_tournament_game_type(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_type = PropertyMock(return_value='NIT')
        type(game)._type = fake_type

        assert game.type == NIT_TOURNAMENT

    def test_cbi_tournament_game_type(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_type = PropertyMock(return_value='CBI')
        type(game)._type = fake_type

        assert game.type == CBI_TOURNAMENT

    def test_team_with_rank_returns_rank(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_name = PropertyMock(return_value='Purdue (3)')
        type(game)._opponent_name = fake_name

        assert game.opponent_rank == 3

    def test_team_with_no_rank_returns_none(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_name = PropertyMock(return_value='Kansas State')
        type(game)._opponent_name = fake_name

        assert game.opponent_rank is None

    def test_overtimes_returns_number_of_overtimes(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_overtime = PropertyMock(return_value='OT')
        type(game)._overtimes = fake_overtime

        assert game.overtimes == 1

    def test_multiple_overtimes_returns_number_of_overtimes(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_overtime = PropertyMock(return_value='2OT')
        type(game)._overtimes = fake_overtime

        assert game.overtimes == 2

    def test_no_overtime_returns_zero(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_overtime = PropertyMock(return_value='')
        type(game)._overtimes = fake_overtime

        assert game.overtimes == 0

    def test_bad_overtime_defaults_to_zero(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)

        game = Game(None)
        fake_overtime = PropertyMock(return_value='BAD')
        type(game)._overtimes = fake_overtime

        assert game.overtimes == 0

    def test_non_major_school_returns_name_for_abbreviation(self):
        text = ('<td class="left " data-stat="opp_name">'
                'City College of New York</td>')
        game_data = pq(text)

        flexmock(utils) \
            .should_receive('parse_field') \
            .and_return(None)

        game = Game(game_data)

        assert game.opponent_abbr == 'City College of New York'

    def test_non_major_school_returns_non_dI_for_conference(self):
        game_data = pq('<td class="left " data-stat="conf_abbr"></td>')

        game = Game(game_data)

        assert game.opponent_conference == NON_DI
