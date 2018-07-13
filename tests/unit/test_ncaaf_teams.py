from flexmock import flexmock
from mock import PropertyMock
from pyquery import PyQuery as pq
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

        assert self.team.conference_wins == 0

    def test_no_conference_losses_data_returns_default(self):
        fake_conference_losses = PropertyMock(return_value='')
        type(self.team)._conference_losses = fake_conference_losses

        assert self.team.conference_losses == 0

    def test_no_conference_percentage_returns_default(self):
        fake_conf_win_percentage = PropertyMock(return_value='')
        type(self.team)._conference_win_percentage = fake_conf_win_percentage

        assert self.team.conference_win_percentage == 0
