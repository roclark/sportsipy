import pandas as pd
import re
from functools import wraps
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from .constants import PLAYER_SCHEME, PLAYER_URL, ROSTER_URL


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


class AbstractPlayer:
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
    player_name : string
        A string representing the player's first and last name, such as 'Drew
        Brees'.
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
        self._attempted_passes = None
        self._passing_yards = None
        self._passing_touchdowns = None
        self._interceptions_thrown = None
        self._longest_pass = None
        self._quarterback_rating = None
        self._times_sacked = None
        # Rushing-specific stats
        self._rush_attempts = None
        self._rush_yards = None
        self._rush_touchdowns = None
        self._longest_rush = None
        # Receiving-specific stats
        self._times_pass_target = None
        self._receptions = None
        self._receiving_yards = None
        self._receiving_yards_per_reception = None
        self._receiving_touchdowns = None
        self._longest_reception = None
        # Combined receiving and rushing stats
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
        # Kicking-specific stats
        self._field_goals_attempted = None
        self._field_goals_made = None
        self._extra_points_attempted = None
        self._extra_points_made = None
        # Punting-specific stats
        self._punts = None
        self._total_punt_yards = None
        self._longest_punt = None
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
        self._assists_on_tackles = None

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
               short_field == 'name' or \
               short_field == 'weight' or \
               short_field == 'height' or \
               short_field == 'birth_date' or \
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
        Returns a ``string`` of the player's ID on pro-football-reference, such
        as 'BreeDr00' for Drew Brees.
        """
        return self._player_id

    @property
    def name(self):
        """
        Returns a ``string`` of the player's name, such as 'Drew Brees'.
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
        return self._attempted_passes

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

    @_int_property_decorator
    def interceptions_thrown(self):
        """
        Returns an ``int`` of the number of interceptions the player has
        thrown.
        """
        return self._interceptions_thrown

    @_int_property_decorator
    def longest_pass(self):
        """
        Returns an ``int`` of the longest completed pass the player threw.
        """
        return self._longest_pass

    @_float_property_decorator
    def quarterback_rating(self):
        """
        Returns a ``float`` of the player's quarterback rating.
        """
        return self._quarterback_rating

    @_int_property_decorator
    def times_sacked(self):
        """
        Returns an ``int`` of the number of times the player was sacked as a
        quarterback.
        """
        return self._times_sacked

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
    def assists_on_tackles(self):
        """
        Returns an ``int`` of the number of assist the player made on tackles.
        """
        return self._assists_on_tackles
