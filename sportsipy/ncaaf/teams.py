import pandas as pd
import re
from .constants import PARSING_SCHEME
from ..decorators import float_property_decorator, int_property_decorator
from .. import utils
from .conferences import Conferences
from .ncaaf_utils import _retrieve_all_teams
from .roster import Roster
from .schedule import Schedule


class Team:
    """
    An object containing all of a team's season information.

    Finds and parses all team stat information and identifiers, such as full
    and short names, and sets them as properties which can be directly read
    from for easy reference.

    If calling directly, the team's abbreviation needs to be passed. Otherwise,
    the Teams class will handle all arguments.

    Parameters
    ----------
    team_name : string (optional)
        The name of the team to pull if being called directly.
    team_data : string (optional)
        A string containing all of the rows of stats for a given team. If
        multiple tables are being referenced, this will be comprised of
        multiple rows in a single string.
    team_conference : string (optional)
        A string of the team's conference abbreviation, such as 'big-12'.
    year : string (optional)
        The requested year to pull stats from.
    season_page : string (optional)
        Optionally specify the filename of a local file to use to pull data
        instead of downloading from sports-reference.com. This file should be
        of the Season page for the designated year.
    offensive_stats : string (optional)
        Optionally specify the filename of a local file to use to pull data
        instead of downloading from sports-reference.com. This file should be
        of the Offensive Stats page for the designated year.
    defensive_stats : string (optional)
        Optionally specify the filename of a local file to use to pull data
        instead of downloading from sports-reference.com. This file should be
        of the Defensive Stats page for the designated year.
    """
    def __init__(self, team_name=None, team_data=None, team_conference=None,
                 year=None, season_page=None, offensive_stats=None,
                 defensive_stats=None):
        self._team_conference = team_conference
        self._year = year
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
        self._opponents_pass_completions = None
        self._opponents_pass_attempts = None
        self._opponents_pass_completion_percentage = None
        self._opponents_pass_yards = None
        self._opponents_interceptions = None
        self._opponents_pass_touchdowns = None
        self._opponents_rush_attempts = None
        self._opponents_rush_yards = None
        self._opponents_rush_yards_per_attempt = None
        self._opponents_rush_touchdowns = None
        self._opponents_plays = None
        self._opponents_yards = None
        self._opponents_turnovers = None
        self._opponents_fumbles_lost = None
        self._opponents_yards_per_play = None
        self._opponents_pass_first_downs = None
        self._opponents_rush_first_downs = None
        self._opponents_first_downs_from_penalties = None
        self._opponents_first_downs = None
        self._opponents_penalties = None
        self._opponents_yards_from_penalties = None

        if team_name:
            team_data = self._retrieve_team_data(year, team_name, season_page,
                                                 offensive_stats,
                                                 defensive_stats)
            conferences_dict = Conferences(year).team_conference
            self._team_conference = conferences_dict[team_name.lower()]
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

    def _retrieve_team_data(self, year, team_name, season_page,
                            offensive_stats, defensive_stats):
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
            A ``string`` of the team's abbreviation, such as 'PURDUE' for the
            Purdue Boilermakers.
        season_page : string (optional)
            Optionally specify the filename of a local file to use to pull data
            instead of downloading from sports-reference.com. This file should
            be of the Season page for the designated year.
        offensive_stats : string (optional)
            Optionally specify the filename of a local file to use to pull data
            instead of downloading from sports-reference.com. This file should
            be of the Offensive Stats page for the designated year.
        defensive_stats : string (optional)
            Optionally specify the filename of a local file to use to pull data
            instead of downloading from sports-reference.com. This file should
            be of the Defensive Stats page for the designated year.

        Returns
        -------
        PyQuery object
            Returns a PyQuery object containing all stats and information for
            the specified team.
        """
        team_data_dict, year = _retrieve_all_teams(year, season_page,
                                                   offensive_stats,
                                                   defensive_stats)
        self._year = year
        team_data = team_data_dict[team_name]['data']
        return team_data

    def _parse_team_data(self, team_data):
        """
        Parses a value for every attribute.

        This function looks through every attribute and retrieves the value
        according to the parsing scheme and index of the attribute from the
        passed HTML data. Once the value is retrieved, the attribute's value is
        updated with the returned result.

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
            if field == '_year' or \
               field == '_team_conference':
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
        team, such as 'PURDUE'.
        """
        fields_to_include = {
            'abbreviation': self.abbreviation,
            'conference': self.conference,
            'conference_losses': self.conference_losses,
            'conference_win_percentage': self.conference_win_percentage,
            'conference_wins': self.conference_wins,
            'first_downs': self.first_downs,
            'opponents_first_downs': self.opponents_first_downs,
            'first_downs_from_penalties': self.first_downs_from_penalties,
            'opponents_first_downs_from_penalties':
                self.opponents_first_downs_from_penalties,
            'fumbles_lost': self.fumbles_lost,
            'opponents_fumbles_lost': self.opponents_fumbles_lost,
            'games': self.games,
            'interceptions': self.interceptions,
            'opponents_interceptions': self.opponents_interceptions,
            'losses': self.losses,
            'name': self.name,
            'pass_attempts': self.pass_attempts,
            'opponents_pass_attempts': self.opponents_pass_attempts,
            'pass_completion_percentage': self.pass_completion_percentage,
            'opponents_pass_completion_percentage':
                self.opponents_pass_completion_percentage,
            'pass_completions': self.pass_completions,
            'opponents_pass_completions': self.opponents_pass_completions,
            'pass_first_downs': self.pass_first_downs,
            'opponents_pass_first_downs': self.opponents_pass_first_downs,
            'pass_touchdowns': self.pass_touchdowns,
            'opponents_pass_touchdowns': self.opponents_pass_touchdowns,
            'pass_yards': self.pass_yards,
            'opponents_pass_yards': self.opponents_pass_yards,
            'penalties': self.penalties,
            'opponents_penalties': self.opponents_penalties,
            'plays': self.plays,
            'opponents_plays': self.opponents_plays,
            'points_against_per_game': self.points_against_per_game,
            'points_per_game': self.points_per_game,
            'rush_attempts': self.rush_attempts,
            'opponents_rush_attempts': self.opponents_rush_attempts,
            'rush_first_downs': self.rush_first_downs,
            'opponents_rush_first_downs': self.opponents_rush_first_downs,
            'rush_touchdowns': self.rush_touchdowns,
            'opponents_rush_touchdowns': self.opponents_rush_touchdowns,
            'rush_yards': self.rush_yards,
            'opponents_rush_yards': self.opponents_rush_yards,
            'rush_yards_per_attempt': self.rush_yards_per_attempt,
            'opponents_rush_yards_per_attempt':
                self.opponents_rush_yards_per_attempt,
            'simple_rating_system': self.simple_rating_system,
            'strength_of_schedule': self.strength_of_schedule,
            'turnovers': self.turnovers,
            'opponents_turnovers': self.opponents_turnovers,
            'win_percentage': self.win_percentage,
            'wins': self.wins,
            'yards': self.yards,
            'opponents_yards': self.opponents_yards,
            'yards_from_penalties': self.yards_from_penalties,
            'opponents_yards_from_penalties':
                self.opponents_yards_from_penalties,
            'yards_per_play': self.yards_per_play,
            'opponents_yards_per_play': self.opponents_yards_per_play
        }
        return pd.DataFrame([fields_to_include], index=[self._abbreviation])

    @property
    def conference(self):
        """
        Returns a ``string`` of the team's conference abbreviation, such as
        'big-12' for the Big 12 Conference.
        """
        return self._team_conference

    @property
    def abbreviation(self):
        """
        Returns a ``string`` of the team's short name, such as 'PURDUE' for the
        Purdue Boilermakers.
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
        Returns a ``string`` of the team's full name, such as 'Purdue
        Boilermakers'.
        """
        return self._name

    @int_property_decorator
    def games(self):
        """
        Returns an ``int`` of the total number of games the team has played
        during the season.
        """
        return self._games

    @int_property_decorator
    def wins(self):
        """
        Returns an ``int`` of the total number of games the team won during the
        season.
        """
        return self._wins

    @int_property_decorator
    def losses(self):
        """
        Returns an ``int`` of the total number of games the team lost during
        the season.
        """
        return self._losses

    @float_property_decorator
    def win_percentage(self):
        """
        Returns a ``float`` of the percentage of wins divided by the number of
        games played during the season. Percentage ranges from 0-1.
        """
        return self._win_percentage

    @int_property_decorator
    def conference_wins(self):
        """
        Returns an ``int`` of the total number of conference games the team won
        during the season.
        """
        return self._conference_wins

    @int_property_decorator
    def conference_losses(self):
        """
        Returns an ``int`` of the total number of conference games the team
        lost during the season.
        """
        return self._conference_losses

    @float_property_decorator
    def conference_win_percentage(self):
        """
        Returns a ``float`` of the percentage of conference wins divided by the
        number of conference games played during the season. Percentage ranges
        from 0-1.
        """
        return self._conference_win_percentage

    @float_property_decorator
    def points_per_game(self):
        """
        Returns a ``float`` of the average number of points scored by the team
        per game.
        """
        return self._points_per_game

    @float_property_decorator
    def points_against_per_game(self):
        """
        Returns a ``float`` of the average number of points conceded per game.
        """
        return self._points_against_per_game

    @float_property_decorator
    def strength_of_schedule(self):
        """
        Returns a ``float`` of the team's strength of schedule based on the
        number of points above or below average. An average difficulty schedule
        is denoted with 0.0 while a negative score indicates a comparatively
        easy schedule.
        """
        return self._strength_of_schedule

    @float_property_decorator
    def simple_rating_system(self):
        """
        Returns a ``float`` of the team's relative strength based on the
        average margin of victory and the strength of schedule. An average team
        is denoted with 0.0 while a negative score indicates a comparatively
        weak team.
        """
        return self._simple_rating_system

    @float_property_decorator
    def pass_completions(self):
        """
        Returns a ``float`` of the average number of completed passes per game.
        """
        return self._pass_completions

    @float_property_decorator
    def opponents_pass_completions(self):
        """
        Returns a ``float`` of the opponents' average number of completed
        passes per game.
        """
        return self._opponents_pass_completions

    @float_property_decorator
    def pass_attempts(self):
        """
        Returns a ``float`` of the average number of passes that are attempted
        per game.
        """
        return self._pass_attempts

    @float_property_decorator
    def opponents_pass_attempts(self):
        """
        Returns a ``float`` of the opponents' average number of passes that
        are attempted per game.
        """
        return self._opponents_pass_attempts

    @float_property_decorator
    def pass_completion_percentage(self):
        """
        Returns a ``float`` of the percentage of completed passes per game.
        Percentage ranges from 0-100.
        """
        return self._pass_completion_percentage

    @float_property_decorator
    def opponents_pass_completion_percentage(self):
        """
        Returns a ``float`` of the opponents' percentage of completed passes
        per game. Percentage ranges from 0-100.
        """
        return self._opponents_pass_completion_percentage

    @float_property_decorator
    def pass_yards(self):
        """
        Returns a ``float`` of the average number of yards gained from passing
        per game.
        """
        return self._pass_yards

    @float_property_decorator
    def opponents_pass_yards(self):
        """
        Returns a ``float`` of the opponents' average number of yards gained
        from passing per game.
        """
        return self._opponents_pass_yards

    @float_property_decorator
    def interceptions(self):
        """
        Returns a ``float`` of the average number of interceptions thrown per
        game.
        """
        return self._interceptions

    @float_property_decorator
    def opponents_interceptions(self):
        """
        Returns a ``float`` of the opponents' average number of interceptions
        thrown per game.
        """
        return self._opponents_interceptions

    @float_property_decorator
    def pass_touchdowns(self):
        """
        Returns a ``float`` of the average number of passing touchdowns scored
        per game.
        """
        return self._pass_touchdowns

    @float_property_decorator
    def opponents_pass_touchdowns(self):
        """
        Returns a ``float`` of the opponents' average number of passing
        touchdowns scored per game.
        """
        return self._opponents_pass_touchdowns

    @float_property_decorator
    def rush_attempts(self):
        """
        Returns a ``float`` of the average number of rushing plays per game.
        """
        return self._rush_attempts

    @float_property_decorator
    def opponents_rush_attempts(self):
        """
        Returns a ``float`` of the opponents' average number of rushing plays
        per game.
        """
        return self._opponents_rush_attempts

    @float_property_decorator
    def rush_yards(self):
        """
        Returns a ``float`` of the average number of yards gained from rushing
        per game.
        """
        return self._rush_yards

    @float_property_decorator
    def opponents_rush_yards(self):
        """
        Returns a ``float`` of the opponents' average number of yards gained
        from rushing per game.
        """
        return self._opponents_rush_yards

    @float_property_decorator
    def rush_yards_per_attempt(self):
        """
        Returns a ``float`` of the average number of yards gained per rushing
        attempt per game.
        """
        return self._rush_yards_per_attempt

    @float_property_decorator
    def opponents_rush_yards_per_attempt(self):
        """
        Returns a ``float`` of the opponents' average number of yards gained
        per rushing attempt per game.
        """
        return self._opponents_rush_yards_per_attempt

    @float_property_decorator
    def rush_touchdowns(self):
        """
        Returns a ``float`` of the average number of rushing touchdowns scored
        per game.
        """
        return self._rush_touchdowns

    @float_property_decorator
    def opponents_rush_touchdowns(self):
        """
        Returns a ``float`` of the opponents' average number of rushing
        touchdowns scored per game.
        """
        return self._opponents_rush_touchdowns

    @float_property_decorator
    def plays(self):
        """
        Returns a ``float`` of the average number of offensive plays per game.
        """
        return self._plays

    @float_property_decorator
    def opponents_plays(self):
        """
        Returns a ``float`` of the opponents' average number of offensive plays
        per game.
        """
        return self._opponents_plays

    @float_property_decorator
    def yards(self):
        """
        Returns a ``float`` of the average number of yards gained per game.
        """
        return self._yards

    @float_property_decorator
    def opponents_yards(self):
        """
        Returns a ``float`` of the opponents' average number of yards gained
        per game.
        """
        return self._opponents_yards

    @float_property_decorator
    def turnovers(self):
        """
        Returns a ``float`` of the average number of turnovers per game.
        """
        return self._turnovers

    @float_property_decorator
    def opponents_turnovers(self):
        """
        Returns a ``float`` of the opponents' average number of turnovers
        per game.
        """
        return self._opponents_turnovers

    @float_property_decorator
    def fumbles_lost(self):
        """
        Returns a ``float`` of the average number of fumbles per game.
        """
        return self._fumbles_lost

    @float_property_decorator
    def opponents_fumbles_lost(self):
        """
        Returns a ``float`` of the opponents' average number of fumbles
        per game.
        """
        return self._opponents_fumbles_lost

    @float_property_decorator
    def yards_per_play(self):
        """
        Returns a ``float`` of the average number of yards gained per play.
        """
        return self._yards_per_play

    @float_property_decorator
    def opponents_yards_per_play(self):
        """
        Returns a ``float`` of the opponents' average number of yards gained
        per play.
        """
        return self._opponents_yards_per_play

    @float_property_decorator
    def pass_first_downs(self):
        """
        Returns a ``float`` of the average number of first downs from passing
        plays per game.
        """
        return self._pass_first_downs

    @float_property_decorator
    def opponents_pass_first_downs(self):
        """
        Returns a ``float`` of the opponents' average number of first downs
        from passing plays per game.
        """
        return self._opponents_pass_first_downs

    @float_property_decorator
    def rush_first_downs(self):
        """
        Returns a ``float`` of the average number of first downs from rushing
        plays per game.
        """
        return self._rush_first_downs

    @float_property_decorator
    def opponents_rush_first_downs(self):
        """
        Returns a ``float`` of the opponents' average number of first downs
        from rushing plays per game.
        """
        return self._opponents_rush_first_downs

    @float_property_decorator
    def first_downs_from_penalties(self):
        """
        Returns a ``float`` of the average number of first downs from an
        opponent's penalties per game.
        """
        return self._first_downs_from_penalties

    @float_property_decorator
    def opponents_first_downs_from_penalties(self):
        """
        Returns a ``float`` of the opponents' average number of first downs
        from an opponent's penalties per game.
        """
        return self._opponents_first_downs_from_penalties

    @float_property_decorator
    def first_downs(self):
        """
        Returns a ``float`` of the total number of first downs achieved per
        game.
        """
        return self._first_downs

    @float_property_decorator
    def opponents_first_downs(self):
        """
        Returns a ``float`` of the opponents' total number of first downs
        achieved per game.
        """
        return self._opponents_first_downs

    @float_property_decorator
    def penalties(self):
        """
        Returns a ``float`` of the average number of penalties conceded per
        game.
        """
        return self._penalties

    @float_property_decorator
    def opponents_penalties(self):
        """
        Returns a ``float`` of the opponents' average number of penalties
        conceded per game.
        """
        return self._opponents_penalties

    @float_property_decorator
    def yards_from_penalties(self):
        """
        Returns a ``float`` of the average number of yards gained from an
        opponent's penalties per game.
        """
        return self._yards_from_penalties

    @float_property_decorator
    def opponents_yards_from_penalties(self):
        """
        Returns a ``float`` of the opponents' average number of yards gained
        from an opponent's penalties per game.
        """
        return self._opponents_yards_from_penalties


class Teams:
    """
    A list of all NCAA Men's Football teams and their stats in a given year.

    Finds and retrieves a list of all NCAA Men's Football teams from
    www.sports-reference.com and creates a Team instance for every team that
    participated in the league in a given year. The Team class comprises a list
    of all major stats and a few identifiers for the requested season.

    Parameters
    ----------
    year : string (optional)
        The requested year to pull stats from.
    season_page : string (optional)
        Optionally specify the filename of a local file to use to pull data
        instead of downloading from sports-reference.com. This file should be
        of the Season page for the designated year.
    offensive_stats : string (optional)
        Optionally specify the filename of a local file to use to pull data
        instead of downloading from sports-reference.com. This file should be
        of the Offensive Stats page for the designated year.
    defensive_stats : string (optional)
        Optionally specify the filename of a local file to use to pull data
        instead of downloading from sports-reference.com. This file should be
        of the Defensive Stats page for the designated year.
    """
    def __init__(self, year=None, season_page=None, offensive_stats=None,
                 defensive_stats=None):
        self._teams = []
        self._conferences_dict = Conferences(year, True).team_conference

        team_data_dict, year = _retrieve_all_teams(year, season_page,
                                                   offensive_stats,
                                                   defensive_stats)
        self._instantiate_teams(team_data_dict, year)

    def __getitem__(self, abbreviation):
        """
        Return a specified team.

        Returns a team's instance in the Teams class as specified by the team's
        short name.

        Parameters
        ----------
        abbreviation : string
            An NCAAF team's short name (ie. 'PURDUE' for the Purdue
            Boilermakers).

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
            An NCAAF team's short name (ie. 'PURDUE' for the Purdue
            Boilermakers).

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
        """Returns an iterator of all of the NCAAF teams for a given season."""
        return iter(self._teams)

    def __len__(self):
        """Returns the number of NCAAF teams for a given season."""
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
        for team_name, team_data in team_data_dict.items():
            if team_name.lower() not in self._conferences_dict:
                conference = None
            else:
                conference = self._conferences_dict[team_name.lower()]
            team = Team(team_data=team_data['data'],
                        team_conference=conference,
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
