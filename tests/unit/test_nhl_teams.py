from flexmock import flexmock
from sportsreference.nhl.schedule import Schedule
from sportsreference.nhl.teams import Team


class TestNHLTeams:
    def test_nhl_schedule_returns_schedule(self, *args, **kwargs):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)

        team = Team(None, 1)

        assert len(team.schedule) == 0
