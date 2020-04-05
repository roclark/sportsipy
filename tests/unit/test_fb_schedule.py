import mock
from datetime import datetime
from flexmock import flexmock
from pyquery import PyQuery as pq
from sportsreference.constants import (AWAY,
                                       DRAW,
                                       HOME,
                                       LOSS,
                                       NEUTRAL,
                                       WIN)
from sportsreference.fb.schedule import Game, Schedule
from urllib.error import HTTPError


def mock_httperror(url):
    class MockPQ:
        def __init__(self, html_contents):
            self.status_code = 504
            self.html_contents = html_contents
            self.text = html_contents
            self.url = url
            self.reason = HTTPError
            self.headers = None

    return MockPQ(None)


class TestFBSchedule:
    def setup_method(self):
        flexmock(Game) \
            .should_receive('_parse_game_data') \
            .and_return(None)
        self.game = Game(None)

    def test_invalid_opponent_id_returns_none(self):
        html = '<td data-stat="opponent"></td>'

        output = self.game._parse_opponent_id(pq(html))

        assert not output

    def test_invalid_date_returns_none_datetime(self):
        self.game._date = None

        output = self.game.datetime

        assert not output

    def test_invalid_time_sets_no_time_in_datetime(self):
        self.game._date = '2019-08-17'
        self.game._time = None

        output = self.game.datetime

        assert output == datetime(2019, 8, 17, 0, 0)

    def test_missing_date_field_returns_none_datetime(self):
        self.game._date = '2019-08'

        output = self.game.datetime

        assert not output

    def test_invalid_date_characters_returns_none_datetime(self):
        self.game._date = 'yyyy-mm-dd'

        output = self.game.datetime

        assert not output

    def test_invalid_time_characters_returns_none_datetime(self):
        self.game._date = '2019-08-17'
        self.game._time = 'hh:mm'

        output = self.game.datetime

        assert output == datetime(2019, 8, 17, 0, 0)

    def test_missing_venue_returns_none(self):
        self.game._venue = None

        output = self.game.venue

        assert not output

    def test_home_venue_returns_home(self):
        self.game._venue = 'Home'

        output = self.game.venue

        assert output == HOME

    def test_away_venue_returns_away(self):
        self.game._venue = 'Away'

        output = self.game.venue

        assert output == AWAY

    def test_neutral_venue_returns_neutral(self):
        self.game._venue = 'Neutral'

        output = self.game.venue

        assert output == NEUTRAL

    def test_missing_result_returns_none(self):
        self.game._result = None

        output = self.game.result

        assert not output

    def test_win_result_returns_win(self):
        self.game._result = 'W'

        output = self.game.result

        assert output == WIN

    def test_draw_result_returns_draw(self):
        self.game._result = 'D'

        output = self.game.result

        assert output == DRAW

    def test_loss_result_returns_loss(self):
        self.game._result = 'L'

        output = self.game.result

        assert output == LOSS

    def test_missing_attendance_returns_none(self):
        self.game._attendance = None

        output = self.game.attendance

        assert not output

    def test_no_goals_dataframe_returns_none(self):
        self.game._goals_for = None
        self.game._goals_against = None

        output = self.game.dataframe

        assert not output

    def test_goals_for_with_shootout(self):
        self.game._goals_for = '3 (5)'

        output = self.game.goals_for

        assert output == 3

    def test_goals_against_with_shootout(self):
        self.game._goals_against = '3 (4)'

        output = self.game.goals_against

        assert output == 3

    def test_shootout_goals_scored(self):
        self.game._goals_for = '3 (5)'

        output = self.game.shootout_scored

        assert output == 5

    def test_shootout_goals_against(self):
        self.game._goals_against = '3 (4)'

        output = self.game.shootout_against

        assert output == 4

    @mock.patch('requests.get', side_effect=mock_httperror)
    def test_invalid_http_page_error(self, *args, **kwargs):
        flexmock(Schedule) \
            .should_receive('__init__') \
            .and_return(None)
        schedule = Schedule(None)
        schedule._squad_id = ''

        output = schedule._pull_schedule('Tottenham Hotspur', None)

        assert not output
