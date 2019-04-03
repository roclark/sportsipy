from flexmock import flexmock
from mock import PropertyMock
from sportsreference.ncaab.schedule import Schedule
from sportsreference.ncaab.teams import Team


class TestNCAABTeams:
    def test_ncaab_schedule_returns_schedule(self, *args, **kwargs):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)

        team = Team(None, 1)

        assert len(team.schedule) == 0

    def test_two_point_field_goal_percentage_returns_default(self):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)

        team = Team(None, 1)
        mock_field_goals = PropertyMock(return_value=0)
        type(team).two_point_field_goals = mock_field_goals
        type(team).two_point_field_goal_attempts = mock_field_goals

        result = team.two_point_field_goal_percentage

        assert result == 0.0

    def test_opp_two_point_field_goal_percentage_returns_default(self):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)

        team = Team(None, 1)
        mock_field_goals = PropertyMock(return_value=0)
        type(team).opp_two_point_field_goals = mock_field_goals
        type(team).opp_two_point_field_goal_attempts = mock_field_goals

        result = team.opp_two_point_field_goal_percentage

        assert result == 0.0

    def test_defensive_rebounds_with_missing_data_returns_default(self):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)

        team = Team(None, 1)
        mock_offensive_rebounds = PropertyMock(return_value=None)
        type(team).offensive_rebounds = mock_offensive_rebounds

        result = team.defensive_rebounds

        assert not result

    def test_opp_defensive_rebounds_with_missing_data_returns_default(self):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)

        team = Team(None, 1)
        mock_offensive_rebounds = PropertyMock(return_value=None)
        type(team).opp_offensive_rebounds = mock_offensive_rebounds

        result = team.opp_defensive_rebounds

        assert not result

    def test_net_rating_with_missing_data_returns_default(self):
        flexmock(Team) \
            .should_receive('_parse_team_data') \
            .and_return(None)
        flexmock(Schedule) \
            .should_receive('_pull_schedule') \
            .and_return(None)

        team = Team(None, 1)
        mock_offensive_rating = PropertyMock(return_value=None)
        type(team).offensive_rating = mock_offensive_rating

        result = team.net_rating

        assert not result
