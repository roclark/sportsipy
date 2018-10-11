import pandas as pd
import re
from functools import wraps
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery as pq
from .. import utils
from .constants import PLAYER_SCHEME, PLAYER_URL, ROSTER_URL
from six.moves.urllib.error import HTTPError


def _cleanup(prop):
    try:
        prop = prop.replace('%', '')
        prop = prop.replace('$', '')
        prop = prop.replace(',', '')
        return prop.replace('+', '')
    # Occurs when a value is of Nonetype. When that happens, return a blank
    # string as whatever came in had an incomplete value.
    except AttributeError:
        return ''


def _int_property_decorator(func):
    @property
    @wraps(func)
    def wrapper(*args):
        index = args[0]._index
        prop = func(*args)
        value = _cleanup(prop[index])
        try:
            return int(value)
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
        value = _cleanup(prop[index])
        try:
            return float(value)
        except (ValueError, TypeError, IndexError):
            # If there is no value, default to None
            return None
    return wrapper


class Player(object):
    """
    Get player information and stats for all seasons.

    Given a player ID, such as 'BreeDr00' for Drew Brees, capture all relevant
    stats and information like name, team, height/weight, career starts, single
    season pasing yards, sacks, and much more.

    By default, the class instance will return the player's career stats, but
    single-season stats can be found by calling the instance with the requested
    season as denoted on pro-football-reference.com.

    Parameters
    ----------
    player_id : string
        A player's ID according to pro-football-reference.com, such as
        'BreeDr00' for Drew Brees. The player ID can be found by navigating to
        the player's stats page and getting the string between the final slash
        and the '.htm' in the URL. In general, the ID is in the format
        'LlllFfNN' where 'Llll' are the first 4 letters in the player's last
        name with the first letter capitalized, 'Ff' are the first 2 letters in
        the player's first name where the first letter is capitalized, and 'NN'
        is a number starting at '00' for the first time that player ID has been
        used and increments by 1 for every successive player.
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
        self._birth_date = None
        self._games = None
        self._games_started = None
        self._approximate_value = None
        # Passing-specific stats
        self._qb_record = None
        self._completed_passes = None
        self._attempted_passes = None
        self._passing_completion = None
        self._passing_yards = None
        self._passing_touchdowns = None
        self._passing_touchdown_percentage = None
        self._interceptions_thrown = None
        self._interception_percentage = None
        self._longest_pass = None
        self._passing_yards_per_attempt = None
        self._adjusted_yards_per_attempt = None
        self._yards_per_completed_pass = None
        self._yards_per_game_played = None
        self._quarterback_rating = None
        self._espn_qbr = None
        self._times_sacked = None
        self._yards_lost_to_sacks = None
        self._net_yards_per_pass_attempt = None
        self._adjusted_net_yards_per_pass_attempt = None
        self._sack_percentage = None
        self._fourth_quarter_comebacks = None
        self._game_winning_drives = None
        self._yards_per_attempt_index = None
        self._net_yards_per_attempt_index = None
        self._adjusted_yards_per_attempt_index = None
        self._adjusted_net_yards_per_attempt_index = None
        self._completion_percentage_index = None
        self._touchdown_percentage_index = None
        self._interception_percentage_index = None
        self._sack_percentage_index = None
        self._passer_rating_index = None
        # Rushing-specific stats
        self._rush_attempts = None
        self._rush_yards = None
        self._rush_touchdowns = None
        self._longest_rush = None
        self._rush_yards_per_attempt = None
        self._rush_yards_per_game = None
        self._rush_attempts_per_game = None
        # Receiving-specific stats
        self._times_pass_target = None
        self._receptions = None
        self._receiving_yards = None
        self._receiving_yards_per_reception = None
        self._receiving_touchdowns = None
        self._longest_reception = None
        self._receptions_per_game = None
        self._receiving_yards_per_game = None
        self._catch_percentage = None
        # Combined receiving and rushing stats
        self._touches = None
        self._yards_per_touch = None
        self._yards_from_scrimmage = None
        self._rushing_and_receiving_touchdowns = None
        self._fumbles = None
        # Punt/Kick return stats
        self._punt_returns = None
        self._punt_return_yards = None
        self._punt_return_touchdown = None
        self._longest_punt_return = None
        self._yards_per_punt_return = None
        self._kickoff_returns = None
        self._kickoff_return_yards = None
        self._kickoff_return_touchdown = None
        self._longest_kickoff_return = None
        self._yards_per_kickoff_return = None
        self._all_purpose_yards = None
        # Kicking-specific stats
        self._less_than_nineteen_yards_field_goal_attempts = None
        self._less_than_nineteen_yards_field_goals_made = None
        self._twenty_to_twenty_nine_yard_field_goal_attempts = None
        self._twenty_to_twenty_nine_yard_field_goals_made = None
        self._thirty_to_thirty_nine_yard_field_goal_attempts = None
        self._thirty_to_thirty_nine_yard_field_goals_made = None
        self._fourty_to_fourty_nine_yard_field_goal_attempts = None
        self._fourty_to_fourty_nine_yard_field_goals_made = None
        self._fifty_plus_yard_field_goal_attempts = None
        self._fifty_plus_yard_field_goals_made = None
        self._field_goals_attempted = None
        self._field_goals_made = None
        self._longest_field_goal_made = None
        self._field_goal_percentage = None
        self._extra_points_attempted = None
        self._extra_points_made = None
        self._extra_point_percentage = None
        # Punting-specific stats
        self._punts = None
        self._total_punt_yards = None
        self._longest_punt = None
        self._blocked_punts = None
        self._yards_per_punt = None
        # Defensive-specific stats
        self._interceptions = None
        self._yards_returned_from_interception = None
        self._interceptions_returned_for_touchdown = None
        self._longest_interception_return = None
        self._passes_defended = None
        self._fumbles_forced = None
        self._fumbles_recovered = None
        self._yards_recovered_from_fumble = None
        self._fumbles_recovered_for_touchdown = None
        self._sacks = None
        self._tackles = None
        self._assists_on_tackles = None
        self._safeties = None

        self._parse_player_data()
        self._find_initial_index()

    def _build_url(self):
        """
        Create the player's URL to pull stats from.

        The player's URL requires the first letter of the player's last name
        followed by the player ID.

        Returns
        -------
        string
            The string URL for the player's stats page.
        """
        # The first letter of the player's last name is used to sort the player
        # list and is a part of the URL.
        first_character = self._player_id[0]
        return PLAYER_URL % (first_character, self._player_id)

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
        # For NFL, a 404 page doesn't actually raise a 404 error, so it needs
        # to be manually checked.
        if 'Page Not Found (404 error)' in str(url_data):
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
        most_recent_season = ''
        for row in table_rows:
            season = self._parse_season(row)
            try:
                all_stats_dict[season]['data'] += str(row)
            except KeyError:
                all_stats_dict[season] = {'data': str(row)}
            most_recent_season = season
        self._most_recent_season = most_recent_season
        try:
            all_stats_dict['career']['data'] += str(next(career_stats))
        except KeyError:
            try:
                all_stats_dict['career'] = {'data': str(next(career_stats))}
            # Occurs when the player doesn't have any career stats listed on
            # their page in error.
            except StopIteration:
                return all_stats_dict
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

        for table_id in ['passing', 'passing_advanced',
                         'rushing_and_receiving', 'defense', 'returns',
                         'kicking']:
            try:
                table_items = utils._get_stats_table(player_info,
                                                     'table#%s' % table_id)
            # Error is thrown when player does not have the corresponding
            # table, such as a quarterback not having any kicking stats.
            except (ParserError, XMLSyntaxError):
                continue
            career_items = utils._get_stats_table(player_info,
                                                  'table#%s' % table_id,
                                                  footer=True)
            all_stats_dict = self._combine_season_stats(table_items,
                                                        career_items,
                                                        all_stats_dict)
        return all_stats_dict

    def _parse_player_information(self, player_info, field):
        """
        Parse general player information.

        Parse general player information such as height, weight, and name. The
        attribute for the requested field will be set with the value prior to
        returning.

        Parameters
        ----------
        player_info : PyQuery object
            A PyQuery object containing the HTML from the player's stats page.
        field : string
            A string of the attribute to parse, such as 'weight'.
        """
        short_field = str(field)[1:]
        value = utils._parse_field(PLAYER_SCHEME, player_info, short_field)
        setattr(self, field, value)

    def _parse_birth_date(self, player_info):
        """
        Parse the player's birth date.

        Parse the player's birth date which is embedded in an attribute in
        their birth tag on the HTML page.

        Parameters
        ----------
        player_info : PyQuery object
            A PyQuery object containing the HTML from the player's stats page.
        """
        birth_date = player_info('span#necro-birth').attr('data-birth')
        setattr(self, '_birth_date', birth_date)

    def _parse_player_data(self):
        """
        Parse all player information and set attributes.

        Pull the player's HTML stats page and go through each class attribute
        to parse the data from the HTML page and set attribute values with the
        result.
        """
        player_info = self._retrieve_html_page()
        if not player_info:
            return
        all_stats_dict = self._combine_all_stats(player_info)

        for field in self.__dict__:
            short_field = str(field)[1:]
            if short_field == 'player_id' or \
               short_field == 'index' or \
               short_field == 'most_recent_season':
                continue
            if short_field == 'name' or \
               short_field == 'weight' or \
               short_field == 'height':
                self._parse_player_information(player_info, field)
                continue
            if short_field == 'birth_date':
                self._parse_birth_date(player_info)
                continue
            field_stats = []
            for year, data in all_stats_dict.items():
                stats = pq(data['data'])
                if short_field == 'season':
                    value = self._parse_season(stats)
                else:
                    value = utils._parse_field(PLAYER_SCHEME,
                                               stats,
                                               short_field)
                field_stats.append(value)
            setattr(self, field, field_stats)

    def _find_initial_index(self):
        """
        Find the index of the career stats.

        When the Player class is instantiated, the default stats to pull are
        the player's career stats. Upon being called, the index of the 'Career'
        element should be the index value.
        """
        index = 0
        # Occurs when the player has invalid data or can't be found.
        if not self._season:
            return
        for season in self._season:
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
            'adjusted_net_yards_per_attempt_index':
            self.adjusted_net_yards_per_attempt_index,
            'adjusted_net_yards_per_pass_attempt':
            self.adjusted_net_yards_per_pass_attempt,
            'adjusted_yards_per_attempt': self.adjusted_yards_per_attempt,
            'adjusted_yards_per_attempt_index':
            self.adjusted_yards_per_attempt_index,
            'all_purpose_yards': self.all_purpose_yards,
            'approximate_value': self.approximate_value,
            'assists_on_tackles': self.assists_on_tackles,
            'attempted_passes': self.attempted_passes,
            'birth_date': self.birth_date,
            'blocked_punts': self.blocked_punts,
            'catch_percentage': self.catch_percentage,
            'completed_passes': self.completed_passes,
            'completion_percentage_index': self.completion_percentage_index,
            'espn_qbr': self.espn_qbr,
            'extra_point_percentage': self.extra_point_percentage,
            'extra_points_attempted': self.extra_points_attempted,
            'extra_points_made': self.extra_points_made,
            'field_goal_percentage': self.field_goal_percentage,
            'field_goals_attempted': self.field_goals_attempted,
            'field_goals_made': self.field_goals_made,
            'fifty_plus_yard_field_goal_attempts':
            self.fifty_plus_yard_field_goal_attempts,
            'fifty_plus_yard_field_goals_made':
            self.fifty_plus_yard_field_goals_made,
            'fourth_quarter_comebacks': self.fourth_quarter_comebacks,
            'fourty_to_fourty_nine_yard_field_goal_attempts':
            self.fourty_to_fourty_nine_yard_field_goal_attempts,
            'fourty_to_fourty_nine_yard_field_goals_made':
            self.fourty_to_fourty_nine_yard_field_goals_made,
            'fumbles': self.fumbles,
            'fumbles_forced': self.fumbles_forced,
            'fumbles_recovered': self.fumbles_recovered,
            'fumbles_recovered_for_touchdown':
            self.fumbles_recovered_for_touchdown,
            'game_winning_drives': self.game_winning_drives,
            'games': self.games,
            'games_started': self.games_started,
            'height': self.height,
            'interception_percentage': self.interception_percentage,
            'interception_percentage_index':
            self.interception_percentage_index,
            'interceptions': self.interceptions,
            'interceptions_returned_for_touchdown':
            self.interceptions_returned_for_touchdown,
            'interceptions_thrown': self.interceptions_thrown,
            'kickoff_return_touchdown': self.kickoff_return_touchdown,
            'kickoff_return_yards': self.kickoff_return_yards,
            'kickoff_returns': self.kickoff_returns,
            'less_than_nineteen_yards_field_goal_attempts':
            self.less_than_nineteen_yards_field_goal_attempts,
            'less_than_nineteen_yards_field_goals_made':
            self.less_than_nineteen_yards_field_goals_made,
            'longest_field_goal_made': self.longest_field_goal_made,
            'longest_interception_return': self.longest_interception_return,
            'longest_kickoff_return': self.longest_kickoff_return,
            'longest_pass': self.longest_pass,
            'longest_punt': self.longest_punt,
            'longest_punt_return': self.longest_punt_return,
            'longest_reception': self.longest_reception,
            'longest_rush': self.longest_rush,
            'name': self.name,
            'net_yards_per_attempt_index': self.net_yards_per_attempt_index,
            'net_yards_per_pass_attempt': self.net_yards_per_pass_attempt,
            'passer_rating_index': self.passer_rating_index,
            'passes_defended': self.passes_defended,
            'passing_completion': self.passing_completion,
            'passing_touchdown_percentage': self.passing_touchdown_percentage,
            'passing_touchdowns': self.passing_touchdowns,
            'passing_yards': self.passing_yards,
            'passing_yards_per_attempt': self.passing_yards_per_attempt,
            'player_id': self.player_id,
            'position': self.position,
            'punt_return_touchdown': self.punt_return_touchdown,
            'punt_return_yards': self.punt_return_yards,
            'punt_returns': self.punt_returns,
            'punts': self.punts,
            'qb_record': self.qb_record,
            'quarterback_rating': self.quarterback_rating,
            'receiving_touchdowns': self.receiving_touchdowns,
            'receiving_yards': self.receiving_yards,
            'receiving_yards_per_game': self.receiving_yards_per_game,
            'receiving_yards_per_reception':
            self.receiving_yards_per_reception,
            'receptions': self.receptions,
            'receptions_per_game': self.receptions_per_game,
            'rush_attempts': self.rush_attempts,
            'rush_attempts_per_game': self.rush_attempts_per_game,
            'rush_touchdowns': self.rush_touchdowns,
            'rush_yards': self.rush_yards,
            'rush_yards_per_attempt': self.rush_yards_per_attempt,
            'rush_yards_per_game': self.rush_yards_per_game,
            'rushing_and_receiving_touchdowns':
            self.rushing_and_receiving_touchdowns,
            'sack_percentage': self.sack_percentage,
            'sack_percentage_index': self.sack_percentage_index,
            'sacks': self.sacks,
            'safeties': self.safeties,
            'season': self.season,
            'tackles': self.tackles,
            'team_abbreviation': self.team_abbreviation,
            'thirty_to_thirty_nine_yard_field_goal_attempts':
            self.thirty_to_thirty_nine_yard_field_goal_attempts,
            'thirty_to_thirty_nine_yard_field_goals_made':
            self.thirty_to_thirty_nine_yard_field_goals_made,
            'times_pass_target': self.times_pass_target,
            'times_sacked': self.times_sacked,
            'total_punt_yards': self.total_punt_yards,
            'touchdown_percentage_index': self.touchdown_percentage_index,
            'touches': self.touches,
            'twenty_to_twenty_nine_yard_field_goal_attempts':
            self.twenty_to_twenty_nine_yard_field_goal_attempts,
            'twenty_to_twenty_nine_yard_field_goals_made':
            self.twenty_to_twenty_nine_yard_field_goals_made,
            'weight': self.weight,
            'yards_from_scrimmage': self.yards_from_scrimmage,
            'yards_lost_to_sacks': self.yards_lost_to_sacks,
            'yards_per_attempt_index': self.yards_per_attempt_index,
            'yards_per_completed_pass': self.yards_per_completed_pass,
            'yards_per_game_played': self.yards_per_game_played,
            'yards_per_kickoff_return': self.yards_per_kickoff_return,
            'yards_per_punt': self.yards_per_punt,
            'yards_per_punt_return': self.yards_per_punt_return,
            'yards_per_touch': self.yards_per_touch,
            'yards_recovered_from_fumble': self.yards_recovered_from_fumble,
            'yards_returned_from_interception':
            self.yards_returned_from_interception
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
    def player_id(self):
        """
        Returns a ``string`` of the player's ID on pro-football-reference, such
        as 'BreeDr00' for Drew Brees.
        """
        return self._player_id

    @property
    def season(self):
        """
        Returns a ``string`` of the season in the format 'YYYY', such as
        '2017'. If no season was requested, the career stats will be returned
        for the player and the season will default to 'Career'.
        """
        return self._season[self._index]

    @property
    def name(self):
        """
        Returns a ``string`` of the player's name, such as 'Drew Brees'.
        """
        return self._name

    @property
    def team_abbreviation(self):
        """
        Returns a ``string`` of the team's abbreviation, such as 'NOR' for the
        New Orleans Saints.
        """
        return self._team_abbreviation[self._index]

    @property
    def position(self):
        """
        Returns a ``string`` of the player's primary position.
        """
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
        return int(self._weight.replace('lb', ''))

    @property
    def birth_date(self):
        """
        Returns a ``datetime`` object of the day and year the player was born.
        """
        return self._birth_date

    @_int_property_decorator
    def games(self):
        """
        Returns an ``int`` of the number of games the player participated in.
        """
        return self._games

    @_int_property_decorator
    def games_started(self):
        """
        Returns an ``int`` of the number of games the player started.
        """
        return self._games_started

    @_int_property_decorator
    def approximate_value(self):
        """
        Returns an ``int`` of the player's approximate value which is a
        singular number used to compare players across seasons and positions,
        but is only intended to be a rough estimate.
        """
        return self._approximate_value

    @property
    def qb_record(self):
        """
        Returns a ``string`` of the player's quarterback record as a starter in
        the format 'W-L-T'.
        """
        return self._qb_record[self._index]

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
        return self._attempted_passes

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
        Returns an ``int`` of the number of yards receivers have gained as a
        result of the player's passes.
        """
        return self._passing_yards

    @_int_property_decorator
    def passing_touchdowns(self):
        """
        Returns an ``int`` of the number of touchdowns passes the player has
        thrown.
        """
        return self._passing_touchdowns

    @_float_property_decorator
    def passing_touchdown_percentage(self):
        """
        Returns a ``float`` of the percentage of total passes that are
        touchdowns. Percentage ranges from 0-100.
        """
        return self._passing_touchdown_percentage

    @_int_property_decorator
    def interceptions_thrown(self):
        """
        Returns an ``int`` of the number of interceptions the player has
        thrown.
        """
        return self._interceptions_thrown

    @_float_property_decorator
    def interception_percentage(self):
        """
        Returns a ``float`` of the percentage of passes the player throws that
        are intercepted. Percentage ranges from 0-100.
        """
        return self._interception_percentage

    @_int_property_decorator
    def longest_pass(self):
        """
        Returns an ``int`` of the longest completed pass the player threw.
        """
        return self._longest_pass

    @_float_property_decorator
    def passing_yards_per_attempt(self):
        """
        Returns a ``float`` of the number of yards gained per passing attempt.
        """
        return self._passing_yards_per_attempt

    @_float_property_decorator
    def adjusted_yards_per_attempt(self):
        """
        Returns a ``float`` of the adjusted number of yards gained per passing
        attempt, equal to (yards + 20 * pass_touchdowns - 45 * interceptions) /
        pass_attempts.
        """
        return self._adjusted_yards_per_attempt

    @_float_property_decorator
    def yards_per_completed_pass(self):
        """
        Returns a ``float`` of the number of yards gained per completed pass.
        """
        return self._yards_per_completed_pass

    @_float_property_decorator
    def yards_per_game_played(self):
        """
        Returns a ``float`` of the number of passing yards gained per gamed.
        """
        return self._yards_per_game_played

    @_float_property_decorator
    def quarterback_rating(self):
        """
        Returns a ``float`` of the player's quarterback rating.
        """
        return self._quarterback_rating

    @_float_property_decorator
    def espn_qbr(self):
        """
        Returns a ``float`` of the player's Total Quarterback Rating according
        to ESPN.
        """
        return self._espn_qbr

    @_int_property_decorator
    def times_sacked(self):
        """
        Returns an ``int`` of the number of times the player was sacked as a
        quarterback.
        """
        return self._times_sacked

    @_int_property_decorator
    def yards_lost_to_sacks(self):
        """
        Returns an ``int`` of the number of yards lost as a result of sacks.
        """
        return self._yards_lost_to_sacks

    @_float_property_decorator
    def net_yards_per_pass_attempt(self):
        """
        Returns a ``float`` of the net yards gained per pass attempt, equal to
        (pass_yards - sack_yards) / (pass_attempts + times_sacked).
        """
        return self._net_yards_per_pass_attempt

    @_float_property_decorator
    def adjusted_net_yards_per_pass_attempt(self):
        """
        Returns a ``float`` of the adjusted net yards gained per pass attempt,
        equal to (pass_yards - sack_yards + (20 * pass_touchdowns) - (45 *
        interceptions)) / (pass_attempts + times_sacked).
        """
        return self._adjusted_net_yards_per_pass_attempt

    @_float_property_decorator
    def sack_percentage(self):
        """
        Returns a ``float`` of the percentage of times sacked during a passing
        attempt, equal to times_sacked / (pass_attempts + times_sacked).
        Percentage ranges from 0-100.
        """
        return self._sack_percentage

    @_int_property_decorator
    def fourth_quarter_comebacks(self):
        """
        Returns an ``int`` of the number of times the player has lead a team to
        victory or a tie as a quarterback while the team trailed at the
        beginning of the fourth quarter by scoring at the end of a drive.
        """
        return self._fourth_quarter_comebacks

    @_int_property_decorator
    def game_winning_drives(self):
        """
        Returns an ``int`` of the number of times the player has lead a drive
        that resulted in a score in the fourth quarter while the team was
        trailing.
        """
        return self._game_winning_drives

    @_int_property_decorator
    def yards_per_attempt_index(self):
        """
        Returns an ``int`` comparing players by the average number of yards
        gained per attempt where 100 denotes an average player in this category
        and higher numbers are better.
        """
        return self._yards_per_attempt_index

    @_int_property_decorator
    def net_yards_per_attempt_index(self):
        """
        Returns an ``int`` comparing players by the net average yards gained
        per attempt where 100 denotes an average player in this category and
        higher numbers are better.
        """
        return self._net_yards_per_attempt_index

    @_int_property_decorator
    def adjusted_yards_per_attempt_index(self):
        """
        Returns an ``int`` comparing players by the average adjusted yards
        gained per attempt where 100 denotes an average player in this category
        and higher numbers are better.
        """
        return self._adjusted_yards_per_attempt_index

    @_int_property_decorator
    def adjusted_net_yards_per_attempt_index(self):
        """
        Returns an ``int`` comparing players by the net average adjusted yards
        gained per attempt where 100 denotes an average player in this category
        and higher numbers are better.
        """
        return self._adjusted_net_yards_per_attempt_index

    @_int_property_decorator
    def completion_percentage_index(self):
        """
        Returns an ``int`` comparing players by their passing completion
        percentage where 100 denotes an average player in this category and
        higher numbers are better.
        """
        return self._completion_percentage_index

    @_int_property_decorator
    def touchdown_percentage_index(self):
        """
        Returns an ``int`` comparing players by the percentage of their passes
        that result in a touchdown where 100 denotes an average player in this
        category and higher numbers are better.
        """
        return self._touchdown_percentage_index

    @_int_property_decorator
    def interception_percentage_index(self):
        """
        Returns an ``int`` comparing players by the percentage of their passes
        that are intercepted where 100 denotes an average player in this
        category and higher numbers are better.
        """
        return self._interception_percentage_index

    @_int_property_decorator
    def sack_percentage_index(self):
        """
        Returns an ``int`` comparing players by the percentage of plays that
        end in the player being sacked where 100 denotes an average player in
        this category and higher numbers are better.
        """
        return self._sack_percentage_index

    @_int_property_decorator
    def passer_rating_index(self):
        """
        Returns an ``int`` comparing players by their quarterback rating where
        100 denotes an average player in this category and higher numbers are
        better.
        """
        return self._passer_rating_index

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

    @_int_property_decorator
    def rush_touchdowns(self):
        """
        Returns an ``int`` of the number of rushing touchdowns the player
        scored.
        """
        return self._rush_touchdowns

    @_int_property_decorator
    def longest_rush(self):
        """
        Returns an ``int`` of the highest number of yards the player gained
        during a single rushing attempt.
        """
        return self._longest_rush

    @_float_property_decorator
    def rush_yards_per_attempt(self):
        """
        Returns a ``float`` of the average number of yards gained per rushing
        attempt.
        """
        return self._rush_yards_per_attempt

    @_float_property_decorator
    def rush_yards_per_game(self):
        """
        Returns a ``float`` of the average number of rushing yards gained per
        game.
        """
        return self._rush_yards_per_game

    @_float_property_decorator
    def rush_attempts_per_game(self):
        """
        Returns a ``float`` of the average number of rushing attempts the
        player made per game.
        """
        return self._rush_attempts_per_game

    @_int_property_decorator
    def times_pass_target(self):
        """
        Returns an ``int`` of the number of times the player was the target of
        a pass.
        """
        return self._times_pass_target

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
    def longest_reception(self):
        """
        Returns an ``int`` of the highest number of yards the player gained as
        a result of a single reception.
        """
        return self._longest_reception

    @_float_property_decorator
    def receptions_per_game(self):
        """
        Returns a ``float`` of the average number of receptions the player
        makes per game.
        """
        return self._receptions_per_game

    @_float_property_decorator
    def receiving_yards_per_game(self):
        """
        Returns a ``float`` of the acerage number of receiving yards the player
        gains per game.
        """
        return self._receiving_yards_per_game

    @_float_property_decorator
    def catch_percentage(self):
        """
        Returns a ``float`` of the percentage of passes the player caught while
        being the target of a pass. Percentage ranges from 0-100.
        """
        return self._catch_percentage

    @_int_property_decorator
    def touches(self):
        """
        Returns an ``int`` of the combined number of rushing attempts and
        receptions the player had.
        """
        return self._touches

    @_float_property_decorator
    def yards_per_touch(self):
        """
        Returns a ``float`` of the average number of yards gained per rushing
        attempt and/or reception.
        """
        return self._yards_per_touch

    @_int_property_decorator
    def yards_from_scrimmage(self):
        """
        Returns an ``int`` of the total number of yards gained from scrimmage
        for both rushing and receiving.
        """
        return self._yards_from_scrimmage

    @_int_property_decorator
    def rushing_and_receiving_touchdowns(self):
        """
        Returns an ``int`` of the combined number of rushing and receiving
        touchdowns the player scored.
        """
        return self._rushing_and_receiving_touchdowns

    @_int_property_decorator
    def fumbles(self):
        """
        Returns an ``int`` of the number of times the player fumbled the ball.
        """
        return self._fumbles

    @_int_property_decorator
    def punt_returns(self):
        """
        Returns an ``int`` of the number of times a player returned a punt.
        """
        return self._punt_returns

    @_int_property_decorator
    def punt_return_yards(self):
        """
        Returns an ``int`` of the amount of yards the player gained while
        returning a punt.
        """
        return self._punt_return_yards

    @_int_property_decorator
    def punt_return_touchdown(self):
        """
        Returns an ``int`` of the number of punts the player returned for a
        touchdown.
        """
        return self._punt_return_touchdown

    @_int_property_decorator
    def longest_punt_return(self):
        """
        Returns an ``int`` of the highest number of yards the player has gained
        while returning a punt.
        """
        return self._longest_punt_return

    @_float_property_decorator
    def yards_per_punt_return(self):
        """
        Returns a ``float`` of the average number of yards the player returned
        per punt.
        """
        return self._yards_per_punt_return

    @_int_property_decorator
    def kickoff_returns(self):
        """
        Returns an ``int`` of the number of kickoffs the player returned.
        """
        return self._kickoff_returns

    @_int_property_decorator
    def kickoff_return_yards(self):
        """
        Returns an ``int`` of the amount of yards the player gained while
        returning a kickoff.
        """
        return self._kickoff_return_yards

    @_int_property_decorator
    def kickoff_return_touchdown(self):
        """
        Returns an ``int`` of the number of kickoffs the player returned for a
        touchdown.
        """
        return self._kickoff_return_touchdown

    @_int_property_decorator
    def longest_kickoff_return(self):
        """
        Returns an ``int`` of the highest number of yards the player has gained
        while returning a kickoff.
        """
        return self._longest_kickoff_return

    @_float_property_decorator
    def yards_per_kickoff_return(self):
        """
        Returns a ``float`` of the average number of yards the player returned
        per kickoff.
        """
        return self._yards_per_kickoff_return

    @_int_property_decorator
    def all_purpose_yards(self):
        """
        Returns an ``int`` of the number of all-purpose yards the player has
        gained from receptions, rushes, and kickoff and punt returns.
        """
        return self._all_purpose_yards

    @_int_property_decorator
    def less_than_nineteen_yards_field_goal_attempts(self):
        """
        Returns an ``int`` of the number of field goals the player attempted
        from nineteen or fewer yards out.
        """
        return self._less_than_nineteen_yards_field_goal_attempts

    @_int_property_decorator
    def less_than_nineteen_yards_field_goals_made(self):
        """
        Returns an ``int`` of the number of field goals the player made from
        nineteen or fewer yards out.
        """
        return self._less_than_nineteen_yards_field_goals_made

    @_int_property_decorator
    def twenty_to_twenty_nine_yard_field_goal_attempts(self):
        """
        Returns an ``int`` of the number of field goals the player attempted
        from twenty to twenty-nine yards out.
        """
        return self._twenty_to_twenty_nine_yard_field_goal_attempts

    @_int_property_decorator
    def twenty_to_twenty_nine_yard_field_goals_made(self):
        """
        Returns an ``int`` of the number of field goals the player made from
        twenty to twenty-nine yards out.
        """
        return self._twenty_to_twenty_nine_yard_field_goals_made

    @_int_property_decorator
    def thirty_to_thirty_nine_yard_field_goal_attempts(self):
        """
        Returns an ``int`` of the number of field goals the player attempted
        from thirty to thirty-nine yards out.
        """
        return self._thirty_to_thirty_nine_yard_field_goal_attempts

    @_int_property_decorator
    def thirty_to_thirty_nine_yard_field_goals_made(self):
        """
        Returns an ``int`` of the number of field goals the player made from
        thirty to thirty-nine yards out.
        """
        return self._thirty_to_thirty_nine_yard_field_goals_made

    @_int_property_decorator
    def fourty_to_fourty_nine_yard_field_goal_attempts(self):
        """
        Returns an ``int`` of the number of field goals the player attempted
        from fourty to fourty-nine yards out.
        """
        return self._fourty_to_fourty_nine_yard_field_goal_attempts

    @_int_property_decorator
    def fourty_to_fourty_nine_yard_field_goals_made(self):
        """
        Returns an ``int`` of the number of field goals the player made from
        fourty to fourty-nine yards out.
        """
        return self._fourty_to_fourty_nine_yard_field_goals_made

    @_int_property_decorator
    def fifty_plus_yard_field_goal_attempts(self):
        """
        Returns an ``int`` of the number of field goals the player attempted
        from fifty or more yards out.
        """
        return self._fifty_plus_yard_field_goal_attempts

    @_int_property_decorator
    def fifty_plus_yard_field_goals_made(self):
        """
        Returns an ``int`` of the number of field goals the player made from
        fifty or more yards out.
        """
        return self._fifty_plus_yard_field_goals_made

    @_int_property_decorator
    def field_goals_attempted(self):
        """
        Returns an ``int`` of the total number of field goals the player
        attempted from any distance.
        """
        return self._field_goals_attempted

    @_int_property_decorator
    def field_goals_made(self):
        """
        Returns an ``int`` of the total number of field goals the player made
        from any distance.
        """
        return self._field_goals_made

    @_int_property_decorator
    def longest_field_goal_made(self):
        """
        Returns an ``int`` of the longest field goal the player made.
        """
        return self._longest_field_goal_made

    @_float_property_decorator
    def field_goal_percentage(self):
        """
        Returns a ``float`` of the percentage of field goals the player made.
        Percentage ranges from 0-100.
        """
        return self._field_goal_percentage

    @_int_property_decorator
    def extra_points_attempted(self):
        """
        Returns an ``int`` of the number of extra points the player attempted.
        """
        return self._extra_points_attempted

    @_int_property_decorator
    def extra_points_made(self):
        """
        Returns an ``int`` of the number of extra points the player made.
        """
        return self._extra_points_made

    @_float_property_decorator
    def extra_point_percentage(self):
        """
        Returns a ``float`` of the percentage of extra points the player made.
        Percentage ranges from 0-100.
        """
        return self._extra_point_percentage

    @_int_property_decorator
    def punts(self):
        """
        Returns an ``int`` of the number of times the player punted the ball.
        """
        return self._punts

    @_int_property_decorator
    def total_punt_yards(self):
        """
        Returns an ``int`` of the total number of yards the player has punted
        the ball.
        """
        return self._total_punt_yards

    @_int_property_decorator
    def longest_punt(self):
        """
        Returns an ``int`` of the longest punt the player has kicked.
        """
        return self._longest_punt

    @_int_property_decorator
    def blocked_punts(self):
        """
        Returns an ``int`` of the number of the player's punts that have been
        blocked.
        """
        return self._blocked_punts

    @_float_property_decorator
    def yards_per_punt(self):
        """
        Returns a ``float`` of the average distance the player punts the ball.
        """
        return self._yards_per_punt

    @_int_property_decorator
    def interceptions(self):
        """
        Returns an ``int`` of the number of times the player intercepted a
        pass.
        """
        return self._interceptions

    @_int_property_decorator
    def yards_returned_from_interception(self):
        """
        Returns an ``int`` of the number of yards the player returned after
        intercepting a pass.
        """
        return self._yards_returned_from_interception

    @_int_property_decorator
    def interceptions_returned_for_touchdown(self):
        """
        Returns an ``int`` of the number of touchdowns the player has scored
        after intercepting a pass. Commonly referred to as a 'Pick-6'.
        """
        return self._interceptions_returned_for_touchdown

    @_int_property_decorator
    def longest_interception_return(self):
        """
        Returns an ``int`` of the most yards the player has returned after
        intercepting a pass.
        """
        return self._longest_interception_return

    @_int_property_decorator
    def passes_defended(self):
        """
        Returns an ``int`` of the number of passes the player has defended as a
        defensive player.
        """
        return self._passes_defended

    @_int_property_decorator
    def fumbles_forced(self):
        """
        Returns an ``int`` of the number of times the player forced a fumble.
        """
        return self._fumbles_forced

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

    @_float_property_decorator
    def sacks(self):
        """
        Returns a ``float`` of the number of times the player sacked a
        quarterback.
        """
        return self._sacks

    @_int_property_decorator
    def tackles(self):
        """
        Returns an ``int`` of the number of tackles the player made.
        """
        return self._tackles

    @_int_property_decorator
    def assists_on_tackles(self):
        """
        Returns an ``int`` of the number of assist the player made on tackles.
        """
        return self._assists_on_tackles

    @_int_property_decorator
    def safeties(self):
        """
        Returns an ``int`` of the number of safeties the player has scored.
        """
        return self._safeties


class Roster(object):
    """
    Get stats for all players on a roster.

    Request a team's roster for a given season and create instances of the
    Player class for each player, containing a detailed list of the player's
    statistics and information.

    Parameters
    ----------
    team : string
        The team's abbreviation, such as 'NOR' for the New Orleans Saints.
    year : string (optional)
        The 4-digit year to pull the roster from, such as '2017'. If left
        blank, defaults to the most recent season.
    """
    def __init__(self, team, year=None):
        self._team = team
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
        name_tag = player('td[data-stat="player"] a')
        name = re.sub(r'.*/players/./', '', str(name_tag))
        return re.sub(r'\.htm.*', '', name)

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
            year = utils._find_year_for_season('nfl')
        url = self._create_url(year)
        page = self._pull_team_page(url)
        if not page:
            output = ("Can't pull requested team page. Ensure the following "
                      "URL exists: %s" % url)
            raise ValueError(output)
        for player in page('table#games_played_team tbody tr').items():
            player_id = self._get_id(player)
            player_instance = Player(player_id)
            self._players.append(player_instance)

    @property
    def players(self):
        """
        Returns a ``list`` of player instances for each player on the requested
        team's roster.
        """
        return self._players
