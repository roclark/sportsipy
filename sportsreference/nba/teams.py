import pandas as pd
import re
from .constants import PARSING_SCHEME, SEASON_PAGE_URL
from pyquery import PyQuery as pq
from ..decorators import float_property_decorator, int_property_decorator
from .. import utils
from .roster import Roster
from .schedule import Schedule


class Team:
    """
    An object containing all of a team's season information.

    Finds and parses all team stat information and identifiers, such as rank,
    name, and abbreviation, and sets them as properties which can be directly
    read from for easy reference.

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
    def __init__(self, team_data, rank, year=None):
        self._year = year
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
            'assists': self.assists,
            'blocks': self.blocks,
            'defensive_rebounds': self.defensive_rebounds,
            'field_goal_attempts': self.field_goal_attempts,
            'field_goal_percentage': self.field_goal_percentage,
            'field_goals': self.field_goals,
            'free_throw_attempts': self.free_throw_attempts,
            'free_throw_percentage': self.free_throw_percentage,
            'free_throws': self.free_throws,
            'games_played': self.games_played,
            'minutes_played': self.minutes_played,
            'name': self.name,
            'offensive_rebounds': self.offensive_rebounds,
            'opp_assists': self.opp_assists,
            'opp_blocks': self.opp_blocks,
            'opp_defensive_rebounds': self.opp_defensive_rebounds,
            'opp_field_goal_attempts': self.opp_field_goal_attempts,
            'opp_field_goal_percentage': self.opp_field_goal_percentage,
            'opp_field_goals': self.opp_field_goals,
            'opp_free_throw_attempts': self.opp_free_throw_attempts,
            'opp_free_throw_percentage': self.opp_free_throw_percentage,
            'opp_free_throws': self.opp_free_throws,
            'opp_offensive_rebounds': self.opp_offensive_rebounds,
            'opp_personal_fouls': self.opp_personal_fouls,
            'opp_points': self.opp_points,
            'opp_steals': self.opp_steals,
            'opp_three_point_field_goal_attempts':
            self.opp_three_point_field_goal_attempts,
            'opp_three_point_field_goal_percentage':
            self.opp_three_point_field_goal_percentage,
            'opp_three_point_field_goals': self.opp_three_point_field_goals,
            'opp_total_rebounds': self.opp_total_rebounds,
            'opp_turnovers': self.opp_turnovers,
            'opp_two_point_field_goal_attempts':
            self.opp_two_point_field_goal_attempts,
            'opp_two_point_field_goal_percentage':
            self.opp_two_point_field_goal_percentage,
            'opp_two_point_field_goals': self.opp_two_point_field_goals,
            'personal_fouls': self.personal_fouls,
            'points': self.points,
            'rank': self.rank,
            'steals': self.steals,
            'three_point_field_goal_attempts':
            self.three_point_field_goal_attempts,
            'three_point_field_goal_percentage':
            self.three_point_field_goal_percentage,
            'three_point_field_goals': self.three_point_field_goals,
            'total_rebounds': self.total_rebounds,
            'turnovers': self.turnovers,
            'two_point_field_goal_attempts':
            self.two_point_field_goal_attempts,
            'two_point_field_goal_percentage':
            self.two_point_field_goal_percentage,
            'two_point_field_goals': self.two_point_field_goals
        }
        return pd.DataFrame([fields_to_include], index=[self._abbreviation])

    @int_property_decorator
    def rank(self):
        """
        Returns an ``int`` of the team's rank based on the number of points
        they score per game.
        """
        return self._rank

    @property
    def abbreviation(self):
        """
        Returns a ``string`` of the team's abbreviation, such as 'DET' for the
        Detroit Pistons.
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
    def roster(self):
        """
        Returns an instance of the Roster class containing all players for the
        team during the season with all career stats.
        """
        return Roster(self._abbreviation, self._year)

    @property
    def name(self):
        """
        Returns a ``string`` of the team's full name, such as 'Detroit
        Pistons'.
        """
        return self._name

    @int_property_decorator
    def games_played(self):
        """
        Returns an ``int`` of the total number of games the team has played
        during the season.
        """
        return self._games_played

    @int_property_decorator
    def minutes_played(self):
        """
        Returns an ``int`` of the total number of minutes played by all players
        on the team during the season.
        """
        return self._minutes_played

    @int_property_decorator
    def field_goals(self):
        """
        Returns an ``int`` of the total number of field goals the team has made
        during the season.
        """
        return self._field_goals

    @int_property_decorator
    def field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of field goals the team has
        attempted during the season.
        """
        return self._field_goal_attempts

    @float_property_decorator
    def field_goal_percentage(self):
        """
        Returns a ``float`` of the percentage of field goals made divided by
        the number of attempts. Percentage ranges from 0-1.
        """
        return self._field_goal_percentage

    @int_property_decorator
    def three_point_field_goals(self):
        """
        Returns an ``int`` of the total number of three point field goals the
        team has made during the season.
        """
        return self._three_point_field_goals

    @int_property_decorator
    def three_point_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of three point field goals the
        team has attempted during the season.
        """
        return self._three_point_field_goal_attempts

    @float_property_decorator
    def three_point_field_goal_percentage(self):
        """
        Returns a ``float`` of the percentage of three point field goals made
        divided by the number of attempts. Percentage ranges from 0-1.
        """
        return self._three_point_field_goal_percentage

    @int_property_decorator
    def two_point_field_goals(self):
        """
        Returns an ``int`` of the total number of two point field goals the
        team has made during the season.
        """
        return self._two_point_field_goals

    @int_property_decorator
    def two_point_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of two point field goals the
        team has attempted during the season.
        """
        return self._two_point_field_goal_attempts

    @float_property_decorator
    def two_point_field_goal_percentage(self):
        """
        Returns a ``float`` of the percentage of two point field goals made
        divided by the number of attempts. Percentage ranges from 0-1.
        """
        return self._two_point_field_goal_percentage

    @int_property_decorator
    def free_throws(self):
        """
        Returns an ``int`` of the total number of free throws made during the
        season.
        """
        return self._free_throws

    @int_property_decorator
    def free_throw_attempts(self):
        """
        Returns an ``int`` of the total number of free throw attempts during
        the season.
        """
        return self._free_throw_attempts

    @float_property_decorator
    def free_throw_percentage(self):
        """
        Returns a ``float`` of the percentage of free throws made divided by
        the attempts. Percentage ranges from 0-1.
        """
        return self._free_throw_percentage

    @int_property_decorator
    def offensive_rebounds(self):
        """
        Returns an ``int`` of the total number of offensive rebounds the team
        has grabbed.
        """
        return self._offensive_rebounds

    @int_property_decorator
    def defensive_rebounds(self):
        """
        Returns an ``int`` of the total number of defensive rebounds the team
        has grabbed.
        """
        return self._defensive_rebounds

    @int_property_decorator
    def total_rebounds(self):
        """
        Returns an ``int`` of the total number of rebounds the team has
        grabbed.
        """
        return self._total_rebounds

    @int_property_decorator
    def assists(self):
        """
        Returns an ``int`` of the total number of field goals that were
        assisted.
        """
        return self._assists

    @int_property_decorator
    def steals(self):
        """
        Returns an ``int`` of the total number of times the team stole the ball
        from the opponent.
        """
        return self._steals

    @int_property_decorator
    def blocks(self):
        """
        Returns an ``int`` of the total number of times the team blocked an
        opponent's shot.
        """
        return self._blocks

    @int_property_decorator
    def turnovers(self):
        """
        Returns an ``int`` of the total number of times the team has turned the
        ball over.
        """
        return self._turnovers

    @int_property_decorator
    def personal_fouls(self):
        """
        Returns an ``int`` of the total number of times the team has fouled an
        opponent.
        """
        return self._personal_fouls

    @int_property_decorator
    def points(self):
        """
        Returns an ``int`` of the total number of points the team has scored
        during the season.
        """
        return self._points

    @int_property_decorator
    def opp_field_goals(self):
        """
        Returns an ``int`` of the total number of field goals the opponents
        made during the season.
        """
        return self._opp_field_goals

    @int_property_decorator
    def opp_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of field goals the opponents
        attempted during the season.
        """
        return self._opp_field_goal_attempts

    @float_property_decorator
    def opp_field_goal_percentage(self):
        """
        Returns a ``float`` of the percentage of field goals made divided by
        the number of attempts by the opponent. Percentage ranges from 0-1.
        """
        return self._opp_field_goal_percentage

    @int_property_decorator
    def opp_three_point_field_goals(self):
        """
        Returns an ``int`` of the total number of three point field goals the
        opponent made during the season.
        """
        return self._opp_three_point_field_goals

    @int_property_decorator
    def opp_three_point_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of three point field goals the
        opponent attempted during the season.
        """
        return self._opp_three_point_field_goal_attempts

    @float_property_decorator
    def opp_three_point_field_goal_percentage(self):
        """
        Returns a ``float`` of the percentage of three point field goals made
        divided by the number of attempts by the opponent. Percentage ranges
        from 0-1.
        """
        return self._opp_three_point_field_goal_percentage

    @int_property_decorator
    def opp_two_point_field_goals(self):
        """
        Returns an ``int`` of the total number of two point field goals the
        opponent made during the season.
        """
        return self._opp_two_point_field_goals

    @int_property_decorator
    def opp_two_point_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of two point field goals the
        opponent attempted during the season.
        """
        return self._opp_two_point_field_goal_attempts

    @float_property_decorator
    def opp_two_point_field_goal_percentage(self):
        """
        Returns a ``float`` of the percentage of two point field goals made
        divided by the number of attempts by the opponent. Percentage ranges
        from 0-1.
        """
        return self._opp_two_point_field_goal_percentage

    @int_property_decorator
    def opp_free_throws(self):
        """
        Returns an ``int`` of the total number of free throws made during the
        season by the opponent.
        """
        return self._opp_free_throws

    @int_property_decorator
    def opp_free_throw_attempts(self):
        """
        Returns an ``int`` of the total number of free throw attempts during
        the season by the opponent.
        """
        return self._opp_free_throw_attempts

    @float_property_decorator
    def opp_free_throw_percentage(self):
        """
        Returns a ``float`` of the percentage of free throws made divided by
        the attempts by the opponent. Percentage ranges from 0-1.
        """
        return self._opp_free_throw_percentage

    @int_property_decorator
    def opp_offensive_rebounds(self):
        """
        Returns an ``int`` of the total number of offensive rebounds the
        opponent grabbed.
        """
        return self._opp_offensive_rebounds

    @int_property_decorator
    def opp_defensive_rebounds(self):
        """
        Returns an ``int`` of the total number of defensive rebounds the
        opponent grabbed.
        """
        return self._opp_defensive_rebounds

    @int_property_decorator
    def opp_total_rebounds(self):
        """
        Returns an ``int`` of the total number of rebounds the opponent
        grabbed.
        """
        return self._opp_total_rebounds

    @int_property_decorator
    def opp_assists(self):
        """
        Returns an ``int`` of the total number of field goals that were
        assisted by the opponent.
        """
        return self._opp_assists

    @int_property_decorator
    def opp_steals(self):
        """
        Returns an ``int`` of the total number of times the opponent stole the
        ball from the team.
        """
        return self._opp_steals

    @int_property_decorator
    def opp_blocks(self):
        """
        Returns an ``int`` of the total number of times the opponent blocked
        the team's shot.
        """
        return self._opp_blocks

    @int_property_decorator
    def opp_turnovers(self):
        """
        Returns an ``int`` of the total number of times the opponent turned the
        ball over.
        """
        return self._opp_turnovers

    @int_property_decorator
    def opp_personal_fouls(self):
        """
        Returns an ``int`` of the total number of times the opponent fouled the
        team.
        """
        return self._opp_personal_fouls

    @int_property_decorator
    def opp_points(self):
        """
        Returns an ``int`` of the total number of points the team has been
        scored on during the season.
        """
        return self._opp_points


