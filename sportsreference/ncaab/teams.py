import re
import urllib2
from constants import (ADVANCED_OPPONENT_STATS_URL,
                       ADVANCED_STATS_URL,
                       BASIC_OPPONENT_STATS_URL,
                       BASIC_STATS_URL,
                       PARSING_SCHEME)
from pyquery import PyQuery as pq
from .. import utils


class Team:
    def __init__(self, team_data):
        self._abbreviation = None
        self._name = None
        self._games_played = None
        self._wins = None
        self._losses = None
        self._win_percentage = None
        self._simple_rating_system = None
        self._strength_of_schedule = None
        self._conference_wins = None
        self._conference_losses = None
        self._home_wins = None
        self._home_losses = None
        self._away_wins = None
        self._away_losses = None
        self._points = None
        self._opp_points = None
        self._minutes_played = None
        self._field_goals = None
        self._field_goal_attempts = None
        self._field_goal_percentage = None
        self._three_point_field_goals = None
        self._three_point_field_goal_attempts = None
        self._three_point_field_goal_percentage = None
        self._free_throws = None
        self._free_throw_attempts = None
        self._free_throw_percentage = None
        self._offensive_rebounds = None
        self._total_rebounds = None
        self._assists = None
        self._steals = None
        self._blocks = None
        self._turnovers = None
        self._personal_fouls = None
        self._opp_field_goals = None
        self._opp_field_goal_attempts = None
        self._opp_field_goal_percentage = None
        self._opp_three_point_field_goals = None
        self._opp_three_point_field_goal_attempts = None
        self._opp_three_point_field_goal_percentage = None
        self._opp_free_throws = None
        self._opp_free_throw_attempts = None
        self._opp_free_throw_percentage = None
        self._opp_offensive_rebounds = None
        self._opp_total_rebounds = None
        self._opp_assists = None
        self._opp_steals = None
        self._opp_blocks = None
        self._opp_turnovers = None
        self._opp_personal_fouls = None
        self._pace = None
        self._offensive_rating = None
        self._free_throw_attempt_rate = None
        self._three_point_attempt_rate = None
        self._true_shooting_percentage = None
        self._total_rebound_percentage = None
        self._assist_percentage = None
        self._steal_percentage = None
        self._block_percentage = None
        self._effective_field_goal_percentage = None
        self._turnover_percentage = None
        self._offensive_rebound_percentage = None
        self._free_throws_per_field_goal_attempt = None
        self._opp_offensive_rating = None
        self._opp_free_throw_attempt_rate = None
        self._opp_three_point_attempt_rate = None
        self._opp_true_shooting_percentage = None
        self._opp_total_rebound_percentage = None
        self._opp_assist_percentage = None
        self._opp_steal_percentage = None
        self._opp_block_percentage = None
        self._opp_effective_field_goal_percentage = None
        self._opp_turnover_percentage = None
        self._opp_offensive_rebound_percentage = None
        self._opp_free_throws_per_field_goal_attempt = None

        self._parse_team_data(team_data)

    def _parse_team_data(self, team_data):
        for field in self.__dict__:
            value = utils.parse_field(PARSING_SCHEME,
                                      team_data,
                                      # Remove the '_' from the name
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
    def wins(self):
        return int(self._wins)

    @property
    def losses(self):
        return int(self._losses)

    @property
    def win_percentage(self):
        return float(self._win_percentage)

    @property
    def simple_rating_system(self):
        return float(self._simple_rating_system)

    @property
    def strength_of_schedule(self):
        return float(self._strength_of_schedule)

    @property
    def conference_wins(self):
        return int(self._conference_wins)

    @property
    def conference_losses(self):
        return int(self._conference_losses)

    @property
    def home_wins(self):
        return int(self._home_wins)

    @property
    def home_losses(self):
        return int(self._home_losses)

    @property
    def away_wins(self):
        return int(self._away_wins)

    @property
    def away_losses(self):
        return int(self._away_losses)

    @property
    def points(self):
        return int(self._points)

    @property
    def opp_points(self):
        return int(self._opp_points)

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
    def pace(self):
        return float(self._pace)

    @property
    def offensive_rating(self):
        return float(self._offensive_rating)

    @property
    def free_throw_attempt_rate(self):
        return float(self._free_throw_attempt_rate)

    @property
    def three_point_attempt_rate(self):
        return float(self._three_point_attempt_rate)

    @property
    def true_shooting_percentage(self):
        return float(self._true_shooting_percentage)

    @property
    def total_rebound_percentage(self):
        return float(self._total_rebound_percentage)

    @property
    def assist_percentage(self):
        return float(self._assist_percentage)

    @property
    def steal_percentage(self):
        return float(self._steal_percentage)

    @property
    def block_percentage(self):
        return float(self._block_percentage)

    @property
    def effective_field_goal_percentage(self):
        return float(self._effective_field_goal_percentage)

    @property
    def turnover_percentage(self):
        return float(self._turnover_percentage)

    @property
    def offensive_rebound_percentage(self):
        return float(self._offensive_rebound_percentage)

    @property
    def free_throws_per_field_goal_attempt(self):
        return float(self._free_throws_per_field_goal_attempt)

    @property
    def opp_offensive_rating(self):
        return float(self._opp_offensive_rating)

    @property
    def opp_free_throw_attempt_rate(self):
        return float(self._opp_free_throw_attempt_rate)

    @property
    def opp_three_point_attempt_rate(self):
        return float(self._opp_three_point_attempt_rate)

    @property
    def opp_true_shooting_percentage(self):
        return float(self._opp_true_shooting_percentage)

    @property
    def opp_total_rebound_percentage(self):
        return float(self._opp_total_rebound_percentage)

    @property
    def opp_assist_percentage(self):
        return float(self._opp_assist_percentage)

    @property
    def opp_steal_percentage(self):
        return float(self._opp_steal_percentage)

    @property
    def opp_block_percentage(self):
        return float(self._opp_block_percentage)

    @property
    def opp_effective_field_goal_percentage(self):
        return float(self._opp_effective_field_goal_percentage)

    @property
    def opp_turnover_percentage(self):
        return float(self._opp_turnover_percentage)

    @property
    def opp_offensive_rebound_percentage(self):
        return float(self._opp_offensive_rebound_percentage)

    @property
    def opp_free_throws_per_field_goal_attempt(self):
        return float(self._opp_free_throws_per_field_goal_attempt)


class Teams:
    def __init__(self, year=None, short=False):
        self._teams = []

        self._retrieve_all_teams(year)

    def __getitem__(self, abbreviation):
        for team in self._teams:
            if team.abbreviation.upper() == abbreviation.upper():
                return team
        raise ValueError('Team abbreviation %s not found' % abbreviation)

    def __call__(self, abbreviation):
        return self.__getitem__(abbreviation)

    def __repr__(self):
        return self._teams

    def __iter__(self):
        return iter(self.__repr__())

    def _add_stats_data(self, teams_list, team_data_dict):
        for team_data in teams_list:
            if 'class="over_header thead"' in str(team_data) or\
               'class="thead"' in str(team_data):
                continue
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            try:
                team_data_dict[abbr]['data'] += team_data
            except KeyError:
                team_data_dict[abbr] = {'data': team_data}
        return team_data_dict

    def _retrieve_all_teams(self, year):
        team_data_dict = {}

        if not year:
            year = utils.find_year_for_season('ncaab')
        doc = pq(BASIC_STATS_URL % year)
        teams_list = utils.get_stats_table(doc, 'table#basic_school_stats')
        doc = pq(BASIC_OPPONENT_STATS_URL % year)
        opp_list = utils.get_stats_table(doc, 'table#basic_opp_stats')
        doc = pq(ADVANCED_STATS_URL % year)
        adv_teams_list = utils.get_stats_table(doc, 'table#adv_school_stats')
        doc = pq(ADVANCED_OPPONENT_STATS_URL % year)
        adv_opp_list = utils.get_stats_table(doc, 'table#adv_opp_stats')

        for stats_list in [teams_list, opp_list, adv_teams_list, adv_opp_list]:
            team_data_dict = self._add_stats_data(stats_list, team_data_dict)

        for team_data in team_data_dict.values():
            team = Team(team_data['data'])
            self._teams.append(team)
