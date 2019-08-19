import pandas as pd
import re
import warnings
from functools import wraps
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from .constants import PLAYER_SCHEME, PLAYER_URL, ROSTER_URL
from .player import AbstractPlayer


def _int_property_decorator(func):
    @property
    @wraps(func)
    def wrapper(*args):
        index = args[0]._index
        prop = func(*args)
        try:
            return int(prop[index])
        except (ValueError, TypeError, IndexError):
            # If there is no value, default to None
            return None
    return wrapper


def _float_property_decorator(func):
    @property
    @wraps(func)
    def wrapper(*args):
        index = args[0]._index
        prop = func(*args)
        try:
            return float(prop[index])
        except (ValueError, TypeError, IndexError):
            # If there is no value, default to None
            return None
    return wrapper


class Player(AbstractPlayer):
    """
    Get player information and stats for all seasons.

    Given a player ID, such as 'david-blough-1' for David Blough, capture all
    relevant stats and information like name, team, height/weight, career
    starts, single season pasing yards, sacks, and much more.

    By default, the class instance will return the player's career stats, but
    single-season stats can be found by calling the instance with the requested
    season as denoted on sports-reference.com.

    Parameters
    ----------
    player_id : string
        A player's ID according to sports-reference.com, such as
        'david-blough-1' for David Blough. The player ID can be found by
        navigating to the player's stats page and getting the string between
        the final slash and the '.html' in the URL. In general, the ID is in
        the format 'first-last-n' where 'first' is the player's first name in
        lowercase, 'last' is the player's last name in lowercase, and 'n' is a
        number starting at '1' for the first time that player ID has been used
        and increments by 1 for every successive player.
    """
    def __init__(self, player_id):
        self._most_recent_season = ''
        self._index = None
        self._player_id = player_id
        self._season = None
        self._name = None
        self._team_abbreviation = None
        self._position = None
        self._height = None
        self._weight = None
        self._year = None
        self._games = None
        # Passing-specific stats
        self._completed_passes = None
        self._pass_attempts = None
        self._passing_completion = None
        self._passing_yards = None
        self._passing_touchdowns = None
        self._interceptions_thrown = None
        self._passing_yards_per_attempt = None
        self._adjusted_yards_per_attempt = None
        self._quarterback_rating = None
        # Rushing and Receiving stats
        self._rush_attempts = None
        self._rush_yards = None
        self._rush_yards_per_attempt = None
        self._rush_touchdowns = None
        self._receptions = None
        self._receiving_yards = None
        self._receiving_yards_per_reception = None
        self._receiving_touchdowns = None
        self._plays_from_scrimmage = None
        self._yards_from_scrimmage = None
        self._yards_from_scrimmage_per_play = None
        self._rushing_and_receiving_touchdowns = None
        # Defensive stats
        self._solo_tackles = None
        self._assists_on_tackles = None
        self._total_tackles = None
        self._tackles_for_loss = None
        self._sacks = None
        self._interceptions = None
        self._yards_returned_from_interceptions = None
        self._yards_returned_per_interception = None
        self._interceptions_returned_for_touchdown = None
        self._passes_defended = None
        self._fumbles_recovered = None
        self._yards_recovered_from_fumble = None
        self._fumbles_recovered_for_touchdown = None
        self._fumbles_forced = None
        # Miscellaneous scoring stats
        self._punt_return_touchdowns = None
        self._kickoff_return_touchdowns = None
        self._other_touchdowns = None
        self._total_touchdowns = None
        self._extra_points_made = None
        self._field_goals_made = None
        self._two_point_conversions = None
        self._safeties = None
        self._points = None

        player_data = self._pull_player_data()
        if not player_data:
            return
        self._find_initial_index()
        AbstractPlayer.__init__(self, player_id, self._name, player_data)

    def _build_url(self):
        """
        Create the player's URL to pull stats from.

        The player's URL requires the player ID.

        Returns
        -------
        string
            The string URL for the player's stats page.
        """
        return PLAYER_URL % self._player_id

    def _retrieve_html_page(self):
        """
        Download the requested player's stats page.

        Download the requested page and strip all of the comment tags before
        returning a PyQuery object which will be used to parse the data.
        Oftentimes, important data is contained in tables which are hidden in
        HTML comments and not accessible via PyQuery.

        Returns
        -------
        PyQuery object
            The requested page is returned as a queriable PyQuery object with
            the comment tags removed.
        """
        url = self._build_url()
        try:
            url_data = pq(url)
        except HTTPError:
            return None
        return pq(utils._remove_html_comment_tags(url_data))

    def _parse_season(self, row):
        """
        Parse the season string from the table.

        The season is generally located in the first column of the stats tables
        and should be parsed to detonate which season metrics are being pulled
        from.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object of a single row in a stats table.

        Returns
        -------
        string
            A string representation of the season in the format 'YYYY', such as
            '2017'.
        """
        season = utils._parse_field(PLAYER_SCHEME, row, 'season')
        return season.replace('*', '').replace('+', '')

    def _combine_season_stats(self, table_rows, career_stats, all_stats_dict):
        """
        Combine all stats for each season.

        Since all of the stats are spread across multiple tables, they should
        be combined into a single field which can be used to easily query stats
        at once.

        Parameters
        ----------
        table_rows : generator
            A generator where each element is a row in a stats table.
        career_stats : generator
            A generator where each element is a row in the footer of a stats
            table. Career stats are kept in the footer, hence the usage.
        all_stats_dict : dictionary
            A dictionary of all stats separated by season where each key is the
            season ``string``, such as '2017', and the value is a
            ``dictionary`` with a ``string`` of 'data' and ``string``
            containing all of the data.

        Returns
        -------
        dictionary
            Returns an updated version of the passed all_stats_dict which
            includes more metrics from the provided table.
        """
        most_recent_season = self._most_recent_season
        if not table_rows:
            table_rows = []
        for row in table_rows:
            season = self._parse_season(row)
            try:
                all_stats_dict[season]['data'] += str(row)
            except KeyError:
                all_stats_dict[season] = {'data': str(row)}
            most_recent_season = season
        self._most_recent_season = most_recent_season
        if not career_stats:
            return all_stats_dict
        try:
            all_stats_dict['Career']['data'] += str(next(career_stats))
        except KeyError:
            all_stats_dict['Career'] = {'data': str(next(career_stats))}
        return all_stats_dict

    def _combine_all_stats(self, player_info):
        """
        Pull stats from all tables into a single data structure.

        Pull the stats from all of the requested tables into a dictionary that
        is separated by season to allow easy queries of the player's stats for
        each season.

        Parameters
        ----------
        player_info : PyQuery object
            A PyQuery object containing all of the stats information for the
            requested player.

        Returns
        -------
        dictionary
            Returns a dictionary where all stats from each table are combined
            by season to allow easy queries by year.
        """
        all_stats_dict = {}

        for table_id in ['passing', 'rushing', 'defense', 'scoring']:
            table_items = utils._get_stats_table(player_info,
                                                 'table#%s' % table_id)
            career_items = utils._get_stats_table(player_info,
                                                  'table#%s' % table_id,
                                                  footer=True)
            all_stats_dict = self._combine_season_stats(table_items,
                                                        career_items,
                                                        all_stats_dict)
        return all_stats_dict

    def _parse_player_information(self, player_info):
        """
        Parse general player information.

        Parse general player information such as height, weight, and name. The
        attribute for the requested field will be set with the value prior to
        returning.

        Parameters
        ----------
        player_info : PyQuery object
            A PyQuery object containing the HTML from the player's stats page.
        """
        for field in ['_height', '_weight', '_name']:
            short_field = str(field)[1:]
            value = utils._parse_field(PLAYER_SCHEME, player_info, short_field)
            setattr(self, field, value)

    def _pull_player_data(self):
        """
        Pull and aggregate all player information.

        Pull the player's HTML stats page and parse unique properties, such as
        the player's height, weight, and name. Next, combine all stats for all
        seasons plus the player's career stats into a single object which can
        easily be iterated upon.

        Returns
        -------
        dictionary
            Returns a dictionary of the player's combined stats where each key
            is a string of the season and the value is the season's associated
            stats.
        """
        player_info = self._retrieve_html_page()
        if not player_info:
            return
        self._parse_player_information(player_info)
        all_stats = self._combine_all_stats(player_info)
        setattr(self, '_season', list(all_stats.keys()))
        return all_stats

    def _find_initial_index(self):
        """
        Find the index of the career stats.

        When the Player class is instantiated, the default stats to pull are
        the player's career stats. Upon being called, the index of the 'Career'
        element should be the index value.
        """
        index = 0
        for season in self._season or season == 'Career':
            if season == 'Career':
                self._index = index
                break
            index += 1

    def __call__(self, requested_season=''):
        """
        Specify a different season to pull stats from.

        A different season can be requested by passing the season string, such
        as '2017' to the class instance.

        Parameters
        ----------
        requested_season : string (optional)
            A string of the requested season to query, such as '2017'. If left
            blank or 'Career' is passed, the career stats will be used for
            stats queries.

        Returns
        -------
        Player class instance
            Returns the class instance with the updated stats being referenced.
        """
        if requested_season.lower() == 'career' or \
           requested_season == '':
            requested_season = 'Career'
        index = 0
        if not self._season:
            return self
        for season in self._season:
            if season == requested_season:
                self._index = index
                break
            index += 1
        return self

    def _dataframe_fields(self):
        """
        Creates a dictionary of all fields to include with DataFrame.

        With the result of the calls to class properties changing based on the
        class index value, the dictionary should be regenerated every time the
        index is changed when the dataframe property is requested.

        Returns
        -------
        dictionary
            Returns a dictionary where the keys are the shortened ``string``
            attribute names and the values are the actual value for each
            attribute for the specified index.
        """
        fields_to_include = {
            'adjusted_yards_per_attempt': self.adjusted_yards_per_attempt,
            'assists_on_tackles': self.assists_on_tackles,
            'completed_passes': self.completed_passes,
            'extra_points_made': self.extra_points_made,
            'field_goals_made': self.field_goals_made,
            'fumbles_forced': self.fumbles_forced,
            'fumbles_recovered': self.fumbles_recovered,
            'fumbles_recovered_for_touchdown':
            self.fumbles_recovered_for_touchdown,
            'games': self.games,
            'height': self.height,
            'interceptions': self.interceptions,
            'interceptions_returned_for_touchdown':
            self.interceptions_returned_for_touchdown,
            'interceptions_thrown': self.interceptions_thrown,
            'kickoff_return_touchdowns': self.kickoff_return_touchdowns,
            'name': self.name,
            'other_touchdowns': self.other_touchdowns,
            'pass_attempts': self.pass_attempts,
            'passes_defended': self.passes_defended,
            'passing_completion': self.passing_completion,
            'passing_touchdowns': self.passing_touchdowns,
            'passing_yards': self.passing_yards,
            'passing_yards_per_attempt': self.passing_yards_per_attempt,
            'player_id': self.player_id,
            'plays_from_scrimmage': self.plays_from_scrimmage,
            'points': self.points,
            'position': self.position,
            'punt_return_touchdowns': self.punt_return_touchdowns,
            'quarterback_rating': self.quarterback_rating,
            'receiving_touchdowns': self.receiving_touchdowns,
            'receiving_yards': self.receiving_yards,
            'receiving_yards_per_reception':
            self.receiving_yards_per_reception,
            'receptions': self.receptions,
            'rush_attempts': self.rush_attempts,
            'rush_touchdowns': self.rush_touchdowns,
            'rush_yards': self.rush_yards,
            'rush_yards_per_attempt': self.rush_yards_per_attempt,
            'rushing_and_receiving_touchdowns':
            self.rushing_and_receiving_touchdowns,
            'sacks': self.sacks,
            'safeties': self.safeties,
            'season': self.season,
            'solo_tackles': self.solo_tackles,
            'tackles_for_loss': self.tackles_for_loss,
            'team_abbreviation': self.team_abbreviation,
            'total_tackles': self.total_tackles,
            'total_touchdowns': self.total_touchdowns,
            'two_point_conversions': self.two_point_conversions,
            'weight': self.weight,
            'yards_from_scrimmage': self.yards_from_scrimmage,
            'yards_from_scrimmage_per_play':
            self.yards_from_scrimmage_per_play,
            'yards_recovered_from_fumble': self.yards_recovered_from_fumble,
            'yards_returned_from_interceptions':
            self.yards_returned_from_interceptions,
            'yards_returned_per_interception':
            self.yards_returned_per_interception,
            'year': self.year
        }
        return fields_to_include

    @property
    def dataframe(self):
        """
        Returns a ``pandas DataFrame`` containing all other relevant class
        properties and values where each index is a different season plus the
        career stats.
        """
        temp_index = self._index
        rows = []
        indices = []
        if not self._season:
            return None
        for season in self._season:
            self._index = self._season.index(season)
            rows.append(self._dataframe_fields())
            indices.append(season)
        self._index = temp_index
        return pd.DataFrame(rows, index=[indices])

    @property
    def season(self):
        """
        Returns a ``string`` of the season in the format 'YYYY', such as
        '2017'. If no season was requested, the career stats will be returned
        for the player and the season will default to 'Career'.
        """
        return self._season[self._index]

    @property
    def team_abbreviation(self):
        """
        Returns a ``string`` of the team's abbreviation, such as 'PURDUE' for
        the Purdue Boilermakers.
        """
        return self._team_abbreviation[self._index]

    @property
    def position(self):
        """
        Returns a ``string`` of the player's primary position.
        """
        # If the position is left blank for the career stats, it will show
        # the player as not having a position. Since player stats default to
        # career, this will make it appear no players have a position. Instead,
        # default to the most recent season.
        if self.season == 'Career' and self._position[self._index] == '':
            index = self._season.index(self._most_recent_season)
            return self._position[index]
        return self._position[self._index]

    @property
    def height(self):
        """
        Returns a ``string`` of the player's height in the format
        "feet-inches".
        """
        return self._height

    @property
    def weight(self):
        """
        Returns an ``int`` of the player's weight in pounds.
        """
        try:
            return int(self._weight.replace('lb', ''))
        except AttributeError:
            return None

    @property
    def year(self):
        """
        Returns a ``string`` of the player's class designation, such as'FR' for
        freshmen.
        """
        return self._year[self._index]

    @_int_property_decorator
    def games(self):
        """
        Returns an ``int`` of the number of games the player participated in.
        """
        return self._games

    @_int_property_decorator
    def completed_passes(self):
        """
        Returns an ``int`` of the number of completed passes the player threw.
        """
        return self._completed_passes

    @_int_property_decorator
    def attempted_passes(self):
        """
        Returns an ``int`` of the number of passes the player attempted.
        """
        warnings.warn('Warning: "attempted_passes" is deprecated and will '
                      'be removed in a future release. Please use '
                      '"pass_attempts" instead for identical functionality.',
                      DeprecationWarning)
        return self._pass_attempts

    @_int_property_decorator
    def pass_attempts(self):
        """
        Returns an ``int`` of the number of passes the player attempted.
        """
        return self._pass_attempts

    @_float_property_decorator
    def passing_completion(self):
        """
        Returns a ``float`` of the percentage of passes that were caught by a
        receiver. Percentage ranges from 0-100.
        """
        return self._passing_completion

    @_int_property_decorator
    def passing_yards(self):
        """
        Returns an ``int`` of the total number of yards the player gained from
        passing the ball.
        """
        return self._passing_yards

    @_int_property_decorator
    def passing_touchdowns(self):
        """
        Returns an ``int`` of the number of touchdowns passes the player has
        thrown.
        """
        return self._passing_touchdowns

    @_int_property_decorator
    def interceptions_thrown(self):
        """
        Returns an ``int`` of the number of interceptions the player has
        thrown.
        """
        return self._interceptions_thrown

    @_float_property_decorator
    def adjusted_yards_per_attempt(self):
        """
        Returns a ``float`` of the adjusted number of yards gained per passing
        attempt, equal to (yards + 20 * pass_touchdowns - 45 * interceptions) /
        pass_attempts.
        """
        return self._adjusted_yards_per_attempt

    @_float_property_decorator
    def quarterback_rating(self):
        """
        Returns a ``float`` of the player's quarterback rating.
        """
        return self._quarterback_rating

    @_int_property_decorator
    def rush_attempts(self):
        """
        Returns an ``int`` of the number of rushing plays the player attempted.
        """
        return self._rush_attempts

    @_int_property_decorator
    def rush_yards(self):
        """
        Returns an ``int`` of the number of rushing yards the player gained.
        """
        return self._rush_yards

    @_float_property_decorator
    def rush_yards_per_attempt(self):
        """
        Returns a ``float`` of the average number of yards gained per rushing
        attempt.
        """
        return self._rush_yards_per_attempt

    @_int_property_decorator
    def rush_touchdowns(self):
        """
        Returns an ``int`` of the number of rushing touchdowns the player
        scored.
        """
        return self._rush_touchdowns

    @_int_property_decorator
    def receptions(self):
        """
        Returns an ``int`` of the number of receptions the player made.
        """
        return self._receptions

    @_int_property_decorator
    def receiving_yards(self):
        """
        Returns an ``int`` of the number of receiving yards the player gained.
        """
        return self._receiving_yards

    @_float_property_decorator
    def receiving_yards_per_reception(self):
        """
        Returns a ``float`` of the average number of yards the player gained
        per reception.
        """
        return self._receiving_yards_per_reception

    @_int_property_decorator
    def receiving_touchdowns(self):
        """
        Returns an ``int`` of the number of touchdowns the player scored after
        receiving a pass.
        """
        return self._receiving_touchdowns

    @_int_property_decorator
    def plays_from_scrimmage(self):
        """
        Returns an ``int`` of the combined number of rushing attempts and
        receptions the player had.
        """
        return self._plays_from_scrimmage

    @_int_property_decorator
    def yards_from_scrimmage(self):
        """
        Returns an ``int`` of the total number of yards gained from scrimmage
        for both rushing and receiving.
        """
        return self._yards_from_scrimmage

    @_float_property_decorator
    def yards_from_scrimmage_per_play(self):
        """
        Returns a ``float`` of the average number of yards gained per rushing
        attempt and/or reception.
        """
        return self._yards_from_scrimmage_per_play

    @_int_property_decorator
    def rushing_and_receiving_touchdowns(self):
        """
        Returns an ``int`` of the combined number of rushing and receiving
        touchdowns the player scored.
        """
        return self._rushing_and_receiving_touchdowns

    @_int_property_decorator
    def solo_tackles(self):
        """
        Returns an ``int`` of the number of tackles the player made by himself.
        """
        return self._solo_tackles

    @_int_property_decorator
    def assists_on_tackles(self):
        """
        Returns an ``int`` of the number of assists the player made on tackles.
        """
        return self._assists_on_tackles

    @_int_property_decorator
    def total_tackles(self):
        """
        Returns an ``int`` of the number of tackles the player made.
        """
        return self._total_tackles

    @_float_property_decorator
    def tackles_for_loss(self):
        """
        Returns a ``float`` of the number of tackles for a loss the player
        made.
        """
        return self._tackles_for_loss

    @_float_property_decorator
    def sacks(self):
        """
        Returns a ``float`` of the number of times the player sacked a
        quarterback.
        """
        return self._sacks

    @_int_property_decorator
    def interceptions(self):
        """
        Returns an ``int`` of the number of times the player intercepted a
        pass.
        """
        return self._interceptions

    @_int_property_decorator
    def yards_returned_from_interceptions(self):
        """
        Returns an ``int`` of the number of yards the player returned after
        intercepting a pass.
        """
        return self._yards_returned_from_interceptions

    @_float_property_decorator
    def yards_returned_per_interception(self):
        """
        Returns a ``float`` of the average number of yards the player returns
        after intercepting a pass.
        """
        return self._yards_returned_per_interception

    @_int_property_decorator
    def interceptions_returned_for_touchdown(self):
        """
        Returns an ``int`` of the number of touchdowns the player has scored
        after intercepting a pass. Commonly referred to as a 'Pick-6'.
        """
        return self._interceptions_returned_for_touchdown

    @_int_property_decorator
    def passes_defended(self):
        """
        Returns an ``int`` of the number of passes the player has defended as a
        defensive player.
        """
        return self._passes_defended

    @_int_property_decorator
    def fumbles_recovered(self):
        """
        Returns an ``int`` of the number of fumbles the player has recovered.
        """
        return self._fumbles_recovered

    @_int_property_decorator
    def yards_recovered_from_fumble(self):
        """
        Returns an ``int`` of the number of yards the player gained after
        recovering a fumble.
        """
        return self._yards_recovered_from_fumble

    @_int_property_decorator
    def fumbles_recovered_for_touchdown(self):
        """
        Returns an ``int`` of the number of touchdowns the player has scored
        after recovering a fumble.
        """
        return self._fumbles_recovered_for_touchdown

    @_int_property_decorator
    def fumbles_forced(self):
        """
        Returns an ``int`` of the number of times the player forced a fumble.
        """
        return self._fumbles_forced

    @_int_property_decorator
    def punt_return_touchdowns(self):
        """
        Returns an ``int`` of the number of punts the player returned for a
        touchdown.
        """
        return self._punt_return_touchdowns

    @_int_property_decorator
    def kickoff_return_touchdowns(self):
        """
        Returns an ``int`` of the number of kickoffs the player returned for a
        touchdown.
        """
        return self._kickoff_return_touchdowns

    @_int_property_decorator
    def other_touchdowns(self):
        """
        Returns an ``int`` of the total number of all other types of touchdowns
        the player has scored.
        """
        return self._other_touchdowns

    @_int_property_decorator
    def total_touchdowns(self):
        """
        Returns an ``int`` of the total number of touchdowns the player has
        scored.
        """
        return self._total_touchdowns

    @_int_property_decorator
    def extra_points_made(self):
        """
        Returns an ``int`` of the number of extra points the player made.
        """
        return self._extra_points_made

    @_int_property_decorator
    def field_goals_made(self):
        """
        Returns an ``int`` of the total number of field goals the player made
        from any distance.
        """
        return self._field_goals_made

    @_int_property_decorator
    def two_point_conversions(self):
        """
        Returns an ``int`` of the number of two point conversions the player
        has scored.
        """
        return self._two_point_conversions

    @_int_property_decorator
    def safeties(self):
        """
        Returns an ``int`` of the number of safeties the player has scored.
        """
        return self._safeties

    @_int_property_decorator
    def points(self):
        """
        Returns an ``int`` of the number of points the player has scored.
        """
        return self._points