class Teams:
    """
    A list of all NBA teams and their stats in a given year.

    Finds and retrieves a list of all NBA teams from
    www.basketball-reference.com and creates a Team instance for every team
    that participated in the league in a given year. The Team class comprises
    a list of all major stats and a few identifiers for the requested season.

    Parameters
    ----------
    year : string (optional)
        The requested year to pull stats from.
    """
    def __init__(self, year=None):
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
            An NBA team's three letter abbreviation (ie. 'DET' for Detroit
            Pistons).

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
            An NBA team's three letter abbreviation (ie. 'DET' for Detroit
            Pistons).

        Returns
        -------
        Team instance
            If the requested team can be found, its Team instance is returned.
        """
        return self.__getitem__(abbreviation)

    def __repr__(self):
        """Returns a ``list`` of all NBA teams for the given season."""
        return self._teams

    def __iter__(self):
        """Returns an iterator of all of the NBA teams for a given season."""
        return iter(self.__repr__())

    def __len__(self):
        """Returns the number of NBA teams for a given season."""
        return len(self.__repr__())

    def _add_stats_data(self, teams_list, team_data_dict):
        """
        Add a team's stats row to a dictionary.

        Pass table contents and a stats dictionary of all teams to accumulate
        all stats for each team in a single variable.

        Parameters
        ----------
        teams_list : generator
            A generator of all row items in a given table.
        team_data_dict : {str: {'data': str, 'rank': int}} dictionary
            A dictionary where every key is the team's abbreviation and every
            value is another dictionary with a 'data' key which contains the
            string version of the row data for the matched team, and a 'rank'
            key which is the rank of the team.

        Returns
        -------
        dictionary
            An updated version of the team_data_dict with the passed table row
            information included.
        """
        # Teams are listed in terms of rank with the first team being #1
        rank = 1
        for team_data in teams_list:
            abbr = utils._parse_field(PARSING_SCHEME,
                                      team_data,
                                      'abbreviation')
            try:
                team_data_dict[abbr]['data'] += team_data
            except KeyError:
                team_data_dict[abbr] = {'data': team_data, 'rank': rank}
            rank += 1
        return team_data_dict

    def _retrieve_all_teams(self, year):
        """
        Find and create Team instances for all teams in the given season.

        For a given season, parses the specified NBA stats table and finds all
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
        team_data_dict = {}

        if not year:
            year = utils._find_year_for_season('nba')
            # If stats for the requested season do not exist yet (as is the
            # case right before a new season begins), attempt to pull the
            # previous year's stats. If it exists, use the previous year
            # instead.
            if not utils._url_exists(SEASON_PAGE_URL % year) and \
               utils._url_exists(SEASON_PAGE_URL % str(int(year) - 1)):
                year = str(int(year) - 1)
        doc = pq(SEASON_PAGE_URL % year)
        teams_list = utils._get_stats_table(doc, 'div#all_team-stats-base')
        opp_teams_list = utils._get_stats_table(doc,
                                                'div#all_opponent-stats-base')
        if not teams_list and not opp_teams_list:
            utils._no_data_found()
            return
        for stats_list in [teams_list, opp_teams_list]:
            team_data_dict = self._add_stats_data(stats_list, team_data_dict)

        for team_data in team_data_dict.values():
            team = Team(team_data['data'], team_data['rank'], year)
            self._teams.append(team)

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
