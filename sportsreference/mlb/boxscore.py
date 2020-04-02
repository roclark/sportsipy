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
                        BOXSCORES_URL,
                        DAY,
                        DOUBLE_HEADER_INDICES,
                        NIGHT)
from .player import (AbstractPlayer,
                     _float_property_decorator,
                     _int_property_decorator)


class BoxscorePlayer(AbstractPlayer):
    """
    Get player stats for an individual game.

    Given a player ID, such as 'altuvjo01' for Jose Altuve, their full name,
    and all associated stats from the Boxscore page in HTML format, parse the
    HTML and extract only the relevant stats for the specified player and
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
        A player's ID according to baseball-reference.com, such as 'altuvjo01'
        for Jose Altuve. The player ID can be found by navigating to the
        player's stats page and getting the string between the final slash and
        the '.html' in the URL. In general, the ID is in the format 'LLLLLFFNN'
        where 'LLLLL' are the first 5 letters in the player's last name, 'FF',
        are the first 2 letters in the player's first name, and 'NN' is a
        number starting at '01' for the first time that player ID has been used
        and increments by 1 for every successive player.
    player_name : string
        A string representing the player's first and last name, such as 'Jose
        Altuve'.
    player_data : string
        A string representation of the player's HTML data from the Boxscore
        page. If the player appears in multiple tables, all of their
        information will appear in one single string concatenated together.
    """
    def __init__(self, player_id, player_name, player_data):
        self._index = 0
        self._player_id = player_id
        self._average_leverage_index = None
        self._base_out_runs_added = None
        self._earned_runs_against = None
        self._innings_pitched = None
        self._pitches_thrown = None
        self._strikes = None
        self._home_runs_thrown = None
        self._strikes_thrown = None
        self._strikes_contact = None
        self._strikes_swinging = None
        self._strikes_looking = None
        self._grounded_balls = None
        self._fly_balls = None
        self._line_drives = None
        self._unknown_bat_types = None
        self._game_score = None
        self._inherited_runners = None
        self._inherited_score = None
        self._win_probability_added_pitcher = None
        self._average_leverage_index_pitcher = None
        self._base_out_runs_saved = None
        self._win_probability_added = None
        self._win_probability_for_offensive_player = None
        self._win_probability_subtracted = None
        AbstractPlayer.__init__(self, player_id, player_name, player_data)

    @property
    def dataframe(self):
        """
        Returns a ``pandas DataFrame`` containing all other relevant class
        properties and values for the specified game.
        """
        fields_to_include = {
            'assists': self.assists,
            'at_bats': self.at_bats,
            'average_leverage_index': self.average_leverage_index,
            'average_leverage_index_pitcher':
            self.average_leverage_index_pitcher,
            'bases_on_balls': self.bases_on_balls,
            'bases_on_balls_given': self.bases_on_balls_given,
            'base_out_runs_added': self.base_out_runs_added,
            'base_out_runs_saved': self.base_out_runs_saved,
            'batters_faced': self.batters_faced,
            'batting_average': self.batting_average,
            'earned_runs_allowed': self.earned_runs_allowed,
            'earned_runs_against': self.earned_runs_against,
            'fly_balls': self.fly_balls,
            'game_score': self.game_score,
            'grounded_balls': self.grounded_balls,
            'hits': self.hits,
            'hits_allowed': self.hits_allowed,
            'home_runs_thrown': self.home_runs_thrown,
            'inherited_runners': self.inherited_runners,
            'inherited_score': self.inherited_score,
            'innings_pitched': self.innings_pitched,
            'line_drives': self.line_drives,
            'name': self.name,
            'on_base_percentage': self.on_base_percentage,
            'on_base_plus_slugging_percentage':
            self.on_base_plus_slugging_percentage,
            'pitches_thrown': self.pitches_thrown,
            'plate_appearances': self.plate_appearances,
            'putouts': self.putouts,
            'runs': self.runs,
            'runs_allowed': self.runs_allowed,
            'runs_batted_in': self.runs_batted_in,
            'slugging_percentage': self.slugging_percentage,
            'strikes': self.strikes,
            'strikes_contact': self.strikes_contact,
            'strikes_looking': self.strikes_looking,
            'strikes_swinging': self.strikes_swinging,
            'strikes_thrown': self.strikes_thrown,
            'strikeouts': self.strikeouts,
            'times_struck_out': self.times_struck_out,
            'unknown_bat_types': self.unknown_bat_types,
            'win_probability_added': self.win_probability_added,
            'win_probability_added_pitcher':
            self.win_probability_added_pitcher,
            'win_probability_for_offensive_player':
            self.win_probability_for_offensive_player,
            'win_probability_subtracted': self.win_probability_subtracted
        }
        return pd.DataFrame([fields_to_include], index=[self._player_id])

    @_float_property_decorator
    def average_leverage_index(self):
        """
        Returns a ``float`` of the amount of pressure the player faced during
        the game. 1.0 denotes average pressure while numbers less than 0 denote
        lighter pressure.
        """
        return self._average_leverage_index

    @_float_property_decorator
    def base_out_runs_added(self):
        """
        Returns a ``float`` of the number of base out runs added by the player.
        """
        return self._base_out_runs_added

    @_float_property_decorator
    def earned_runs_against(self):
        """
        Returns a ``float`` of the player's overall Earned Runs Against average
        as calculated by 9 * earned_runs / innings_pitched.
        """
        return self._earned_runs_against

    @_float_property_decorator
    def innings_pitched(self):
        """
        Returns a ``float`` of the number of innings the player pitched in.
        Numbers ending in '.0' indicate complete innings, while numbers ending
        in '.1' are for 1/3 of an inning, and '.2' is for 2/3 of an inning.
        """
        return self._innings_pitched

    @_int_property_decorator
    def home_runs_thrown(self):
        """
        Returns an ``int`` of the number of home runs the player threw.
        """
        return self._home_runs_thrown

    @_int_property_decorator
    def pitches_thrown(self):
        """
        Returns an ``int`` of the number of pitches the player threw.
        """
        return self._pitches_thrown

    @_int_property_decorator
    def strikes(self):
        """
        Returns an ``int`` of the number of times a strike was called against
        the player.
        """
        return self._strikes

    @_int_property_decorator
    def strikes_thrown(self):
        """
        Returns an ``int`` of the number of times a strikes the player threw.
        """
        return self._strikes_thrown

    @_int_property_decorator
    def strikes_contact(self):
        """
        Returns an ``int`` of the number of times the player threw a strike
        when the player made contact with the ball.
        """
        return self._strikes_contact

    @_int_property_decorator
    def strikes_swinging(self):
        """
        Returns an ``int`` of the number of times the player threw a strike
        with the batter swinging.
        """
        return self._strikes_swinging

    @_int_property_decorator
    def strikes_looking(self):
        """
        Returns an ``int`` of the number of times the player threw a strike
        with the player looking.
        """
        return self._strikes_looking

    @_int_property_decorator
    def grounded_balls(self):
        """
        Returns an ``int`` of the number of grounded balls the player allowed.
        """
        return self._grounded_balls

    @_int_property_decorator
    def fly_balls(self):
        """
        Returns an ``int`` of the number of fly balls the player allowed.
        """
        return self._fly_balls

    @_int_property_decorator
    def line_drives(self):
        """
        Returns an ``int`` of the number of line drives the player allowed.
        """
        return self._line_drives

    @_int_property_decorator
    def unknown_bat_types(self):
        """
        Returns an ``int`` of the number of line drives the player allowed.
        """
        return self._unknown_bat_types

    @_int_property_decorator
    def game_score(self):
        """
        Returns an ``int`` of the pitcher's score determine by many factors,
        such as number of runs scored against, number of strikes, etc.
        """
        return self._game_score

    @_int_property_decorator
    def inherited_runners(self):
        """
        Returns an ``int`` of the number of runners a relief pitcher inherited.
        """
        return self._inherited_runners

    @_int_property_decorator
    def inherited_score(self):
        """
        Returns an ``int`` of the number of runners on base when a relief
        pitcher entered the game that ended up scoring.
        """
        return self._inherited_score

    @_float_property_decorator
    def win_probability_added_pitcher(self):
        """
        Returns a ``float`` of the total positive influence the pitcher's
        offense had on the outcome of the game.
        """
        return self._win_probability_added_pitcher

    @_float_property_decorator
    def average_leverage_index_pitcher(self):
        """
        Returns a ``float`` of the amount of pressure the pitcher faced during
        the game. 1.0 denotes average pressure while numbers less than 0 denote
        lighter pressure.
        """
        return self._average_leverage_index_pitcher

    @_float_property_decorator
    def base_out_runs_saved(self):
        """
        Returns a ``float`` of the number of runs saved by the pitcher based on
        the number of players on bases. 0.0 denotes an average value.
        """
        return self._base_out_runs_saved

    @_float_property_decorator
    def win_probability_added(self):
        """
        Returns a ``float`` of the total positive influence the player's
        offense had on the outcome of the game.
        """
        return self._win_probability_added

    @_float_property_decorator
    def win_probability_subtracted(self):
        """
        Returns a ``float`` of the total negative influence the player's
        offense had on the outcome of the game.
        """
        return self._win_probability_subtracted

    @_float_property_decorator
    def win_probability_for_offensive_player(self):
        """
        Returns a ``float`` of the overall influence the player's offense had
        on the outcome of the game where 0.0 denotes no influence and 1.0
        denotes the offense was solely responsible for the outcome.
        """
        return self._win_probability_for_offensive_player


