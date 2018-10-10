import pandas as pd
import re
from functools import wraps
from pyquery import PyQuery as pq
from .. import utils
from .constants import PLAYER_SCHEME, PLAYER_URL, ROSTER_URL
from six.moves.urllib.error import HTTPError


def _cleanup(prop):
    try:
        prop = prop.replace('%', '')
        prop = prop.replace(',', '')
        return prop.replace('+', '')
    # Occurs when a value is of Nonetype. When that happens, return a blank
    # string as whatever have come in had an incomplete value.
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
        except ValueError:
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
        except ValueError:
            # If there is no value, default to None
            return None
    return wrapper


def _most_recent_decorator(func):
    @property
    @wraps(func)
    def wrapper(*args):
        season = args[0]._most_recent_season
        seasons = args[0]._season
        index = seasons.index(season)
        prop = func(*args)
        return prop[index]
    return wrapper


class Player(object):
    """
    Get player information and stats for all seasons.

    Given a player ID, such as 'carsen-edwards-1' for Carsen Edwards, capture
    all relevant stats and information like name, height/weight, career
    three-pointers, last season's offensive rebounds, offensive points
    contributed, and much more.

    By default, the class instance will return the player's career stats, but
    single-season stats can be found by calling the instance with the requested
    season as denoted on sports-reference.com.

    Parameters
    ----------
    player_id : string
        A player's ID according to sports-reference.com, such as
        'carsen-edwards-1' for Carsen Edwards. The player ID can be found by
        navigating to the player's stats page and getting the string between
        the final slash and the '.html' in the URL. In general, the ID is in
        the format 'first-last-N' where 'first' is the player's first name in
        lowercase, 'last' is the player's last name in lowercase, and 'N' is a
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
        self._conference = None
        self._position = None
        self._height = None
        self._weight = None
        self._games_played = None
        self._games_started = None
        self._minutes_played = None
        self._field_goals = None
        self._field_goal_attempts = None
        self._field_goal_percentage = None
        self._three_pointers = None
        self._three_point_attempts = None
        self._three_point_percentage = None
        self._two_pointers = None
        self._two_point_attempts = None
        self._two_point_percentage = None
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
        self._player_efficiency_rating = None
        self._true_shooting_percentage = None
        self._effective_field_goal_percentage = None
        self._three_point_attempt_rate = None
        self._free_throw_attempt_rate = None
        self._points_produced = None
        self._offensive_rebound_percentage = None
        self._defensive_rebound_percentage = None
        self._total_rebound_percentage = None
        self._assist_percentage = None
        self._steal_percentage = None
        self._block_percentage = None
        self._turnover_percentage = None
        self._usage_percentage = None
        self._offensive_win_shares = None
        self._defensive_win_shares = None
        self._win_shares = None
        self._win_shares_per_40_minutes = None
        self._offensive_box_plus_minus = None
        self._defensive_box_plus_minus = None
        self._box_plus_minus = None

        self._parse_player_data()
        self._find_initial_index()

    def _retrieve_html_page(self):
        """
        Download the requested player's stats page.

        Download the requested page and strip all of the comment tags before
        returning a pyquery object which will be used to parse the data.

        Returns
        -------
        PyQuery object
            The requested page is returned as a queriable PyQuery object with
            the comment tags removed.
        """
        url = PLAYER_URL % self._player_id
        try:
            url_data = pq(url)
        except HTTPError:
            return None
        return pq(utils._remove_html_comment_tags(url_data))

    def _parse_season(self, row):
        """
        Parse the season string from the table.

        The season is generally located in the first column of the stats tables
        and should be parsed to denote which season metrics are being pulled
        from.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object of a single row in a stats table.

        Returns
        -------
        string
            A string representation of the season in the format 'YYYY-YY', such
            as '2017-18'.
        """
        return utils._parse_field(PLAYER_SCHEME, row, 'season')

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
            season ``string``, such as '2017-18', and the value is a
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
            all_stats_dict['career'] = {'data': str(next(career_stats))}
        return all_stats_dict

    def _combine_all_stats(self, player_info):
        """
        Pull stats from all tables into single data structure.

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

        for table_id in ['players_totals', 'players_advanced']:
            table_items = utils._get_stats_table(player_info,
                                                 'table#%s' % table_id)
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

        Parse general player information such as height and weight. The
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

    def _parse_player_position(self, player_info):
        """
        Parse the player's position.

        The player's position isn't contained within a unique tag and the
        player's meta information should be iterated through until 'Position'
        is found as it contains the desired text.

        Parameters
        ----------
        player_info : PyQuery object
            A PyQuery object of the player's information on the HTML stats
            page.

        Returns
        -------
        string
            Returns a string of the player's position, such as 'Guard'.
        """
        for section in player_info('div#meta p').items():
            if 'Position' in str(section):
                return section.text().replace('Position: ', '')

    def _parse_conference(self, stats):
        """
        Parse the conference abbreviation for the player's team.

        The conference abbreviation is embedded within the conference name tag
        and should be special-parsed to extract it.

        Parameters
        ----------
        stats : PyQuery object
            A PyQuery object containing the HTML from the player's stats page.

        Returns
        -------
        string
            Returns a string of the conference abbreviation, such as 'big-12'.
        """
        conference_tag = stats(PLAYER_SCHEME['conference'])
        conference = re.sub(r'.*/cbb/conferences/',
                            '',
                            str(conference_tag('a')))
        conference = re.sub(r'/.*', '', conference)
        return conference

    def _parse_team_abbreviation(self, stats):
        """
        Parse the team abbreviation.

        The team abbreviation is embedded within the team name tag and should
        be special-parsed to extract it.

        Parameters
        ----------
        stats : PyQuery object
            A PyQuery object containing the HTML from the player's stats page.

        Returns
        -------
        string
            Returns a string of the team's abbreviation, such as 'PURDUE' for
            the Purdue Boilermakers.
        """
        team_tag = stats(PLAYER_SCHEME['team_abbreviation'])
        team = re.sub(r'.*/cbb/schools/', '', str(team_tag('a')))
        team = re.sub(r'/.*', '', team)
        return team

    def _parse_player_data(self):
        """
        Parse all player information and set attributes.

        Pull the player's HTML stats page and go through each class attribute
        to parse the data from the HTML page and set attribute value with the
        result.
        """
        player_info = self._retrieve_html_page()
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
            if short_field == 'position':
                value = self._parse_player_position(player_info)
                setattr(self, field, value)
                continue
            field_stats = []
            for year, data in all_stats_dict.items():
                stats = pq(data['data'])
                if short_field == 'conference':
                    value = self._parse_conference(stats)
                elif short_field == 'team_abbreviation':
                    value = self._parse_team_abbreviation(stats)
                else:
                    value = utils._parse_field(PLAYER_SCHEME,
                                               stats,
                                               short_field)
                field_stats.append(value)
            setattr(self, field, field_stats)

    def _find_initial_index(self):
        """
        Find the index of career stats.

        When the Player class is instantiated, the default stats to pull are
        the player's career stats. Upon being called, the index of the 'Career'
        element should be the index value.
        """
        index = 0
        for season in self._season:
            if season == 'Career':
                self._index = index
                break
            index += 1

    def __call__(self, requested_season=''):
        """
        Specify a different season to pull stats from.

        A different season can be requested by passing the season string, such
        as '2017-18' to the class instance.

        Parameters
        ----------
        requested_season : string (optional)
            A string of the requested season to query, such as '2017-18'. If
            left blank or 'Career' is passed, the career stats will be used for
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
            'assist_percentage': self.assist_percentage,
            'assists': self.assists,
            'block_percentage': self.block_percentage,
            'blocks': self.blocks,
            'box_plus_minus': self.box_plus_minus,
            'conference': self.conference,
            'defensive_box_plus_minus': self.defensive_box_plus_minus,
            'defensive_rebound_percentage': self.defensive_rebound_percentage,
            'defensive_rebounds': self.defensive_rebounds,
            'defensive_win_shares': self.defensive_win_shares,
            'effective_field_goal_percentage':
            self.effective_field_goal_percentage,
            'field_goal_attempts': self.field_goal_attempts,
            'field_goal_percentage': self.field_goal_percentage,
            'field_goals': self.field_goals,
            'free_throw_attempt_rate': self.free_throw_attempt_rate,
            'free_throw_attempts': self.free_throw_attempts,
            'free_throw_percentage': self.free_throw_percentage,
            'free_throws': self.free_throws,
            'games_played': self.games_played,
            'games_started': self.games_started,
            'height': self.height,
            'minutes_played': self.minutes_played,
            'offensive_box_plus_minus': self.offensive_box_plus_minus,
            'offensive_rebound_percentage': self.offensive_rebound_percentage,
            'offensive_rebounds': self.offensive_rebounds,
            'offensive_win_shares': self.offensive_win_shares,
            'personal_fouls': self.personal_fouls,
            'player_efficiency_rating': self.player_efficiency_rating,
            'player_id': self.player_id,
            'points': self.points,
            'points_produced': self.points_produced,
            'position': self.position,
            'steal_percentage': self.steal_percentage,
            'steals': self.steals,
            'team_abbreviation': self.team_abbreviation,
            'three_point_attempt_rate': self.three_point_attempt_rate,
            'three_point_attempts': self.three_point_attempts,
            'three_point_percentage': self.three_point_percentage,
            'three_pointers': self.three_pointers,
            'total_rebound_percentage': self.total_rebound_percentage,
            'total_rebounds': self.total_rebounds,
            'true_shooting_percentage': self.true_shooting_percentage,
            'turnover_percentage': self.turnover_percentage,
            'turnovers': self.turnovers,
            'two_point_attempts': self.two_point_attempts,
            'two_point_percentage': self.two_point_percentage,
            'two_pointers': self.two_pointers,
            'usage_percentage': self.usage_percentage,
            'weight': self.weight,
            'win_shares': self.win_shares,
            'win_shares_per_40_minutes': self.win_shares_per_40_minutes,
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
        for season in self._season:
            self._index = self._season.index(season)
            rows.append(self._dataframe_fields())
            indices.append(season)
        self._index = temp_index
        return pd.DataFrame(rows, index=[indices])

    @property
    def player_id(self):
        """
        Returns a ``string`` of the player's ID on sports-reference, such as
        'carsen-edwards-1' for Carsen Edwards.
        """
        return self._player_id

    @property
    def season(self):
        """
        Returns a ``string`` of the season in the format 'YYYY-YY', such as
        '2017-18'. If no season was requested, the career stats will be
        returned for the player and the season will default to 'Career'.
        """
        return self._season[self._index]

    @property
    def conference(self):
        """
        Returns a ``string`` of the abbreviation for the conference the team
        participated in for the requested season.
        """
        return self._conference[self._index]

    @property
    def name(self):
        """
        Returns a ``string`` of the players name, such as 'Carsen Edwards'.
        """
        return self._name

    @_most_recent_decorator
    def team_abbreviation(self):
        """
        Returns a ``string`` of the abbrevation for the team the player plays
        for, such as 'PURDUE' for Carsen Edwards.
        """
        return self._team_abbreviation

    @property
    def position(self):
        """
        Returns a ``string`` constant of the player's primary position.
        """
        return self._position

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

    @_int_property_decorator
    def games_played(self):
        """
        Returns an ``int`` of the number of games the player participated in.
        """
        return self._games_played

    @_int_property_decorator
    def games_started(self):
        """
        Returns an ``int`` of the number of games the player started.
        """
        return self._games_started

    @_int_property_decorator
    def minutes_played(self):
        """
        Returns an ``int`` of the total number of minutes the player played.
        """
        return self._minutes_played

    @_int_property_decorator
    def field_goals(self):
        """
        Returns an ``int`` of the total number of field goals the player
        scored.
        """
        return self._field_goals

    @_int_property_decorator
    def field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of field goals the player
        attempted during the season.
        """
        return self._field_goal_attempts

    @_float_property_decorator
    def field_goal_percentage(self):
        """
        Returns a ``float`` of the player's field goal percentage during the
        season. Percentage ranges from 0-1.
        """
        return self._field_goal_percentage

    @_int_property_decorator
    def three_pointers(self):
        """
        Returns an ``int`` of the total number of three point field goals the
        player made.
        """
        return self._three_pointers

    @_int_property_decorator
    def three_point_attempts(self):
        """
        Returns an ``int`` of the total number of three point field goals the
        player attempted during the season.
        """
        return self._three_point_attempts

    @_float_property_decorator
    def three_point_percentage(self):
        """
        Returns a ``float`` of the player's three point field goal percentage
        during the season. Percentage ranges from 0-1.
        """
        return self._three_point_percentage

    @_int_property_decorator
    def two_pointers(self):
        """
        Returns an ``int`` of the total number of two point field goals the
        player made.
        """
        return self._two_pointers

    @_int_property_decorator
    def two_point_attempts(self):
        """
        Returns an ``int`` of the total number of two point field goals the
        player attempted during the season.
        """
        return self._two_point_attempts

    @_float_property_decorator
    def two_point_percentage(self):
        """
        Returns a ``float`` of the player's two point field goal percentage
        during the season. Percentage ranges from 0-1.
        """
        return self._two_point_percentage

    @_float_property_decorator
    def effective_field_goal_percentage(self):
        """
        Returns a ``float`` of the player's field goal percentage while giving
        extra weight to 3-point field goals. Percentage ranges from 0-1.
        """
        return self._effective_field_goal_percentage

    @_int_property_decorator
    def free_throws(self):
        """
        Returns an ``int`` of the total number of free throws the player made
        during the season.
        """
        return self._free_throws

    @_int_property_decorator
    def free_throw_attempts(self):
        """
        Returns an ``int`` of the total number of free throws the player
        attempted during the season.
        """
        return self._free_throw_attempts

    @_float_property_decorator
    def free_throw_percentage(self):
        """
        Returns a ``float`` of the player's free throw percentage during the
        season. Percentage ranges from 0-1.
        """
        return self._free_throw_percentage

    @_int_property_decorator
    def offensive_rebounds(self):
        """
        Returns an ``int`` of the total number of offensive rebounds the player
        grabbed during the season.
        """
        return self._offensive_rebounds

    @_int_property_decorator
    def defensive_rebounds(self):
        """
        Returns an ``int`` of the total number of defensive rebounds the player
        grabbed during the season.
        """
        return self._defensive_rebounds

    @_int_property_decorator
    def total_rebounds(self):
        """
        Returns an ``int`` of the total number of offensive and defensive
        rebounds the player grabbed during the season.
        """
        return self._total_rebounds

    @_int_property_decorator
    def assists(self):
        """
        Returns an ``int`` of the total number of assists the player tallied
        during the season.
        """
        return self._assists

    @_int_property_decorator
    def steals(self):
        """
        Returns an ``int`` of the total number of steals the player tallied
        during the season.
        """
        return self._steals

    @_int_property_decorator
    def blocks(self):
        """
        Returns an ``int`` of the total number of shots the player blocked
        during the season.
        """
        return self._blocks

    @_int_property_decorator
    def turnovers(self):
        """
        Returns an ``int`` of the total number of times the player turned the
        ball over during the season for any reason.
        """
        return self._turnovers

    @_int_property_decorator
    def personal_fouls(self):
        """
        Returns an ``int`` of the total number of personal fouls the player
        committed during the season.
        """
        return self._personal_fouls

    @_int_property_decorator
    def points(self):
        """
        Returns an ``int`` of the total number of points the player scored
        during the season.
        """
        return self._points

    @_float_property_decorator
    def player_efficiency_rating(self):
        """
        Returns a ``float`` of the player's efficiency rating which represents
        the player's relative production level. An average player in the league
        has an efficiency rating of 15.
        """
        return self._player_efficiency_rating

    @_float_property_decorator
    def true_shooting_percentage(self):
        """
        Returns a ``float`` of the player's true shooting percentage which
        takes into account two and three pointers as well as free throws.
        Percentage ranges from 0-1.
        """
        return self._true_shooting_percentage

    @_float_property_decorator
    def three_point_attempt_rate(self):
        """
        Returns a ``float`` of the percentage of field goals that are shot from
        beyond the 3-point arc. Percentage ranges from 0-1.
        """
        return self._three_point_attempt_rate

    @_float_property_decorator
    def free_throw_attempt_rate(self):
        """
        Returns a ``float`` of the number of free throw attempts per field goal
        attempt.
        """
        return self._free_throw_attempt_rate

    @_int_property_decorator
    def points_produced(self):
        """
        Returns an ``int`` of the number of offensive points the player
        produced.
        """
        return self._points_produced

    @_float_property_decorator
    def offensive_rebound_percentage(self):
        """
        Returns a ``float`` of the percentage of available offensive rebounds
        the player grabbed. Percentage ranges from 0-100.
        """
        return self._offensive_rebound_percentage

    @_float_property_decorator
    def defensive_rebound_percentage(self):
        """
        Returns a ``float`` of the percentage of available defensive rebounds
        the player grabbed. Percentage ranges from 0-100.
        """
        return self._defensive_rebound_percentage

    @_float_property_decorator
    def total_rebound_percentage(self):
        """
        Returns a ``float`` of the percentage of available rebounds the player
        grabbed, both offensive and defensive. Percentage ranges from 0-100.
        """
        return self._total_rebound_percentage

    @_float_property_decorator
    def assist_percentage(self):
        """
        Returns a ``float`` of the percentage of field goals the player
        assisted while on the floor. Percentage ranges from 0-100.
        """
        return self._assist_percentage

    @_float_property_decorator
    def steal_percentage(self):
        """
        Returns a ``float`` of the percentage of defensive possessions that
        ended with the player stealing the ball while on the floor. Percentage
        ranges from 0-100.
        """
        return self._steal_percentage

    @_float_property_decorator
    def block_percentage(self):
        """
        Returns a ``float`` of the percentage of opposing two-point field goal
        attempts that were blocked by the player while on the floor. Percentage
        ranges from 0-100.
        """
        return self._block_percentage

    @_float_property_decorator
    def turnover_percentage(self):
        """
        Returns a ``float`` of the average number of turnovers per 100
        possessions by the player.
        """
        return self._turnover_percentage

    @_float_property_decorator
    def usage_percentage(self):
        """
        Returns a ``float`` of the percentage of plays the player is involved
        in while on the floor. Percentage ranges from 0-100.
        """
        return self._usage_percentage

    @_float_property_decorator
    def offensive_win_shares(self):
        """
        Returns a ``float`` of the number of wins the player contributed to the
        team as a result of his offensive plays.
        """
        return self._offensive_win_shares

    @_float_property_decorator
    def defensive_win_shares(self):
        """
        Returns a ``float`` of the number of wins the player contributed to the
        team as a result of his defensive plays.
        """
        return self._defensive_win_shares

    @_float_property_decorator
    def win_shares(self):
        """
        Returns a ``float`` of the number of wins the player contributed to the
        team as a result of his offensive and defensive plays.
        """
        return self._win_shares

    @_float_property_decorator
    def win_shares_per_40_minutes(self):
        """
        Returns a ``float`` of the number of wins the player contributed to the
        team per 40 minutes of playtime. An average player has a contribution
        of 0.100.
        """
        return self._win_shares_per_40_minutes

    @_float_property_decorator
    def offensive_box_plus_minus(self):
        """
        Returns a ``float`` of the number of offensive points per 100
        possessions the player contributed in comparison to an average player
        in the league.
        """
        return self._offensive_box_plus_minus

    @_float_property_decorator
    def defensive_box_plus_minus(self):
        """
        Returns a ``float`` of the number of defensive points per 100
        possessions the player contributed in comparison to an average player
        in the league.
        """
        return self._defensive_box_plus_minus

    @_float_property_decorator
    def box_plus_minus(self):
        """
        Returns a ``float`` of the total number of points per 100 possessions
        the player contributed in comparison to an average player in the
        league.
        """
        return self._box_plus_minus


class Roster(object):
    """
    Get stats for all players on a roster.

    Request a team's roster for a given season and create instances of the
    Player class for each player, containing a detailed list of the players
    statistics and information.

    Parameters
    ----------
    team : string
        The team's abbreviation, such as 'PURDUE' for the Purdue Boilermakers.
    year : string (optional)
        The 4-digit year to pull the roster from, such as '2018'. If left
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
            return pq(url)
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
        name = re.sub(r'.*/cbb/players/', '', str(name_tag))
        return re.sub(r'\.html.*', '', name)

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
            year = utils._find_year_for_season('ncaab')
        url = self._create_url(year)
        page = self._pull_team_page(url)
        if not page:
            output = ("Can't pull requested team page. Ensure the follow "
                      "URL exists: %s" % url)
            raise ValueError(output)
        players = page('table#roster tbody tr').items()
        for player in players:
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
