import pandas as pd
import re
from functools import wraps
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from .constants import (BOXSCORE_SCHEME,
                        NATIONALITY,
                        PLAYER_ELEMENT_INDEX,
                        PLAYER_SCHEME,
                        PLAYER_URL,
                        ROSTER_URL)


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
        element_ind = 0
        if func.__name__ in PLAYER_ELEMENT_INDEX.keys():
            element_ind = PLAYER_ELEMENT_INDEX[func.__name__]
        try:
            value = _cleanup(prop[index][element_ind])
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
        element_ind = 0
        if func.__name__ in PLAYER_ELEMENT_INDEX.keys():
            element_ind = PLAYER_ELEMENT_INDEX[func.__name__]
        try:
            value = _cleanup(prop[index][element_ind])
            return float(value)
        except (ValueError, TypeError, IndexError):
            # If there is no value, default to None
            return None
    return wrapper


class AbstractPlayer:
    """
    Get player information and stats for all seasons.

    Given a player ID, such as 'altuvjo01' for Jose Altuve, capture all
    relevant stats and information like name, nationality, height/weight,
    career home runs, last season's batting average, salary, contract amount,
    and much more.

    By default, the class instance will return the player's career stats, but
    single-season stats can be found by calling the instance with the requested
    season as denoted on baseball-reference.com.

    Parameters
    ----------
    player_id : string
        A player's ID according to basketball-reference.com, such as
        'altuvjo01' for Jose Altuve. The player ID can be found by navigating
        to the player's stats page and getting the string between the final
        slash and the '.html' in the URL. In general, the ID is in the format
        'LLLLLFFNN' where 'LLLLL' are the first 5 letters in the player's last
        name, 'FF', are the first 2 letters in the player's first name, and
        'NN' is a number starting at '01' for the first time that player ID has
        been used and increments by 1 for every successive player.
    """
    def __init__(self, player_id, player_name, player_data):
        self._player_id = player_id
        self._name = player_name
        self._plate_appearances = None
        self._at_bats = None
        self._runs = None
        self._hits = None
        self._runs_batted_in = None
        self._bases_on_balls = None
        self._times_struck_out = None
        self._batting_average = None
        self._on_base_percentage = None
        self._slugging_percentage = None
        self._on_base_plus_slugging_percentage = None
        self._putouts = None
        self._assists = None
        # Stats specific to pitchers
        self._hits_allowed = None
        self._runs_allowed = None
        self._earned_runs_allowed = None
        self._home_runs_allowed = None
        self._bases_on_balls_given = None
        self._strikeouts = None
        self._batters_faced = None

        self._parse_player_data(player_data)

    def _parse_value(self, stats, field):
        """
        Pull the specified value from the HTML contents.

        Given a field, find the corresponding HTML tag for that field and parse
        its value before returning the value as a string.

        Parameters
        ----------
        stats : PyQuery object
            A PyQuery object containing all stats in HTML format for a
            particular player.
        field : string
            A string of the field to parse from the HTML.

        Returns
        -------
        list
            A list of all values that match the requested field. If no value
            could be found, returns None.
        """
        scheme = PLAYER_SCHEME[field]
        items = [i.text() for i in stats(scheme).items()]
        # Stats can be added and removed on a yearly basis. If no stats are
        # found, return None and have that be the value.
        if len(items) == 0:
            return None
        return items

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
               short_field == 'season' or \
               short_field == 'name' or \
               short_field == 'weight' or \
               short_field == 'height' or \
               short_field == 'nationality' or \
               short_field == 'birth_date' or \
               short_field == 'contract':
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
        'altuvjo01' for Jose Altuve.
        """
        return self._player_id

    @property
    def name(self):
        """
        Returns a ``string`` of the player's name, such as 'Jose Altuve'.
        """
        return self._name

    @_int_property_decorator
    def plate_appearances(self):
        """
        Returns an ``int`` of the number of plate appearances the player had.
        """
        return self._plate_appearances

    @_int_property_decorator
    def at_bats(self):
        """
        Returns an ``int`` of the number of at bats the player had.
        """
        return self._at_bats

    @_int_property_decorator
    def runs(self):
        """
        Returns an ``int`` of the number of runs the player scored.
        """
        return self._runs

    @_int_property_decorator
    def hits(self):
        """
        Returns an ``int`` of the number of hits the player had.
        """
        return self._hits

    @_int_property_decorator
    def runs_batted_in(self):
        """
        Returns an ``int`` of the number of runs batted in the player
        registered.
        """
        return self._runs_batted_in

    @_int_property_decorator
    def bases_on_balls(self):
        """
        Returns an ``int`` of the number of bases the player registered as a
        result of balls.
        """
        return self._bases_on_balls

    @_int_property_decorator
    def times_struck_out(self):
        """
        Returns an ``int`` of the number of times the player was struck out.
        """
        return self._times_struck_out

    @_float_property_decorator
    def batting_average(self):
        """
        Returns a ``float`` of the batting average for the player.
        """
        return self._batting_average

    @_float_property_decorator
    def on_base_percentage(self):
        """
        Returns a ``float`` of the percentage of at bats that result in the
        batter getting on base.
        """
        return self._on_base_percentage

    @_float_property_decorator
    def slugging_percentage(self):
        """
        Returns a ``float`` of the slugging percentage for the player based
        on the number of bases gained per at-bat with bigger plays getting more
        weight.
        """
        return self._slugging_percentage

    @_float_property_decorator
    def on_base_plus_slugging_percentage(self):
        """
        Returns a ``float`` of the on base percentage plus the slugging
        percentage. Percentage ranges from 0-1.
        """
        return self._on_base_plus_slugging_percentage

    @_int_property_decorator
    def putouts(self):
        """
        Returns an ``int`` of the number of putouts the player had.
        """
        return self._putouts

    @_int_property_decorator
    def assists(self):
        """
        Returns an ``int`` of the number of assists the player had.
        """
        return self._assists

    @_int_property_decorator
    def hits_allowed(self):
        """
        Returns an ``int`` of the number of hits the player allowed as a
        pitcher.
        """
        return self._hits_allowed

    @_int_property_decorator
    def runs_allowed(self):
        """
        Returns an ``int`` of the number of runs the player allowed as a
        pitcher.
        """
        return self._runs_allowed

    @_int_property_decorator
    def earned_runs_allowed(self):
        """
        Returns an ``int`` of the number of earned runs the player allowed as a
        pitcher.
        """
        return self._earned_runs_allowed

    @_int_property_decorator
    def bases_on_balls_given(self):
        """
        Returns an ``int`` of the number of bases on balls the player has given
        as a pitcher.
        """
        return self._bases_on_balls_given

    @_int_property_decorator
    def strikeouts(self):
        """
        Returns an ``int`` of the number of strikeouts the player threw as a
        pitcher.
        """
        return self._strikeouts

    @_int_property_decorator
    def batters_faced(self):
        """
        Returns an ``int`` of the number of batters the pitcher has faced.
        """
        return self._batters_faced
