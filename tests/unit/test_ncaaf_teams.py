from flexmock import flexmock
from mock import PropertyMock
from sportsreference.ncaaf.schedule import Schedule
from sportsreference.ncaaf.teams import Team


class TestNCAAFTeams:
    def setup_method(self, *args, **kwargs):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)

        self.team = Team(None)

    def test_no_conference_wins_data_returns_default(self):
        fake_conference_wins = PropertyMock(return_value='')
        type(self.team)._conference_wins = fake_conference_wins

        assert self.team.conference_wins is None

    def test_no_conference_losses_data_returns_default(self):
        fake_conference_losses = PropertyMock(return_value='')
        type(self.team)._conference_losses = fake_conference_losses

        assert self.team.conference_losses is None

    def test_no_conference_percentage_returns_default(self):
        fake_conf_win_percentage = PropertyMock(return_value='')
        type(self.team)._conference_win_percentage = fake_conf_win_percentage

        assert self.team.conference_win_percentage is None

    def test_ncaaf_schedule_returns_schedule(self):
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)

        team = Team(None, 1)

        assert len(team.schedule) == 0
