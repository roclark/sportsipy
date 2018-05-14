import re
import urllib2
from constants import PARSING_SCHEME, SEASON_PAGE_URL
from pyquery import PyQuery as pq
from .. import utils


class Team:
    def __init__(self, team_data, rank):
        self._rank = rank
        self._abbreviation = None
        self._name = None
        self._games_played = None
        self._minutes_played = None
        self._field_goals = None
        self._field_goal_attempts = None
        self._field_goal_percentage = None
        self._three_point_field_goals = None
        self._three_point_field_goal_attempts = None
        self._three_point_field_goal_percentage = None
        self._two_point_field_goals = None
        self._two_point_field_goal_attempts = None
        self._two_point_field_goal_percentage = None
        self._free_throws = None
        self._free_throw_attempts = None
        self._free_throw_percentage = None
        self._offensive_rebounds = None
        self._defensive_rebounds = None
        self._total_rebounds = None
        self._assists = None
        self._steals = None
        self._blocks = None
        self._turnovers = None
        self._personal_fouls = None
        self._points = None
        self._opp_minutes_played = None
        self._opp_field_goals = None
        self._opp_field_goal_attempts = None
        self._opp_field_goal_percentage = None
        self._opp_three_point_field_goals = None
        self._opp_three_point_field_goal_attempts = None
        self._opp_three_point_field_goal_percentage = None
        self._opp_two_point_field_goals = None
        self._opp_two_point_field_goal_attempts = None
        self._opp_two_point_field_goal_percentage = None
        self._opp_free_throws = None
        self._opp_free_throw_attempts = None
        self._opp_free_throw_percentage = None
        self._opp_offensive_rebounds = None
        self._opp_defensive_rebounds = None
        self._opp_total_rebounds = None
        self._opp_assists = None
        self._opp_steals = None
        self._opp_blocks = None
        self._opp_turnovers = None
        self._opp_personal_fouls = None
        self._opp_points = None

        self._parse_team_data(team_data)

    def _parse_team_data(self, team_data):
        for field in self.__dict__:
            # The rank attribute is passed directly to the class during
            # instantiation.
            if field == '_rank':
                continue
            value = utils.parse_field(PARSING_SCHEME,
                                      team_data,
                                      str(field)[1:])
            setattr(self, field, value)

    @property
    def rank(self):
        return int(self._rank)

    @property
    def abbreviation(self):
        return self._abbreviation

    @property
    def name(self):
        return self._name

    @property
    def games_played(self):
        return int(self._games_played)

    @property
    def minutes_played(self):
        return int(self._minutes_played)

    @property
    def field_goals(self):
        return int(self._field_goals)

    @property
    def field_goal_attempts(self):
        return int(self._field_goal_attempts)

    @property
    def field_goal_percentage(self):
        return float(self._field_goal_percentage)

    @property
    def three_point_field_goals(self):
        return int(self._three_point_field_goals)

    @property
    def three_point_field_goal_attempts(self):
        return int(self._three_point_field_goal_attempts)

    @property
    def three_point_field_goal_percentage(self):
        return float(self._three_point_field_goal_percentage)

    @property
    def two_point_field_goals(self):
        return int(self._two_point_field_goals)

    @property
    def two_point_field_goal_attempts(self):
        return int(self._two_point_field_goal_attempts)

    @property
    def two_point_field_goal_percentage(self):
        return float(self._two_point_field_goal_percentage)

    @property
    def free_throws(self):
        return int(self._free_throws)

    @property
    def free_throw_attempts(self):
        return int(self._free_throw_attempts)

    @property
    def free_throw_percentage(self):
        return float(self._free_throw_percentage)

    @property
    def offensive_rebounds(self):
        return int(self._offensive_rebounds)

    @property
    def defensive_rebounds(self):
        return int(self._defensive_rebounds)

    @property
    def total_rebounds(self):
        return int(self._total_rebounds)

    @property
    def assists(self):
        return int(self._assists)

    @property
    def steals(self):
        return int(self._steals)

    @property
    def blocks(self):
        return int(self._blocks)

    @property
    def turnovers(self):
        return int(self._turnovers)

    @property
    def personal_fouls(self):
        return int(self._personal_fouls)

    @property
    def points(self):
        return int(self._points)

    @property
    def opp_minutes_played(self):
        return int(self._opp_minutes_played)

    @property
    def opp_field_goals(self):
        return int(self._opp_field_goals)

    @property
    def opp_field_goal_attempts(self):
        return int(self._opp_field_goal_attempts)

    @property
    def opp_field_goal_percentage(self):
        return float(self._opp_field_goal_percentage)

    @property
    def opp_three_point_field_goals(self):
        return int(self._opp_three_point_field_goals)

    @property
    def opp_three_point_field_goal_attempts(self):
        return int(self._opp_three_point_field_goal_attempts)

    @property
    def opp_three_point_field_goal_percentage(self):
        return float(self._opp_three_point_field_goal_percentage)

    @property
    def opp_two_point_field_goals(self):
        return int(self._opp_two_point_field_goals)

    @property
    def opp_two_point_field_goal_attempts(self):
        return int(self._opp_two_point_field_goal_attempts)

    @property
    def opp_two_point_field_goal_percentage(self):
        return float(self._opp_two_point_field_goal_percentage)

    @property
    def opp_free_throws(self):
        return int(self._opp_free_throws)

    @property
    def opp_free_throw_attempts(self):
        return int(self._opp_free_throw_attempts)

    @property
    def opp_free_throw_percentage(self):
        return float(self._opp_free_throw_percentage)

    @property
    def opp_offensive_rebounds(self):
        return int(self._opp_offensive_rebounds)

    @property
    def opp_defensive_rebounds(self):
        return int(self._opp_defensive_rebounds)

    @property
    def opp_total_rebounds(self):
        return int(self._opp_total_rebounds)

    @property
    def opp_assists(self):
        return int(self._opp_assists)

    @property
    def opp_steals(self):
        return int(self._opp_steals)

    @property
    def opp_blocks(self):
        return int(self._opp_blocks)

    @property
    def opp_turnovers(self):
        return int(self._opp_turnovers)

    @property
    def opp_personal_fouls(self):
        return int(self._opp_personal_fouls)

    @property
    def opp_points(self):
        return int(self._opp_points)


class Teams:
    def __init__(self, year=None, short=False):
        self._teams = []

        self._retrieve_all_teams(year)

    def __getitem__(self, abbreviation):
        for team in self._teams:
            if team.abbreviation.upper() == abbreviation.upper():
                return team
        raise ValueError('Team abbreviation %s not found' % abbreviation)

    def __repr__(self):
        return self._teams

    def __iter__(self):
        return iter(self.__repr__())

    def _retrieve_all_teams(self, year):
        team_data_dict = {}

        if not year:
            year = utils.find_year_for_season('nba')
        doc = pq(SEASON_PAGE_URL % year)
        teams_list = utils.get_stats_table(doc, 'div#all_team-stats-base')
        opp_teams_list = utils.get_stats_table(doc,
                                               'div#all_opponent-stats-base')
        # Teams are listed in terms of rank with the first team being #1
        rank = 1
        for team_data in teams_list:
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            team_data_dict[abbr] = {'data': team_data,
                                    'rank': rank}
            rank += 1

        for team_data in opp_teams_list:
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            data = team_data_dict[abbr]['data'] + team_data
            team = Team(data, team_data_dict[abbr]['rank'])
            self._teams.append(team)
