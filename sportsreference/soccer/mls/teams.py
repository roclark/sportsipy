import pandas as pd
from .constants import (MLS_CURRENT_SEASON_URL,
                        MLS_SEASON_URL,
                        ID_MAP,
                        PARSING_SCHEME)
from pyquery import PyQuery as pq
from sportsreference.decorators import float_property_decorator, int_property_decorator
from sportsreference import utils


class Team:
    """
    An object containing all of a team's season information.

    Finds and parses all team stat information and identifiers, such as full
    and short names, and sets them as properties which can be directly read
    from for easy reference.

    Parameters
    ----------
    team_data : string
        A string containing all of the rows of stats for a given team. If
        multiple tables are being referenced, this will be comprised of
        multiple rows in a single string.
    year : string (optional)
        The requested year to pull stats from.
    """
    def __init__(self, team_data, year=None):
        self._year = year
        self._abbreviation = None
        self._name = None
        self._games = None
        self._wins = None
        self._draws = None
        self._losses = None
        self._goals_for = None
        self._goals_against = None
        self._goal_diff = None
        self._points = None
        self._attendance_per_game = None
        self._top_team_scorers = None
        self._top_keeper = None
        self._notes = None

        self._parse_team_data(team_data)

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
            if field == '_year':
                continue
            value = utils._parse_field(PARSING_SCHEME,
                                       team_data,
                                       # Remove the '_' from the name
                                       str(field)[1:])
            setattr(self, field, value)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the string abbreviation of the
        team, such as 'TODO'.
        """
        fields_to_include = {
            'abbreviation': self.abbreviation,
            'name': self.name,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'goals_for': self.goals_for,
            'goals_against': self.goals_against,
            'goal_differential': self.goals_differential,
            'points': self.points,
            'average_attendance': self.attendance_per_game,
            'top_team_scorers': self.top_team_scorers,
            'top_goalkeeper': self.top_keeper,
            'notes': self.notes
        }
        return pd.DataFrame([fields_to_include], index=[self._abbreviation])

    @property
    def abbreviation(self):
        """
        Returns a ``string`` of the team's short name
        """
        return self._abbreviation

    @property
    def name(self):
        """
        Returns a ``string`` of the team's full name, such as 'Columbus Crew'.
        """
        return self._name

    @int_property_decorator
    def games_played(self):
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

    @int_property_decorator
    def draws(self):
        """
        Returns an ``int`` of the total number of games the team draw during
        the season.
        """
        return self._draws

    @int_property_decorator
    def goals_for(self):
        """
        Returns an ``int`` of the total number of goals scored during
        the season.
        """
        return self._goals_for

    @int_property_decorator
    def goals_against(self):
        """
        Returns an ``int`` of the total number of goals scored against during
        the season.
        """
        return self._goals_against

    @int_property_decorator
    def goals_differential(self):
        """
        Returns an ``int`` of the difference in the number of goals scored and against
        during the season.
        """
        return self._goal_diff

    @int_property_decorator
    def points(self):
        """
        Returns an ``int`` of the number of points earned
        during the season.
        """
        return self._points

    @int_property_decorator
    def attendance_per_game(self):
        """
        Returns an ``int`` of the average game attendance during
        the season.
        """
        return self._goals_against

    @property
    def top_team_scorers(self):
        """
        Returns an ``str`` of the top goal scorers during
        the season.
        """
        return self._top_team_scorers

    @property
    def top_keeper(self):
        """
        Returns an ``str`` of the top goalkeeper during
        the season.
        """
        return self._top_keeper

    @property
    def notes(self):
        """
        Returns an ``str`` of the team notes
        """
        return self._notes


class Teams:
    """
    A list of all Major League Soccer teams and their stats in a given year.

    Finds and retrieves a list of all Major League Soccer teams from
    www.fbref.com and creates a Team instance for every team that
    participated in the league in a given year. The Team class comprises a list
    of all major stats and a few identifiers for the requested season.

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
        short name.

        Parameters
        ----------
        abbreviation : string
            An MLS team's short name (ie. 'Columbus-Crew' for the Columbus Crew).

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
        short name. This method is a wrapper for __getitem__.

        Parameters
        ----------
        abbreviation : string
            An MLS team's short name (ie. 'Columbus-Crew' for the Columbus Crew).

        Returns
        -------
        Team instance
            if the requested team can be found, its Team instance is returned
        """
        return self.__getitem__(abbreviation)

    def __repr__(self):
        """Returns a ``list`` of all MLS teams for the given season."""
        return self._teams

    def __iter__(self):
        """Returns an iterator of all of the MLS teams for a given season."""
        return iter(self.__repr__())

    def __len__(self):
        """Returns the number of MLS teams for a given season."""
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
        team_data_dict : {str: {'data': str}} dictionary
            A dictionary where every key is the team's abbreviation and every
            value is another dictionary with a 'data' key which contains the
            string version of the row data for the matched team.

        Returns
        -------
        dictionary
            An updated version of the team_data_dict with the passed table row
            information included.
        """
        for team_data in teams_list:
            if 'class="over_header thead"' in str(team_data) or\
               'class="thead"' in str(team_data):
                continue
            abbr = utils._parse_field(PARSING_SCHEME,
                                      team_data,
                                      'abbreviation')
            try:
                team_data_dict[abbr]['data'] += team_data
            except KeyError:
                team_data_dict[abbr] = {'data': team_data}
        return team_data_dict

    def _retrieve_all_teams(self, year):
        """
        Find and create Team instances for all teams in the given season.

        For a given season, parses the specified NCAAB stats table and finds
        all requested stats. Each team then has a Team instance created which
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
            url = MLS_CURRENT_SEASON_URL
            mls_season_id = ID_MAP[sorted(ID_MAP.keys())[-1]]
        else:
            mls_season_id = ID_MAP[year]
            url = MLS_SEASON_URL % (mls_season_id, year)

        doc = pq(url)
        regular_season_teams_list = utils._get_stats_table(doc, f'table#results{mls_season_id}1')
        eastern_conf_teams_list = utils._get_stats_table(doc, f'table#results{mls_season_id}1Eastern-Conference')
        western_conf_teams_list = utils._get_stats_table(doc, f'table#results{mls_season_id}1Western-Conference')

        list_to_process = []

        if regular_season_teams_list is not None:
            list_to_process.append(regular_season_teams_list)
        if eastern_conf_teams_list is not None:
            list_to_process.append(eastern_conf_teams_list)
        if western_conf_teams_list is not None:
            list_to_process.append(western_conf_teams_list)

        for stats_list in list_to_process:
            team_data_dict = self._add_stats_data(stats_list, team_data_dict)

        for team_name, team_data in team_data_dict.items():
            team = Team(team_data['data'], year)
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
