import mock
import pytest
from flexmock import flexmock
from sportsreference.fb.roster import Roster
from sportsreference.fb.schedule import Schedule
from sportsreference.fb.team import Team
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


class TestFBTeam:
    def setup_method(self):
        flexmock(Team) \
            .should_receive('_pull_team_page') \
            .and_return(None)
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)
        flexmock(Roster) \
            .should_receive('_pull_stats') \
            .and_return(None)
        self.team = Team('Tottenham Hotspur')

    def test_location_record_missing_result(self):
        html = 'Home Record: (5-0-0)'

        output = self.team._location_records(html)

        assert output == (None, None, None, None)

    def test_location_record_missing_points(self):
        html = 'Home Record: 15 points (5-0-0)'

        output = self.team._location_records(html)

        assert output == (None, None, None, None)

    def test_records_missing_result(self):
        html = 'Record: 5-0-0, 15 points (3.0 per game)'

        output = self.team._records(html)

        assert output == (None, None, None)

    def test_goals_missing(self):
        html = 'Goals: 20 (2.5 per game), Goals Against: 11 (1.38 per game)'

        output = self.team._goals(html)

        assert output == (None, None, None)

    def test_expected_goals(self):
        html = 'xG: 19.3, xGA: 12.1'

        output = self.team._parse_expected_goals(html)

        assert output == (None, None, None)

    def test_missing_home_games_returns_none(self):
        output = self.team.home_games

        assert not output

    def test_missing_away_games_returns_none(self):
        output = self.team.away_games

        assert not output

    def test_invalid_home_wins_returns_none(self):
        self.team._home_record = 'a-0-0'

        output = self.team.home_wins

        assert not output

    def test_invalid_home_draws_returns_none(self):
        self.team._home_record = '5-a-0'

        output = self.team.home_draws

        assert not output

    def test_missing_home_draws_returns_none(self):
        self.team._home_record = '5'

        output = self.team.home_draws

        assert not output

    def test_invalid_home_losses_returns_none(self):
        self.team._home_record = '5-0-a'

        output = self.team.home_losses

        assert not output

    def test_missing_home_losses_returns_none(self):
        self.team._home_record = '5-0'

        output = self.team.home_losses

        assert not output

    def test_invalid_home_record_returns_none_for_losses(self):
        self.team._home_record = None

        output = self.team.home_losses

        assert not output

    def test_invalid_away_wins_returns_none(self):
        self.team._away_record = 'a-0-0'

        output = self.team.away_wins

        assert not output

    def test_missing_away_draws_returns_none(self):
        self.team._away_record = '5'

        output = self.team.away_draws

        assert not output

    def test_invalid_away_draws_returns_none(self):
        self.team._away_record = '5-a-0'

        output = self.team.away_draws

        assert not output

    def test_missing_away_losses_returns_none(self):
        self.team._away_record = '5-0'

        output = self.team.away_losses

        assert not output

    def test_invalid_away_losses_returns_none(self):
        self.team._away_record = '5-0-a'

        output = self.team.away_losses

        assert not output

    def test_invalid_away_record_returns_none_for_losses(self):
        self.team._away_record = None

        output = self.team.away_losses

        assert not output

    def test_fb_schedule_returns_schedule(self):
        self.team._doc = None

        assert len(self.team.schedule) == 0

    def test_fb_roster_returns_roster(self):
        self.team._doc = None

        assert len(self.team.roster) == 0


class TestFBTeamInvalidPage:
    @mock.patch('requests.get', side_effect=mock_httperror)
    def test_invalid_http_page_error(self, *args, **kwargs):
        flexmock(Team) \
            .should_receive('__init__') \
            .and_return(None)
        team = Team(None)
        team._squad_id = ''

        output = team._pull_team_page()

        assert not output
