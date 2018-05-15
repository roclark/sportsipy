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
        self._average_age = None
        self._games_played = None
        self._wins = None
        self._losses = None
        self._overtime_losses = None
        self._points = None
        self._points_percentage = None
        self._goals_for = None
        self._goals_against = None
        self._simple_rating_system = None
        self._strength_of_schedule = None
        self._total_goals_per_game = None
        self._power_play_goals = None
        self._power_play_opportunities = None
        self._power_play_percentage = None
        self._power_play_goals_against = None
        self._power_play_opportunities_against = None
        self._penalty_killing_percentage = None
        self._short_handed_goals = None
        self._short_handed_goals_against = None
        self._shots_on_goal = None
        self._shooting_percentage = None
        self._shots_against = None
        self._save_percentage = None
        self._pdo_at_even_strength = None

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
    def average_age(self):
        return float(self._average_age)

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
    def overtime_losses(self):
        return int(self._overtime_losses)

    @property
    def points(self):
        return int(self._points)

    @property
    def points_percentage(self):
        return float(self._points_percentage)

    @property
    def goals_for(self):
        return int(self._goals_for)

    @property
    def goals_against(self):
        return int(self._goals_against)

    @property
    def simple_rating_system(self):
        return float(self._simple_rating_system)

    @property
    def strength_of_schedule(self):
        return float(self._strength_of_schedule)

    @property
    def total_goals_per_game(self):
        return float(self._total_goals_per_game)

    @property
    def power_play_goals(self):
        return int(self._power_play_goals)

    @property
    def power_play_opportunities(self):
        return int(self._power_play_opportunities)

    @property
    def power_play_percentage(self):
        return float(self._power_play_percentage)

    @property
    def power_play_goals_against(self):
        return int(self._power_play_goals_against)

    @property
    def power_play_opportunities_against(self):
        return int(self._power_play_opportunities_against)

    @property
    def penalty_killing_percentage(self):
        return float(self._penalty_killing_percentage)

    @property
    def short_handed_goals(self):
        return int(self._short_handed_goals)

    @property
    def short_handed_goals_against(self):
        return int(self._short_handed_goals_against)

    @property
    def shots_on_goal(self):
        return int(self._shots_on_goal)

    @property
    def shooting_percentage(self):
        return float(self._shooting_percentage)

    @property
    def shots_against(self):
        return int(self._shots_against)

    @property
    def save_percentage(self):
        return float(self._save_percentage)

    @property
    def pdo_at_even_strength(self):
        return float(self._pdo_at_even_strength)


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
        if not year:
            year = utils.find_year_for_season('nhl')
        doc = pq(SEASON_PAGE_URL % year)
        teams_list = utils.get_stats_table(doc, 'div#all_stats')
        # Teams are listed in terms of rank with the first team being #1
        rank = 1
        for team_data in teams_list:
            team = Team(team_data, rank)
            self._teams.append(team)
            rank += 1
