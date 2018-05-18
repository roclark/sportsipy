import re
from .constants import PARSING_SCHEME, OFFENSIVE_STATS_URL, SEASON_PAGE_URL
from pyquery import PyQuery as pq
from .. import utils


class Team:
    """
    An object containing all of a team's season information.

    Finds and parses all team stat information and identifiers, such as full
    and short names, and sets them as properties which can be directly read
    from for easy reference.
    """
    def __init__(self, team_data):
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
        """
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
            value = utils.parse_field(PARSING_SCHEME,
                                      team_data,
                                      str(field)[1:])
            setattr(self, field, value)

    @property
    def abbreviation(self):
        """
        Returns a string of the team's short name, such as 'PURDUE' for the
        Purdue Boilermakers.
        """
        return self._abbreviation

    @property
    def name(self):
        """
        Returns a string of the team's full name, such as 'Purdue
        Boilermakers'.
        """
        return self._name

    @property
    def games(self):
        """
        Returns an int of the total number of games the team has played during
        the season.
        """
        return int(self._games)

    @property
    def wins(self):
        """
        Returns an int of the total number of games the team won during the
        season.
        """
        return int(self._wins)

    @property
    def losses(self):
        """
        Returns an int of the total number of games the team lost during the
        season.
        """
        return int(self._losses)

    @property
    def win_percentage(self):
        """
        Returns a float of the percentage of wins divided by the number of
        games played during the season. Percentage ranges from 0-1.
        """
        return float(self._win_percentage)

    @property
    def conference_wins(self):
        """
        Returns an int of the total number of conference games the team won
        during the season.
        """
        return int(self._conference_wins)

    @property
    def conference_losses(self):
        """
        Returns an int of the total number of conference games the team lost
        during the season.
        """
        return int(self._conference_losses)

    @property
    def conference_win_percentage(self):
        """
        Returns a float of the percentage of conference wins divided by the
        number of conference games played during the season. Percentage ranges
        from 0-1.
        """
        return float(self._conference_win_percentage)

    @property
    def points_per_game(self):
        """
        Returns a float of the average number of points scored by the team per
        game.
        """
        return float(self._points_per_game)

    @property
    def points_against_per_game(self):
        """
        Returns a float of the average number of points conceded per game.
        """
        return float(self._points_against_per_game)

    @property
    def strength_of_schedule(self):
        """
        Returns a float of the team's strength of schedule based on the number
        of points above or below average. An average difficulty schedule is
        denoted with 0.0 while a negative score indicates a comparatively easy
        schedule.
        """
        return float(self._strength_of_schedule)

    @property
    def simple_rating_system(self):
        """
        Returns a float of the team's relative strength based on the average
        margin of victory and the strength of schedule. An average team is
        denoted with 0.0 while a negative score indicates a comparatively weak
        team.
        """
        return float(self._simple_rating_system)

    @property
    def pass_completions(self):
        """
        Returns a float of the average number of completed passes per game.
        """
        return float(self._pass_completions)

    @property
    def pass_attempts(self):
        """
        Returns a float of the average number of passes that are attempted per
        game.
        """
        return float(self._pass_attempts)

    @property
    def pass_completion_percentage(self):
        """
        Returns a float of the percentage of completed passes per game.
        Percentage ranges from 0-100.
        """
        return float(self._pass_completion_percentage)

    @property
    def pass_yards(self):
        """
        Returns a float of the average number of yards gained from passing per
        game.
        """
        return float(self._pass_yards)

    @property
    def interceptions(self):
        """
        Returns a float of the average number of interceptions thrown per game.
        """
        return float(self._interceptions)

    @property
    def pass_touchdowns(self):
        """
        Returns a float of the average number of passing touchdowns scored per
        game.
        """
        return float(self._pass_touchdowns)

    @property
    def rush_attempts(self):
        """
        Returns a float of the average number of rushing plays per game.
        """
        return float(self._rush_attempts)

    @property
    def rush_yards(self):
        """
        Returns a float of the average number of yards gained from rushing per
        game.
        """
        return float(self._rush_yards)

    @property
    def rush_yards_per_attempt(self):
        """
        Returns a float of the average number of yards gained per rushing
        attempt per game.
        """
        return float(self._rush_yards_per_attempt)

    @property
    def rush_touchdowns(self):
        """
        Returns a float of the average number of rushing touchdowns scored per
        game.
        """
        return float(self._rush_touchdowns)

    @property
    def plays(self):
        """
        Returns a float of the average number of offensive plays per game.
        """
        return float(self._plays)

    @property
    def yards(self):
        """
        Returns a float of the average number of yards gained per game.
        """
        return float(self._yards)

    @property
    def turnovers(self):
        """
        Returns a float of the average number of turnovers per game.
        """
        return float(self._turnovers)

    @property
    def fumbles_lost(self):
        """
        Returns a float of the average number of fumbles per game.
        """
        return float(self._fumbles_lost)

    @property
    def yards_per_play(self):
        """
        Returns a float of the average number of yards gained per play.
        """
        return float(self._yards_per_play)

    @property
    def pass_first_downs(self):
        """
        Returns a float of the average number of first downs from passing plays
        per game.
        """
        return float(self._pass_first_downs)

    @property
    def rush_first_downs(self):
        """
        Returns a float of the average number of first downs from rushing plays
        per game.
        """
        return float(self._rush_first_downs)

    @property
    def first_downs_from_penalties(self):
        """
        Returns a float of the average number of first downs from an opponent's
        penalties per game.
        """
        return float(self._first_downs_from_penalties)

    @property
    def first_downs(self):
        """
        Returns a float of the total number of first downs achieved per game.
        """
        return float(self._first_downs)

    @property
    def penalties(self):
        """
        Returns the average number of penalties conceded per game.
        """
        return float(self._penalties)

    @property
    def yards_from_penalties(self):
        """
        Returns a float of the average number of yards gained from an
        opponent's penalties per game.
        """
        return float(self._yards_from_penalties)


class Teams:
    """
    A list of all NCAA Men's Football teams and their stats in a given year.

    Finds and retrieves a list of all NCAA Men's Football teams from
    www.sports-reference.com and creates a Team instance for every team that
    participated in the league in a given year. The Team class comprises a list
    of all major stats and a few identifiers for the requested season.
    """
    def __init__(self, year=None):
        """
        Get a list of all Team instances

        Once Teams is invoked, it retrieves a list of all NCAAF teams in the
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

    def __repr__(self):
        """Returns a list of all NCAAF teams for the given season."""
        return self._teams

    def __iter__(self):
        """Returns an iterator of all of the NCAAF teams for a given season."""
        return iter(self.__repr__())

    def __len__(self):
        """Returns the number of NCAAF teams for a given season."""
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
        """
        Find and create Team instances for all teams in the given season.

        For a given season, parses the specified NCAAF stats table and finds
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
