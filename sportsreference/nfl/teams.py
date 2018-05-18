import re
from .constants import PARSING_SCHEME, SEASON_PAGE_URL
from pyquery import PyQuery as pq
from .. import utils


class Team:
    """
    An object containing all of a team's season information.

    Finds and parses all team stat information and identifiers, such as rank,
    name, and abbreviation, and sets them as properties which can be directly
    read from for easy reference.
    """
    def __init__(self, team_data, rank):
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
        """
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
            if field == '_rank':
                continue
            value = utils.parse_field(PARSING_SCHEME,
                                      team_data,
                                      str(field)[1:])
            setattr(self, field, value)

    @property
    def rank(self):
        """
        Returns an int of the team's rank based on the number of points they
        scored during the season.
        """
        return int(self._rank)

    @property
    def abbreviation(self):
        """
        Returns a string of team's abbreviation, such as 'KAN' for the Kansas
        City Chiefs.
        """
        return self._abbreviation

    @property
    def name(self):
        """
        Returns a string of the team's full name, such as 'Kansas City Chiefs'.
        """
        return self._name

    @property
    def wins(self):
        """
        Returns an int of the number of games the team won during the season.
        """
        return int(self._wins)

    @property
    def losses(self):
        """
        Returns an int of the number of games the team lost during the season.
        """
        return int(self._losses)

    @property
    def win_percentage(self):
        """
        Returns a float of the number of wins divided by the number of games
        played. Percentage ranges from 0-1.
        """
        return float(self._win_percentage)

    @property
    def games_played(self):
        """
        Returns an int of the number of games played during the season.
        """
        return int(self._games_played)

    @property
    def points_for(self):
        """
        Returns an int of the total number of points scored during the season.
        """
        return int(self._points_for)

    @property
    def points_against(self):
        """
        Returns an int of the total number of points allowed during the season.
        """
        return int(self._points_against)

    @property
    def points_difference(self):
        """
        Returns an int of the difference between the number of points scored
        and allowed during the season.
        """
        return int(self._points_difference)

    @property
    def margin_of_victory(self):
        """
        Returns a float of the average margin of victory per game.
        """
        return float(self._margin_of_victory)

    @property
    def strength_of_schedule(self):
        """
        Returns a float of the team's strength of schedule. An average
        difficulty schedule is denoted with a 0.0 and a negative number is
        comparatively easier than average.
        """
        return float(self._strength_of_schedule)

    @property
    def simple_rating_system(self):
        """
        Returns a float of the team's relative strength based on average margin
        of victory plus strength of schedule. An average team is denoted with
        0.0 and a negative score is a comparatively weaker team.
        """
        return float(self._simple_rating_system)

    @property
    def offensive_simple_rating_system(self):
        """
        Returns a float of the team's offensive strength according to the
        simple rating system. An average team is denoted with 0.0 and a
        negative score is a comparatively weaker team.
        """
        return float(self._offensive_simple_rating_system)

    @property
    def defensive_simple_rating_system(self):
        """
        Returns a float of the team's defensive strength according to the
        simple rating system. An average team is denoted with 0.0 and a
        negative score is a comparatively weaker team.
        """
        return float(self._defensive_simple_rating_system)

    @property
    def yards(self):
        """
        Returns an int of the total number of yards the team has gained during
        the season.
        """
        return int(self._yards)

    @property
    def plays(self):
        """
        Returns an int of the total number of offensive plays the team has made
        during the season.
        """
        return int(self._plays)

    @property
    def yards_per_play(self):
        """
        Returns a float of the average number of yards gained per play during
        the season.
        """
        return float(self._yards_per_play)

    @property
    def turnovers(self):
        """
        Returns an int of the total number of turnovers the team committed
        during the season.
        """
        return int(self._turnovers)

    @property
    def fumbles(self):
        """
        Returns an int of the total number of times the team fumbled the ball
        during the season.
        """
        return int(self._fumbles)

    @property
    def first_downs(self):
        """
        Returns an int of the total number of first downs the team achieved
        during the season.
        """
        return int(self._first_downs)

    @property
    def pass_completions(self):
        """
        Returns an int of the total number of passes that were completed.
        """
        return int(self._pass_completions)

    @property
    def pass_attempts(self):
        """
        Returns an int of the total number of passes that were attempted.
        """
        return int(self._pass_attempts)

    @property
    def pass_yards(self):
        """
        Returns an int of the total number of yards the team gained from
        passing.
        """
        return int(self._pass_yards)

    @property
    def pass_touchdowns(self):
        """
        Returns an int of the total number of touchdowns the team has scored
        from passing.
        """
        return int(self._pass_touchdowns)

    @property
    def interceptions(self):
        """
        Returns an int of the total number of interceptions the team has
        thrown.
        """
        return int(self._interceptions)

    @property
    def pass_net_yards_per_attempt(self):
        """
        Returns a float of the net yards gained per passing play including
        sacks.
        """
        return float(self._pass_net_yards_per_attempt)

    @property
    def pass_first_downs(self):
        """
        Returns an int of the number of first downs the team gained from
        passing plays.
        """
        return int(self._pass_first_downs)

    @property
    def rush_attempts(self):
        """
        Returns an int of the total number of rushing plays that were
        attempted.
        """
        return int(self._rush_attempts)

    @property
    def rush_yards(self):
        """
        Returns an int of the total number of yards that were gained from
        rushing plays.
        """
        return int(self._rush_yards)

    @property
    def rush_touchdowns(self):
        """
        Returns an int of the total number of touchdowns from rushing plays.
        """
        return int(self._rush_touchdowns)

    @property
    def rush_yards_per_attempt(self):
        """
        Returns a float of the average number of yards gained per rushing play.
        """
        return float(self._rush_yards_per_attempt)

    @property
    def rush_first_downs(self):
        """
        Returns an int of the total number of first downs gained from rushing
        plays.
        """
        return int(self._rush_first_downs)

    @property
    def penalties(self):
        """
        Returns an int of the total number of penalties called on the team
        during the season.
        """
        return int(self._penalties)

    @property
    def yards_from_penalties(self):
        """
        Returns an int of the total number of yards surrendered as a result of
        penalties called on the team.
        """
        return int(self._yards_from_penalties)

    @property
    def first_downs_from_penalties(self):
        """
        Returns an int of the total number of first downs conceded as a result
        of penalties called on the team.
        """
        return int(self._first_downs_from_penalties)

    @property
    def percent_drives_with_points(self):
        """
        Returns a float of the percentage of drives that result in points for
        the offense. Percentage ranges from 0-100.
        """
        return float(self._percent_drives_with_points)

    @property
    def percent_drives_with_turnovers(self):
        """
        Returns a float of the percentage of drives that result in an offensive
        turnover. Percentage ranges from 0-100.
        """
        return float(self._percent_drives_with_turnovers)

    @property
    def points_contributed_by_offense(self):
        """
        Returns a float of the number of expected points contributed by the
        offense.
        """
        return float(self._points_contributed_by_offense)


class Teams:
    """
    A list of all NFL teams and their stats in a given year.

    Finds and retrieves a list of all NFL teams from
    www.pro-football-reference.com and creates a Team instance for every team
    that participated in the league in a given year. The Team class comprises
    a list of all major stats and a few identifiers for the requested season.
    """
    def __init__(self, year=None):
        """
        Get a list of all Team instances

        Once Teams is invoked, it retrieves a list of all NFL teams in the
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

    def __repr__(self):
        """Returns a list of all NFL teams for the given season."""
        return self._teams

    def __iter__(self):
        """Returns an iterator of all of the NFL teams for a given season."""
        return iter(self.__repr__())

    def __len__(self):
        """Returns the number of NFL teams for a given season."""
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
            if 'class="thead onecell"' in str(team_data):
                continue
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            try:
                team_data_dict[abbr]['data'] += team_data
            except KeyError:
                team_data_dict[abbr] = {'data': team_data, 'rank': rank}
            rank += 1
        return team_data_dict

    def _retrieve_all_teams(self, year):
        """
        Find and create Team instances for all teams in the given season.

        For a given season, parses the specified NFL stats table and finds all
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
            year = utils.find_year_for_season('nfl')
        doc = pq(SEASON_PAGE_URL % year)
        teams_list = utils.get_stats_table(doc, 'div#all_team_stats')
        afc_list = utils.get_stats_table(doc, 'table#AFC')
        nfc_list = utils.get_stats_table(doc, 'table#NFC')
        for stats_list in [teams_list, afc_list, nfc_list]:
            team_data_dict = self._add_stats_data(stats_list, team_data_dict)

        for team_data in team_data_dict.values():
            team = Team(team_data['data'], team_data['rank'])
            self._teams.append(team)
