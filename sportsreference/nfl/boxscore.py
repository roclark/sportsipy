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


def nfl_int_property_sub_index(func):
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

    Given a player ID, such as 'BreeDr01' for Drew Brees, their full name, and
    all associated stats from the Boxscore page in HTML format, parse the HTML
    and extract only the relevant stats for the specified player and assign
    them to readable properties.

    This class inherits the ``AbstractPlayer`` class. As a result, all
    properties associated with ``AbstractPlayer`` can also be read directly
    from this class.

    As this class is instantiated from within the Boxscore class, it should not
    be called directly and should instead be queried using the appropriate
    players properties from the Boxscore class.

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
        A string representing the player's first and last name, such as 'David
        Blough'.
    player_data : string
        A string representation of the player's HTML data from the Boxscore
        page. If the player appears in multiple tables, all of their
        information will appear in one single string concatenated together.
    """
    def __init__(self, player_id, player_name, player_data):
        self._index = 0
        self._yards_lost_from_sacks = None
        self._fumbles_lost = None
        self._combined_tackles = None
        self._solo_tackles = None
        self._tackles_for_loss = None
        self._quarterback_hits = None
        self._average_kickoff_return_yards = None
        AbstractPlayer.__init__(self, player_id, player_name, player_data)

    @property
    def dataframe(self):
        """
        Returns a ``pandas DataFrame`` containing all other relevant class
        properties and values for the specified game.
        """
        fields_to_include = {
            'completed_passes': self.completed_passes,
            'attempted_passes': self.attempted_passes,
            'passing_yards': self.passing_yards,
            'passing_touchdowns': self.passing_touchdowns,
            'interceptions_thrown': self.interceptions_thrown,
            'times_sacked': self.times_sacked,
            'yards_lost_from_sacks': self.yards_lost_from_sacks,
            'longest_pass': self.longest_pass,
            'quarterback_rating': self.quarterback_rating,
            'rush_attempts': self.rush_attempts,
            'rush_yards': self.rush_yards,
            'rush_touchdowns': self.rush_touchdowns,
            'longest_rush': self.longest_rush,
            'times_pass_target': self.times_pass_target,
            'receptions': self.receptions,
            'receiving_yards': self.receiving_yards,
            'receiving_touchdowns': self.receiving_touchdowns,
            'longest_reception': self.longest_reception,
            'fumbles': self.fumbles,
            'fumbles_lost': self.fumbles_lost,
            'interceptions': self.interceptions,
            'yards_returned_from_interception':
            self.yards_returned_from_interception,
            'interceptions_returned_for_touchdown':
            self.interceptions_returned_for_touchdown,
            'longest_interception_return': self.longest_interception_return,
            'passes_defended': self.passes_defended,
            'sacks': self.sacks,
            'combined_tackles': self.combined_tackles,
            'solo_tackles': self.solo_tackles,
            'assists_on_tackles': self.assists_on_tackles,
            'tackles_for_loss': self.tackles_for_loss,
            'quarterback_hits': self.quarterback_hits,
            'fumbles_recovered': self.fumbles_recovered,
            'yards_recovered_from_fumble': self.yards_recovered_from_fumble,
            'fumbles_recovered_for_touchdown':
            self.fumbles_recovered_for_touchdown,
            'fumbles_forced': self.fumbles_forced,
            'kickoff_returns': self.kickoff_returns,
            'kickoff_return_yards': self.kickoff_return_yards,
            'average_kickoff_return_yards': self.average_kickoff_return_yards,
            'kickoff_return_touchdown': self.kickoff_return_touchdown,
            'longest_kickoff_return': self.longest_kickoff_return,
            'punt_returns': self.punt_returns,
            'punt_return_yards': self.punt_return_yards,
            'yards_per_punt_return': self.yards_per_punt_return,
            'punt_return_touchdown': self.punt_return_touchdown,
            'longest_punt_return': self.longest_punt_return,
            'extra_points_made': self.extra_points_made,
            'extra_points_attempted': self.extra_points_attempted,
            'field_goals_made': self.field_goals_made,
            'field_goals_attempted': self.field_goals_attempted,
            'punts': self.punts,
            'total_punt_yards': self.total_punt_yards,
            'yards_per_punt': self.yards_per_punt,
            'longest_punt': self.longest_punt
        }
        return pd.DataFrame([fields_to_include], index=[self._player_id])

    @_int_property_decorator
    def yards_lost_from_sacks(self):
        """
        Returns an ``int`` of the total number of yards the player lost after
        being sacked by the opponent.
        """
        return self._yards_lost_from_sacks

    @_int_property_decorator
    def fumbles_lost(self):
        """
        Returns an ``int`` of the number of times the player fumbled the ball
        and the opponent recovered the ball.
        """
        return self._fumbles_lost

    @_int_property_decorator
    def combined_tackles(self):
        """
        Returns an ``int`` of the number of solo and assisted tackles the
        player made.
        """
        return self._combined_tackles

    @_int_property_decorator
    def solo_tackles(self):
        """
        Returns an ``int`` of the number of solo tackles the player made during
        the game.
        """
        return self._solo_tackles

    @_int_property_decorator
    def tackles_for_loss(self):
        """
        Returns an ``int`` of the number of times the player tackles an
        opponent for a loss on the play.
        """
        return self._tackles_for_loss

    @_int_property_decorator
    def quarterback_hits(self):
        """
        Returns an ``int`` of the number of times the player hit the
        quarterback.
        """
        return self._quarterback_hits

    @_float_property_decorator
    def average_kickoff_return_yards(self):
        """
        Returns a ``float`` of the average number of yards the player returned
        a kickoff for.
        """
        return self._average_kickoff_return_yards


class Boxscore:
    """
    Detailed information about the final statistics for a game.

    Stores all relevant information for a game such as the date, time,
    location, result, and more advanced metrics such as the number of yards
    from sacks, a team's passing completion, rushing touchdowns and much more.

    Parameters
    ----------
    uri : string
        The relative link to the boxscore HTML page, such as
        '201802040nwe'.
    """
    def __init__(self, uri):
        self._uri = uri
        self._date = None
        self._time = None
        self._stadium = None
        self._attendance = None
        self._duration = None
        self._away_name = None
        self._home_name = None
        self._winner = None
        self._winning_name = None
        self._winning_abbr = None
        self._losing_name = None
        self._losing_abbr = None
        self._summary = None
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
        self._away_times_sacked = None
        self._away_yards_lost_from_sacks = None
        self._away_net_pass_yards = None
        self._away_total_yards = None
        self._away_fumbles = None
        self._away_fumbles_lost = None
        self._away_turnovers = None
        self._away_penalties = None
        self._away_yards_from_penalties = None
        self._away_third_down_conversions = None
        self._away_third_down_attempts = None
        self._away_fourth_down_conversions = None
        self._away_fourth_down_attempts = None
        self._away_time_of_possession = None
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
        self._home_times_sacked = None
        self._home_yards_lost_from_sacks = None
        self._home_net_pass_yards = None
        self._home_total_yards = None
        self._home_fumbles = None
        self._home_fumbles_lost = None
        self._home_turnovers = None
        self._home_penalties = None
        self._home_yards_from_penalties = None
        self._home_third_down_conversions = None
        self._home_third_down_attempts = None
        self._home_fourth_down_conversions = None
        self._home_fourth_down_attempts = None
        self._home_time_of_possession = None

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
            '201802040nwe'.

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
        # For NFL, a 404 page doesn't actually raise a 404 error, so it needs
        # to be manually checked.
        if '404 error' in str(url_data):
            return None
        return pq(utils._remove_html_comment_tags(url_data))

    def _parse_game_date_and_location(self, boxscore):
        """
        Retrieve the game's date and location.

        The games' meta information, such as date, location, attendance, and
        duration, follow a complex parsing scheme that changes based on the
        layout of the page. The information should be able to be parsed and set
        regardless of the order and how much information is included. To do
        this, the meta information should be iterated through line-by-line and
        fields should be determined by the values that are found in each line.

        Parameters
        ----------
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.
        """
        scheme = BOXSCORE_SCHEME["game_info"]
        items = [i.text() for i in boxscore(scheme).items()]
        game_info = items[0].split('\n')
        attendance = None
        date = None
        duration = None
        stadium = None
        time = None
        date = game_info[0]
        for line in game_info:
            if 'Attendance' in line:
                attendance = line.replace('Attendance: ', '').replace(',', '')
            if 'Time of Game' in line:
                duration = line.replace('Time of Game: ', '')
            if 'Stadium' in line:
                stadium = line.replace('Stadium: ', '')
            if 'Start Time' in line:
                time = line.replace('Start Time: ', '')
        setattr(self, '_attendance', attendance)
        setattr(self, '_date', date)
        setattr(self, '_duration', duration)
        setattr(self, '_stadium', stadium)
        setattr(self, '_time', time)

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
        return pq(str(boxscore(scheme)).strip())

    def _parse_summary(self, boxscore):
        """
        Find the game summary including score in each quarter.

        The game summary provides further information on the points scored
        during each quarter, including the final score and any overtimes if
        applicable. The final output will be in a dictionary with two keys,
        'away' and 'home'. The value of each key will be a list for each
        respective team's score by order of the quarter, with the first element
        belonging to the first quarter, similar to the following:

        {
            'away': [0, 7, 3, 14],
            'home': [7, 7, 3, 0]
        }

        Parameters
        ----------
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML from the boxscore.

        Returns
        -------
        dict
            Returns a ``dictionary`` representing the score for each team in
            each quarter of the game.
        """
        team = ['away', 'home']
        summary = {'away': [], 'home': []}
        game_summary = boxscore(BOXSCORE_SCHEME['summary'])
        for ind, team_info in enumerate(game_summary('tbody tr').items()):
            # Only pull the first N-1 items as the last element is the final
            # score for each team which is already stored in an attribute, and
            # shouldn't be duplicated.
            for quarter in list(team_info('td[class="center"]').items())[:-1]:
                # The first element contains the logo and name of the teams,
                # but not any score information, and should be skipped.
                if quarter('div'):
                    continue
                try:
                    summary[team[ind]].append(int(quarter.text()))
                except ValueError:
                    summary[team[ind]].append(None)
        return summary

    def _find_boxscore_tables(self, boxscore):
        """
        Find all tables with boxscore information on the page.

        Iterate through all tables on the page and see if any of them are
        boxscore pages by checking if the ID matches the expected list. If so,
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
        valid_tables = ['player_offense', 'player_defense', 'returns',
                        'kicking']

        for table in boxscore('table').items():
            if table.attr['id'] in valid_tables:
                tables.append(table)
        return tables

    def _find_player_id(self, row):
        """
        Find the player's ID.

        Find the player's ID as embedded in the 'data-append-csv' attribute,
        such as 'BreeDr01' for Drew Brees.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object representing a single row in a boxscore table for
            a single player.

        Returns
        -------
        str
            Returns a ``string`` of the player's ID, such as 'BreeDr01'
            for Drew Brees.
        """
        return row('th').attr('data-append-csv')

    def _find_player_name(self, row):
        """
        Find the player's full name.

        Find the player's full name, such as 'Drew Brees'. The name is the
        text displayed for a link to the player's individual stats.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object representing a single row in a boxscore table for
            a single player.

        Returns
        -------
        str
            Returns a ``string`` of the player's full name, such as 'Drew
            Brees'.
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
        name = row('td[data-stat="team"]').text().upper()
        if name == self.home_abbreviation.upper():
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
            '201802040nwe'.
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
               short_field == 'stadium' or \
               short_field == 'attendance' or \
               short_field == 'duration':
                continue
            if short_field == 'away_name' or \
               short_field == 'home_name':
                value = self._parse_name(short_field, boxscore)
                setattr(self, field, value)
                continue
            if short_field == 'summary':
                value = self._parse_summary(boxscore)
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
        instantiate the class, such as '201802040nwe'.
        """
        for points in [self._away_points, self._home_points]:
            if points is None or points == '':
                return None
        fields_to_include = {
            'attendance': self.attendance,
            'away_first_downs': self.away_first_downs,
            'away_fourth_down_attempts': self.away_fourth_down_attempts,
            'away_fourth_down_conversions': self.away_fourth_down_conversions,
            'away_fumbles': self.away_fumbles,
            'away_fumbles_lost': self.away_fumbles_lost,
            'away_interceptions': self.away_interceptions,
            'away_net_pass_yards': self.away_net_pass_yards,
            'away_pass_attempts': self.away_pass_attempts,
            'away_pass_completions': self.away_pass_completions,
            'away_pass_touchdowns': self.away_pass_touchdowns,
            'away_pass_yards': self.away_pass_yards,
            'away_penalties': self.away_penalties,
            'away_points': self.away_points,
            'away_rush_attempts': self.away_rush_attempts,
            'away_rush_touchdowns': self.away_rush_touchdowns,
            'away_rush_yards': self.away_rush_yards,
            'away_third_down_attempts': self.away_third_down_attempts,
            'away_third_down_conversions': self.away_third_down_conversions,
            'away_time_of_possession': self.away_time_of_possession,
            'away_times_sacked': self.away_times_sacked,
            'away_total_yards': self.away_total_yards,
            'away_turnovers': self.away_turnovers,
            'away_yards_from_penalties': self.away_yards_from_penalties,
            'away_yards_lost_from_sacks': self.away_yards_lost_from_sacks,
            'date': self.date,
            'duration': self.duration,
            'home_first_downs': self.home_first_downs,
            'home_fourth_down_attempts': self.home_fourth_down_attempts,
            'home_fourth_down_conversions': self.home_fourth_down_conversions,
            'home_fumbles': self.home_fumbles,
            'home_fumbles_lost': self.home_fumbles_lost,
            'home_interceptions': self.home_interceptions,
            'home_net_pass_yards': self.home_net_pass_yards,
            'home_pass_attempts': self.home_pass_attempts,
            'home_pass_completions': self.home_pass_completions,
            'home_pass_touchdowns': self.home_pass_touchdowns,
            'home_pass_yards': self.home_pass_yards,
            'home_penalties': self.home_penalties,
            'home_points': self.home_points,
            'home_rush_attempts': self.home_rush_attempts,
            'home_rush_touchdowns': self.home_rush_touchdowns,
            'home_rush_yards': self.home_rush_yards,
            'home_third_down_attempts': self.home_third_down_attempts,
            'home_third_down_conversions': self.home_third_down_conversions,
            'home_time_of_possession': self.home_time_of_possession,
            'home_times_sacked': self.home_times_sacked,
            'home_total_yards': self.home_total_yards,
            'home_turnovers': self.home_turnovers,
            'home_yards_from_penalties': self.home_yards_from_penalties,
            'home_yards_lost_from_sacks': self.home_yards_lost_from_sacks,
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
    def away_abbreviation(self):
        """
        Returns a ``string`` of the away team's abbreviation, such as 'NWE'.
        """
        abbr = re.sub(r'.*/teams/', '', str(self._away_name))
        abbr = re.sub(r'/.*', '', abbr)
        return abbr

    @property
    def home_abbreviation(self):
        """
        Returns a ``string`` of the home team's abbreviation, such as 'KAN'.
        """
        abbr = re.sub(r'.*/teams/', '', str(self._home_name))
        abbr = re.sub(r'/.*', '', abbr)
        return abbr

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
        return self._time

    @property
    def stadium(self):
        """
        Returns a ``string`` of the name of the stadium where the game was
        played.
        """
        return self._stadium

    @int_property_decorator
    def attendance(self):
        """
        Returns an ``int`` of the game's listed attendance.
        """
        return self._attendance

    @property
    def duration(self):
        """
        Returns a ``string`` of the game's duration in the format 'H:MM'.
        """
        return self._duration

    @property
    def summary(self):
        """
        Returns a ``dictionary`` with two keys, 'away' and 'home'. The value of
        each key will be a list for each respective team's score by order of
        the quarter, with the first element belonging to the first quarter,
        similar to the following:

        {
            'away': [0, 7, 3, 14],
            'home': [7, 7, 3, 0]
        }
        """
        return self._summary

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
        Returns a ``string`` of the winning team's name, such as 'New England
        Patriots'.
        """
        if self.winner == HOME:
            return self._home_name.text()
        return self._away_name.text()

    @property
    def winning_abbr(self):
        """
        Returns a ``string`` of the winning team's abbreviation, such as 'NWE'
        for the New England Patriots.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._home_name)
        return utils._parse_abbreviation(self._away_name)

    @property
    def losing_name(self):
        """
        Returns a ``string`` of the losing team's name, such as 'Kansas City
        Chiefs'.
        """
        if self.winner == HOME:
            return self._away_name.text()
        return self._home_name.text()

    @property
    def losing_abbr(self):
        """
        Returns a ``string`` of the losing team's abbreviation, such as 'KAN'
        for the Kansas City Chiefs.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._away_name)
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

    @nfl_int_property_sub_index
    def away_rush_attempts(self):
        """
        Returns an ``int`` of the number of rushing plays the away team made.
        """
        return self._away_rush_attempts

    @nfl_int_property_sub_index
    def away_rush_yards(self):
        """
        Returns an ``int`` of the number of rushing yards the away team gained.
        """
        return self._away_rush_yards

    @nfl_int_property_sub_index
    def away_rush_touchdowns(self):
        """
        Returns an ``int`` of the number of rushing touchdowns the away team
        scored.
        """
        return self._away_rush_touchdowns

    @nfl_int_property_sub_index
    def away_pass_completions(self):
        """
        Returns an ``int`` of the number of completed passes the away team
        made.
        """
        return self._away_pass_completions

    @nfl_int_property_sub_index
    def away_pass_attempts(self):
        """
        Returns an ``int`` of the number of passes that were thrown by the away
        team.
        """
        return self._away_pass_attempts

    @nfl_int_property_sub_index
    def away_pass_yards(self):
        """
        Returns an ``int`` of the number of passing yards the away team gained.
        """
        return self._away_pass_yards

    @nfl_int_property_sub_index
    def away_pass_touchdowns(self):
        """
        Returns an ``int`` of the number of passing touchdowns the away team
        scored.
        """
        return self._away_pass_touchdowns

    @nfl_int_property_sub_index
    def away_interceptions(self):
        """
        Returns an ``int`` of the number of interceptions the away team threw.
        """
        return self._away_interceptions

    @nfl_int_property_sub_index
    def away_times_sacked(self):
        """
        Returns an ``int`` of the number of times the away team was sacked.
        """
        return self._away_times_sacked

    @nfl_int_property_sub_index
    def away_yards_lost_from_sacks(self):
        """
        Returns an ``int`` of the number of yards the away team lost as the
        result of a sack.
        """
        return self._away_yards_lost_from_sacks

    @int_property_decorator
    def away_net_pass_yards(self):
        """
        Returns an ``int`` of the net pass yards gained by the away team.
        """
        return self._away_net_pass_yards

    @int_property_decorator
    def away_total_yards(self):
        """
        Returns an ``int`` of the total number of yards the away team gained.
        """
        return self._away_total_yards

    @nfl_int_property_sub_index
    def away_fumbles(self):
        """
        Returns an ``int`` of the number of times the away team fumbled the
        ball.
        """
        return self._away_fumbles

    @nfl_int_property_sub_index
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

    @nfl_int_property_sub_index
    def away_penalties(self):
        """
        Returns an ``int`` of the number of penalties called on the away team.
        """
        return self._away_penalties

    @nfl_int_property_sub_index
    def away_yards_from_penalties(self):
        """
        Returns an ``int`` of the number of yards gifted as a result of
        penalties called on the away team.
        """
        return self._away_yards_from_penalties

    @nfl_int_property_sub_index
    def away_third_down_conversions(self):
        """
        Returns an ``int`` of the number of third down plays the away team
        successfully converted.
        """
        return self._away_third_down_conversions

    @nfl_int_property_sub_index
    def away_third_down_attempts(self):
        """
        Returns an ``int`` of the number of third down plays the away team
        attempted to convert.
        """
        return self._away_third_down_attempts

    @nfl_int_property_sub_index
    def away_fourth_down_conversions(self):
        """
        Returns an ``int`` of the number of fourth down plays the away team
        successfully converted.
        """
        return self._away_fourth_down_conversions

    @nfl_int_property_sub_index
    def away_fourth_down_attempts(self):
        """
        Returns an ``int`` of the number of fourth down plays the away team
        attempted to convert.
        """
        return self._away_fourth_down_attempts

    @property
    def away_time_of_possession(self):
        """
        Returns a ``string`` of the amount of time the home team had possession
        of the football in the format 'MM:SS'.
        """
        return self._away_time_of_possession

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

    @nfl_int_property_sub_index
    def home_rush_attempts(self):
        """
        Returns an ``int`` of the number of rushing plays the home team made.
        """
        return self._home_rush_attempts

    @nfl_int_property_sub_index
    def home_rush_yards(self):
        """
        Returns an ``int`` of the number of rushing yards the home team gained.
        """
        return self._home_rush_yards

    @nfl_int_property_sub_index
    def home_rush_touchdowns(self):
        """
        Returns an ``int`` of the number of rushing touchdowns the home team
        scored.
        """
        return self._home_rush_touchdowns

    @nfl_int_property_sub_index
    def home_pass_completions(self):
        """
        Returns an ``int`` of the number of completed passes the home team
        made.
        """
        return self._home_pass_completions

    @nfl_int_property_sub_index
    def home_pass_attempts(self):
        """
        Returns an ``int`` of the number of passes that were thrown by the home
        team.
        """
        return self._home_pass_attempts

    @nfl_int_property_sub_index
    def home_pass_yards(self):
        """
        Returns an ``int`` of the number of passing yards the home team gained.
        """
        return self._home_pass_yards

    @nfl_int_property_sub_index
    def home_pass_touchdowns(self):
        """
        Returns an ``int`` of the number of passing touchdowns the home team
        scored.
        """
        return self._home_pass_touchdowns

    @nfl_int_property_sub_index
    def home_interceptions(self):
        """
        Returns an ``int`` of the number of interceptions the home team threw.
        """
        return self._home_pass_touchdowns

    @nfl_int_property_sub_index
    def home_times_sacked(self):
        """
        Returns an ``int`` of the number of times the home team was sacked.
        """
        return self._home_times_sacked

    @nfl_int_property_sub_index
    def home_yards_lost_from_sacks(self):
        """
        Returns an ``int`` of the number of yards the home team lost as the
        result of a sack.
        """
        return self._home_yards_lost_from_sacks

    @int_property_decorator
    def home_net_pass_yards(self):
        """
        Returns an ``int`` of the net pass yards gained by the home team.
        """
        return self._home_net_pass_yards

    @int_property_decorator
    def home_total_yards(self):
        """
        Returns an ``int`` of the total number of yards the home team gained.
        """
        return self._home_total_yards

    @nfl_int_property_sub_index
    def home_fumbles(self):
        """
        Returns an ``int`` of the number of times the home team fumbled the
        ball.
        """
        return self._home_fumbles

    @nfl_int_property_sub_index
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

    @nfl_int_property_sub_index
    def home_penalties(self):
        """
        Returns an ``int`` of the number of penalties called on the home team.
        """
        return self._home_penalties

    @nfl_int_property_sub_index
    def home_yards_from_penalties(self):
        """
        Returns an ``int`` of the number of yards gifted as a result of
        penalties called on the home team.
        """
        return self._home_yards_from_penalties

    @nfl_int_property_sub_index
    def home_third_down_conversions(self):
        """
        Returns an ``int`` of the number of third down plays the home team
        successfully converted.
        """
        return self._home_third_down_conversions

    @nfl_int_property_sub_index
    def home_third_down_attempts(self):
        """
        Returns an ``int`` of the number of third down plays the home team
        attempted to convert.
        """
        return self._home_third_down_attempts

    @nfl_int_property_sub_index
    def home_fourth_down_conversions(self):
        """
        Returns an ``int`` of the number of fourth down plays the home team
        successfully converted.
        """
        return self._home_fourth_down_conversions

    @nfl_int_property_sub_index
    def home_fourth_down_attempts(self):
        """
        Returns an ``int`` of the number of fourth down plays the home team
        attempted to convert.
        """
        return self._home_fourth_down_conversions

    @property
    def home_time_of_possession(self):
        """
        Returns a ``string`` of the amount of time the home team had possession
        of the football in the format 'MM:SS'.
        """
        return self._home_time_of_possession


class Boxscores:
    """
    Search for NFL games taking place on a particular day.

    Retrieve a dictionary which contains a list of all games being played on a
    particular day. Output includes a link to the boxscore, and the names and
    abbreviations for both the home teams. If no games are played on a
    particular day, the list will be empty.

    Parameters
    ----------
    week : int
        The week number to pull games from.
    year : int
        The 4-digit year to pull games from.
    end_week : int (optional)
        Optionally specify an end week to iterate until. All boxscores starting
        from the week specified in the 'week' parameter up to and including the
        boxscores specified in the 'end_week' parameter will be pulled. If left
        empty, or if 'end_week' is prior to 'week', only the games from the day
        specified in the 'date' parameter will be saved.
    """
    def __init__(self, week, year, end_week=None):
        self._boxscores = {}

        self._find_games(week, year, end_week)

    @property
    def games(self):
        """
        Returns a ``dictionary`` object representing all of the games played on
        the requested day. Dictionary is in the following format::

            {'week' : [  # 'week' is the string week in format 'W-YYYY'
                {
                    'home_name': Name of the home team, such as 'Kansas City
                                 Chiefs' (`str`),
                    'home_abbr': Abbreviation for the home team, such as 'KAN'
                                 (`str`),
                    'away_name': Name of the away team, such as 'Houston
                                 Texans' (`str`),
                    'away_abbr': Abbreviation for the away team, such as 'HTX'
                                 (`str`),
                    'boxscore': String representing the boxscore URI, such as
                                'SLN/SLN201807280' (`str`),
                    'winning_name': Full name of the winning team, such as
                                    'Kansas City Chiefs' (`str`),
                    'winning_abbr': Abbreviation for the winning team, such as
                                    'KAN' (`str`),
                    'losing_name': Full name of the losing team, such as
                                   'Houston Texans' (`str`),
                    'losing_abbr': Abbreviation for the losing team, such as
                                   'HTX' (`str`),
                    'home_score': Integer score for the home team (`int`),
                    'away_score': Integer score for the away team (`int`)
                },
                { ... },
                ...
                ]
            }

        If no games were played on 'week', the list for ['week'] will be empty.
        """
        return self._boxscores

    def _create_url(self, week, year):
        """
        Build the URL based on the passed week number.

        In order to get the proper boxscore page, the URL needs to include the
        requested week number.

        Parameters
        ----------
        week : int
            The week number to pull games from.
        year : int
            The 4-digit year to pull games from.

        Returns
        -------
        string
            Returns a ``string`` of the boxscore URL including the requested
            date.
        """
        return BOXSCORES_URL % (year, week)

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
        uri = re.sub(r'.*/boxscores/', '', str(url))
        uri = re.sub(r'\.htm.*', '', uri).strip()
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
        abbr = re.sub(r'.*/teams/', '', str(abbr))
        abbr = re.sub(r'/.*', '', abbr)
        return abbr

    def _get_name(self, name):
        """
        Find a team's name and abbreviation.

        Given the team's HTML name tag, determine their name, and abbreviation.

        Parameters
        ----------
        name : PyQuery object
            A PyQuery object of a team's HTML name tag in the boxscore.

        Returns
        -------
        tuple
            Returns a tuple containing the name and abbreviation for a team.
            Tuple is in the following order: Team Name, Team Abbreviation.
        """
        team_name = name.text()
        abbr = self._parse_abbreviation(name)
        return team_name, abbr

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

    def _get_team_details(self, game):
        """
        Find the names and abbreviations for both teams in a game.

        Using the HTML contents in a boxscore, find the name and abbreviation
        for both teams.

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
            Score, Home Name, Home Abbreviation, Home Score.
        """
        links = [i for i in game('td a').items()]
        # The away team is the first link in the boxscore
        away = links[0]
        # The home team is the last (3rd) link in the boxscore
        home = links[-1]
        scores = re.findall(r'<td class="right">\d+</td>', str(game))
        away_score = None
        home_score = None
        # If the game hasn't started or hasn't been updated on sports-reference
        # yet, no score will be shown and therefore can't be parsed.
        if len(scores) == 2:
            away_score = self._get_score(scores[0])
            home_score = self._get_score(scores[1])
        away_name, away_abbr = self._get_name(away)
        home_name, home_abbr = self._get_name(home)
        return (away_name, away_abbr, away_score, home_name, home_abbr,
                home_score)

    def _get_team_results(self, team_result_html):
        """
        Extract the winning or losing team's name and abbreviation.

        Depending on which team's data field is passed (either the winner or
        loser), return the name and abbreviation of that team to denote which
        team won and which lost the game.

        Parameters
        ----------
        team_result_html : PyQuery object
            A PyQuery object representing either the winning or losing team's
            data field within the boxscore.

        Returns
        -------
        tuple
            Returns a tuple of the team's name followed by the abbreviation.
        """
        link = [i for i in team_result_html('td a').items()]
        # If there are no links, the boxscore is likely misformed and can't be
        # parsed. In this case, the boxscore should be skipped.
        if len(link) < 1:
            return None
        name, abbreviation = self._get_name(link[0])
        return name, abbreviation

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
            the name and abbreviations for both the home and away teams, and a
            link to the game's boxscore.
        """
        all_boxscores = []

        for game in games:
            details = self._get_team_details(game)
            away_name, away_abbr, away_score, home_name, home_abbr, \
                home_score = details
            boxscore_url = game('td[class="right gamelink"] a')
            boxscore_uri = self._get_boxscore_uri(boxscore_url)
            losers = [l for l in game('tr[class="loser"]').items()]
            winner = self._get_team_results(game('tr[class="winner"]'))
            loser = self._get_team_results(game('tr[class="loser"]'))
            # Occurs when the boxscore format is invalid and the game should be
            # skipped to avoid conflicts populating the game information.
            if (len(losers) != 2 and loser and not winner) or \
               (len(losers) != 2 and winner and not loser):
                continue
            # Occurs when information couldn't be parsed from the boxscore or
            # the game hasn't occurred yet. In this case, the winner should be
            # None to avoid conflicts.
            if not winner or len(losers) == 2:
                winning_name = None
                winning_abbreviation = None
            else:
                winning_name, winning_abbreviation = winner
            # Occurs when information couldn't be parsed from the boxscore or
            # the game hasn't occurred yet. In this case, the winner should be
            # None to avoid conflicts.
            if not loser or len(losers) == 2:
                losing_name = None
                losing_abbreviation = None
            else:
                losing_name, losing_abbreviation = loser
            game_info = {
                'boxscore': boxscore_uri,
                'away_name': away_name,
                'away_abbr': away_abbr,
                'away_score': away_score,
                'home_name': home_name,
                'home_abbr': home_abbr,
                'home_score': home_score,
                'winning_name': winning_name,
                'winning_abbr': winning_abbreviation,
                'losing_name': losing_name,
                'losing_abbr': losing_abbreviation
            }
            all_boxscores.append(game_info)
        return all_boxscores

    def _find_games(self, week, year, end_week):
        """
        Retrieve all major games played for a given week.

        Builds a URL based on the requested date and downloads the HTML
        contents before parsing any and all games played during that week. Any
        games that are found are added to the boxscores dictionary with
        high-level game information such as the home and away team names and a
        link to the boxscore page.

        Parameters
        ----------
        week : int
            The week number to pull games from.
        year : int
            The 4-digit year to pull games from.
        end_week : int (optional)
            Optionally specify an end week to iterate until. All boxscores
            starting from the week specified in the 'week' parameter up to and
            including the boxscores specified in the 'end_week' parameter will
            be pulled. If left empty, or if 'end_week' is prior to 'week', only
            the games from the day specified in the 'date' parameter will be
            saved.
        """
        if not end_week or week > end_week:
            end_week = week
        while week <= end_week:
            url = self._create_url(week, year)
            page = self._get_requested_page(url)
            games = page('table[class="teams"]').items()
            boxscores = self._extract_game_info(games)
            timestamp = '%s-%s' % (week, year)
            self._boxscores[timestamp] = boxscores
            week += 1
