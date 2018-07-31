from flexmock import flexmock
from sportsreference.mlb.schedule import Schedule
from sportsreference.mlb.teams import Team


class TestMLBTeams:
    def test_mlb_schedule_returns_schedule(self, *args, **kwargs):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)

        team = Team(None, 1)

        assert len(team.schedule) == 0
