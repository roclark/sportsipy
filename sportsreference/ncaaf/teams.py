import re
import urllib2
from constants import PARSING_SCHEME, OFFENSIVE_STATS_URL, SEASON_PAGE_URL
from pyquery import PyQuery as pq
from .. import utils


class Team:
    def __init__(self, team_data):
        self._abbreviation = None
        self._name = None
        self._games = None
        self._wins = None
        self._losses = None
        self._conferene_wins = None
        self._conference_losses = None
        self._conference_win_percentage = None
        self._games_played = None
        self._points_for_per_game = None
        self._points_against_per_game = None
        self._points_difference = None
        self._margin_of_victory = None
        self._strength_of_schedule = None
        self._simple_rating_system = None
        self._pass_completions = None
        self._pass_attempts = None
        self._pass_completion_percentage = None
        self._pass_yards = None
        self._interceptions = None
        self._pass_touchdowns = None
        self._rush_attempts = None
        self._rush_yards = None
        self._rush_yards_per_attempt = None
        self._rush_touchdowns = None
        self._plays = None
        self._yards = None
        self._turnovers = None
        self._fumbles_lost = None
        self._yards_per_play = None
        self._pass_first_downs = None
        self._rush_first_downs = None
        self._first_downs_from_penalties = None
        self._first_downs = None
        self._penalties = None
        self._yards_from_penalties = None

        self._parse_team_data(team_data)

    def _parse_abbreviation(self, abbr):
        abbr = re.sub(r'/[0-9]+.html', '', abbr)
        return abbr.replace('/teams/', '')

    def _parse_team_data(self, team_data):
        for field in self.__dict__:
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
    def games(self):
        return int(self._games)

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
    def conference_wins(self):
        return int(self._conference_wins)

    @property
    def conference_losses(self):
        return int(self._conference_losses)

    @property
    def conference_win_percentage(self):
        return float(self._conference_win_percentage)

    @property
    def games_played(self):
        return int(self._games_played)

    @property
    def points_for(self):
        return float(self._points_for)

    @property
    def points_against(self):
        return float(self._points_against)

    @property
    def points_difference(self):
        return float(self._points_difference)

    @property
    def margin_of_victory(self):
        return float(self._margin_of_victory)

    @property
    def strength_of_schedule(self):
        return float(self._strength_of_schedule)

    @property
    def simple_rating_system(self):
        return float(self._simple_rating_system)

    @property
    def pass_completions(self):
        return float(self._pass_completions)

    @property
    def pass_attempts(self):
        return float(self._pass_attempts)

    @property
    def pass_completion_percentage(self):
        return float(self._pass_completion_percentage)

    @property
    def pass_yards(self):
        return float(self._pass_yards)

    @property
    def interceptions(self):
        return float(self._interceptions)

    @property
    def pass_touchdowns(self):
        return float(self._pass_touchdowns)

    @property
    def rush_attempts(self):
        return float(self._rush_attempts)

    @property
    def rush_yards(self):
        return float(self._rush_yards)

    @property
    def rush_yards_per_attempt(self):
        return float(self._rush_yards_per_attempt)

    @property
    def rush_touchdowns(self):
        return float(self._rush_touchdowns)

    @property
    def plays(self):
        return float(self._plays)

    @property
    def yards(self):
        return float(self._yards)

    @property
    def turnovers(self):
        return float(self._turnovers)

    @property
    def fumbles_lost(self):
        return float(self._fumbles_lost)

    @property
    def yards_per_play(self):
        return float(self._yards_per_play)

    @property
    def pass_first_downs(self):
        return float(self._pass_first_downs)

    @property
    def rush_first_downs(self):
        return float(self._rush_first_downs)

    @property
    def first_downs_from_penalties(self):
        return float(self._first_downs_from_penalties)

    @property
    def first_downs(self):
        return float(self._first_downs)

    @property
    def penalties(self):
        return float(self._penalties)

    @property
    def yards_from_penalties(self):
        return float(self._yards_from_penalties)


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
        team_stats_dict = {}

        if not year:
            year = utils.find_year_for_season('ncaaf')
        doc = pq(SEASON_PAGE_URL % year)
        teams_list = utils.get_stats_table(doc, 'div#div_standings')
        offense_doc = pq(OFFENSIVE_STATS_URL % year)
        offense_list = utils.get_stats_table(offense_doc, 'table#offense')
        for team_data in teams_list:
            # Skip the sub-header rows
            if 'class="over_header thead"' in str(team_data) or \
               'class="thead"' in str(team_data):
                continue
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            team_stats_dict[abbr] = {'data': team_data}

        for team_data in offense_list:
            # Skip the sub-header rows
            if 'class="over_header thead"' in str(team_data) or \
               'class="thead"' in str(team_data):
                continue
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            data = team_stats_dict[abbr]['data'] + team_data
            team = Team(data)
            self._teams.append(team)
