import pandas as pd
import re
from datetime import timedelta
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from ..constants import AWAY, HOME
from ..decorators import float_property_decorator, int_property_decorator
from .constants import (BOXSCORE_ELEMENT_INDEX,
                        BOXSCORE_SCHEME,
                        BOXSCORE_URL,
                        BOXSCORES_URL)
from .player import AbstractPlayer, _int_property_decorator


class BoxscorePlayer(AbstractPlayer):
    """
    Get player stats for an individual game.

    Given a player ID, such as 'carsen-edwards-1' for Carsen Edwards, their
    full name, and all associated stats from the Boxscore page in HTML format,
    parse the HTML and extract only the relevant stats for the specified player
    and assign them to readable properties.

    This class inherits the ``AbstractPlayer`` class. As a result, all
    properties associated with ``AbstractPlayer`` can also be read directly
    from this class.

    As this class is instantiated from within the Boxscore class, it should not
    be called directly and should instead be queried using the appropriate
    players properties from the Boxscore class.

    Parameters
    ----------
    player_id : string
        A player's ID accorsing to sports-reference.com, such as
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
        information will appear in one single string concatenated together.
    """
    def __init__(self, player_id, player_name, player_data):
        self._index = 0
        self._player_id = player_id
        self._defensive_rating = None
        self._offensive_rating = None
        AbstractPlayer.__init__(self, player_id, player_name, player_data)

    @property
    def dataframe(self):
        """
        Returns a ``pandas DataFrame`` containing all other relevant class
        properties and values for the specified game.
        """
        fields_to_include = {
            'assist_percentage': self.assist_percentage,
            'assists': self.assists,
            'block_percentage': self.block_percentage,
            'blocks': self.blocks,
            'defensive_rating': self.defensive_rating,
            'defensive_rebound_percentage': self.defensive_rebound_percentage,
            'defensive_rebounds': self.defensive_rebounds,
            'effective_field_goal_percentage':
            self.effective_field_goal_percentage,
            'field_goal_attempts': self.field_goal_attempts,
            'field_goal_percentage': self.field_goal_percentage,
            'field_goals': self.field_goals,
            'free_throw_attempt_rate': self.free_throw_attempt_rate,
            'free_throw_attempts': self.free_throw_attempts,
            'free_throw_percentage': self.free_throw_percentage,
            'free_throws': self.free_throws,
            'minutes_played': self.minutes_played,
            'offensive_rating': self.offensive_rating,
            'offensive_rebound_percentage': self.offensive_rebound_percentage,
            'offensive_rebounds': self.offensive_rebounds,
            'personal_fouls': self.personal_fouls,
            'points': self.points,
            'steal_percentage': self.steal_percentage,
            'steals': self.steals,
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
            'usage_percentage': self.usage_percentage
        }
        return pd.DataFrame([fields_to_include], index=[self._player_id])

    @_int_property_decorator
    def offensive_rating(self):
        """
        Returns an ``int`` of the player's offensive rating as measured by the
        points produced per 100 possessions.
        """
        return self._offensive_rating

    @_int_property_decorator
    def defensive_rating(self):
        """
        Returns an ``int`` of the player's defensive rating as measured by the
        points allowed per 100 possesions.
        """
        return self._defensive_rating


