import pandas as pd
import re
from datetime import timedelta
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from ..constants import AWAY, HOME
from ..decorators import int_property_decorator
from .constants import (BOXSCORE_ELEMENT_INDEX,
                        BOXSCORE_ELEMENT_SUB_INDEX,
                        BOXSCORE_SCHEME,
                        BOXSCORE_URL,
                        BOXSCORES_URL)
from .player import (AbstractPlayer,
                     _float_property_decorator,
                     _int_property_decorator)
from functools import wraps


def ncaaf_int_property_sub_index(func):
    # Decorator dedicated to properties with sub-indices, such as pass yards
    # which is indexed within a table cell but also has multiple other values
    # in that same cell that need to be ignored.
    @property
    @wraps(func)
    def wrapper(*args):
        value = func(*args)
        # Equivalent to the calling property's method name
        field = func.__name__
        try:
            field_items = value.replace('--', '-').split('-')
        except AttributeError:
            return None
        try:
            return int(field_items[BOXSCORE_ELEMENT_SUB_INDEX[field]])
        except (TypeError, ValueError, IndexError):
            return None
    return wrapper


class BoxscorePlayer(AbstractPlayer):
    """
    Get player stats for an individual game.

    Given a player ID, such as 'david-blough-1' for David Blough, their full
    name, and all associated stats from the Boxscore page in HTML format, parse
    the HTML and extract only the relevant stats for the specified player and
    assign them to readable properties.

    This class inherits the ``AbstractPlayer`` class. As a result, all
    properties associated with ``AbstractPlayer`` can also be read directly
    from this class.

    As this class is instantiated from within the Boxscore class, it should not
    be called directly and should instead be queried using the appropriate
    players properties from the Boxscore class.

    Parameters
    ----------
    player_id : string
        A player's ID according to sports-reference.com, such as
        'david-blough-1' for David Blough. The player ID can be found by
        navigating to the player's stats page and getting the string between
        the final slash and the '.html' in the URL. In general, the ID is in
        the format 'first-last-n' where 'first' is the player's first name,
        'last' is the player's last name, and 'n' is a number starting at 1 for
        the first time that player ID has been used and increments by 1 for
        every successive player.
    player_name : string
        A string representing the player's first and last name, such as 'David
        Blough'.
    player_data : string
        A string representation of the player's HTML data from the Boxscore
        page. If the player appears in multiple tables, all of their
        information will appear in one single string concatenated together.
    """
    def __init__(self, player_id, player_name, player_data):
        self._index = 0
        self._player_id = player_id
        self._pass_yards_per_attempt = None
        self._kickoff_returns = None
        self._kickoff_return_yards = None
        self._average_kickoff_return_yards = None
        self._punt_returns = None
        self._punt_return_yards = None
        self._average_punt_return_yards = None
        self._extra_points_attempted = None
        self._extra_point_percentage = None
        self._field_goals_attempted = None
        self._field_goal_percentage = None
        self._points_kicking = None
        self._punts = None
        self._punting_yards = None
        self._punting_yards_per_attempt = None
        AbstractPlayer.__init__(self, player_id, player_name, player_data)

    @property
    def dataframe(self):
        """
        Returns a ``pandas DataFrame`` containing all other relevant class
        properties and value for the specified game.
        """
        fields_to_include = {
            'completed_passes': self.completed_passes,
            'pass_attempts': self.pass_attempts,
            'passing_completion': self.passing_completion,
            'passing_yards': self.passing_yards,
            'pass_yards_per_attempt': self.pass_yards_per_attempt,
            'adjusted_yards_per_attempt': self.adjusted_yards_per_attempt,
            'passing_touchdowns': self.passing_touchdowns,
            'interceptions_thrown': self.interceptions_thrown,
            'quarterback_rating': self.quarterback_rating,
            'rush_attempts': self.rush_attempts,
            'rush_yards': self.rush_yards,
            'rush_yards_per_attempt': self.rush_yards_per_attempt,
            'rush_touchdowns': self.rush_touchdowns,
            'receptions': self.receptions,
            'receiving_yards': self.receiving_yards,
            'receiving_yards_per_reception':
            self.receiving_yards_per_reception,
            'receiving_touchdowns': self.receiving_touchdowns,
            'plays_from_scrimmage': self.plays_from_scrimmage,
            'yards_from_scrimmage': self.yards_from_scrimmage,
            'yards_from_scrimmage_per_play':
            self.yards_from_scrimmage_per_play,
            'rushing_and_receiving_touchdowns':
            self.rushing_and_receiving_touchdowns,
            'solo_tackles': self.solo_tackles,
            'assists_on_tackles': self.assists_on_tackles,
            'total_tackles': self.total_tackles,
            'tackles_for_loss': self.tackles_for_loss,
            'sacks': self.sacks,
            'interceptions': self.interceptions,
            'yards_returned_from_interceptions':
            self.yards_returned_from_interceptions,
            'yards_returned_per_interception':
            self.yards_returned_per_interception,
            'interceptions_returned_for_touchdown':
            self.interceptions_returned_for_touchdown,
            'passes_defended': self.passes_defended,
            'fumbles_recovered': self.fumbles_recovered,
            'yards_recovered_from_fumble': self.yards_recovered_from_fumble,
            'fumbles_recovered_for_touchdown':
            self.fumbles_recovered_for_touchdown,
            'fumbles_forced': self.fumbles_forced,
            'kickoff_returns': self.kickoff_returns,
            'kickoff_return_yards': self.kickoff_return_yards,
            'average_kickoff_return_yards': self.average_kickoff_return_yards,
            'kickoff_return_touchdowns': self.kickoff_return_touchdowns,
            'punt_returns': self.punt_returns,
            'punt_return_yards': self.punt_return_yards,
            'average_punt_return_yards': self.average_punt_return_yards,
            'punt_return_touchdowns': self.punt_return_touchdowns,
            'extra_points_made': self.extra_points_made,
            'extra_points_attempted': self.extra_points_attempted,
            'extra_point_percentage': self.extra_point_percentage,
            'field_goals_made': self.field_goals_made,
            'field_goals_attempted': self.field_goals_attempted,
            'field_goal_percentage': self.field_goal_percentage,
            'points_kicking': self.points_kicking,
            'punts': self.punts,
            'punting_yards': self.punting_yards,
            'punting_yards_per_punt': self.punting_yards_per_attempt
        }
        return pd.DataFrame([fields_to_include], index=[self._player_id])

    @_float_property_decorator
    def pass_yards_per_attempt(self):
        """
        Returns a ``float`` of the average number of yards the player gained
        per pass attempt.
        """
        return self._pass_yards_per_attempt

    @_int_property_decorator
    def kickoff_returns(self):
        """
        Returns an ``int`` of the number of kickoffs the player attempted to
        return.
        """
        return self._kickoff_returns

    @_int_property_decorator
    def kickoff_return_yards(self):
        """
        Returns an ``int`` of the total number of yards the player gained while
        the player attempted to return a kickoff.
        """
        return self._kickoff_return_yards

    @_float_property_decorator
    def average_kickoff_return_yards(self):
        """
        Returns a ``float`` of the average number of yards the player gained
        per attempted kickoff return.
        """
        return self._average_kickoff_return_yards

    @_int_property_decorator
    def punt_returns(self):
        """
        Returns an ``int`` of the number of punts the player attempted to
        return.
        """
        return self._punt_returns

    @_int_property_decorator
    def punt_return_yards(self):
        """
        Returns an ``int`` of the total number of yards the player gained while
        the player attempted to return a punt.
        """
        return self._punt_return_yards

    @_float_property_decorator
    def average_punt_return_yards(self):
        """
        Returns a ``float`` of the average number of yards the player gained
        per attempted punt return.
        """
        return self._average_punt_return_yards

    @_int_property_decorator
    def extra_points_attempted(self):
        """
        Returns an ``int`` of the total number of extra points the player
        attempted.
        """
        return self._extra_points_attempted

    @_float_property_decorator
    def extra_point_percentage(self):
        """
        Returns a ``float`` of the percentage of attempted extra points the
        player made. Percentage ranges from 0-100.
        """
        return self._extra_point_percentage

    @_int_property_decorator
    def field_goals_attempted(self):
        """
        Returns an ``int`` of the total number of field goals the player
        attempted.
        """
        return self._field_goals_attempted

    @_float_property_decorator
    def field_goal_percentage(self):
        """
        Returns a ``float`` of the percentage of attempted field goals the
        player made. Percentage ranges from 0-100.
        """
        return self._field_goal_percentage

    @_int_property_decorator
    def points_kicking(self):
        """
        Returns an ``int`` of the total number of points the player gained from
        kicking field goals or extra points.
        """
        return self._points_kicking

    @_int_property_decorator
    def punts(self):
        """
        Returns an ``int`` of the number of times the player punted the ball.
        """
        return self._punts

    @_int_property_decorator
    def punting_yards(self):
        """
        Returns an ``int`` of the total number of yards the player punted the
        ball.
        """
        return self._punting_yards

    @_float_property_decorator
    def punting_yards_per_attempt(self):
        """
        Returns a ``float`` of the average number of yards the player punted
        per attempt.
        """
        return self._punting_yards_per_attempt


