import pandas as pd
import re
from functools import wraps
from pyquery import PyQuery as pq
from .. import utils
from .constants import PLAYER_SCHEME


def _cleanup(prop):
    try:
        prop = prop.replace('%', '')
        prop = prop.replace('$', '')
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


class AbstractPlayer:
    """
    Get player information and stats for all seasons.

    Given a player ID, such as 'hardeja01' for James Harden, capture all
    relevant stats and information like name, nationality, height/weight,
    career three-pointers, last season's offensive rebounds, salary, contract
    amount, and much more.

    By default, the class instance will return the player's career stats, but
    single-season stats can be found by calling the instance with the requested
    season as denoted on basketball-reference.com.

    Parameters
    ----------
    player_id : string
        A player's ID according to basketball-reference.com, such as
        'hardeja01' for James Harden. The player ID can be found by navigating
        to the player's stats page and getting the string between the final
        slash and the '.html' in the URL. In general, the ID is in the format
        'LLLLLFFNN' where 'LLLLL' are the first 5 letters in the player's last
        name, 'FF', are the first 2 letters in the player's first name, and
        'NN' is a number starting at '01' for the first time that player ID has
        been used and increments by 1 for every successive player.
    player_name : string
        A string representing the player's first and last name, such as 'James
        Harden'.
    player_data : string
        A string representation of the player's HTML data from the Boxscore
        page. If the player appears in multiple tables, all of their
        information will appear in one single string concatenated together.
    """
    def __init__(self, player_id, player_name, player_data):
        self._player_id = player_id
        self._name = player_name
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
        self._effective_field_goal_percentage = None
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
        self._true_shooting_percentage = None
        self._three_point_attempt_rate = None
        self._free_throw_attempt_rate = None
        self._offensive_rebound_percentage = None
        self._defensive_rebound_percentage = None
        self._total_rebound_percentage = None
        self._assist_percentage = None
        self._steal_percentage = None
        self._block_percentage = None
        self._turnover_percentage = None
        self._usage_percentage = None
        self._box_plus_minus = None

        self._parse_player_data(player_data)

    def _parse_value(self, stats, field):
        """
        Pull the specified value from the HTML contents.

        Given a field, find the corresponding HTML tag for that field and parse
        its value before returning the value as a string. A couple fields, such
        as 'conference' and 'team_abbreviation' don't follow a standard parsing
        scheme and need to be handled differently to get the correct value.

        Parameters
        ----------
        stats : PyQuery object
            A PyQuery object containing all stats in HTML format for a
            particular player.
        field : string
            A string of the field to parse from the HTML.

        Returns
        -------
        string
            Returns the desired value as a string.
        """
        return utils._parse_field(PLAYER_SCHEME, stats, field)

    def _parse_player_data(self, player_data):
        """
        Parse all player information and set attributes.

        Iterate through each class attribute to parse the data from the HTML
        page and set the attribute value with the result.

        Parameters
        ----------
        player_data : dictionary or string
            If this class is inherited from the ``Player`` class, player_data
            will be a dictionary where each key is a string representing the
            season and each value contains the HTML data as a string. If this
            class is inherited from the ``BoxscorePlayer`` class, player_data
            will be a string representing the player's game statistics in HTML
            format.
        """
        for field in self.__dict__:
            short_field = str(field)[1:]
            if short_field == 'player_id' or \
               short_field == 'index' or \
               short_field == 'most_recent_season' or \
               short_field == 'contract' or \
               short_field == 'name' or \
               short_field == 'height' or \
               short_field == 'weight' or \
               short_field == 'birth_date' or \
               short_field == 'nationality':
                continue
            field_stats = []
            if type(player_data) == dict:
                for year, data in player_data.items():
                    stats = pq(data['data'])
                    value = self._parse_value(stats, short_field)
                    field_stats.append(value)
            else:
                if short_field == 'box_plus_minus':
                    short_field = 'boxscore_box_plus_minus'
                stats = pq(player_data)
                value = self._parse_value(stats, short_field)
                field_stats.append(value)
            setattr(self, field, field_stats)

    @property
    def player_id(self):
        """
        Returns a ``string`` of the player's ID on sports-reference, such as
        'hardeja01' for James Harden.
        """
        return self._player_id

    @property
    def name(self):
        """
        Returns a ``string`` of the players name, such as 'James Harden'.
        """
        return self._name

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
    def box_plus_minus(self):
        """
        Returns a ``float`` of the total number of points per 100 possessions
        the player contributed in comparison to an average player in the
        league.
        """
        return self._box_plus_minus
