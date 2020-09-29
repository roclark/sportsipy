import pandas as pd
import re
from .constants import (CONF_CHAMPIONSHIP,
                        DIVISION,
                        LOST_CONF_CHAMPS,
                        LOST_DIVISIONAL,
                        LOST_SUPER_BOWL,
                        LOST_WILD_CARD,
                        PARSING_SCHEME,
                        SUPER_BOWL,
                        WILD_CARD,
                        WON_SUPER_BOWL)
from ..constants import LOSS, WIN
from ..decorators import float_property_decorator, int_property_decorator
from .. import utils
from .nfl_utils import _retrieve_all_teams
from .roster import Roster
from .schedule import Schedule


class Team:
    """
    An object containing all of a team's season information.

    Finds and parses all team stat information and identifiers, such as rank,
    name, and abbreviation, and sets them as properties which can be directly
    read from for easy reference.

    If calling directly, the team's abbreviation needs to be passed. Otherwise,
    the Teams class will handle all arguments.

    Parameters
    ----------
    team_name : string (optional)
        The name of the team to pull if being called directly.
    team_data : string (optional)
        A string containing all of the rows of stats for a given team. If
        multiple tables are being referenced, this will be comprised of
        multiple rows in a single string. Is only used when called directly
        from the Teams class.
    rank : int (optional)
        A team's position in the league based on the number of points they
        obtained during the season. Is only used when called directly from the
        Teams class.
    season_page : string (optional)
        Optionally specify the filename of a local file to use to pull data
        instead of downloading from sports-reference.com. This file should be
        of the Season page for the designated year.
    """
    def __init__(self, team_name=None, team_data=None, rank=None, year=None,
                 season_page=None):
        self._year = year
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
        self._rush_first_downs = None
        self._penalties = None
        self._yards_from_penalties = None
        self._first_downs_from_penalties = None
        self._percent_drives_with_points = None
        self._percent_drives_with_turnovers = None
        self._points_contributed_by_offense = None

        if team_name:
            team_data = self._retrieve_team_data(year, team_name, season_page)
        self._parse_team_data(team_data)

    def __str__(self):
        """
        Return the string representation of the class.
        """
        return f'{self.name} ({self.abbreviation}) - {self._year}'

    def __repr__(self):
        """
        Return the string representation of the class.
        """
        return self.__str__()

    def _retrieve_team_data(self, year, team_name, season_page):
        """
        Pull all stats for a specific team.

        By first retrieving a dictionary containing all information for all
        teams in the league, only select the desired team for a specific year
        and return only their relevant results.

        Parameters
        ----------
        year : string
            A ``string`` of the requested year to pull stats from.
        team_name : string
            A ``string`` of the team's 3-letter abbreviation, such as 'KAN' for
            the Kansas City Chiefs.
        season_page : string (optional)
            Optionally specify the filename of a local file to use to pull data
            instead of downloading from sports-reference.com. This file should
            be of the Season page for the designated year.

        Returns
        -------
        PyQuery object
            Returns a PyQuery object containing all stats and information for
            the specified team.
        """
        team_data_dict, year = _retrieve_all_teams(year, season_page)
        self._year = year
        team_data = team_data_dict[team_name]['data']
        self._rank = team_data_dict[team_name]['rank']
        return team_data

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
        team, such as 'KAN'.
        """
        fields_to_include = {
            'abbreviation': self.abbreviation,
            'defensive_simple_rating_system':
            self.defensive_simple_rating_system,
            'first_downs': self.first_downs,
            'first_downs_from_penalties': self.first_downs_from_penalties,
            'fumbles': self.fumbles,
            'games_played': self.games_played,
            'interceptions': self.interceptions,
            'losses': self.losses,
            'margin_of_victory': self.margin_of_victory,
            'name': self.name,
            'offensive_simple_rating_system':
            self.offensive_simple_rating_system,
            'pass_attempts': self.pass_attempts,
            'pass_completions': self.pass_completions,
            'pass_first_downs': self.pass_first_downs,
            'pass_net_yards_per_attempt': self.pass_net_yards_per_attempt,
            'pass_touchdowns': self.pass_touchdowns,
            'pass_yards': self.pass_yards,
            'penalties': self.penalties,
            'percent_drives_with_points': self.percent_drives_with_points,
            'percent_drives_with_turnovers':
            self.percent_drives_with_turnovers,
            'plays': self.plays,
            'points_against': self.points_against,
            'points_contributed_by_offense':
            self.points_contributed_by_offense,
            'points_difference': self.points_difference,
            'points_for': self.points_for,
            'post_season_result': self.post_season_result,
            'rank': self.rank,
            'rush_attempts': self.rush_attempts,
            'rush_first_downs': self.rush_first_downs,
            'rush_touchdowns': self.rush_touchdowns,
            'rush_yards': self.rush_yards,
            'rush_yards_per_attempt': self.rush_yards_per_attempt,
            'simple_rating_system': self.simple_rating_system,
            'strength_of_schedule': self.strength_of_schedule,
            'turnovers': self.turnovers,
            'win_percentage': self.win_percentage,
            'wins': self.wins,
            'yards': self.yards,
            'yards_from_penalties': self.yards_from_penalties,
            'yards_per_play': self.yards_per_play
        }
        return pd.DataFrame([fields_to_include], index=[self._abbreviation])

    @int_property_decorator
    def rank(self):
        """
        Returns an ``int`` of the team's rank based on the number of points
        they scored during the season.
        """
        return self._rank

    @property
    def abbreviation(self):
        """
        Returns a ``string`` of team's abbreviation, such as 'KAN' for the
        Kansas City Chiefs.
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
        Returns a ``string`` of the team's full name, such as 'Kansas City
        Chiefs'.
        """
        return self._name

    @int_property_decorator
    def wins(self):
        """
        Returns an ``int`` of the number of games the team won during the
        season.
        """
        return self._wins

    @int_property_decorator
    def losses(self):
        """
        Returns an ``int`` of the number of games the team lost during the
        season.
        """
        return self._losses

    @float_property_decorator
    def win_percentage(self):
        """
        Returns a ``float`` of the number of wins divided by the number of
        games played. Percentage ranges from 0-1.
        """
        return self._win_percentage

    @int_property_decorator
    def games_played(self):
        """
        Returns an ``int`` of the number of games played during the season.
        """
        return self._games_played

    @property
    def post_season_result(self):
        """
        Returns a ``string constant`` denoting how far the team made it in the
        post-season.
        """
        final_game = self.schedule[-1]
        result = final_game.result
        if result == LOSS and final_game.week in [WILD_CARD, 18]:
            return LOST_WILD_CARD
        if result == LOSS and final_game.week in [DIVISION, 19]:
            return LOST_DIVISIONAL
        if result == LOSS and final_game.week in [CONF_CHAMPIONSHIP, 20]:
            return LOST_CONF_CHAMPS
        if result == LOSS and final_game.week in [SUPER_BOWL, 21]:
            return LOST_SUPER_BOWL
        if result == WIN and final_game.week in [SUPER_BOWL, 21]:
            return WON_SUPER_BOWL
        # If none of the above conditions are true, the team failed to qualify
        # for the post-season.
        return None

    @int_property_decorator
    def points_for(self):
        """
        Returns an ``int`` of the total number of points scored during the
        season.
        """
        return self._points_for

    @int_property_decorator
    def points_against(self):
        """
        Returns an ``int`` of the total number of points allowed during the
        season.
        """
        return self._points_against

    @int_property_decorator
    def points_difference(self):
        """
        Returns an ``int`` of the difference between the number of points
        scored and allowed during the season.
        """
        return self._points_difference

    @float_property_decorator
    def margin_of_victory(self):
        """
        Returns a ``float`` of the average margin of victory per game.
        """
        return self._margin_of_victory

    @float_property_decorator
    def strength_of_schedule(self):
        """
        Returns a ``float`` of the team's strength of schedule. An average
        difficulty schedule is denoted with a 0.0 and a negative number is
        comparatively easier than average.
        """
        return self._strength_of_schedule

    @float_property_decorator
    def simple_rating_system(self):
        """
        Returns a ``float`` of the team's relative strength based on average
        margin of victory plus strength of schedule. An average team is denoted
        with 0.0 and a negative score is a comparatively weaker team.
        """
        return self._simple_rating_system

    @float_property_decorator
    def offensive_simple_rating_system(self):
        """
        Returns a ``float`` of the team's offensive strength according to the
        simple rating system. An average team is denoted with 0.0 and a
        negative score is a comparatively weaker team.
        """
        return self._offensive_simple_rating_system

    @float_property_decorator
    def defensive_simple_rating_system(self):
        """
        Returns a ``float`` of the team's defensive strength according to the
        simple rating system. An average team is denoted with 0.0 and a
        negative score is a comparatively weaker team.
        """
        return self._defensive_simple_rating_system

    @int_property_decorator
    def yards(self):
        """
        Returns an ``int`` of the total number of yards the team has gained
        during the season.
        """
        return self._yards

    @int_property_decorator
    def plays(self):
        """
        Returns an ``int`` of the total number of offensive plays the team has
        made during the season.
        """
        return self._plays

    @float_property_decorator
    def yards_per_play(self):
        """
        Returns a ``float`` of the average number of yards gained per play
        during the season.
        """
        return self._yards_per_play

    @int_property_decorator
    def turnovers(self):
        """
        Returns an ``int`` of the total number of turnovers the team committed
        during the season.
        """
        return self._turnovers

    @int_property_decorator
    def fumbles(self):
        """
        Returns an ``int`` of the total number of times the team fumbled the
        ball during the season.
        """
        return self._fumbles

    @int_property_decorator
    def first_downs(self):
        """
        Returns an ``int`` of the total number of first downs the team achieved
        during the season.
        """
        return self._first_downs

    @int_property_decorator
    def pass_completions(self):
        """
        Returns an ``int`` of the total number of passes that were completed.
        """
        return self._pass_completions

    @int_property_decorator
    def pass_attempts(self):
        """
        Returns an ``int`` of the total number of passes that were attempted.
        """
        return self._pass_attempts

    @int_property_decorator
    def pass_yards(self):
        """
        Returns an ``int`` of the total number of yards the team gained from
        passing.
        """
        return self._pass_yards

    @int_property_decorator
    def pass_touchdowns(self):
        """
        Returns an ``int`` of the total number of touchdowns the team has
        scored from passing.
        """
        return self._pass_touchdowns

    @int_property_decorator
    def interceptions(self):
        """
        Returns an ``int`` of the total number of interceptions the team has
        thrown.
        """
        return self._interceptions

    @float_property_decorator
    def pass_net_yards_per_attempt(self):
        """
        Returns a ``float`` of the net yards gained per passing play including
        sacks.
        """
        return self._pass_net_yards_per_attempt

    @int_property_decorator
    def pass_first_downs(self):
        """
        Returns an ``int`` of the number of first downs the team gained from
        passing plays.
        """
        return self._pass_first_downs

    @int_property_decorator
    def rush_attempts(self):
        """
        Returns an ``int`` of the total number of rushing plays that were
        attempted.
        """
        return self._rush_attempts

    @int_property_decorator
    def rush_yards(self):
        """
        Returns an ``int`` of the total number of yards that were gained from
        rushing plays.
        """
        return self._rush_yards

    @int_property_decorator
    def rush_touchdowns(self):
        """
        Returns an ``int`` of the total number of touchdowns from rushing
        plays.
        """
        return self._rush_touchdowns

    @float_property_decorator
    def rush_yards_per_attempt(self):
        """
        Returns a ``float`` of the average number of yards gained per rushing
        play.
        """
        return self._rush_yards_per_attempt

    @int_property_decorator
    def rush_first_downs(self):
        """
        Returns an ``int`` of the total number of first downs gained from
        rushing plays.
        """
        return self._rush_first_downs

    @int_property_decorator
    def penalties(self):
        """
        Returns an ``int`` of the total number of penalties called on the team
        during the season.
        """
        return self._penalties

    @int_property_decorator
    def yards_from_penalties(self):
        """
        Returns an ``int`` of the total number of yards surrendered as a result
        of penalties called on the team.
        """
        return self._yards_from_penalties

    @int_property_decorator
    def first_downs_from_penalties(self):
        """
        Returns an ``int`` of the total number of first downs conceded as a
        result of penalties called on the team.
        """
        return self._first_downs_from_penalties

    @float_property_decorator
    def percent_drives_with_points(self):
        """
        Returns a ``float`` of the percentage of drives that result in points
        for the offense. Percentage ranges from 0-100.
        """
        return self._percent_drives_with_points

    @float_property_decorator
    def percent_drives_with_turnovers(self):
        """
        Returns a ``float`` of the percentage of drives that result in an
        offensive turnover. Percentage ranges from 0-100.
        """
        return self._percent_drives_with_turnovers

    @float_property_decorator
    def points_contributed_by_offense(self):
        """
        Returns a ``float`` of the number of expected points contributed by the
        offense.
        """
        return self._points_contributed_by_offense


class Teams:
    """
    A list of all NFL teams and their stats in a given year.

    Finds and retrieves a list of all NFL teams from
    www.pro-football-reference.com and creates a Team instance for every team
    that participated in the league in a given year. The Team class comprises
    a list of all major stats and a few identifiers for the requested season.

    Parameters
    ----------
    year : string (optional)
        The requested year to pull stats from.
    season_page : string (optional)
        Optionally specify the filename of a local file to use to pull data
        instead of downloading from sports-reference.com. This file should be
        of the Season page for the designated year.
    """
    def __init__(self, year=None, season_page=None):
        self._teams = []

        team_data_dict, year = _retrieve_all_teams(year, season_page)
        self._instantiate_teams(team_data_dict, year)

    def __getitem__(self, abbreviation):
        """
        Return a specified team.

        Returns a team's instance in the Teams class as specified by the team's
        abbreviation.

        Parameters
        ----------
        abbreviation : string
            An NFL team's three letter abbreviation (ie. 'KAN' for Kansas City
            Chiefs).

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
            An NFL team's three letter abbreviation (ie. 'KAN' for Kansas City
            Chiefs).

        Returns
        -------
        Team instance
            If the requested team can be found, its Team instance is returned.
        """
        return self.__getitem__(abbreviation)

    def __str__(self):
        """
        Return the string representation of the class.
        """
        teams = [f'{team.name} ({team.abbreviation})'.strip()
                 for team in self._teams]
        return '\n'.join(teams)

    def __repr__(self):
        """
        Return the string representation of the class.
        """
        return self.__str__()

    def __iter__(self):
        """Returns an iterator of all of the NFL teams for a given season."""
        return iter(self._teams)

    def __len__(self):
        """Returns the number of NFL teams for a given season."""
        return len(self._teams)

    def _instantiate_teams(self, team_data_dict, year):
        """
        Create a Team instance for all teams.

        Once all team information has been pulled from the various webpages,
        create a Team instance for each team and append it to a larger list of
        team instances for later use.

        Parameters
        ----------
        team_data_dict : dictionary
            A ``dictionary`` containing all stats information in HTML format as
            well as team rankings, indexed by team abbreviation.
        year : string
            A ``string`` of the requested year to pull stats from.
        """
        if not team_data_dict:
            return
        for team_data in team_data_dict.values():
            team = Team(team_data=team_data['data'],
                        rank=team_data['rank'],
                        year=year)
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
