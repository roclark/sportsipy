from functools import wraps
from pyquery import PyQuery as pq
from sportsreference import utils
from .constants import PLAYER_SCHEME


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


class AbstractPlayer:
    """
    Get player information and stats for all seasons.

    Given a player ID, such as 'carsen-edwards-1' for Carsen Edwards, capture
    all relevant stats and information like name, height/weight, career
    three-pointers, last season's offensive rebounds, offensive points
    contributed, and much more.

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
    player_name : string
        A string representing the player's first and last name, such as 'Carsen
        Edwards'.
    player_data : string
        A string representation of the player's HTML data from the Boxscore
        page. If the player appears in multiple tables, all of their
        information will appear in one single string concatenated togather.
    """
    def __init__(self, player_id, player_name, player_data):
        self._player_data = player_data

        self._player_id = player_id
        self._name = player_name
        self._nationality = None
        self._age = None
        self._position = None

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
               short_field == 'player_data' or \
               short_field == 'name':
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
        'carsen-edwards-1' for Carsen Edwards.
        """
        return self._player_id

    @property
    def name(self):
        """
        Returns a ``string`` of the players name
        """
        return self._name

    @property
    def nationality(self):
        """
        Returns a ``string`` of the players nationality
        """
        return self._nationality

    @property
    def position(self):
        """
        Returns a ``string`` of the players position
        """
        return self._position

    @_int_property_decorator
    def age(self):
        """
        Returns a ``int`` of the players age
        """
        return self._age
