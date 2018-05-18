import re
from .constants import PARSING_SCHEME, OFFENSIVE_STATS_URL, SEASON_PAGE_URL
from pyquery import PyQuery as pq
from .. import utils


class Team:
    def __init__(self, team_data):
        self._abbreviation = None
        self._name = None
        self._games = None
        self._wins = None
        self._losses = None
        self._win_percentage = None
        self._conference_wins = None
        self._conference_losses = None
        self._conference_win_percentage = None
        self._points_per_game = None
        self._points_against_per_game = None
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

    def _parse_team_data(self, team_data):
        for field in self.__dict__:
            value = utils.parse_field(PARSING_SCHEME,
                                      team_data,
                                      str(field)[1:])
            setattr(self, field, value)

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
    def points_per_game(self):
        return float(self._points_per_game)

    @property
    def points_against_per_game(self):
        return float(self._points_against_per_game)

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
    def __init__(self, year=None):
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

    def __len__(self):
        return len(self.__repr__())

    def _add_stats_data(self, teams_list, team_data_dict):
        for team_data in teams_list:
            # Skip the sub-header rows
            if 'class="over_header thead"' in str(team_data) or \
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
            year = utils.find_year_for_season('ncaaf')
        doc = pq(SEASON_PAGE_URL % year)
        teams_list = utils.get_stats_table(doc, 'div#div_standings')
        offense_doc = pq(OFFENSIVE_STATS_URL % year)
        offense_list = utils.get_stats_table(offense_doc, 'table#offense')
        for stats_list in [teams_list, offense_list]:
            team_data_dict = self._add_stats_data(stats_list, team_data_dict)

        for team_data in team_data_dict.values():
            team = Team(team_data['data'])
            self._teams.append(team)
