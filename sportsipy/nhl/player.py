import pandas as pd
from functools import wraps
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from .constants import BOXSCORE_RETRY, PLAYER_SCHEME


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

    Given a player ID, such as 'zettehe01' for Henrik Zetterberg, capture all
    relevant stats and information like name, team, height/weight, career
    goals, single-season assits, penalty minutes, and much more.

    By default, the class instance will return the player's career stats, but
    single-season stats can be found by calling the instance with the requested
    season as denoted on sports-reference.com.

    Parameters
    ----------
    player_id : string
        A player's ID according to hockey-reference.com, such as 'zettehe01'
        for Henrik Zetterberg. The player ID can be found by navigating to the
        player's stats page and getting the string between the final slash and
        the '.html' in the URL. In general, the ID is in the format 'lllllffnn'
        where 'lllll' is the first five letters of the player's last name, 'ff'
        is the first two letters of the player's first name, and 'nn' is a
        number starting at '01' for the first time that player ID has been used
        and increments by 1 for every successive player.
    player_name : string
        A string representing the player's first and last name, such as 'Henrik
        Zetterberg'.
    player_data : string
        A string representation of the player's HTML data from the Boxscore
        page. If the player appears in multiple tables, all of their
        information will appear in one single string concatenated together.
    """
    def __init__(self, player_id, player_name, player_data):
        self._player_id = player_id
        self._name = player_name
        self._goals = None
        self._assists = None
        self._points = None
        self._plus_minus = None
        self._penalties_in_minutes = None
        self._even_strength_goals = None
        self._power_play_goals = None
        self._short_handed_goals = None
        self._game_winning_goals = None
        self._even_strength_assists = None
        self._power_play_assists = None
        self._short_handed_assists = None
        self._shots_on_goal = None
        self._shooting_percentage = None
        self._time_on_ice = None
        self._blocks_at_even_strength = None
        self._hits_at_even_strength = None
        # Possession Metrics
        self._corsi_for_percentage = None
        self._relative_corsi_for_percentage = None
        self._offensive_zone_start_percentage = None
        # Goalie Metrics
        self._goals_against = None
        self._shots_against = None
        self._saves = None
        self._save_percentage = None
        self._shutouts = None

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
               short_field == 'weight' or \
               short_field == 'height' or \
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
        Returns a ``string`` of the player's ID on hockey-reference, such as
        'zettehe01' for Henrik Zetterberg.
        """
        return self._player_id

    @property
    def name(self):
        """
        Returns a ``string`` of the player's name, such as 'Henrik Zetterberg'.
        """
        return self._name

    @_int_property_decorator
    def goals(self):
        """
        Returns an ``int`` of the number of goals the player scored.
        """
        return self._goals

    @_int_property_decorator
    def assists(self):
        """
        Returns an ``int`` of the number of goals the player has assisted.
        """
        return self._assists

    @_int_property_decorator
    def points(self):
        """
        Returns an ``int`` of the number of points the player has gained.
        """
        return self._points

    @_int_property_decorator
    def plus_minus(self):
        """
        Returns an ``int`` representing the relative presence the player has on
        the outcome of the game.
        """
        return self._plus_minus

    @_int_property_decorator
    def penalties_in_minutes(self):
        """
        Returns an ``int`` of the number of minutes the player has served as a
        result of penalties.
        """
        return self._penalties_in_minutes

    @_int_property_decorator
    def even_strength_goals(self):
        """
        Returns an ``int`` of the number of goals the player has scored at even
        strength.
        """
        return self._even_strength_goals

    @_int_property_decorator
    def power_play_goals(self):
        """
        Returns an ``int`` of the number of goals the player has scored while
        on a power play.
        """
        return self._power_play_goals

    @_int_property_decorator
    def short_handed_goals(self):
        """
        Returns an ``int`` of the number of goals the player has scored while
        short handed.
        """
        return self._short_handed_goals

    @_int_property_decorator
    def game_winning_goals(self):
        """
        Returns an ``int`` of the number of game-winning goals the player has
        scored.
        """
        return self._game_winning_goals

    @_int_property_decorator
    def even_strength_assists(self):
        """
        Returns an ``int`` of the number of goals the player has assisted while
        at even strength.
        """
        return self._even_strength_assists

    @_int_property_decorator
    def power_play_assists(self):
        """
        Returns an ``int`` of the number of goals the player has assisted while
        on a power play.
        """
        return self._power_play_assists

    @_int_property_decorator
    def short_handed_assists(self):
        """
        Returns an ``int`` of the number of goals the player has assisted while
        short handed.
        """
        return self._short_handed_assists

    @_int_property_decorator
    def shots_on_goal(self):
        """
        Returns an ``int`` of the number of shots on goal the player has made.
        """
        return self._shots_on_goal

    @_float_property_decorator
    def shooting_percentage(self):
        """
        Returns a ``float`` of the percentage of the player's shots that go in
        the goal. Percentage ranges from 0-100.
        """
        return self._shooting_percentage

    @_int_property_decorator
    def blocks_at_even_strength(self):
        """
        Returns an ``int`` of the number of shots the player blocks while at
        even strength.
        """
        return self._blocks_at_even_strength

    @_int_property_decorator
    def hits_at_even_strength(self):
        """
        Returns an ``int`` of the number of hits the player makes while at even
        strength.
        """
        return self._hits_at_even_strength

    @_float_property_decorator
    def corsi_for_percentage(self):
        """
        Returns a ``float`` of the 'Corsi For' percentage, equal to corsi_for /
        (corsi_for + corsi_against). Percentage ranges from 0-100.
        """
        return self._corsi_for_percentage

    @_float_property_decorator
    def relative_corsi_for_percentage(self):
        """
        Returns a ``float`` of the player's relative 'Corsi For' percentage,
        equal to the difference between the player's on and off-ice Corsi For
        percentage.
        """
        return self._relative_corsi_for_percentage

    @_float_property_decorator
    def offensive_zone_start_percentage(self):
        """
        Returns a ``float`` of the percentage of faceoffs that occur in the
        offensive zone while the player is on ice. Percentage ranges from
        0-100.
        """
        return self._offensive_zone_start_percentage

    @_int_property_decorator
    def goals_against(self):
        """
        Returns an ``int`` of the number of goals the opponent scored on the
        player while in goal.
        """
        return self._goals_against

    @_int_property_decorator
    def shots_against(self):
        """
        Returns an ``int`` of the number of shots the opponent took while the
        player is in goal.
        """
        return self._shots_against

    @_int_property_decorator
    def saves(self):
        """
        Returns an ``int`` of the number of shots the player has saved while in
        goal.
        """
        return self._saves

    @_float_property_decorator
    def save_percentage(self):
        """
        Returns a ``float`` of the percentage of shots the player has saved.
        Percentage ranges from 0-1.
        """
        return self._save_percentage

    @_int_property_decorator
    def shutouts(self):
        """
        Returns an ``int`` of the number of shutouts the player has registered
        while in goal.
        """
        return self._shutouts