class Boxscore:
    """
    Detailed information about the final statistics for a game.

    Stores all relevant information for a game such as the date, time,
    location, result, and more advanced metrics such as the number of strikes,
    a pitcher's influence on the game, the number of putouts and much more.

    Parameters
    ----------
    uri : string
        The relative link to the boxscore HTML page, such as
        'BOS/BOS201806070'.
    """
    def __init__(self, uri):
        self._uri = uri
        self._date = None
        self._time = None
        self._attendance = None
        self._venue = None
        self._time_of_day = None
        self._duration = None
        self._away_name = None
        self._home_name = None
        self._summary = None
        self._winner = None
        self._winning_name = None
        self._winning_abbr = None
        self._losing_name = None
        self._losing_abbr = None
        self._losing_abbr = None
        self._away_at_bats = None
        self._away_runs = None
        self._away_hits = None
        self._away_rbi = None
        self._away_earned_runs = None
        self._away_bases_on_balls = None
        self._away_strikeouts = None
        self._away_plate_appearances = None
        self._away_batting_average = None
        self._away_on_base_percentage = None
        self._away_slugging_percentage = None
        self._away_on_base_plus = None
        self._away_pitches = None
        self._away_strikes = None
        self._away_win_probability_for_offensive_player = None
        self._away_average_leverage_index = None
        self._away_win_probability_added = None
        self._away_win_probability_subtracted = None
        self._away_base_out_runs_added = None
        self._away_putouts = None
        self._away_assists = None
        self._away_innings_pitched = None
        self._away_home_runs = None
        self._away_strikes_by_contact = None
        self._away_strikes_swinging = None
        self._away_strikes_looking = None
        self._away_grounded_balls = None
        self._away_fly_balls = None
        self._away_line_drives = None
        self._away_unknown_bat_type = None
        self._away_game_score = None
        self._away_inherited_runners = None
        self._away_inherited_score = None
        self._away_win_probability_by_pitcher = None
        self._away_base_out_runs_saved = None
        self._home_at_bats = None
        self._home_runs = None
        self._home_hits = None
        self._home_rbi = None
        self._home_earned_runs = None
        self._home_bases_on_balls = None
        self._home_strikeouts = None
        self._home_plate_appearances = None
        self._home_batting_average = None
        self._home_on_base_percentage = None
        self._home_slugging_percentage = None
        self._home_on_base_plus = None
        self._home_pitches = None
        self._home_strikes = None
        self._home_win_probability_for_offensive_player = None
        self._home_average_leverage_index = None
        self._home_win_probability_added = None
        self._home_win_probability_subtracted = None
        self._home_base_out_runs_added = None
        self._home_putouts = None
        self._home_assists = None
        self._home_innings_pitched = None
        self._home_home_runs = None
        self._home_strikes_by_contact = None
        self._home_strikes_swinging = None
        self._home_strikes_looking = None
        self._home_grounded_balls = None
        self._home_fly_balls = None
        self._home_line_drives = None
        self._home_unknown_bat_type = None
        self._home_game_score = None
        self._home_inherited_runners = None
        self._home_inherited_score = None
        self._home_win_probability_by_pitcher = None
        self._home_base_out_runs_saved = None

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
            'BOS/BOS201806070'.

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

        The game's meta information, such as date, location, attendance, and
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
        time = None
        time_of_day = None
        venue = None
        if len(game_info) > 0:
            date = game_info[0]
        for line in game_info:
            if 'Start Time: ' in line:
                time = line.replace('Start Time: ', '')
            if 'Attendance: ' in line:
                attendance = line.replace('Attendance: ', '').replace(',', '')
            if 'Venue: ' in line:
                venue = line.replace('Venue: ', '')
            if 'Game Duration: ' in line:
                duration = line.replace('Game Duration: ', '')
            if 'Night Game' in line or 'Day Game' in line:
                time_of_day = line
        setattr(self, '_attendance', attendance)
        setattr(self, '_date', date)
        setattr(self, '_duration', duration)
        setattr(self, '_time', time)
        setattr(self, '_time_of_day', time_of_day)
        setattr(self, '_venue', venue)

    def _parse_summary(self, boxscore):
        """
        Find the game summary including score in each inning.

        The game summary provides further information on the points scored
        during each inning, including the final score and any extra innings if
        applicable. The final output will be in a dictionary with two keys,
        'away' and 'home'. The value of each key will be a list for each
        respective team's score by order of the inning, with the first element
        belonging to the first inning, similar to the following:

        {
            'away': [0, 0, 0, 0, 0, 0, 0, 3, 1, 2],
            'home': [0, 1, 0, 0, 1, 0, 0, 0, 0, 0]
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
        for ind, team_info in enumerate(game_summary('tr').items()):
            ind = (ind + 1) % 2
            # Only pull the first N-1 items as the last three elements are the
            # total runs, hits, and errors for each team which is already
            # stored in an attribute, and shouldn't be duplicated.
            for inning in list(team_info('td[class="center"]').items())[:-3]:
                if inning('div'):
                    continue
                try:
                    summary[team[ind]].append(int(inning.text()))
                except ValueError:
                    summary[team[ind]].append(None)
        return summary

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

        for table in boxscore('table').items():
            try:
                if 'pitching' in table.attr['id'] or \
                   'batting' in table.attr['id']:
                    tables.append(table)
            except (KeyError, TypeError):
                continue
        return tables

    def _find_player_id(self, row):
        """
        Find the player's ID.

        Find the player's ID as embedded in the 'data-append-csv' attribute,
        such as 'altuvjo01' for Jose Altuve.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object representing a single row in a boxscore table for
            a single player.

        Returns
        -------
        str
            Returns a ``string`` of the player's ID, such as 'altuvjo01' for
            Jose Altuve.
        """
        return row('th').attr('data-append-csv')

    def _find_player_name(self, row):
        """
        Find the player's full name.

        Find the player's full name, such as 'Jose Altuve'. The name is the
        text displayed for a link to the player's individual stats.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object representing a single row in a boxscore table for
            a single player.

        Returns
        -------
        str
            Returns a ``string`` of the player's full name, such as 'Jose
            Altuve'.
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
            home_or_away = AWAY
            # There are two tables per team with the odd tables belonging to
            # the home team.
            if table_count % 2 == 1:
                home_or_away = HOME
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
            'BOS/BOS201806070'.
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
               short_field == 'venue' or \
               short_field == 'attendance' or \
               short_field == 'time_of_day' or \
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
        instantiate the class, such as 'BOS201806070'.
        """
        if self._away_runs is None and self._home_runs is None:
            return None
        fields_to_include = {
            'date': self.date,
            'time': self.time,
            'venue': self.venue,
            'attendance': self.attendance,
            'duration': self.duration,
            'time_of_day': self.time_of_day,
            'winner': self.winner,
            'winning_name': self.winning_name,
            'winning_abbr': self.winning_abbr,
            'losing_name': self.losing_name,
            'losing_abbr': self.losing_abbr,
            'away_at_bats': self.away_at_bats,
            'away_runs': self.away_runs,
            'away_hits': self.away_hits,
            'away_rbi': self.away_rbi,
            'away_earned_runs': self.away_earned_runs,
            'away_bases_on_balls': self.away_bases_on_balls,
            'away_strikeouts': self.away_strikeouts,
            'away_plate_appearances': self.away_plate_appearances,
            'away_batting_average': self.away_batting_average,
            'away_on_base_percentage': self.away_on_base_percentage,
            'away_slugging_percentage': self.away_slugging_percentage,
            'away_on_base_plus': self.away_on_base_plus,
            'away_pitches': self.away_pitches,
            'away_strikes': self.away_strikes,
            'away_win_probability_for_offensive_player':
            self.away_win_probability_for_offensive_player,
            'away_average_leverage_index': self.away_average_leverage_index,
            'away_win_probability_added': self.away_win_probability_added,
            'away_win_probability_subtracted':
            self.away_win_probability_subtracted,
            'away_base_out_runs_added': self.away_base_out_runs_added,
            'away_putouts': self.away_putouts,
            'away_assists': self.away_assists,
            'away_innings_pitched': self.away_innings_pitched,
            'away_home_runs': self.away_home_runs,
            'away_strikes_by_contact': self.away_strikes_by_contact,
            'away_strikes_swinging': self.away_strikes_swinging,
            'away_strikes_looking': self.away_strikes_looking,
            'away_grounded_balls': self.away_grounded_balls,
            'away_fly_balls': self.away_fly_balls,
            'away_line_drives': self.away_line_drives,
            'away_unknown_bat_type': self.away_unknown_bat_type,
            'away_game_score': self.away_game_score,
            'away_inherited_runners': self.away_inherited_runners,
            'away_inherited_score': self.away_inherited_score,
            'away_win_probability_by_pitcher':
            self.away_win_probability_by_pitcher,
            'away_base_out_runs_saved': self.away_base_out_runs_saved,
            'home_at_bats': self.home_at_bats,
            'home_runs': self.home_runs,
            'home_hits': self.home_hits,
            'home_rbi': self.home_rbi,
            'home_earned_runs': self.home_earned_runs,
            'home_bases_on_balls': self.home_bases_on_balls,
            'home_strikeouts': self.home_strikeouts,
            'home_plate_appearances': self.home_plate_appearances,
            'home_batting_average': self.home_batting_average,
            'home_on_base_percentage': self.home_on_base_percentage,
            'home_slugging_percentage': self.home_slugging_percentage,
            'home_on_base_plus': self.home_on_base_plus,
            'home_pitches': self.home_pitches,
            'home_strikes': self.home_strikes,
            'home_win_probability_for_offensive_player':
            self.home_win_probability_for_offensive_player,
            'home_average_leverage_index': self.home_average_leverage_index,
            'home_win_probability_added': self.home_win_probability_added,
            'home_win_probability_subtracted':
            self.home_win_probability_subtracted,
            'home_base_out_runs_added': self.home_base_out_runs_added,
            'home_putouts': self.home_putouts,
            'home_assists': self.home_assists,
            'home_innings_pitched': self.home_innings_pitched,
            'home_home_runs': self.home_home_runs,
            'home_strikes_by_contact': self.home_strikes_by_contact,
            'home_strikes_swinging': self.home_strikes_swinging,
            'home_strikes_looking': self.home_strikes_looking,
            'home_grounded_balls': self.home_grounded_balls,
            'home_fly_balls': self.home_fly_balls,
            'home_line_drives': self.home_line_drives,
            'home_unknown_bat_type': self.home_unknown_bat_type,
            'home_game_score': self.home_game_score,
            'home_inherited_runners': self.home_inherited_runners,
            'home_inherited_score': self.home_inherited_score,
            'home_win_probability_by_pitcher':
            self.home_win_probability_by_pitcher,
            'home_base_out_runs_saved': self.home_base_out_runs_saved
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
        return self._time

    @property
    def venue(self):
        """
        Returns a ``string`` of the name of the ballpark where the game was
        played.
        """
        return self._venue

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
    def time_of_day(self):
        """
        Returns a ``string`` constant indicated whether the game was played
        during the day or at night.
        """
        if 'night' in self._time_of_day.lower():
            return NIGHT
        return DAY

    @property
    def summary(self):
        """
        Returns a ``dictionary`` with two keys, 'away' and 'home'. The value of
        each key will be a list for each respective team's score by order of
        the inning, with the first element belonging to the first inning,
        similar to the following:

        {
            'away': [5, 0, 1, 0, 0, 0, 0, 1, 0],
            'home': [1, 0, 0, 0, 1, 0, 0, 0, 0]
        }
        """
        return self._summary

    @property
    def winner(self):
        """
        Returns a ``string`` constant indicating whether the home or away team
        won.
        """
        if self.home_runs > self.away_runs:
            return HOME
        return AWAY

    @property
    def winning_name(self):
        """
        Returns a ``string`` of the winning team's name, such as 'Houston
        Astros'.
        """
        if self.winner == HOME:
            return self._home_name.text()
        return self._away_name.text()

    @property
    def winning_abbr(self):
        """
        Returns a ``string`` of the winning team's abbreviation, such as 'HOU'
        for the Houston Astros.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._home_name)
        return utils._parse_abbreviation(self._away_name)

    @property
    def losing_name(self):
        """
        Returns a ``string`` of the losing team's name, such as 'Los Angeles
        Dodgers'.
        """
        if self.winner == HOME:
            return self._away_name.text()
        return self._home_name.text()

    @property
    def losing_abbr(self):
        """
        Returns a ``string`` of the losing team's abbreviation, such as 'LAD'
        for the Los Angeles Dodgers.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._away_name)
        return utils._parse_abbreviation(self._home_name)

    @int_property_decorator
    def away_at_bats(self):
        """
        Returns an ``int`` of the number of at bats the away team had.
        """
        return self._away_at_bats

    @int_property_decorator
    def away_runs(self):
        """
        Returns an ``int`` of the number of runs the away team scored.
        """
        return self._away_runs

    @int_property_decorator
    def away_hits(self):
        """
        Returns an ``int`` of the number of hits the away team had.
        """
        return self._away_hits

    @int_property_decorator
    def away_rbi(self):
        """
        Returns an ``int`` of the number of runs batted in the away team
        registered.
        """
        return self._away_rbi

    @float_property_decorator
    def away_earned_runs(self):
        """
        Returns a ``float`` of the number of runs the away team earned.
        """
        return self._away_earned_runs

    @int_property_decorator
    def away_bases_on_balls(self):
        """
        Returns an ``int`` of the number of bases the away team registerd as a
        result of balls.
        """
        return self._away_bases_on_balls

    @int_property_decorator
    def away_strikeouts(self):
        """
        Returns an ``int`` of the number of times the away team was struck out.
        """
        return self._away_strikeouts

    @int_property_decorator
    def away_plate_appearances(self):
        """
        Returns an ``int`` of the number of plate appearances the away team
        made.
        """
        return self._away_plate_appearances

    @float_property_decorator
    def away_batting_average(self):
        """
        Returns a ``float`` of the batting average for the away team.
        """
        return self._away_batting_average

    @float_property_decorator
    def away_on_base_percentage(self):
        """
        Returns a ``float`` of the percentage of at bats that result in the
        batter getting on base.
        """
        return self._away_on_base_percentage

    @float_property_decorator
    def away_slugging_percentage(self):
        """
        Returns a ``float`` of the slugging percentage for the away team based
        on the number of bases gained per at-bat with bigger plays getting more
        weight.
        """
        return self._away_slugging_percentage

    @float_property_decorator
    def away_on_base_plus(self):
        """
        Returns a ``float`` of the on base percentage plus the slugging
        percentage. Percentage ranges from 0-1.
        """
        return self._away_on_base_plus

    @int_property_decorator
    def away_pitches(self):
        """
        Returns an ``int`` of the number of pitches the away team faced.
        """
        return self._away_pitches

    @int_property_decorator
    def away_strikes(self):
        """
        Returns an ``int`` of the number of times a strike was called against
        the away team.
        """
        return self._away_strikes

    @float_property_decorator
    def away_win_probability_for_offensive_player(self):
        """
        Returns a ``float`` of the overall influence the away team's offense
        had on the outcome of the game where 0.0 denotes no influence and 1.0
        denotes the offense was solely responsible for the outcome.
        """
        return self._away_win_probability_for_offensive_player

    @float_property_decorator
    def away_average_leverage_index(self):
        """
        Returns a ``float`` of the amount of pressure the away team's pitcher
        faced during the game. 1.0 denotes average pressure while numbers less
        than 0 denote lighter pressure.
        """
        return self._away_average_leverage_index

    @float_property_decorator
    def away_win_probability_added(self):
        """
        Returns a ``float`` of the total positive influence the away team's
        offense had on the outcome of the game.
        """
        return self._away_win_probability_added

    @float_property_decorator
    def away_win_probability_subtracted(self):
        """
        Returns a ``float`` of the total negative influence the away team's
        offense had on the outcome of the game.
        """
        return self._away_win_probability_subtracted

    @float_property_decorator
    def away_base_out_runs_added(self):
        """
        Returns a ``float`` of the number of base out runs added by the away
        team.
        """
        return self._away_base_out_runs_added

    @int_property_decorator
    def away_putouts(self):
        """
        Returns an ``int`` of the number of putouts the away team registered.
        """
        return self._away_putouts

    @int_property_decorator
    def away_assists(self):
        """
        Returns an ``int`` of the number of assists the away team registered.
        """
        return self._away_assists

    @float_property_decorator
    def away_innings_pitched(self):
        """
        Returns a ``float`` of the number of innings the away team pitched.
        """
        return self._away_innings_pitched

    @int_property_decorator
    def away_home_runs(self):
        """
        Returns an ``int`` of the number of times the away team gave up a home
        run.
        """
        return self._away_home_runs

    @int_property_decorator
    def away_strikes_by_contact(self):
        """
        Returns an ``int`` of the number of times the away team struck out a
        batter who made contact with the pitch.
        """
        return self._away_strikes_by_contact

    @int_property_decorator
    def away_strikes_swinging(self):
        """
        Returns an ``int`` of the number of times the away team struck out a
        batter who was swinging.
        """
        return self._away_strikes_swinging

    @int_property_decorator
    def away_strikes_looking(self):
        """
        Returns an ``int`` of the number of times the away team struck out a
        batter who was looking.
        """
        return self._away_strikes_looking

    @int_property_decorator
    def away_grounded_balls(self):
        """
        Returns an ``int`` of the number of grounded balls the away team
        allowed.
        """
        return self._away_grounded_balls

    @int_property_decorator
    def away_fly_balls(self):
        """
        Returns an ``int`` of the number of fly balls the away team allowed.
        """
        return self._away_fly_balls

    @int_property_decorator
    def away_line_drives(self):
        """
        Returns an ``int`` of the number of line drives the away team allowed.
        """
        return self._away_line_drives

    @int_property_decorator
    def away_unknown_bat_type(self):
        """
        Returns an ``int`` of the number of away at bats that were not properly
        tracked and therefore cannot be safely placed in another statistical
        category.
        """
        return self._away_unknown_bat_type

    @int_property_decorator
    def away_game_score(self):
        """
        Returns an ``int`` of the starting away pitcher's score determine by
        many factors, such as number of runs scored against, number of strikes,
        etc.
        """
        return self._away_game_score

    @int_property_decorator
    def away_inherited_runners(self):
        """
        Returns an ``int`` of the number of runners a pitcher inherited when he
        entered the game.
        """
        return self._away_inherited_runners

    @int_property_decorator
    def away_inherited_score(self):
        """
        Returns an ``int`` of the number of scorers a pitcher inherited when he
        entered the game.
        """
        return self._away_inherited_score

    @float_property_decorator
    def away_win_probability_by_pitcher(self):
        """
        Returns a ``float`` of the amount of influence the away pitcher had on
        the game's result with 0.0 denoting zero influence and 1.0 denoting he
        was solely responsible for the team's win.
        """
        return self._away_win_probability_by_pitcher

    @float_property_decorator
    def away_base_out_runs_saved(self):
        """
        Returns a ``float`` of the number of runs saved by the away pitcher
        based on the number of players on bases. 0.0 denotes an average value.
        """
        return self._away_base_out_runs_saved

    @int_property_decorator
    def home_at_bats(self):
        """
        Returns an ``int`` of the number of at bats the home team had.
        """
        return self._home_at_bats

    @int_property_decorator
    def home_runs(self):
        """
        Returns an ``int`` of the number of runs the home team scored.
        """
        return self._home_runs

    @int_property_decorator
    def home_hits(self):
        """
        Returns an ``int`` of the number of hits the home team had.
        """
        return self._home_hits

    @int_property_decorator
    def home_rbi(self):
        """
        Returns an ``int`` of the number of runs batted in the home team
        registered.
        """
        return self._home_rbi

    @float_property_decorator
    def home_earned_runs(self):
        """
        Returns a ``float`` of the number of runs the home team earned.
        """
        return self._home_earned_runs

    @int_property_decorator
    def home_bases_on_balls(self):
        """
        Returns an ``int`` of the number of bases the home team registerd as a
        result of balls.
        """
        return self._home_bases_on_balls

    @int_property_decorator
    def home_strikeouts(self):
        """
        Returns an ``int`` of the number of times the home team was struck out.
        """
        return self._home_strikeouts

    @int_property_decorator
    def home_plate_appearances(self):
        """
        Returns an ``int`` of the number of plate appearances the home team
        made.
        """
        return self._home_plate_appearances

    @float_property_decorator
    def home_batting_average(self):
        """
        Returns a ``float`` of the batting average for the home team.
        """
        return self._home_batting_average

    @float_property_decorator
    def home_on_base_percentage(self):
        """
        Returns a ``float`` of the percentage of at bats that result in the
        batter getting on base.
        """
        return self._home_on_base_percentage

    @float_property_decorator
    def home_slugging_percentage(self):
        """
        Returns a ``float`` of the slugging percentage for the home team based
        on the number of bases gained per at-bat with bigger plays getting more
        weight.
        """
        return self._home_slugging_percentage

    @float_property_decorator
    def home_on_base_plus(self):
        """
        Returns a ``float`` of the on base percentage plus the slugging
        percentage. Percentage ranges from 0-1.
        """
        return self._home_on_base_plus

    @int_property_decorator
    def home_pitches(self):
        """
        Returns an ``int`` of the number of pitches the home team faced.
        """
        return self._home_pitches

    @int_property_decorator
    def home_strikes(self):
        """
        Returns an ``int`` of the number of times a strike was called against
        the home team.
        """
        return self._home_strikes

    @float_property_decorator
    def home_win_probability_for_offensive_player(self):
        """
        Returns a ``float`` of the overall influence the home team's offense
        had on the outcome of the game where 0.0 denotes no influence and 1.0
        denotes the offense was solely responsible for the outcome.
        """
        return self._home_win_probability_for_offensive_player

    @float_property_decorator
    def home_average_leverage_index(self):
        """
        Returns a ``float`` of the amount of pressure the home team's pitcher
        faced during the game. 1.0 denotes average pressure while numbers less
        than 0 denote lighter pressure.
        """
        return self._home_average_leverage_index

    @float_property_decorator
    def home_win_probability_added(self):
        """
        Returns a ``float`` of the total positive influence the home team's
        offense had on the outcome of the game.
        """
        return self._home_win_probability_added

    @float_property_decorator
    def home_win_probability_subtracted(self):
        """
        Returns a ``float`` of the total negative influence the home team's
        offense had on the outcome of the game.
        """
        return self._home_win_probability_subtracted

    @float_property_decorator
    def home_base_out_runs_added(self):
        """
        Returns a ``float`` of the number of base out runs added by the home
        team.
        """
        return self._home_base_out_runs_added

    @int_property_decorator
    def home_putouts(self):
        """
        Returns an ``int`` of the number of putouts the home team registered.
        """
        return self._home_putouts

    @int_property_decorator
    def home_assists(self):
        """
        Returns an ``int`` of the number of assists the home team registered.
        """
        return self._home_assists

    @float_property_decorator
    def home_innings_pitched(self):
        """
        Returns a ``float`` of the number of innings the home team pitched.
        """
        return self._home_innings_pitched

    @int_property_decorator
    def home_home_runs(self):
        """
        Returns an ``int`` of the number of times the home team gave up a home
        run.
        """
        return self._home_home_runs

    @int_property_decorator
    def home_strikes_by_contact(self):
        """
        Returns an ``int`` of the number of times the home team struck out a
        batter who made contact with the pitch.
        """
        return self._home_strikes_by_contact

    @int_property_decorator
    def home_strikes_swinging(self):
        """
        Returns an ``int`` of the number of times the home team struck out a
        batter who was swinging.
        """
        return self._home_strikes_swinging

    @int_property_decorator
    def home_strikes_looking(self):
        """
        Returns an ``int`` of the number of times the home team struck out a
        batter who was looking.
        """
        return self._home_strikes_looking

    @int_property_decorator
    def home_grounded_balls(self):
        """
        Returns an ``int`` of the number of grounded balls the home team
        allowed.
        """
        return self._home_grounded_balls

    @int_property_decorator
    def home_fly_balls(self):
        """
        Returns an ``int`` of the number of fly balls the home team allowed.
        """
        return self._home_fly_balls

    @int_property_decorator
    def home_line_drives(self):
        """
        Returns an ``int`` of the number of line drives the home team allowed.
        """
        return self._home_line_drives

    @int_property_decorator
    def home_unknown_bat_type(self):
        """
        Returns an ``int`` of the number of home at bats that were not properly
        tracked and therefore cannot be safely placed in another statistical
        category.
        """
        return self._home_unknown_bat_type

    @int_property_decorator
    def home_game_score(self):
        """
        Returns an ``int`` of the starting home pitcher's score determine by
        many factors, such as number of runs scored against, number of strikes,
        etc.
        """
        return self._home_game_score

    @int_property_decorator
    def home_inherited_runners(self):
        """
        Returns an ``int`` of the number of runners a pitcher inherited when he
        entered the game.
        """
        return self._home_inherited_runners

    @int_property_decorator
    def home_inherited_score(self):
        """
        Returns an ``int`` of the number of scorers a pitcher inherited when he
        entered the game.
        """
        return self._home_inherited_score

    @float_property_decorator
    def home_win_probability_by_pitcher(self):
        """
        Returns a ``float`` of the amount of influence the home pitcher had on
        the game's result with 0.0 denoting zero influence and 1.0 denoting he
        was solely responsible for the team's win.
        """
        return self._home_win_probability_by_pitcher

    @float_property_decorator
    def home_base_out_runs_saved(self):
        """
        Returns a ``float`` of the number of runs saved by the home pitcher
        based on the number of players on bases. 0.0 denotes an average value.
        """
        return self._home_base_out_runs_saved


class Boxscores:
    """
    Search for MLB games taking place on a particular day.

    Retrieve a dictionary which contains a list of all games being played on a
    particular day. Output includes a link to the boxscore, and the names and
    abbreviations for both the home teams. If no games are played on a
    particular day, the list will be empty.

    Parameters
    ----------
    date : datetime object
        The date to search for any matches. The month, day, and year are
        required for the search, but time is not factored into the search.
    end_date : datetime object (optional)
        Optionally specify an end date to iterate until. All boxscores
        starting from the date specified in the 'date' parameter up to and
        including the boxscores specified in the 'end_date' parameter will be
        pulled. If left empty, or if 'end_date' is prior to 'date', only the
        games from the day specified in the 'date' parameter will be saved.
    """
    def __init__(self, date, end_date=None):
        self._boxscores = {}

        self._find_games(date, end_date)

    @property
    def games(self):
        """
        Returns a ``dictionary`` object representing all of the games played on
        the requested day. Dictionary is in the following format::

            {
                'date': [  # 'date' is the string date in format 'MM-DD-YYYY'
                    {
                        'home_name': Name of the home team, such as 'New York
                                     Yankees' (`str`),
                        'home_abbr': Abbreviation for the home team, such as
                                     'NYY' (`str`),
                        'away_name': Name of the away team, such as 'Houston
                                     Astros' (`str`),
                        'away_abbr': Abbreviation for the away team, such as
                                     'HOU' (`str`),
                        'boxscore': String representing the boxscore URI, such
                                    as 'SLN/SLN201807280' (`str`),
                        'winning_name': Full name of the winning team, such as
                                        'New York Yankees' (`str`),
                        'winning_abbr': Abbreviation for the winning team, such
                                        as 'NYY' (`str`),
                        'losing_name': Full name of the losing team, such as
                                       'Houston Astros' (`str`),
                        'losing_abbr': Abbreviation for the losing team, such
                                       as 'HOU' (`str`),
                        'home_score': Integer score for the home team (`int`),
                        'away_score': Integer score for the away team (`int`)
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
        return BOXSCORES_URL % (date.year, date.month, date.day)

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
        uri = re.sub(r'.*/boxes/', '', str(url))
        uri = re.sub(r'\.shtml.*', '', uri).strip()
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
        end_date : datetime object (optional)
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