class Boxscore:
    """
    Detailed information about the final statistics for a game.

    Stores all relevant information for a game such as the date, time,
    location, result, and more advanced metrics such as the number of fumbles
    from sacks, a team's passing completion, rushing touchdowns and much more.

    Parameters
    ----------
    uri : string
        The relative link to the boxscore HTML page, such as
        '2018-01-08-georgia'.
    """
    def __init__(self, uri):
        self._uri = uri
        self._date = None
        self._time = None
        self._stadium = None
        self._away_name = None
        self._home_name = None
        self._winner = None
        self._winning_name = None
        self._winning_abbr = None
        self._losing_name = None
        self._losing_abbr = None
        self._away_points = None
        self._away_first_downs = None
        self._away_rush_attempts = None
        self._away_rush_yards = None
        self._away_rush_touchdowns = None
        self._away_pass_completions = None
        self._away_pass_attempts = None
        self._away_pass_yards = None
        self._away_pass_touchdowns = None
        self._away_interceptions = None
        self._away_total_yards = None
        self._away_fumbles = None
        self._away_fumbles_lost = None
        self._away_turnovers = None
        self._away_penalties = None
        self._away_yards_from_penalties = None
        self._home_points = None
        self._home_first_downs = None
        self._home_rush_attempts = None
        self._home_rush_yards = None
        self._home_rush_touchdowns = None
        self._home_pass_completions = None
        self._home_pass_attempts = None
        self._home_pass_yards = None
        self._home_pass_touchdowns = None
        self._home_interceptions = None
        self._home_total_yards = None
        self._home_fumbles = None
        self._home_fumbles_lost = None
        self._home_turnovers = None
        self._home_penalties = None
        self._home_yards_from_penalties = None

        self._parse_game_data(uri)

    def _retrieve_html_page(self, uri):
        """
        Download the requested HTML page.

        Given a relative link, download the requested page and strip it of all
        comment tags before returning a pyquery object which will be used to
        parse the data.

        Parameters
        ----------
        uri : string
            The relative link to the boxscore HTML page, such as
            '2018-01-08-georgia'.

        Returns
        -------
        PyQuery object
            The requested page is returned as a queriable PyQuery object with
            the comment tags removed.
        """
        url = BOXSCORE_URL % uri
        try:
            url_data = pq(url)
        except HTTPError:
            return None
        return pq(utils._remove_html_comment_tags(url_data))

    def _parse_game_date_and_location(self, boxscore):
        """
        Retrieve the game's date and location.

        The date and location of the game follow a more complicated parsing
        scheme and should be handled differently from other tags. Both fields
        are separated by a newline character ('\n') with the first line being
        the date and the second being the location.

        Parameters
        ----------
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.
        """
        scheme = BOXSCORE_SCHEME['time']
        items = [i.text() for i in boxscore(scheme).items()]
        game_info = items[0].split('\n')
        time = ''
        date = ''
        stadium = ''
        for line in game_info:
            time_match = re.findall(r'(\d:\d\d|\d\d:\d\d)', line.lower())
            if len(time_match) > 0:
                time = line
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                        'saturday', 'sunday']:
                if day in line.lower():
                    date = line
            # In general, locations are in the format 'Stadium Name - City,
            # State'. Since the ' - ' characters seem to be unique to the
            # location line, it should be safe to use this as a matcher.
            if ' - ' in line:
                stadium = line
        setattr(self, '_time', time)
        setattr(self, '_date', date)
        setattr(self, '_stadium', stadium)

    def _parse_name(self, field, boxscore):
        """
        Retrieve the team's complete name tag.

        Both the team's full name (embedded in the tag's text) and the team's
        abbreviation are stored in the name tag which can be used to parse
        the winning and losing team's information.

        Parameters
        ----------
        field : string
            The name of the attribute to parse
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.

        Returns
        -------
        PyQuery object
            The complete text for the requested tag.
        """
        scheme = BOXSCORE_SCHEME[field]
        return boxscore(scheme)

    def _find_boxscore_tables(self, boxscore):
        """
        Find all tables with boxscore information on the page.

        Iterate through all tables on the page and see if any of them are
        boxscore pages by checking if the ID is prefixed with 'box_'. If so,
        add it to a list and return the final list at the end.

        Parameters
        ----------
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.

        Returns
        -------
        list
            Returns a ``list`` of the PyQuery objects where each object
            represents a boxscore table.
        """
        tables = []
        valid_tables = ['passing', 'rushing_and_receiving', 'defense',
                        'returns', 'kicking_and_punting']

        for table in boxscore('table').items():
            if table.attr['id'] in valid_tables:
                tables.append(table)
        return tables

    def _find_player_id(self, row):
        """
        Find the player's ID.

        Find the player's ID as embedded in the 'data-append-csv' attribute,
        such as 'david-blough-1' for David Blough.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object representing a single row in a boxscore table for
            a single player.

        Returns
        -------
        str
            Returns a ``string`` of the player's ID, such as 'david-blough-1'
            for David Blough.
        """
        return row('th').attr('data-append-csv')

    def _find_player_name(self, row):
        """
        Find the player's full name.

        Find the player's full name, such as 'David Blough'. The name is the
        text displayed for a link to the player's individual stats.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object representing a single row in a boxscore table for
            a single player.

        Returns
        -------
        str
            Returns a ``string`` of the player's full name, such as 'David
            Blough'.
        """
        return row('a:first').text()

    def _find_home_or_away(self, row):
        """
        Determine whether the player is on the home or away team.

        Next to every player is their school's name. This name can be matched
        with the previously parsed home team's name to determine if the player
        is a member of the home or away team.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object representing a single row in a boxscore table for
            a single player.

        Returns
        -------
        str
            Returns a ``string`` constant denoting whether the team plays for
            the home or away team.
        """
        name = row('a:last').text()
        if name == self._home_name.text():
            return HOME
        else:
            return AWAY

    def _extract_player_stats(self, table, player_dict):
        """
        Combine all player stats into a single object.

        Since each player generally has a couple of rows worth of stats
        (rushing, passing, defense, and more) on the boxscore page, both rows
        should be combined into a single string object to easily query all
        fields from a single object instead of determining which row to pull
        metrics from.

        Parameters
        ----------
        table : PyQuery object
            A PyQuery object of a single boxscore table, such as the home
            team's advanced stats or the away team's basic stats.
        player_dict : dictionary
            A dictionary where each key is a string of the player's ID and each
            value is a dictionary where the values contain the player's name,
            HTML data, and a string constant indicating which team the player
            is a member of.

        Returns
        -------
        dictionary
            Returns a ``dictionary`` where each key is a string of the player's
            ID and each value is a dictionary where the values contain the
            player's name, HTML data, and a string constant indicating which
            team the player is a member of.
        """
        for row in table('tbody tr').items():
            player_id = self._find_player_id(row)
            # Occurs when a header row is identified instead of a player.
            if not player_id:
                continue
            name = self._find_player_name(row)
            home_or_away = self._find_home_or_away(row)
            try:
                player_dict[player_id]['data'] += str(row).strip()
            except KeyError:
                player_dict[player_id] = {
                    'name': name,
                    'data': str(row).strip(),
                    'team': home_or_away
                }
        return player_dict

    def _instantiate_players(self, player_dict):
        """
        Create a list of player instances for both the home and away teams.

        For every player listed on the boxscores page, create an instance of
        the BoxscorePlayer class for that player and add them to a list of
        players for their respective team.

        Parameters
        ----------
        player_dict : dictionary
            A dictionary containing information for every player on the
            boxscores page. Each key is a string containing the player's ID
            and each value is a dictionary with the player's full name, a
            string representation of their HTML stats, and a string constant
            denoting which team they play for as the values.

        Returns
        -------
        tuple
            Returns a ``tuple`` in the format (away_players, home_players)
            where each element is a list of player instances for the away and
            home teams, respectively.
        """
        home_players = []
        away_players = []
        for player_id, details in player_dict.items():
            player = BoxscorePlayer(player_id,
                                    details['name'],
                                    details['data'])
            if details['team'] == HOME:
                home_players.append(player)
            else:
                away_players.append(player)
        return away_players, home_players

    def _find_players(self, boxscore):
        """
        Find all players for each team.

        Iterate through every player for both teams as found in the boxscore
        tables and create a list of instances of the BoxscorePlayer class for
        each player. Return lists of player instances comprising the away and
        home team players, respectively.

        Parameters
        ----------
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.

        Returns
        -------
        tuple
            Returns a ``tuple`` in the format (away_players, home_players)
            where each element is a list of player instances for the away and
            home teams, respectively.
        """
        player_dict = {}

        tables = self._find_boxscore_tables(boxscore)
        for table in tables:
            player_dict = self._extract_player_stats(table, player_dict)
        away_players, home_players = self._instantiate_players(player_dict)
        return away_players, home_players

    def _parse_game_data(self, uri):
        """
        Parses a value for every attribute.

        This function looks through every attribute and retrieves the value
        according to the parsing scheme and index of the attribute from the
        passed HTML data. Once the value is retrieved, the attribute's value is
        updated with the returned result.

        Note that this method is called directly once Boxscore is invoked and
        does not need to be called manually.

        Parameters
        ----------
        uri : string
            The relative link to the boxscore HTML page, such as
            '2018-01-08-georgia'.
        """
        boxscore = self._retrieve_html_page(uri)
        # If the boxscore is None, the game likely hasn't been played yet and
        # no information can be gathered. As there is nothing to grab, the
        # class instance should just be empty.
        if not boxscore:
            return

        for field in self.__dict__:
            # Remove the '_' from the name
            short_field = str(field)[1:]
            if short_field == 'winner' or \
               short_field == 'winning_name' or \
               short_field == 'winning_abbr' or \
               short_field == 'losing_name' or \
               short_field == 'losing_abbr' or \
               short_field == 'uri' or \
               short_field == 'date' or \
               short_field == 'time' or \
               short_field == 'stadium':
                continue
            if short_field == 'away_name' or \
               short_field == 'home_name':
                value = self._parse_name(short_field, boxscore)
                setattr(self, field, value)
                continue
            index = 0
            if short_field in BOXSCORE_ELEMENT_INDEX.keys():
                index = BOXSCORE_ELEMENT_INDEX[short_field]
            value = utils._parse_field(BOXSCORE_SCHEME,
                                       boxscore,
                                       short_field,
                                       index)
            setattr(self, field, value)
        self._parse_game_date_and_location(boxscore)
        self._away_players, self._home_players = self._find_players(boxscore)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the string URI that is used to
        instantiate the class, such as '2018-01-08-georgia'.
        """
        for points in [self._away_points, self._home_points]:
            if points is None or points == '':
                return None
        fields_to_include = {
            'away_first_downs': self.away_first_downs,
            'away_fumbles': self.away_fumbles,
            'away_fumbles_lost': self.away_fumbles_lost,
            'away_interceptions': self.away_interceptions,
            'away_pass_attempts': self.away_pass_attempts,
            'away_pass_completions': self.away_pass_completions,
            'away_pass_touchdowns': self.away_pass_touchdowns,
            'away_pass_yards': self.away_pass_yards,
            'away_penalties': self.away_penalties,
            'away_points': self.away_points,
            'away_rush_attempts': self.away_rush_attempts,
            'away_rush_touchdowns': self.away_rush_touchdowns,
            'away_rush_yards': self.away_rush_yards,
            'away_total_yards': self.away_total_yards,
            'away_turnovers': self.away_turnovers,
            'away_yards_from_penalties': self.away_yards_from_penalties,
            'date': self.date,
            'home_first_downs': self.home_first_downs,
            'home_fumbles': self.home_fumbles,
            'home_fumbles_lost': self.home_fumbles_lost,
            'home_interceptions': self.home_interceptions,
            'home_pass_attempts': self.home_pass_attempts,
            'home_pass_completions': self.home_pass_completions,
            'home_pass_touchdowns': self.home_pass_touchdowns,
            'home_pass_yards': self.home_pass_yards,
            'home_penalties': self.home_penalties,
            'home_points': self.home_points,
            'home_rush_attempts': self.home_rush_attempts,
            'home_rush_touchdowns': self.home_rush_touchdowns,
            'home_rush_yards': self.home_rush_yards,
            'home_total_yards': self.home_total_yards,
            'home_turnovers': self.home_turnovers,
            'home_yards_from_penalties': self.home_yards_from_penalties,
            'losing_abbr': self.losing_abbr,
            'losing_name': self.losing_name,
            'stadium': self.stadium,
            'time': self.time,
            'winner': self.winner,
            'winning_abbr': self.winning_abbr,
            'winning_name': self.winning_name
        }
        return pd.DataFrame([fields_to_include], index=[self._uri])

    @property
    def away_players(self):
        """
        Returns a ``list`` of ``BoxscorePlayer`` class instances for each
        player on the away team.
        """
        return self._away_players

    @property
    def home_players(self):
        """
        Returns a ``list`` of ``BoxscorePlayer`` class instances for each
        player on the home team.
        """
        return self._home_players

    @property
    def date(self):
        """
        Returns a ``string`` of the date the game took place.
        """
        return self._date

    @property
    def time(self):
        """
        Returns a ``string`` of the time the game started.
        """
        return self._time.replace('Start Time: ', '')

    @property
    def stadium(self):
        """
        Returns a ``string`` of the name of the stadium where the game was
        played.
        """
        return self._stadium.replace('Stadium: ', '')

    @property
    def winner(self):
        """
        Returns a ``string`` constant indicating whether the home or away team
        won.
        """
        if self.home_points > self.away_points:
            return HOME
        return AWAY

    @property
    def winning_name(self):
        """
        Returns a ``string`` of the winning team's name, such as 'Alabama'.
        """
        if self.winner == HOME:
            return self._home_name.text()
        return self._away_name.text()

    @property
    def winning_abbr(self):
        """
        Returns a ``string`` of the winning team's abbreviation, such as
        'ALABAMA'
        for the Alabama Crimson Tide.
        """
        if self.winner == HOME:
            if 'cfb/schools' not in str(self._home_name):
                return self._home_name.text()
            return utils._parse_abbreviation(self._home_name)
        if 'cfb/schools' not in str(self._away_name):
            return self._away_name.text()
        return utils._parse_abbreviation(self._away_name)

    @property
    def losing_name(self):
        """
        Returns a ``string`` of the losing team's name, such as 'Georgia'.
        """
        if self.winner == HOME:
            return self._away_name.text()
        return self._home_name.text()

    @property
    def losing_abbr(self):
        """
        Returns a ``string`` of the losing team's abbreviation, such as
        'GEORGIA' for the Georgia Bulldogs.
        """
        if self.winner == HOME:
            if 'cfb/schools' not in str(self._away_name):
                return self._away_name.text()
            return utils._parse_abbreviation(self._away_name)
        if 'cfb/schools' not in str(self._home_name):
            return self._home_name.text()
        return utils._parse_abbreviation(self._home_name)

    @int_property_decorator
    def away_points(self):
        """
        Returns an ``int`` of the number of points the away team scored.
        """
        return self._away_points

    @int_property_decorator
    def away_first_downs(self):
        """
        Returns an ``int`` of the number of first downs the away team gained.
        """
        return self._away_first_downs

    @ncaaf_int_property_sub_index
    def away_rush_attempts(self):
        """
        Returns an ``int`` of the number of rushing plays the away team made.
        """
        return self._away_rush_attempts

    @ncaaf_int_property_sub_index
    def away_rush_yards(self):
        """
        Returns an ``int`` of the number of rushing yards the away team gained.
        """
        return self._away_rush_yards

    @ncaaf_int_property_sub_index
    def away_rush_touchdowns(self):
        """
        Returns an ``int`` of the number of rushing touchdowns the away team
        scored.
        """
        return self._away_rush_touchdowns

    @ncaaf_int_property_sub_index
    def away_pass_completions(self):
        """
        Returns an ``int`` of the number of completed passes the away team
        made.
        """
        return self._away_pass_completions

    @ncaaf_int_property_sub_index
    def away_pass_attempts(self):
        """
        Returns an ``int`` of the number of passes that were thrown by the away
        team.
        """
        return self._away_pass_attempts

    @ncaaf_int_property_sub_index
    def away_pass_yards(self):
        """
        Returns an ``int`` of the number of passing yards the away team gained.
        """
        return self._away_pass_yards

    @ncaaf_int_property_sub_index
    def away_pass_touchdowns(self):
        """
        Returns an ``int`` of the number of passing touchdowns the away team
        scored.
        """
        return self._away_pass_touchdowns

    @ncaaf_int_property_sub_index
    def away_interceptions(self):
        """
        Returns an ``int`` of the number of interceptions the away team threw.
        """
        return self._away_interceptions

    @int_property_decorator
    def away_total_yards(self):
        """
        Returns an ``int`` of the total number of yards the away team gained.
        """
        return self._away_total_yards

    @ncaaf_int_property_sub_index
    def away_fumbles(self):
        """
        Returns an ``int`` of the number of times the away team fumbled the
        ball.
        """
        return self._away_fumbles

    @ncaaf_int_property_sub_index
    def away_fumbles_lost(self):
        """
        Returns an ``int`` of the number of times the away team turned the ball
        over as the result of a fumble.
        """
        return self._away_fumbles

    @int_property_decorator
    def away_turnovers(self):
        """
        Returns an ``int`` of the number of times the away team turned the ball
        over.
        """
        return self._away_turnovers

    @ncaaf_int_property_sub_index
    def away_penalties(self):
        """
        Returns an ``int`` of the number of penalties called on the away team.
        """
        return self._away_penalties

    @ncaaf_int_property_sub_index
    def away_yards_from_penalties(self):
        """
        Returns an ``int`` of the number of yards gifted as a result of
        penalties called on the away team.
        """
        return self._away_yards_from_penalties

    @int_property_decorator
    def home_points(self):
        """
        Returns an ``int`` of the number of points the home team scored.
        """
        return self._home_points

    @int_property_decorator
    def home_first_downs(self):
        """
        Returns an ``int`` of the number of first downs the home team gained.
        """
        return self._home_first_downs

    @ncaaf_int_property_sub_index
    def home_rush_attempts(self):
        """
        Returns an ``int`` of the number of rushing plays the home team made.
        """
        return self._home_rush_attempts

    @ncaaf_int_property_sub_index
    def home_rush_yards(self):
        """
        Returns an ``int`` of the number of rushing yards the home team gained.
        """
        return self._home_rush_yards

    @ncaaf_int_property_sub_index
    def home_rush_touchdowns(self):
        """
        Returns an ``int`` of the number of rushing touchdowns the home team
        scored.
        """
        return self._home_rush_touchdowns

    @ncaaf_int_property_sub_index
    def home_pass_completions(self):
        """
        Returns an ``int`` of the number of completed passes the home team
        made.
        """
        return self._home_pass_completions

    @ncaaf_int_property_sub_index
    def home_pass_attempts(self):
        """
        Returns an ``int`` of the number of passes that were thrown by the home
        team.
        """
        return self._home_pass_attempts

    @ncaaf_int_property_sub_index
    def home_pass_yards(self):
        """
        Returns an ``int`` of the number of passing yards the home team gained.
        """
        return self._home_pass_yards

    @ncaaf_int_property_sub_index
    def home_pass_touchdowns(self):
        """
        Returns an ``int`` of the number of passing touchdowns the home team
        scored.
        """
        return self._home_pass_touchdowns

    @ncaaf_int_property_sub_index
    def home_interceptions(self):
        """
        Returns an ``int`` of the number of interceptions the home team threw.
        """
        return self._home_pass_touchdowns

    @int_property_decorator
    def home_total_yards(self):
        """
        Returns an ``int`` of the total number of yards the home team gained.
        """
        return self._home_total_yards

    @ncaaf_int_property_sub_index
    def home_fumbles(self):
        """
        Returns an ``int`` of the number of times the home team fumbled the
        ball.
        """
        return self._home_fumbles

    @ncaaf_int_property_sub_index
    def home_fumbles_lost(self):
        """
        Returns an ``int`` of the number of times the home team turned the ball
        over as the result of a fumble.
        """
        return self._home_fumbles_lost

    @int_property_decorator
    def home_turnovers(self):
        """
        Returns an ``int`` of the number of times the home team turned the ball
        over.
        """
        return self._home_turnovers

    @ncaaf_int_property_sub_index
    def home_penalties(self):
        """
        Returns an ``int`` of the number of penalties called on the home team.
        """
        return self._home_penalties

    @ncaaf_int_property_sub_index
    def home_yards_from_penalties(self):
        """
        Returns an ``int`` of the number of yards gifted as a result of
        penalties called on the home team.
        """
        return self._home_yards_from_penalties


class Boxscores:
    """
    Search for NCAAF games taking place on a particular day.

    Retrieve a dictionary which contains a list of all games being played on a
    particular day. Output includes a link to the boxscore, a boolean value
    which indicates if the game is between two Division-I teams or not, and the
    names and abbreviations for both the home teams. If no games are played on
    a particular day, the list will be empty.

    Parameters
    ----------
    date : datetime object
        The date to search for any matches. The month, day, and year are
        required for the search, but time is not factored into the search.
    end_date : datetime object
        Optionally specify an end date to iterate until. All boxscores starting
        from the date specified in the 'date' parameter up to and including the
        boxscores specified in the 'end_date' parameter will be pulled. If left
        empty, or if 'end_date' is prior to 'date', only the games from the day
        specified in the 'date' parameter will be saved.
    """
    def __init__(self, date, end_date=None):
        self._boxscores = {}

        self._find_games(date, end_date)

    @property
    def games(self):
        """
        Returns a ``dictionary`` object representing all of the games played on
        the requested day. Dictionary is in the following format::

            {'date' : [  # 'date' is the string date in format 'MM-DD-YYYY'
                {
                    'home_name': Name of the home team, such as 'Purdue
                                 Boilermakers' (`str`),
                    'home_abbr': Abbreviation for the home team, such as
                                 'PURDUE' (`str`),
                    'away_name': Name of the away team, such as 'Indiana
                                 Hoosiers' (`str`),
                    'away_abbr': Abbreviation for the away team, such as
                                 'INDIANA' (`str`),
                    'boxscore': String representing the boxscore URI, such as
                                '2018-01-28-15-indiana' (`str`),
                    'non_di': Boolean value which evaluates to True when at
                              least one of the teams does not compete in NCAA
                              Division-I basketball (`bool`),
                    'top_25': Boolean value which evaluates to True when at
                              least one of the teams is ranked in the AP Top 25
                              polls (`bool`),
                    'winning_name': Full name of the winning team, such as
                                    'Purdue Boilermakers' (`str`),
                    'winning_abbr': Abbreviation for the winning team, such as
                                    'PURDUE' (`str`),
                    'losing_name': Full name of the losing team, such as
                                   'Indiana Hoosiers' (`str`),
                    'losing_abbr': Abbreviation for the losing team, such as
                                   'INDIANA' (`str`),
                    'home_score': Integer score for the home team (`int`),
                    'home_rank': Integer representing the home team's rank
                                 (`int`),
                    'away_score': Integer score for the away team (`int`),
                    'away_rank': Integer representing the away team's rank
                                 (`int`)
                },
                { ... },
                ...
                ]
            }

        If no games were played on 'date', the list for ['date'] will be empty.
        """
        return self._boxscores

    def _create_url(self, date):
        """
        Build the URL based on the passed datetime object.

        In order to get the proper boxscore page, the URL needs to include the
        requested month, day, and year.

        Parameters
        ----------
        date : datetime object
            The date to search for any matches. The month, day, and year are
            required for the search, but time is not factored into the search.

        Returns
        -------
        string
            Returns a ``string`` of the boxscore URL including the requested
            date.
        """
        return BOXSCORES_URL % (date.month, date.day, date.year)

    def _get_requested_page(self, url):
        """
        Get the requested page.

        Download the requested page given the created URL and return a PyQuery
        object.

        Parameters
        ----------
        url : string
            The URL containing the boxscores to find.

        Returns
        -------
        PyQuery object
            A PyQuery object containing the HTML contents of the requested
            page.
        """
        return pq(url)

    def _get_boxscore_uri(self, url):
        """
        Find the boxscore URI.

        Given the boxscore tag for a game, parse the embedded URI for the
        boxscore.

        Parameters
        ----------
        url : PyQuery object
            A PyQuery object containing the game's boxscore tag which has the
            boxscore URI embedded within it.

        Returns
        -------
        string
            Returns a ``string`` containing the link to the game's boxscore
            page.
        """
        uri = re.sub(r'.*cfb/boxscores/', '', str(url))
        uri = re.sub(r'\.html.*', '', uri).strip()
        return uri

    def _parse_abbreviation(self, abbr):
        """
        Parse a team's abbreviation.

        Given the team's HTML name tag, parse their abbreviation.

        Parameters
        ----------
        abbr : string
            A string of a team's HTML name tag.

        Returns
        -------
        string
            Returns a ``string`` of the team's abbreviation.
        """
        if 'cfb/schools' not in str(abbr):
            return None
        abbr = re.sub(r'.*/schools/', '', str(abbr))
        abbr = re.sub(r'/.*', '', abbr)
        return abbr

    def _get_name(self, name):
        """
        Find a team's name and abbreviation.

        Given the team's HTML name tag, determine their name, abbreviation, and
        whether or not they compete in Division-I.

        Parameters
        ----------
        name : PyQuery object
            A PyQuery object of a team's HTML name tag in the boxscore.

        Returns
        -------
        tuple
            Returns a tuple containing the name, abbreviation, and whether or
            not the team participates in Division-I. Tuple is in the following
            order: Team Name, Team Abbreviation, boolean which evaluates to
            True if the team does not participate in Division-I.
        """
        team_name = name.text()
        abbr = self._parse_abbreviation(name)
        non_di = False
        if not abbr:
            abbr = team_name
            non_di = True
        return team_name, abbr, non_di

    def _get_score(self, score_link):
        """
        Find a team's final score.

        Given an HTML string of a team's boxscore, extract the integer
        representing the final score and return the number.

        Parameters
        ----------
        score_link : string
            An HTML string representing a team's final score in the format
            '<td class="right">NN</td>' where 'NN' is the team's score.

        Returns
        -------
        int
            Returns an int representing the team's final score in runs.
        """
        score = score_link.replace('<td class="right">', '')
        score = score.replace('</td>', '')
        return int(score)

    def _get_rank(self, team):
        """
        Find the team's rank when applicable.

        If a team is ranked, it will showup in a separate <span> tag with the
        actual rank embedded between parentheses. When a team is ranked, the
        integer value representing their ranking should be returned. For teams
        that are not ranked, None should be returned.

        Parameters
        ----------
        team : PyQuery object
            A PyQuery object of a team's HTML tag in the boxscore.

        Returns
        -------
        int
            Returns an integer representing the team's ranking when applicable,
            or None if the team is not ranked.
        """
        rank = None
        rank_field = team('span[class="pollrank"]')
        if len(rank_field) > 0:
            rank = re.findall(r'\(\d+\)', str(rank_field))[0]
            rank = int(rank.replace('(', '').replace(')', ''))
        return rank

    def _get_team_names(self, game):
        """
        Find the names and abbreviations for both teams in a game.

        Using the HTML contents in a boxscore, find the name and abbreviation
        for both teams and determine wether or not this is a matchup between
        two Division-I teams.

        Parameters
        ----------
        game : PyQuery object
            A PyQuery object of a single boxscore containing information about
            both teams.

        Returns
        -------
        tuple
            Returns a tuple containing the names and abbreviations of both
            teams in the following order: Away Name, Away Abbreviation, Away
            Score, Away Ranking, Home Name, Home Abbreviation, Home Score, Home
            Ranking, a boolean which evaluates to True if either team does not
            participate in Division-I athletics, and a boolean which evalutes
            to True if either team is currently ranked.
        """
        # Grab the first <td...> tag for each <tr> row in the boxscore,
        # representing the name for each participating team.
        links = [g('td:first') for g in game('tr').items()]
        # The away team is the second link in the boxscore
        away = links[1]
        # The home team is the last (3rd) link in the boxscore
        home = links[-1]
        non_di = False
        scores = re.findall(r'<td class="right">\d+</td>', str(game))
        away_score = None
        home_score = None
        # If the game hasn't started or hasn't been updated on sports-reference
        # yet, no score will be shown and therefore can't be parsed.
        if len(scores) == 2:
            away_score = self._get_score(scores[0])
            home_score = self._get_score(scores[1])
        away_name, away_abbr, away_non_di = self._get_name(away('a'))
        home_name, home_abbr, home_non_di = self._get_name(home('a'))
        non_di = away_non_di or home_non_di
        away_rank = self._get_rank(away)
        home_rank = self._get_rank(home)
        top_25 = bool(away_rank or home_rank)
        return (away_name, away_abbr, away_score, away_rank, home_name,
                home_abbr, home_score, home_rank, non_di, top_25)

    def _get_team_results(self, away_name, away_abbr, away_score, home_name,
                          home_abbr, home_score):
        """
        Determine the winner and loser of the game.

        If the game has been completed and sports-reference has been updated
        with the score, determine the winner and loser and return their
        respective names and abbreviations.

        Parameters
        ----------
        away_name : string
            The name of the away team, such as 'Indiana'.
        away_abbr : string
            The abbreviation of the away team, such as 'indiana'.
        away_score : int
            The number of points the away team scored, or None if the game
            hasn't completed yet.
        home_score : string
            The name of the home team, such as 'Purdue'.
        home_abbr : string
            The abbreviation of the home team, such as 'purdue'.
        home_score : int
            The number of points the home team scored, or None if the game
            hasn't completed yet.

        Returns
        -------
        tuple, tuple
            Returns two tuples, each containing the name followed by the
            abbreviation of the winning and losing team, respectively. If the
            game doesn't have a score associated with it yet, both tuples will
            be None.
        """
        if not away_score or not home_score:
            return None, None
        if away_score > home_score:
            return (away_name, away_abbr), (home_name, home_abbr)
        else:
            return (home_name, home_abbr), (away_name, away_abbr)

    def _extract_game_info(self, games):
        """
        Parse game information from all boxscores.

        Find the major game information for all boxscores listed on a
        particular boxscores webpage and return the results in a list.

        Parameters
        ----------
        games : generator
            A generator where each element points to a boxscore on the parsed
            boxscores webpage.

        Returns
        -------
        list
            Returns a ``list`` of dictionaries where each dictionary contains
            the name and abbreviations for both the home and away teams, a
            boolean value indicating whether or not both teams compete in
            Division-I, and a link to the boxscore.
        """
        all_boxscores = []

        for game in games:
            names = self._get_team_names(game)
            away_name, away_abbr, away_score, away_rank, home_name, \
                home_abbr, home_score, home_rank, non_di, top_25 = names
            boxscore_url = game('td[class="right gamelink"] a')
            boxscore_uri = self._get_boxscore_uri(boxscore_url)
            winning_name = None
            winning_abbr = None
            losing_name = None
            losing_abbr = None
            winner, loser = self._get_team_results(away_name, away_abbr,
                                                   away_score, home_name,
                                                   home_abbr, home_score)
            if winner and loser:
                winning_name, winning_abbr = winner
                losing_name, losing_abbr = loser
            game_info = {
                'boxscore': boxscore_uri,
                'away_name': away_name,
                'away_abbr': away_abbr,
                'away_score': away_score,
                'away_rank': away_rank,
                'home_name': home_name,
                'home_abbr': home_abbr,
                'home_score': home_score,
                'home_rank': home_rank,
                'non_di': non_di,
                'top_25': top_25,
                'winning_name': winning_name,
                'winning_abbr': winning_abbr,
                'losing_name': losing_name,
                'losing_abbr': losing_abbr
            }
            all_boxscores.append(game_info)
        return all_boxscores

    def _find_games(self, date, end_date):
        """
        Retrieve all major games played on a given day.

        Builds a URL based on the requested date and downloads the HTML
        contents before parsing any and all games played during that day. Any
        games that are found are added to the boxscores dictionary with
        high-level game information such as the home and away team names and a
        link to the boxscore page.

        Parameters
        ----------
        date : datetime object
            The date to search for any matches. The month, day, and year are
            required for the search, but time is not factored into the search.
        end_date : datetime object
            Optionally specify an end date to iterate until. All boxscores
            starting from the date specified in the 'date' parameter up to and
            including the boxscores specified in the 'end_date' parameter will
            be pulled. If left empty, or if 'end_date' is prior to 'date', only
            the games from the day specified in the 'date' parameter will be
            saved.
        """
        # Set the end date to the start date if the end date is before the
        # start date.
        if not end_date or date > end_date:
            end_date = date
        date_step = date
        while date_step <= end_date:
            url = self._create_url(date_step)
            page = self._get_requested_page(url)
            games = page('table[class="teams"]').items()
            boxscores = self._extract_game_info(games)
            timestamp = '%s-%s-%s' % (date_step.month, date_step.day,
                                      date_step.year)
            self._boxscores[timestamp] = boxscores
            date_step += timedelta(days=1)
