import pandas as pd
import re
from .constants import PARSING_SCHEME, SEASON_PAGE_URL
from pyquery import PyQuery as pq
from .. import utils
from .schedule import Schedule


class Team:
    """
    An object containing all of a team's season information.

    Finds and parses all team stat information and identifiers, such as rank,
    name, and abbreviation, and sets them as properties which can be directly
    read from for easy reference.
    """
    def __init__(self, team_data, rank, year=None):
        """
        Parse all of the attributes located in the HTML data.

        Once Team is invoked, it parses all of the listed attributes for the
        team which can be found in the passed HTML data. All attributes below
        are properties which can be directly read for easy reference.

        Parameters
        ----------
        team_data : string
            A string containing all of the rows of stats for a given team. If
            multiple tables are being referenced, this will be comprised of
            multiple rows in a single string.
        rank : int
            A team's position in the league based on the number of points they
            obtained during the season.
        year : string (optional)
            The requested year to pull stats from.
        """
        self._year = year
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
        """
        Parses a value for every attribute.

        This function looks through every attribute with the exception of
        '_rank' and retrieves the value according to the parsing scheme and
        index of the attribute from the passed HTML data. Once the value is
        retrieved, the attribute's value is updated with the returned result.

        Note that this method is called directly once Team is invoked and does
        not need to be called manually.

        Parameters
        ----------
        team_data : string
            A string containing all of the rows of stats for a given team. If
            multiple tables are being referenced, this will be comprised of
            multiple rows in a single string.
        """
        for field in self.__dict__:
            # The rank attribute is passed directly to the class during
            # instantiation.
            if field == '_rank' or \
               field == '_year':
                continue
            value = utils._parse_field(PARSING_SCHEME,
                                       team_data,
                                       str(field)[1:])
            setattr(self, field, value)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the string abbreviation of the
        team, such as 'DET'.
        """
        fields_to_include = {
            'abbreviation': self.abbreviation,
            'average_age': self.average_age,
            'games_played': self.games_played,
            'goals_against': self.goals_against,
            'goals_for': self.goals_for,
            'losses': self.losses,
            'name': self.name,
            'overtime_losses': self.overtime_losses,
            'pdo_at_even_strength': self.pdo_at_even_strength,
            'penalty_killing_percentage': self.penalty_killing_percentage,
            'points': self.points,
            'points_percentage': self.points_percentage,
            'power_play_goals': self.power_play_goals,
            'power_play_goals_against': self.power_play_goals_against,
            'power_play_opportunities': self.power_play_opportunities,
            'power_play_opportunities_against':
            self.power_play_opportunities_against,
            'power_play_percentage': self.power_play_percentage,
            'rank': self.rank,
            'save_percentage': self.save_percentage,
            'shooting_percentage': self.shooting_percentage,
            'short_handed_goals': self.short_handed_goals,
            'short_handed_goals_against': self.short_handed_goals_against,
            'shots_against': self.shots_against,
            'shots_on_goal': self.shots_on_goal,
            'simple_rating_system': self.simple_rating_system,
            'strength_of_schedule': self.strength_of_schedule,
            'total_goals_per_game': self.total_goals_per_game,
            'wins': self.wins
        }
        return pd.DataFrame([fields_to_include], index=[self._abbreviation])

    @property
    def rank(self):
        """
        Returns an ``int`` of the team's rank based on the number of points
        they obtained in the season.
        """
        return int(self._rank)

    @property
    def abbreviation(self):
        """
        Returns a ``string`` of the team's abbreviation, such as 'DET' for the
        Detroit Red Wings.
        """
        return self._abbreviation

    @property
    def schedule(self):
        """
        Returns an instance of the Schedule class containing the team's
        complete schedule for the season.
        """
        return Schedule(self._abbreviation, self._year)

    @property
    def name(self):
        """
        Returns a ``string`` of the team's full name, such as 'Detroit Red
        Wings'.
        """
        return self._name

    @property
    def average_age(self):
        """
        Returns a ``float`` of the average age of all players on the team,
        weighted by their time on ice.
        """
        return float(self._average_age)

    @property
    def games_played(self):
        """
        Returns an ``int`` of the total number of games the team has played in
        the season.
        """
        return int(self._games_played)

    @property
    def wins(self):
        """
        Returns an ``int`` of the total number of wins the team had in the
        season.
        """
        return int(self._wins)

    @property
    def losses(self):
        """
        Returns an ``int`` of the total number of losses the team had in the
        season.
        """
        return int(self._losses)

    @property
    def overtime_losses(self):
        """
        Returns an ``int`` of the total number of overtime losses the team had
        in the season.
        """
        return int(self._overtime_losses)

    @property
    def points(self):
        """
        Returns an ``int`` of the total number of points the team gained in the
        season.
        """
        return int(self._points)

    @property
    def points_percentage(self):
        """
        Returns a ``float`` denoting the percentage of points gained divided by
        the maximum possible points available during the season. Percentage
        ranges from 0-1.
        """
        return float(self._points_percentage)

    @property
    def goals_for(self):
        """
        Returns an ``int`` of the total number of goals a team scored during
        the season.
        """
        return int(self._goals_for)

    @property
    def goals_against(self):
        """
        Returns an ``int`` of the total number of goals opponents scored
        against the team during the season.
        """
        return int(self._goals_against)

    @property
    def simple_rating_system(self):
        """
        Returns a ``float`` which takes into account the average goal
        differential vs a team's strength of schedule. The league average
        evaluates to 0.0. Teams which have a positive score are comparatively
        stronger than average while teams with a negative score are weaker.
        """
        return float(self._simple_rating_system)

    @property
    def strength_of_schedule(self):
        """
        Returns a ``float`` denoting a team's strength of schedule, based on
        goals scores and conceded. Higher values result in more challenging
        schedules while 0.0 is an average schedule.
        """
        return float(self._strength_of_schedule)

    @property
    def total_goals_per_game(self):
        """
        Returns a ``float`` for the average number of goals scored per game.
        """
        return float(self._total_goals_per_game)

    @property
    def power_play_goals(self):
        """
        Returns an ``int`` of the total number of power play goals scored.
        """
        return int(self._power_play_goals)

    @property
    def power_play_opportunities(self):
        """
        Returns an ``int`` of the total number of power play opportunities for
        a team during the season.
        """
        return int(self._power_play_opportunities)

    @property
    def power_play_percentage(self):
        """
        Returns a ``float`` denoting the percentage of power play opportunities
        where the team has scored. Percentage ranges from 0-100.
        """
        return float(self._power_play_percentage)

    @property
    def power_play_goals_against(self):
        """
        Returns an ``int`` of the total number of power play goals conceded.
        """
        return int(self._power_play_goals_against)

    @property
    def power_play_opportunities_against(self):
        """
        Returns an ``int`` of the total number of power play opportunities for
        the opponents during the season.
        """
        return int(self._power_play_opportunities_against)

    @property
    def penalty_killing_percentage(self):
        """
        Returns a ``float`` denoting the percentage of power plays that have
        been successfully defended without a goal being conceded. Percentage
        ranges from 0-100.
        """
        return float(self._penalty_killing_percentage)

    @property
    def short_handed_goals(self):
        """
        Returns an ``int`` of the number of short handed goals the team has
        scored during the season.
        """
        return int(self._short_handed_goals)

    @property
    def short_handed_goals_against(self):
        """
        Returns an ``int`` of the number of short handed goals the team has
        conceded during the season.
        """
        return int(self._short_handed_goals_against)

    @property
    def shots_on_goal(self):
        """
        Returns an ``int`` of the total number of shots on goal the team made
        during the season.
        """
        return int(self._shots_on_goal)

    @property
    def shooting_percentage(self):
        """
        Returns a ``float`` denoting the percentage of shots to goals during
        the season. Percentage ranges from 0-100.
        """
        return float(self._shooting_percentage)

    @property
    def shots_against(self):
        """
        Returns an ``int`` of the total number of shots on goal the team's
        opponents made during the season.
        """
        return int(self._shots_against)

    @property
    def save_percentage(self):
        """
        Returns a ``float`` denoting the percentage of shots the team has saved
        during the season. Percentage ranges from 0-1.
        """
        return float(self._save_percentage)

    @property
    def pdo_at_even_strength(self):
        """
        Returns a ``float`` of the PDO at even strength which equates to the
        shooting percentage plus the save percentage.
        """
        return float(self._pdo_at_even_strength)


class Teams:
    """
    A list of all NHL teams and their stats in a given year.

    Finds and retrieves a list of all NHL teams from www.hockey-reference.com
    and creates a Team instance for every team that participated in the league
    in a given year. The Team class comprises a list of all major stats and a
    few identifiers for the requested season.
    """
    def __init__(self, year=None):
        """
        Get a list of all Team instances

        Once Teams is invoked, it retrieves a list of all NHL teams in the
        desired season and adds them to the '_teams' attribute.

        Parameters
        ----------
        year : string (optional)
            The requested year to pull stats from.
        """
        self._teams = []

        self._retrieve_all_teams(year)

    def __getitem__(self, abbreviation):
        """
        Return a specified team.

        Returns a team's instance in the Teams class as specified by the team's
        abbreviation.

        Parameters
        ----------
        abbreviation : string
            An NHL team's three letter abbreviation (ie. 'DET' for Detroit Red
            Wings).

        Returns
        -------
        Team instance
            If the requested team can be found, its Team instance is returned.

        Raises
        ------
        ValueError
            If the requested team is not present within the Teams list.
        """
        for team in self._teams:
            if team.abbreviation.upper() == abbreviation.upper():
                return team
        raise ValueError('Team abbreviation %s not found' % abbreviation)

    def __call__(self, abbreviation):
        """
        Return a specified team.

        Returns a team's instance in the Teams class as specified by the team's
        abbreviation. This method is a wrapper for __getitem__.

        Parameters
        ----------
        abbreviation : string
            An NHL team's three letter abbreviation (ie. 'DET' for Detroit Red
            Wings).

        Returns
        -------
        Team instance
            If the requested team can be found, its Team instance is returned.
        """
        return self.__getitem__(abbreviation)

    def __repr__(self):
        """Returns a ``list`` of all NHL teams for the given season."""
        return self._teams

    def __iter__(self):
        """Returns an iterator of all of the NHL teams for a given season."""
        return iter(self.__repr__())

    def __len__(self):
        """Returns the number of NHL teams for a given season."""
        return len(self.__repr__())

    def _retrieve_all_teams(self, year):
        """
        Find and create Team instances for all teams in the given season.

        For a given season, parses the specified NHL stats table and finds all
        requested stats. Each team then has a Team instance created which
        includes all requested stats and a few identifiers, such as the team's
        name and abbreviation. All of the individual Team instances are added
        to a list.

        Note that this method is called directly once Teams is invoked and does
        not need to be called manually.

        Parameters
        ----------
        year : string
            The requested year to pull stats from.
        """
        if not year:
            year = utils._find_year_for_season('nhl')
        doc = pq(SEASON_PAGE_URL % year)
        teams_list = utils._get_stats_table(doc, 'div#all_stats')
        # Teams are listed in terms of rank with the first team being #1
        rank = 1
        for team_data in teams_list:
            team = Team(team_data, rank, year)
            self._teams.append(team)
            rank += 1

    @property
    def dataframes(self):
        """
        Returns a pandas DataFrame where each row is a representation of the
        Team class. Rows are indexed by the team abbreviation.
        """
        frames = []
        for team in self.__iter__():
            frames.append(team.dataframe)
        return pd.concat(frames)