class Roster:
    """
    Get stats for all players on a roster.

    Request a team's roster for a given season and create instances of the
    Player class for each player, containing a detailed list of the player's
    statistics and information.

    Parameters
    ----------
    team : string
        The team's abbreviation, such as 'PURDUE' for the Purdue Boilermakers.
    year : string (optional)
        The 4-digit year to pull the roster from, such as '2017'. If left
        blank, defaults to the most recent season.
    slim : boolean (optional)
        Set to True to return a limited subset of player information including
        the name and player ID for each player as opposed to all of their
        respective stats which greatly reduces the time to return a response if
        just the names and IDs are desired. Defaults to False.
    """
    def __init__(self, team, year=None, slim=False):
        self._team = team
        self._slim = slim
        if slim:
            self._players = {}
        else:
            self._players = []

        self._find_players(year)

    def _pull_team_page(self, url):
        """
        Download the team page.

        Download the requested team's season page and create a PyQuery object.

        Parameters
        ----------
        url : string
            A string of the built URL for the requested team and season.

        Returns
        -------
        PyQuery object
            Returns a PyQuery object of the team's HTML page.
        """
        try:
            return pq(utils._remove_html_comment_tags(pq(url)))
        except HTTPError:
            return None

    def _create_url(self, year):
        """
        Build the team URL.

        Build a URL given a team's abbreviation and the 4-digit year.

        Parameters
        ----------
        year : string
            The 4-digit string representing the year to pull the team's roster
            from.

        Returns
        -------
        string
            Returns a string of the team's season page for the requested team
            and year.
        """
        return ROSTER_URL % (self._team.lower(), year)

    def _get_id(self, player):
        """
        Parse the player ID.

        Given a PyQuery object representing a single player on the team roster,
        parse the player ID and return it as a string.

        Parameters
        ----------
        player : PyQuery object
            A PyQuery object representing the player information from the
            roster table.

        Returns
        -------
        string
            Returns a string of the player ID.
        """
        name_tag = player('th[data-stat="player"] a')
        name = re.sub(r'.*/players/', '', str(name_tag))
        return re.sub(r'\.htm.*', '', name)

    def _get_name(self, player):
        """
        Parse the player's name.

        Given a PyQuery object representing a single player on the team roster,
        parse the player ID and return it as a string.

        Parameters
        ----------
        player : PyQuery object
            A PyQuery object representing the player information from the
            roster table.

        Returns
        -------
        string
            Returns a string of the player's name.
        """
        name_tag = player('th[data-stat="player"] a')
        return name_tag.text()

    def _find_players(self, year):
        """
        Find all player IDs for the requested team.

        For the requested team and year (if applicable), pull the roster table
        and parse the player ID for all players on the roster and create an
        instance of the Player class for the player. All player instances are
        added to the 'players' property to get all stats for all players on a
        team.

        Parameters
        ----------
        year : string
            The 4-digit string representing the year to pull the team's roster
            from.
        """
        if not year:
            year = utils._find_year_for_season('ncaaf')
            # If stats for the requested season do not exist yet (as is the
            # case right before a new season begins), attempt to pull the
            # previous year's stats. If it exists, use the previous year
            # instead.
            if not utils._url_exists(self._create_url(year)) and \
               utils._url_exists(self._create_url(str(int(year) - 1))):
                year = str(int(year) - 1)
        url = self._create_url(year)
        page = self._pull_team_page(url)
        if not page:
            output = ("Can't pull requested team page. Ensure the following "
                      "URL exists: %s" % url)
            raise ValueError(output)
        for player in page('table#roster tbody tr').items():
            player_id = self._get_id(player)
            if self._slim:
                name = self._get_name(player)
                self._players[player_id] = name
            else:
                player_instance = Player(player_id)
                self._players.append(player_instance)

    @property
    def players(self):
        """
        Returns a ``list`` of player instances for each player on the requested
        team's roster if the ``slim`` property is False when calling the Roster
        class. If the ``slim`` property is True, returns a ``dictionary`` where
        each key is a string of the player's ID and each value is the player's
        first and last name as listed on the roster page.
        """
        return self._players
