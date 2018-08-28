from flexmock import flexmock
from mock import PropertyMock
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

    def test_mlb_bad_attribute_property_returns_default(self):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        team = Team(None, 1)

        fake_record = PropertyMock(return_value=None)
        type(team)._extra_inning_record = fake_record

        assert team.extra_inning_wins is None

    def test_mlb_bad_int_property_returns_default(self):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        team = Team(None, 1)

        fake_record = PropertyMock(return_value='Bad-Bad')
        type(team)._extra_inning_record = fake_record

        assert team.extra_inning_wins is None
