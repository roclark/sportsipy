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
        self._wins = None
        self._losses = None
        self._win_percentage = None
        self._games_played = None
        self._points_for = None
        self._points_against = None
        self._points_difference = None
        self._margin_of_victory = None
        self._strength_of_schedule = None
        self._simple_rating_system = None
        self._offensive_simple_rating_system = None
        self._defensive_simple_rating_system = None
        self._yards = None
        self._plays = None
        self._yards_per_play = None
        self._turnovers = None
        self._fumbles = None
        self._first_downs = None
        self._pass_completions = None
        self._pass_attempts = None
        self._pass_yards = None
        self._pass_touchdowns = None
        self._interceptions = None
        self._pass_net_yards_per_attempt = None
        self._pass_first_downs = None
        self._rush_attempts = None
        self._rush_yards = None
        self._rush_touchdowns = None
        self._rush_yards_per_attempt = None
        self._penalties = None
        self._yards_from_penalties = None
        self._first_downs_from_penalties = None
        self._percent_drives_with_points = None
        self._percent_drives_with_turnovers = None
        self._points_contributed_by_offense = None

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
    def wins(self):
        return int(self._wins)

    @property
    def losses(self):
        return int(self._losses)

    @property
    def win_percentage(self):
        return float(self._win_percentage)

    @property
    def games_played(self):
        return int(self._games_played)

    @property
    def points_for(self):
        return int(self._points_for)

    @property
    def points_against(self):
        return int(self._points_against)

    @property
    def points_difference(self):
        return int(self._points_difference)

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
    def offensive_rating_system(self):
        return float(self._offensive_rating_system)

    @property
    def defensive_rating_system(self):
        return float(self._defensive_rating_system)

    @property
    def yards(self):
        return int(self._yards)

    @property
    def plays(self):
        return int(self._plays)

    @property
    def yards_per_play(self):
        return float(self._yards_per_play)

    @property
    def turnovers(self):
        return int(self._turnovers)

    @property
    def fumbles(self):
        return int(self._fumbles)

    @property
    def first_downs(self):
        return int(self._first_downs)

    @property
    def pass_completions(self):
        return int(self._pass_completions)

    @property
    def pass_attempts(self):
        return int(self._pass_attempts)

    @property
    def pass_yards(self):
        return int(self._pass_yards)

    @property
    def pass_touchdowns(self):
        return int(self._pass_touchdowns)

    @property
    def interceptions(self):
        return int(self._interceptions)

    @property
    def pass_net_yards_per_attempt(self):
        return float(self._pass_net_yards_per_attempt)

    @property
    def pass_first_downs(self):
        return int(self._pass_first_downs)

    @property
    def rush_attempts(self):
        return int(self._rush_attempts)

    @property
    def rush_yards(self):
        return int(self._rush_yards)

    @property
    def rush_touchdowns(self):
        return int(self._rush_touchdowns)

    @property
    def rush_yards_per_attempt(self):
        return float(self._rush_yards_per_attempt)

    @property
    def penalties(self):
        return int(self._penalties)

    @property
    def yards_from_penalties(self):
        return int(self._yards_from_penalties)

    @property
    def first_downs_from_penalties(self):
        return int(self._first_downs_from_penalties)

    @property
    def percent_drives_with_points(self):
        return float(self._percent_drives_with_points)

    @property
    def percent_drives_with_turnovers(self):
        return float(self._percent_drives_with_turnovers)

    @property
    def points_contributed_by_offense(self):
        return float(self._points_contributed_by_offense)


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

    def _retrieve_all_teams(self, year):
        team_stats_dict = {}

        if not year:
            year = utils.find_year_for_season('nfl')
        doc = pq(SEASON_PAGE_URL % year)
        teams_list = utils.get_stats_table(doc, 'div#all_team_stats')
        afc_list = utils.get_stats_table(doc, 'table#AFC')
        nfc_list = utils.get_stats_table(doc, 'table#NFC')
        # Teams are listed in terms of rank with the first team being #1
        rank = 1
        for team_data in teams_list:
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            team_stats_dict[abbr] = {'data': team_data,
                                     'rank': rank}
            rank += 1

        for team_data in afc_list:
            # Skip the sub-header rows
            if 'class="thead onecell"' in str(team_data):
                continue
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            team_stats_dict[abbr]['data'] += team_data

        for team_data in nfc_list:
            # Skip the sub-header rows
            if 'class="thead onecell"' in str(team_data):
                continue
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            data = team_stats_dict[abbr]['data'] + team_data
            team = Team(data, team_stats_dict[abbr]['rank'])
            self._teams.append(team)