class Boxscore:
    """
    Detailed information about the final statistics for a game.

    Stores all relevant metrics for a game such as the date, time, location,
    result, and more advanced metrics such as the effective field goal rate,
    the true shooting percentage, the game's pace, and much more.

    Parameters
    ----------
    uri : string
        The relative link to the boxscore HTML page, such as
        '2017-11-10-21-kansas'.
    """
    def __init__(self, uri):
        self._uri = uri
        self._date = None
        self._location = None
        self._home_name = None
        self._away_name = None
        self._winner = None
        self._winning_name = None
        self._winning_abbr = None
        self._losing_name = None
        self._losing_abbr = None
        self._pace = None
        self._away_ranking = None
        self._away_record = None
        self._away_minutes_played = None
        self._away_field_goals = None
        self._away_field_goal_attempts = None
        self._away_field_goal_percentage = None
        self._away_two_point_field_goals = None
        self._away_two_point_field_goal_attempts = None
        self._away_two_point_field_goal_percentage = None
        self._away_three_point_field_goals = None
        self._away_three_point_field_goal_attempts = None
        self._away_three_point_field_goal_percentage = None
        self._away_free_throws = None
        self._away_free_throw_attempts = None
        self._away_free_throw_percentage = None
        self._away_offensive_rebounds = None
        self._away_defensive_rebounds = None
        self._away_total_rebounds = None
        self._away_assists = None
        self._away_steals = None
        self._away_blocks = None
        self._away_turnovers = None
        self._away_personal_fouls = None
        self._away_points = None
        self._away_true_shooting_percentage = None
        self._away_effective_field_goal_percentage = None
        self._away_three_point_attempt_rate = None
        self._away_free_throw_attempt_rate = None
        self._away_offensive_rebound_percentage = None
        self._away_defensive_rebound_percentage = None
        self._away_total_rebound_percentage = None
        self._away_assist_percentage = None
        self._away_steal_percentage = None
        self._away_block_percentage = None
        self._away_turnover_percentage = None
        self._away_offensive_rating = None
        self._away_defensive_rating = None
        self._home_ranking = None
        self._home_record = None
        self._home_minutes_played = None
        self._home_field_goals = None
        self._home_field_goal_attempts = None
        self._home_field_goal_percentage = None
        self._home_two_point_field_goals = None
        self._home_two_point_field_goal_attempts = None
        self._home_two_point_field_goal_percentage = None
        self._home_three_point_field_goals = None
        self._home_three_point_field_goal_attempts = None
        self._home_three_point_field_goal_percentage = None
        self._home_free_throws = None
        self._home_free_throw_attempts = None
        self._home_free_throw_percentage = None
        self._home_offensive_rebounds = None
        self._home_defensive_rebounds = None
        self._home_total_rebounds = None
        self._home_assists = None
        self._home_steals = None
        self._home_blocks = None
        self._home_turnovers = None
        self._home_personal_fouls = None
        self._home_points = None
        self._home_true_shooting_percentage = None
        self._home_effective_field_goal_percentage = None
        self._home_three_point_attempt_rate = None
        self._home_free_throw_attempt_rate = None
        self._home_offensive_rebound_percentage = None
        self._home_defensive_rebound_percentage = None
        self._home_total_rebound_percentage = None
        self._home_assist_percentage = None
        self._home_steal_percentage = None
        self._home_block_percentage = None
        self._home_turnover_percentage = None
        self._home_offensive_rating = None
        self._home_defensive_rating = None

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
            '2017-11-10-21-kansas'.

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

    def _parse_game_date_and_location(self, field, boxscore):
        """
        Retrieve the game's date and location.

        The date and location of the game follow a more complicated parsing
        scheme and should be handled differently from other tags. Both fields
        are separated by a newline character ('\n') with the first line being
        the date and the second being the location.

        Parameters
        ----------
        field : string
            The name of the attribute to parse
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.

        Returns
        -------
        string
            Depending on the requested field, returns a text representation of
            either the date or location of the game.
        """
        scheme = BOXSCORE_SCHEME[field]
        items = [i.text() for i in boxscore(scheme).items()]
        game_info = items[0].split('\n')
        if len(game_info) < 3 and field == 'location':
            return None
        return game_info[BOXSCORE_ELEMENT_INDEX[field]]

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
        name = boxscore(scheme)
        if 'cbb/schools' not in str(name):
            name = re.sub(r'.*name">', '', str(name))
            name = re.sub(r'<.*', '', str(name))
        return name

    def _parse_ranking(self, field, boxscore):
        """
        Parse each team's rank if applicable.

        Retrieve the team's rank according to the rankings published each week.
        The ranking for the week is only located in the scores section at
        the top of the page and not in the actual boxscore information. The
        rank is after the team name inside a parenthesis with a special
        'pollrank' attribute. If this is not in the team's boxscore
        information, the team is assumed to not have a rank and will return a
        value of None.

        Parameters
        ----------
        field : string
            The name of the attribute to parse.
        boxscore : PyQuery object
            A PyQuery obejct containing all of the HTML data from the boxscore.

        Returns
        -------
        int
            An int representing the team's ranking or None if the team is not
            ranked.
        """
        ranking = None
        index = BOXSCORE_ELEMENT_INDEX[field]
        teams_boxscore = boxscore(BOXSCORE_SCHEME[field])
        # Occasionally, the list of boxscores for the day won't be saved on the
        # page. If that's the case, return the default ranking.
        if str(teams_boxscore) == '':
            return ranking
        team = pq(teams_boxscore[index])
        if 'pollrank' in str(team):
            rank_str = re.findall(r'\(\d+\)', str(team))
            if len(rank_str) == 1:
                ranking = int(rank_str[0].replace('(', '').replace(')', ''))
        return ranking

    def _parse_record(self, field, boxscore, index):
        """
        Parse each team's record.

        Find the record for both the home and away teams which are listed above
        the basic boxscore stats tables. Depending on whether or not the
        advanced stats table is included on the page (generally only for more
        recent matchups), a blank header is added to the list which should be
        removed. With all blank headers removed, the home and away team records
        can be easily parsed by specifying which team is desired.

        Parameters
        ----------
        field : string
            The name of the attribute to parse.
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.
        index : int
            An int of the index to pull the record from, as specified in the
            BOXSCORE_ELEMENT_INDEX dictionary.

        Returns
        -------
        string
            A string of the team's record in the format 'Team Name (W-L)'.
        """
        records = boxscore(BOXSCORE_SCHEME[field]).items()
        records = [x.text() for x in records if x.text() != '']
        return records[index]

    def _find_boxscore_tables(self, boxscore):
        """
        Find all tables with boxscore information on the page.

        Iterate through all tables on the page and see if any of them are
        boxscore pages by checking if the ID is prefixed with 'box-score-'. If
        so, add it to a list and return the final list at the end.

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

        for table in boxscore('table').items():
            try:
                if 'box-score-' in table.attr['id']:
                    tables.append(table)
            except (KeyError, TypeError):
                continue
        return tables

    def _find_player_id(self, row):
        """
        Find the player's ID.

        Find the player's ID as embedded in the 'data-append-csv' attibute,
        such as 'carsen-edwards-1' for Carsen Edwards.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object representing a single row in a boxscore table for
            a single player.

        Returns
        -------
        str
            Returns a ``string`` of the player's ID, such as 'carsen-edwards-1'
            for Carsen Edwards.
        """
        return row('th').attr('data-append-csv')

    def _find_player_name(self, row):
        """
        Find the player's full name.

        Find the player's full name, such as 'Carsen Edwards'. The name is the
        text displayed for a link to the player's individual stats page.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object representing a single row in a boxscore table for
            a single player.

        Returns
        -------
        str
            Returns a ``string`` of the player's full name, such as 'Carsen
            Edwards'.
        """
        return row('a').text()

    def _extract_player_stats(self, table, player_dict, home_or_away):
        """
        Combine all player stats into a single object.

        Since each player generally has a couple of rows worth of stats (one
        for basic stats and another for advanced stats) on the boxscore page,
        both rows should be combined into a single string object to easily
        query all fields from a single object instead of determining which row
        to pull metrics from.

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
        home_or_away : string constant
            A string constant indicating whether the player plays for the home
            or away team.

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
        table_count = 0

        tables = self._find_boxscore_tables(boxscore)
        for table in tables:
            home_or_away = HOME
            # There are two tables per team with the first two tables belonging
            # to the home team.
            if table_count < 2:
                home_or_away = AWAY
            player_dict = self._extract_player_stats(table,
                                                     player_dict,
                                                     home_or_away)
            table_count += 1
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
            '2017-11-10-21-kansas'.
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
               short_field == 'uri':
                continue
            if short_field == 'location' or \
               short_field == 'date':
                value = self._parse_game_date_and_location(short_field,
                                                           boxscore)
                setattr(self, field, value)
                continue
            if short_field == 'away_name' or \
               short_field == 'home_name':
                value = self._parse_name(short_field, boxscore)
                setattr(self, field, value)
                continue
            if short_field == 'away_ranking' or \
               short_field == 'home_ranking':
                value = self._parse_ranking(short_field, boxscore)
                setattr(self, field, value)
                continue
            index = 0
            if short_field in BOXSCORE_ELEMENT_INDEX.keys():
                index = BOXSCORE_ELEMENT_INDEX[short_field]
            if short_field == 'away_record' or \
               short_field == 'home_record':
                value = self._parse_record(short_field, boxscore, index)
                setattr(self, field, value)
                continue
            value = utils._parse_field(BOXSCORE_SCHEME,
                                       boxscore,
                                       short_field,
                                       index)
            setattr(self, field, value)
        self._away_players, self._home_players = self._find_players(boxscore)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the string URI that is used to
        instantiate the class, such as '2017-11-10-21-kansas'.
        """
        if self._away_points is None and self._home_points is None:
            return None
        fields_to_include = {
            'away_assist_percentage': self.away_assist_percentage,
            'away_assists': self.away_assists,
            'away_block_percentage': self.away_block_percentage,
            'away_blocks': self.away_blocks,
            'away_defensive_rating': self.away_defensive_rating,
            'away_defensive_rebound_percentage':
            self.away_defensive_rebound_percentage,
            'away_defensive_rebounds': self.away_defensive_rebounds,
            'away_effective_field_goal_percentage':
            self.away_effective_field_goal_percentage,
            'away_field_goal_attempts': self.away_field_goal_attempts,
            'away_field_goal_percentage': self.away_field_goal_percentage,
            'away_field_goals': self.away_field_goals,
            'away_free_throw_attempt_rate': self.away_free_throw_attempt_rate,
            'away_free_throw_attempts': self.away_free_throw_attempts,
            'away_free_throw_percentage': self.away_free_throw_percentage,
            'away_free_throws': self.away_free_throws,
            'away_losses': self.away_losses,
            'away_minutes_played': self.away_minutes_played,
            'away_offensive_rating': self.away_offensive_rating,
            'away_offensive_rebound_percentage':
            self.away_offensive_rebound_percentage,
            'away_offensive_rebounds': self.away_offensive_rebounds,
            'away_personal_fouls': self.away_personal_fouls,
            'away_points': self.away_points,
            'away_ranking': self.away_ranking,
            'away_steal_percentage': self.away_steal_percentage,
            'away_steals': self.away_steals,
            'away_three_point_attempt_rate':
            self.away_three_point_attempt_rate,
            'away_three_point_field_goal_attempts':
            self.away_three_point_field_goal_attempts,
            'away_three_point_field_goal_percentage':
            self.away_three_point_field_goal_percentage,
            'away_three_point_field_goals': self.away_three_point_field_goals,
            'away_total_rebound_percentage':
            self.away_total_rebound_percentage,
            'away_total_rebounds': self.away_total_rebounds,
            'away_true_shooting_percentage':
            self.away_true_shooting_percentage,
            'away_turnover_percentage': self.away_turnover_percentage,
            'away_turnovers': self.away_turnovers,
            'away_two_point_field_goal_attempts':
            self.away_two_point_field_goal_attempts,
            'away_two_point_field_goal_percentage':
            self.away_two_point_field_goal_percentage,
            'away_two_point_field_goals': self.away_two_point_field_goals,
            'away_win_percentage': self.away_win_percentage,
            'away_wins': self.away_wins,
            'date': self.date,
            'home_assist_percentage': self.home_assist_percentage,
            'home_assists': self.home_assists,
            'home_block_percentage': self.home_block_percentage,
            'home_blocks': self.home_blocks,
            'home_defensive_rating': self.home_defensive_rating,
            'home_defensive_rebound_percentage':
            self.home_defensive_rebound_percentage,
            'home_defensive_rebounds': self.home_defensive_rebounds,
            'home_effective_field_goal_percentage':
            self.home_effective_field_goal_percentage,
            'home_field_goal_attempts': self.home_field_goal_attempts,
            'home_field_goal_percentage': self.home_field_goal_percentage,
            'home_field_goals': self.home_field_goals,
            'home_free_throw_attempt_rate': self.home_free_throw_attempt_rate,
            'home_free_throw_attempts': self.home_free_throw_attempts,
            'home_free_throw_percentage': self.home_free_throw_percentage,
            'home_free_throws': self.home_free_throws,
            'home_losses': self.home_losses,
            'home_minutes_played': self.home_minutes_played,
            'home_offensive_rating': self.home_offensive_rating,
            'home_offensive_rebound_percentage':
            self.home_offensive_rebound_percentage,
            'home_offensive_rebounds': self.home_offensive_rebounds,
            'home_personal_fouls': self.home_personal_fouls,
            'home_points': self.home_points,
            'home_ranking': self.home_ranking,
            'home_steal_percentage': self.home_steal_percentage,
            'home_steals': self.home_steals,
            'home_three_point_attempt_rate':
            self.home_three_point_attempt_rate,
            'home_three_point_field_goal_attempts':
            self.home_three_point_field_goal_attempts,
            'home_three_point_field_goal_percentage':
            self.home_three_point_field_goal_percentage,
            'home_three_point_field_goals': self.home_three_point_field_goals,
            'home_total_rebound_percentage':
            self.home_total_rebound_percentage,
            'home_total_rebounds': self.home_total_rebounds,
            'home_true_shooting_percentage':
            self.home_true_shooting_percentage,
            'home_turnover_percentage': self.home_turnover_percentage,
            'home_turnovers': self.home_turnovers,
            'home_two_point_field_goal_attempts':
            self.home_two_point_field_goal_attempts,
            'home_two_point_field_goal_percentage':
            self.home_two_point_field_goal_percentage,
            'home_two_point_field_goals': self.home_two_point_field_goals,
            'home_win_percentage': self.home_win_percentage,
            'home_wins': self.home_wins,
            'location': self.location,
            'losing_abbr': self.losing_abbr,
            'losing_name': self.losing_name,
            'pace': self.pace,
            'winner': self.winner,
            'winning_abbr': self.winning_abbr,
            'winning_name': self.winning_name
        }
        return pd.DataFrame([fields_to_include], index=[self._uri])

    @property
    def date(self):
        """
        Returns a ``string`` of the date the game took place.
        """
        return self._date

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
    def location(self):
        """
        Returns a ``string`` of the name of the venue where the game was
        played.
        """
        return self._location

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
        Returns a ``string`` of the winning team's name, such as 'Purdue
        Boilermakers'.
        """
        if self.winner == HOME:
            if 'cbb/schools' not in str(self._home_name):
                return str(self._home_name)
            return self._home_name.text()
        if 'cbb/schools' not in str(self._away_name):
            return str(self._away_name)
        return self._away_name.text()

    @property
    def winning_abbr(self):
        """
        Returns a ``string`` of the winning team's abbreviation, such as
        'PURDUE' for the Purdue Boilermakers.
        """
        if self.winner == HOME:
            if 'cbb/schools' not in str(self._home_name):
                return str(self._home_name)
            return utils._parse_abbreviation(self._home_name)
        if 'cbb/schools' not in str(self._away_name):
            return str(self._away_name)
        return utils._parse_abbreviation(self._away_name)

    @property
    def losing_name(self):
        """
        Returns a ``string`` of the losing team's name, such as 'Indiana'
        Hoosiers'.
        """
        if self.winner == HOME:
            if 'cbb/schools' not in str(self._away_name):
                return str(self._away_name)
            return self._away_name.text()
        if 'cbb/schools' not in str(self._home_name):
            return str(self._home_name)
        return self._home_name.text()

    @property
    def losing_abbr(self):
        """
        Returns a ``string`` of the losing team's abbreviation, such as
        'INDIANA' for the Indiana Hoosiers.
        """
        if self.winner == HOME:
            if 'cbb/schools' not in str(self._away_name):
                return str(self._away_name)
            return utils._parse_abbreviation(self._away_name)
        if 'cbb/schools' not in str(self._home_name):
            return str(self._home_name)
        return utils._parse_abbreviation(self._home_name)

    @float_property_decorator
    def pace(self):
        """
        Returns a ``float`` of the game's overall pace, measured by the number
        of possessions per 40 minutes.
        """
        return self._pace

    @int_property_decorator
    def away_ranking(self):
        """
        Returns an ``int`` of the away team's ranking during the week, or
        ``None`` if the team wasn't ranked.
        """
        return self._away_ranking

    @float_property_decorator
    def away_win_percentage(self):
        """
        Returns a ``float`` of the percentage of games the away team has won
        after the conclusion of the game. Percentage ranges from 0-1.
        """
        try:
            result = float(self.away_wins) / \
                     float(self.away_wins + self.away_losses)
            return round(result, 3)
        except ZeroDivisionError:
            return 0.0

    @int_property_decorator
    def away_wins(self):
        """
        Returns an ``int`` of the number of games the team has won after the
        conclusion of the game.
        """
        try:
            wins, losses = re.findall(r'\d+', self._away_record)
            return wins
        except (ValueError, TypeError):
            return 0

    @int_property_decorator
    def away_losses(self):
        """
        Returns an ``int`` of the number of games the team has lost after the
        conclusion of the game.
        """
        try:
            wins, losses = re.findall(r'\d+', self._away_record)
            return losses
        except (ValueError, TypeError):
            return 0

    @int_property_decorator
    def away_minutes_played(self):
        """
        Returns an ``int`` of the total number of minutes the team played
        during the game.
        """
        return self._away_minutes_played

    @int_property_decorator
    def away_field_goals(self):
        """
        Returns an ``int`` of the total number of field goals made by the away
        team.
        """
        return self._away_field_goals

    @int_property_decorator
    def away_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of field goal attempts by the
        away team.
        """
        return self._away_field_goal_attempts

    @float_property_decorator
    def away_field_goal_percentage(self):
        """
        Returns a ``float`` of the number of field goals made divided by the
        total number of field goal attempts by the away team. Percentage ranges
        from 0-1.
        """
        return self._away_field_goal_percentage

    @int_property_decorator
    def away_three_point_field_goals(self):
        """
        Returns an ``int`` of the total number of three point field goals made
        by the away team.
        """
        return self._away_three_point_field_goals

    @int_property_decorator
    def away_three_point_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of three point field goal
        attempts by the away team.
        """
        return self._away_three_point_field_goal_attempts

    @float_property_decorator
    def away_three_point_field_goal_percentage(self):
        """
        Returns a ``float`` of the number of three point field goals made
        divided by the number of three point field goal attempts by the away
        team. Percentage ranges from 0-1.
        """
        return self._away_three_point_field_goal_percentage

    @int_property_decorator
    def away_two_point_field_goals(self):
        """
        Returns an ``int`` of the total number of two point field goals made
        by the away team.
        """
        return self._away_two_point_field_goals

    @int_property_decorator
    def away_two_point_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of two point field goal attempts
        by the away team.
        """
        return self._away_two_point_field_goal_attempts

    @float_property_decorator
    def away_two_point_field_goal_percentage(self):
        """
        Returns a ``float`` of the number of two point field goals made divided
        by the number of two point field goal attempts by the away team.
        Percentage ranges from 0-1.
        """
        return self._away_two_point_field_goal_percentage

    @int_property_decorator
    def away_free_throws(self):
        """
        Returns an ``int`` of the total number of free throws made by the away
        team.
        """
        return self._away_free_throws

    @int_property_decorator
    def away_free_throw_attempts(self):
        """
        Returns an ``int`` of the total number of free throw attempts by the
        away team.
        """
        return self._away_free_throw_attempts

    @float_property_decorator
    def away_free_throw_percentage(self):
        """
        Returns a ``float`` of the number of free throws made divided by the
        number of free throw attempts  by the away team.
        """
        return self._away_free_throw_percentage

    @int_property_decorator
    def away_offensive_rebounds(self):
        """
        Returns an ``int`` of the total number of offensive rebounds by the
        away team.
        """
        return self._away_offensive_rebounds

    @int_property_decorator
    def away_defensive_rebounds(self):
        """
        Returns an ``int`` of the total number of defensive rebounds by the
        away team.
        """
        return self._away_defensive_rebounds

    @int_property_decorator
    def away_total_rebounds(self):
        """
        Returns an ``int`` of the total number of rebounds by the away team.
        """
        return self._away_total_rebounds

    @int_property_decorator
    def away_assists(self):
        """
        Returns an ``int`` of the total number of assists by the away team.
        """
        return self._away_assists

    @int_property_decorator
    def away_steals(self):
        """
        Returns an ``int`` of the total number of steals by the away team.
        """
        return self._away_steals

    @int_property_decorator
    def away_blocks(self):
        """
        Returns an ``int`` of the total number of blocks by the away team.
        """
        return self._away_blocks

    @int_property_decorator
    def away_turnovers(self):
        """
        Returns an ``int`` of the total number of turnovers by the away team.
        """
        return self._away_turnovers

    @int_property_decorator
    def away_personal_fouls(self):
        """
        Returns an ``int`` of the total number of personal fouls by the away
        team.
        """
        return self._away_personal_fouls

    @int_property_decorator
    def away_points(self):
        """
        Returns an ``int`` of the number of points the away team scored.
        """
        return self._away_points

    @float_property_decorator
    def away_true_shooting_percentage(self):
        """
        Returns a ``float`` of the away team's true shooting percentage which
        considers free throws, 2-point field goals, and 3-point field goals.
        Percentage ranges from 0-1.
        """
        return self._away_true_shooting_percentage

    @float_property_decorator
    def away_effective_field_goal_percentage(self):
        """
        Returns a ``float`` of the away team's field goal percentage while
        giving extra weight to 3-point field goals. Percentage ranges from 0-1.
        """
        return self._away_effective_field_goal_percentage

    @float_property_decorator
    def away_three_point_attempt_rate(self):
        """
        Returns a ``float`` of the percentage of field goal attempts from
        3-point range by the away team. Percentage ranges from 0-1.
        """
        return self._away_three_point_attempt_rate

    @float_property_decorator
    def away_free_throw_attempt_rate(self):
        """
        Returns a ``float`` of the average number of free throw attempts per
        field goal attempt by the away team.
        """
        return self._away_free_throw_attempt_rate

    @float_property_decorator
    def away_offensive_rebound_percentage(self):
        """
        Returns a ``float`` of the percentage of available offensive rebounds
        the away team grabbed. Percentage ranges from 0-100.
        """
        return self._away_offensive_rebound_percentage

    @float_property_decorator
    def away_defensive_rebound_percentage(self):
        """
        Returns a ``float`` of the percentage of available defensive rebounds
        the away team grabbed. Percentage ranges from 0-100.
        """
        return self._away_defensive_rebound_percentage

    @float_property_decorator
    def away_total_rebound_percentage(self):
        """
        Returns a ``float`` of the percentage of available rebounds the away
        team grabbed. Percentage ranges from 0-100.
        """
        return self._away_total_rebound_percentage

    @float_property_decorator
    def away_assist_percentage(self):
        """
        Returns a ``float`` of the percentage of the away team's field goals
        that were assisted. Percentage ranges from 0-100.
        """
        return self._away_assist_percentage

    @float_property_decorator
    def away_steal_percentage(self):
        """
        Returns a ``float`` of the percentage of possessions that ended in a
        steal by the away team. Percentage ranges from 0-100.
        """
        return self._away_steal_percentage

    @float_property_decorator
    def away_block_percentage(self):
        """
        Returns a ``float`` of the percentage of 2-point field goals that were
        blocked by the away team. Percentage ranges from 0-100.
        """
        return self._away_block_percentage

    @float_property_decorator
    def away_turnover_percentage(self):
        """
        Returns a ``float`` of the number of times the away team turned the
        ball over per 100 possessions.
        """
        return self._away_turnover_percentage

    @float_property_decorator
    def away_offensive_rating(self):
        """
        Returns a ``float`` of the average number of points scored per 100
        possessions by the away team.
        """
        return self._away_offensive_rating

    @float_property_decorator
    def away_defensive_rating(self):
        """
        Returns a ``float`` of the average number of points scored per 100
        possessions by the away team.
        """
        return self._away_defensive_rating

    @int_property_decorator
    def home_ranking(self):
        """
        Returns an ``int`` of the home team's ranking during the week, or
        ``None`` if they were not ranked.
        """
        return self._home_ranking

    @float_property_decorator
    def home_win_percentage(self):
        """
        Returns a ``float`` of the percentage of games the home team has won
        after the conclusion of the game. Percentage ranges from 0-1.
        """
        try:
            result = float(self.home_wins) / \
                     float(self.home_wins + self.home_losses)
            return round(result, 3)
        except ZeroDivisionError:
            return 0.0

    @int_property_decorator
    def home_wins(self):
        """
        Returns an ``int`` of the number of games the home team won after the
        conclusion of the game.
        """
        try:
            wins, losses = re.findall(r'\d+', self._home_record)
            return wins
        except (ValueError, TypeError):
            return 0

    @int_property_decorator
    def home_losses(self):
        """
        Returns an ``int`` of the number of games the home team lost after the
        conclusion of the game.
        """
        try:
            wins, losses = re.findall(r'\d+', self._home_record)
            return losses
        except (ValueError, TypeError):
            return 0

    @int_property_decorator
    def home_minutes_played(self):
        """
        Returns an ``int`` of the total number of minutes the team played
        during the game.
        """
        return self._home_minutes_played

    @int_property_decorator
    def home_field_goals(self):
        """
        Returns an ``int`` of the total number of field goals made by the home
        team.
        """
        return self._home_field_goals

    @int_property_decorator
    def home_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of field goal attempts by the
        home team.
        """
        return self._home_field_goal_attempts

    @float_property_decorator
    def home_field_goal_percentage(self):
        """
        Returns a ``float`` of the number of field goals made divided by the
        total number of field goal attempts by the home team. Percentage ranges
        from 0-1.
        """
        return self._home_field_goal_percentage

    @int_property_decorator
    def home_three_point_field_goals(self):
        """
        Returns an ``int`` of the total number of three point field goals made
        by the home team.
        """
        return self._home_three_point_field_goals

    @int_property_decorator
    def home_three_point_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of three point field goal
        attempts by the home team.
        """
        return self._home_three_point_field_goal_attempts

    @float_property_decorator
    def home_three_point_field_goal_percentage(self):
        """
        Returns a ``float`` of the number of three point field goals made
        divided by the number of three point field goal attempts by the home
        team. Percentage ranges from 0-1.
        """
        return self._home_three_point_field_goal_percentage

    @int_property_decorator
    def home_two_point_field_goals(self):
        """
        Returns an ``int`` of the total number of two point field goals made
        by the home team.
        """
        return self._home_two_point_field_goals

    @int_property_decorator
    def home_two_point_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of two point field goal attempts
        by the home team.
        """
        return self._home_two_point_field_goal_attempts

    @float_property_decorator
    def home_two_point_field_goal_percentage(self):
        """
        Returns a ``float`` of the number of two point field goals made divided
        by the number of two point field goal attempts by the home team.
        Percentage ranges from 0-1.
        """
        return self._home_two_point_field_goal_percentage

    @int_property_decorator
    def home_free_throws(self):
        """
        Returns an ``int`` of the total number of free throws made by the home
        team.
        """
        return self._home_free_throws

    @int_property_decorator
    def home_free_throw_attempts(self):
        """
        Returns an ``int`` of the total number of free throw attempts by the
        home team.
        """
        return self._home_free_throw_attempts

    @float_property_decorator
    def home_free_throw_percentage(self):
        """
        Returns a ``float`` of the number of free throws made divided by the
        number of free throw attempts  by the home team.
        """
        return self._home_free_throw_percentage

    @int_property_decorator
    def home_offensive_rebounds(self):
        """
        Returns an ``int`` of the total number of offensive rebounds by the
        home team.
        """
        return self._home_offensive_rebounds

    @int_property_decorator
    def home_defensive_rebounds(self):
        """
        Returns an ``int`` of the total number of defensive rebounds by the
        home team.
        """
        return self._home_defensive_rebounds

    @int_property_decorator
    def home_total_rebounds(self):
        """
        Returns an ``int`` of the total number of rebounds by the home team.
        """
        return self._home_total_rebounds

    @int_property_decorator
    def home_assists(self):
        """
        Returns an ``int`` of the total number of assists by the home team.
        """
        return self._home_assists

    @int_property_decorator
    def home_steals(self):
        """
        Returns an ``int`` of the total number of steals by the home team.
        """
        return self._home_steals

    @int_property_decorator
    def home_blocks(self):
        """
        Returns an ``int`` of the total number of blocks by the home team.
        """
        return self._home_blocks

    @int_property_decorator
    def home_turnovers(self):
        """
        Returns an ``int`` of the total number of turnovers by the home team.
        """
        return self._home_turnovers

    @int_property_decorator
    def home_personal_fouls(self):
        """
        Returns an ``int`` of the total number of personal fouls by the home
        team.
        """
        return self._home_personal_fouls

    @int_property_decorator
    def home_points(self):
        """
        Returns an ``int`` of the number of points the home team scored.
        """
        return self._home_points

    @float_property_decorator
    def home_true_shooting_percentage(self):
        """
        Returns a ``float`` of the home team's true shooting percentage which
        considers free throws, 2-point field goals, and 3-point field goals.
        Percentage ranges from 0-1.
        """
        return self._home_true_shooting_percentage

    @float_property_decorator
    def home_effective_field_goal_percentage(self):
        """
        Returns a ``float`` of the home team's field goal percentage while
        giving extra weight to 3-point field goals. Percentage ranges from 0-1.
        """
        return self._home_effective_field_goal_percentage

    @float_property_decorator
    def home_three_point_attempt_rate(self):
        """
        Returns a ``float`` of the percentage of field goal attempts from
        3-point range by the home team. Percentage ranges from 0-1.
        """
        return self._home_three_point_attempt_rate

    @float_property_decorator
    def home_free_throw_attempt_rate(self):
        """
        Returns a ``float`` of the average number of free throw attempts per
        field goal attempt by the home team.
        """
        return self._home_free_throw_attempt_rate

    @float_property_decorator
    def home_offensive_rebound_percentage(self):
        """
        Returns a ``float`` of the percentage of available offensive rebounds
        the home team grabbed. Percentage ranges from 0-100.
        """
        return self._home_offensive_rebound_percentage

    @float_property_decorator
    def home_defensive_rebound_percentage(self):
        """
        Returns a ``float`` of the percentage of available defensive rebounds
        the home team grabbed. Percentage ranges from 0-100.
        """
        return self._home_defensive_rebound_percentage

    @float_property_decorator
    def home_total_rebound_percentage(self):
        """
        Returns a ``float`` of the percentage of available rebounds the home
        team grabbed. Percentage ranges from 0-100.
        """
        return self._home_total_rebound_percentage

    @float_property_decorator
    def home_assist_percentage(self):
        """
        Returns a ``float`` of the percentage of the home team's field goals
        that were assisted. Percentage ranges from 0-100.
        """
        return self._home_assist_percentage

    @float_property_decorator
    def home_steal_percentage(self):
        """
        Returns a ``float`` of the percentage of possessions that ended in a
        steal by the home team. Percentage ranges from 0-100.
        """
        return self._home_steal_percentage

    @float_property_decorator
    def home_block_percentage(self):
        """
        Returns a ``float`` of the percentage of 2-point field goals that were
        blocked by the home team. Percentage ranges from 0-100.
        """
        return self._home_block_percentage

    @float_property_decorator
    def home_turnover_percentage(self):
        """
        Returns a ``float`` of the number of times the home team turned the
        ball over per 100 possessions.
        """
        return self._home_turnover_percentage

    @float_property_decorator
    def home_offensive_rating(self):
        """
        Returns a ``float`` of the average number of points scored per 100
        possessions by the home team.
        """
        return self._home_offensive_rating

    @float_property_decorator
    def home_defensive_rating(self):
        """
        Returns a ``float`` of the average number of points scored per 100
        possessions by the away team.
        """
        return self._home_defensive_rating


class Boxscores:
    """
    Search for NCAAB games taking place on a particular day.

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
        uri = re.sub(r'.*cbb/boxscores/', '', str(url))
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
        if 'cbb/schools' not in str(abbr):
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
        links = [g('td:first') for g in game('tr').items()
                 if 'class="desc"' not in str(g('td:first'))]
        # The away team is the first link in the boxscore
        away = links[0]
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
