import pandas as pd
import re
import warnings
from functools import wraps
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from .constants import BOXSCORE_RETRY, PLAYER_SCHEME, PLAYER_URL, ROSTER_URL


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


class AbstractPlayer:
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
    player_name : string
        A string representing the player's first and last name, such as 'David
        Blough'.
    player_data : string
        A string representation of the player's HTML data from the Boxscore
        page. If the player appears in multiple tables, all of their
        information will appear in one single string concatenated together.
    """
    def __init__(self, player_id, player_name, player_data):
        self._player_id = player_id
        self._name = player_name
        # Passing-specific stats
        self._completed_passes = None
        self._pass_attempts = None
        self._passing_completion = None
        self._passing_touchdowns = None
        self._passing_yards = None
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
        self._total_touchdowns = None
        self._extra_points_made = None
        self._field_goals_made = None

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
        value = utils._parse_field(PLAYER_SCHEME, stats, field)
        if not value and field in BOXSCORE_RETRY:
            value = utils._parse_field(BOXSCORE_RETRY, stats, field)
        return value

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
               short_field == 'name' or \
               short_field == 'height' or \
               short_field == 'weight' or \
               short_field == 'season':
                continue
            field_stats = []
            if type(player_data) == dict:
                for year, data in player_data.items():
                    stats = pq(data['data'])
                    value = self._parse_value(stats, short_field)
                    field_stats.append(value)
            else:
                stats = pq(player_data)
                value = self._parse_value(stats, short_field)
                field_stats.append(value)
            setattr(self, field, field_stats)

    @property
    def player_id(self):
        """
        Returns a ``string`` of the player's ID on sports-reference, such as
        'david-blough-1' for David Blough.
        """
        return self._player_id

    @property
    def name(self):
        """
        Returns a ``string`` of the player's name, such as 'David Blough'.
        """
        return self._name

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
