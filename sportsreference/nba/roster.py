import pandas as pd
import re
from datetime import datetime
from functools import wraps
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from .constants import NATIONALITY, PLAYER_SCHEME, PLAYER_URL, ROSTER_URL
from .player import AbstractPlayer


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


def _int_property_decorator_default_zero(func):
    @property
    @wraps(func)
    def wrapper(*args):
        index = args[0]._index
        prop = func(*args)
        value = _cleanup(prop[index])
        try:
            return int(value)
        except ValueError:
            # If there is no value, default to 0
            return 0
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


def _most_recent_decorator(func):
    @property
    @wraps(func)
    def wrapper(*args):
        season = args[0]._most_recent_season
        seasons = args[0]._season
        index = seasons.index(season)
        prop = func(*args)
        return prop[index]
    return wrapper


class Player(AbstractPlayer):
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
    """
    def __init__(self, player_id):
        self._most_recent_season = ''
        self._index = None
        self._player_id = player_id
        self._season = None
        self._name = None
        self._team_abbreviation = None
        self._position = None
        self._height = None
        self._weight = None
        self._birth_date = None
        self._nationality = None
        self._games_played = None
        self._games_started = None
        self._player_efficiency_rating = None
        self._offensive_win_shares = None
        self._defensive_win_shares = None
        self._win_shares = None
        self._win_shares_per_48_minutes = None
        self._offensive_box_plus_minus = None
        self._defensive_box_plus_minus = None
        self._box_plus_minus = None
        self._value_over_replacement_player = None
        self._shooting_distance = None
        self._percentage_shots_two_pointers = None
        self._percentage_zero_to_three_footers = None
        self._percentage_three_to_ten_footers = None
        self._percentage_ten_to_sixteen_footers = None
        self._percentage_sixteen_foot_plus_two_pointers = None
        self._percentage_shots_three_pointers = None
        self._field_goal_perc_zero_to_three_feet = None
        self._field_goal_perc_three_to_ten_feet = None
        self._field_goal_perc_ten_to_sixteen_feet = None
        self._field_goal_perc_sixteen_foot_plus_two_pointers = None
        self._two_pointers_assisted_percentage = None
        self._percentage_field_goals_as_dunks = None
        self._dunks = None
        self._three_pointers_assisted_percentage = None
        self._percentage_of_three_pointers_from_corner = None
        self._three_point_shot_percentage_from_corner = None
        self._half_court_heaves = None
        self._half_court_heaves_made = None
        self._point_guard_percentage = None
        self._shooting_guard_percentage = None
        self._small_forward_percentage = None
        self._power_forward_percentage = None
        self._center_percentage = None
        self._on_court_plus_minus = None
        self._net_plus_minus = None
        self._passing_turnovers = None
        self._lost_ball_turnovers = None
        self._other_turnovers = None
        self._shooting_fouls = None
        self._blocking_fouls = None
        self._offensive_fouls = None
        self._take_fouls = None
        self._points_generated_by_assists = None
        self._shooting_fouls_drawn = None
        self._and_ones = None
        self._shots_blocked = None
        self._salary = None
        self._contract = None

        player_data = self._pull_player_data()
        if not player_data:
            return
        self._find_initial_index()
        AbstractPlayer.__init__(self, player_id, self._name, player_data)

    def _build_url(self):
        """
        Create the player's URL to pull stats from.

        The player's URL requires the first letter of the player's last name
        followed by the player ID.

        Returns
        -------
        string
            The string URL for the player's stats page.
        """
        # The first letter of the player's last name is used to sort the player
        # list and is a part of the URL.
        first_character = self._player_id[0]
        return PLAYER_URL % (first_character, self._player_id)

    def _retrieve_html_page(self):
        """
        Download the requested player's stats page.

        Download the requested page and strip all of the comment tags before
        returning a pyquery object which will be used to parse the data.

        Returns
        -------
        PyQuery object
            The requested page is returned as a queriable PyQuery object with
            the comment tags removed.
        """
        url = self._build_url()
        try:
            url_data = pq(url)
        except HTTPError:
            return None
        return pq(utils._remove_html_comment_tags(url_data))

    def _parse_season(self, row):
        """
        Parse the season string from the table.

        The season is generally located in the first column of the stats tables
        and should be parsed to denote which season metrics are being pulled
        from.

        Parameters
        ----------
        row : PyQuery object
            A PyQuery object of a single row in a stats table.

        Returns
        -------
        string
            A string representation of the season in the format 'YYYY-YY', such
            as '2017-18'.
        """
        return utils._parse_field(PLAYER_SCHEME, row, 'season')

    def _combine_season_stats(self, table_rows, career_stats, all_stats_dict):
        """
        Combine all stats for each season.

        Since all of the stats are spread across multiple tables, they should
        be combined into a single field which can be used to easily query stats
        at once.

        Parameters
        ----------
        table_rows : generator
            A generator where each element is a row in a stats table.
        career_stats : generator
            A generator where each element is a row in the footer of a stats
            table. Career stats are kept in the footer, hence the usage.
        all_stats_dict : dictionary
            A dictionary of all stats separated by season where each key is the
            season ``string``, such as '2017-18', and the value is a
            ``dictionary`` with a ``string`` of 'data' and ``string``
            containing all of the data.

        Returns
        -------
        dictionary
            Returns an updated version of the passed all_stats_dict which
            includes more metrics from the provided table.
        """
        most_recent_season = self._most_recent_season
        if not table_rows:
            table_rows = []
        for row in table_rows:
            season = self._parse_season(row)
            try:
                all_stats_dict[season]['data'] += str(row)
            except KeyError:
                all_stats_dict[season] = {'data': str(row)}
            most_recent_season = season
        self._most_recent_season = most_recent_season
        if not career_stats:
            return all_stats_dict
        try:
            all_stats_dict['Career']['data'] += str(next(career_stats))
        except KeyError:
            all_stats_dict['Career'] = {'data': str(next(career_stats))}
        return all_stats_dict

    def _combine_all_stats(self, player_info):
        """
        Pull stats from all tables into single data structure.

        Pull the stats from all of the requested tables into a dictionary that
        is separated by season to allow easy queries of the player's stats for
        each season.

        Parameters
        ----------
        player_info : PyQuery object
            A PyQuery object containing all of the stats information for the
            requested player.

        Returns
        -------
        dictionary
            Returns a dictionary where all stats from each table are combined
            by season to allow easy queries by year.
        """
        all_stats_dict = {}

        for table_id in ['totals', 'advanced', 'shooting', 'advanced_pbp',
                         'all_salaries']:
            table_items = utils._get_stats_table(player_info,
                                                 'table#%s' % table_id)
            career_items = utils._get_stats_table(player_info,
                                                  'table#%s' % table_id,
                                                  footer=True)
            all_stats_dict = self._combine_season_stats(table_items,
                                                        career_items,
                                                        all_stats_dict)
        return all_stats_dict

    def _parse_nationality(self, player_info):
        """
        Parse the player's nationality.

        The player's nationality is denoted by a flag in the information
        section with a country code for each nation. The country code needs to
        pulled and then matched to find the player's home country. Once found,
        the '_nationality' attribute is set for the player.

        Parameters
        ----------
        player_info : PyQuery object
            A PyQuery object containing the HTML from the player's stats page.
        """
        for span in player_info('span').items():
            if 'class="f-i' in str(span):
                nationality = span.text()
                nationality = NATIONALITY[nationality]
                setattr(self, '_nationality', nationality)
                break

    def _parse_player_information(self, player_info):
        """
        Parse general player information.

        Parse general player information such as height, weight, and name. The
        attribute for the requested field will be set with the value prior to
        returning.

        Parameters
        ----------
        player_info : PyQuery object
            A PyQuery object containing the HTML from the player's stats page.
        """
        for field in ['_height', '_weight', '_name']:
            short_field = str(field)[1:]
            value = utils._parse_field(PLAYER_SCHEME, player_info, short_field)
            setattr(self, field, value)

    def _parse_birth_date(self, player_info):
        """
        Parse the player's birth date.

        Pull the player's birth date from the player information and set the
        '_birth_date' attribute with the value prior to returning.

        Parameters
        ----------
        player_info : PyQuery object
            A PyQuery object containing the HTML from the player's stats page.
        """
        date = player_info('span[itemprop="birthDate"]').attr('data-birth')
        setattr(self, '_birth_date', date)

    def _parse_contract_headers(self, table):
        """
        Parse the years on the contract.

        The years are listed as the headers on the contract. The first header
        contains 'Team' which specifies the player's current team and should
        not be included in the years.

        Parameters
        ----------
        table : PyQuery object
            A PyQuery object containing the contract table.

        Returns
        -------
        list
            Returns a list where each element is a string denoting the season,
            such as '2017-18'.
        """
        years = [i.text() for i in table('th').items()]
        years.remove('Team')
        return years

    def _parse_contract_wages(self, table):
        """
        Parse the wages on the contract.

        The wages are listed as the data points in the contract table. Any
        values that don't have a value which starts with a '$' sign are likely
        not valid and should be dropped.

        Parameters
        ----------
        table : PyQuery object
            A PyQuery object containing the contract table.

        Returns
        -------
        list
            Returns a list of all wages where each element is a string denoting
            the dollar amount, such as '$40,000,000'.
        """
        wages = [i.text() if i.text().startswith('$') else ''
                 for i in table('td').items()]
        wages.remove('')
        return wages

    def _combine_contract(self, years, wages):
        """
        Combine the contract wages and year.

        Match the wages with the year and add to a dictionary representing the
        player's contract.

        Parameters
        ----------
        years : list
            A list where each element is a string denoting the season, such as
            '2017-18'.
        wages : list
            A list of all wages where each element is a string denoting the
            dollar amount, such as '$40,000,000'.

        Returns
        -------
        dictionary
            Returns a dictionary representing the player's contract where each
            key is a ``string`` of the season, such as '2017-18' and each value
            is a ``string`` of the wages, such as '$40,000,000'.
        """
        contract = {}

        for i in range(len(years)):
            contract[years[i]] = wages[i]
        return contract

    def _parse_contract(self, player_info):
        """
        Parse the player's contract.

        Depending on the player's contract status, a contract table is located
        at the bottom of the stats page and includes player wages by season. If
        found, create a dictionary housing the wages by season.

        Parameters
        ----------
        player_info : PyQuery object
            A PyQuery object containing the HTML from the player's stats page.
        """
        tables = player_info('table').items()
        for table in tables:
            id_attr = table.attr('id')
            if id_attr:
                if id_attr.startswith('contracts_'):
                    years = self._parse_contract_headers(table)
                    wages = self._parse_contract_wages(table)
                    contract = self._combine_contract(years, wages)
                    # If the contract is empty, the player likely doesn't have
                    # a contract and should have a value of None instead.
                    if contract == {}:
                        contract = None
                    setattr(self, '_contract', contract)
                    break

    def _pull_player_data(self):
        """
        Pull and aggregate all player information.

        Pull the player's HTML stats page and parse unique properties, such as
        the player's height, weight, and position. Next, combine all stats for
        all seasons plus the player's career stats into a single object which
        can easily be iterated upon.

        Returns
        -------
        dictionary
            Returns a dictionary of the player's combined stats where each key
            is a string of the season and the value is the season's associated
            stats.
        """
        player_info = self._retrieve_html_page()
        if not player_info:
            return
        self._parse_player_information(player_info)
        self._parse_nationality(player_info)
        self._parse_birth_date(player_info)
        self._parse_contract(player_info)
        all_stats = self._combine_all_stats(player_info)
        setattr(self, '_season', all_stats.keys())
        return all_stats

    def _find_initial_index(self):
        """
        Find the index of career stats.

        When the Player class is instantiated, the default stats to pull are
        the player's career stats. Upon being called, the index of the 'Career'
        element should be the index value.
        """
        index = 0
        for season in self._season:
            if season == 'Career':
                self._index = index
                break
            index += 1

    def __call__(self, requested_season=''):
        """
        Specify a different season to pull stats from.

        A different season can be requested by passing the season string, such
        as '2017-18' to the class instance.

        Parameters
        ----------
        requested_season : string (optional)
            A string of the requested season to query, such as '2017-18'. If
            left blank or 'Career' is passed, the career stats will be used for
            stats queries.

        Returns
        -------
        Player class instance
            Returns the class instance with the updated stats being referenced.
        """
        if requested_season.lower() == 'career' or \
           requested_season == '':
            requested_season = 'Career'
        index = 0
        for season in self._season:
            if season == requested_season:
                self._index = index
                break
            index += 1
        return self

    def _dataframe_fields(self):
        """
        Creates a dictionary of all fields to include with DataFrame.

        With the result of the calls to class properties changing based on the
        class index value, the dictionary should be regenerated every time the
        index is changed when the dataframe property is requested.

        Returns
        -------
        dictionary
            Returns a dictionary where the keys are the shortened ``string``
            attribute names and the values are the actual value for each
            attribute for the specified index.
        """
        fields_to_include = {
            'and_ones': self.and_ones,
            'assist_percentage': self.assist_percentage,
            'assists': self.assists,
            'block_percentage': self.block_percentage,
            'blocking_fouls': self.blocking_fouls,
            'blocks': self.blocks,
            'box_plus_minus': self.box_plus_minus,
            'center_percentage': self.center_percentage,
            'defensive_box_plus_minus': self.defensive_box_plus_minus,
            'defensive_rebound_percentage': self.defensive_rebound_percentage,
            'defensive_rebounds': self.defensive_rebounds,
            'defensive_win_shares': self.defensive_win_shares,
            'dunks': self.dunks,
            'effective_field_goal_percentage':
            self.effective_field_goal_percentage,
            'field_goal_attempts': self.field_goal_attempts,
            'field_goal_perc_sixteen_foot_plus_two_pointers':
            self.field_goal_perc_sixteen_foot_plus_two_pointers,
            'field_goal_perc_ten_to_sixteen_feet':
            self.field_goal_perc_ten_to_sixteen_feet,
            'field_goal_perc_three_to_ten_feet':
            self.field_goal_perc_three_to_ten_feet,
            'field_goal_perc_zero_to_three_feet':
            self.field_goal_perc_zero_to_three_feet,
            'field_goal_percentage': self.field_goal_percentage,
            'field_goals': self.field_goals,
            'free_throw_attempt_rate': self.free_throw_attempt_rate,
            'free_throw_attempts': self.free_throw_attempts,
            'free_throw_percentage': self.free_throw_percentage,
            'free_throws': self.free_throws,
            'games_played': self.games_played,
            'games_started': self.games_started,
            'half_court_heaves': self.half_court_heaves,
            'half_court_heaves_made': self.half_court_heaves_made,
            'height': self.height,
            'lost_ball_turnovers': self.lost_ball_turnovers,
            'minutes_played': self.minutes_played,
            'nationality': self.nationality,
            'net_plus_minus': self.net_plus_minus,
            'offensive_box_plus_minus': self.offensive_box_plus_minus,
            'offensive_fouls': self.offensive_fouls,
            'offensive_rebound_percentage': self.offensive_rebound_percentage,
            'offensive_rebounds': self.offensive_rebounds,
            'offensive_win_shares': self.offensive_win_shares,
            'on_court_plus_minus': self.on_court_plus_minus,
            'other_turnovers': self.other_turnovers,
            'passing_turnovers': self.passing_turnovers,
            'percentage_field_goals_as_dunks':
            self.percentage_field_goals_as_dunks,
            'percentage_of_three_pointers_from_corner':
            self.percentage_of_three_pointers_from_corner,
            'percentage_shots_three_pointers':
            self.percentage_shots_three_pointers,
            'percentage_shots_two_pointers':
            self.percentage_shots_two_pointers,
            'percentage_sixteen_foot_plus_two_pointers':
            self.percentage_sixteen_foot_plus_two_pointers,
            'percentage_ten_to_sixteen_footers':
            self.percentage_ten_to_sixteen_footers,
            'percentage_three_to_ten_footers':
            self.percentage_three_to_ten_footers,
            'percentage_zero_to_three_footers':
            self.percentage_zero_to_three_footers,
            'personal_fouls': self.personal_fouls,
            'player_efficiency_rating': self.player_efficiency_rating,
            'player_id': self.player_id,
            'point_guard_percentage': self.point_guard_percentage,
            'points': self.points,
            'points_generated_by_assists': self.points_generated_by_assists,
            'position': self.position,
            'power_forward_percentage': self.power_forward_percentage,
            'salary': self.salary,
            'shooting_distance': self.shooting_distance,
            'shooting_fouls': self.shooting_fouls,
            'shooting_fouls_drawn': self.shooting_fouls_drawn,
            'shooting_guard_percentage': self.shooting_guard_percentage,
            'shots_blocked': self.shots_blocked,
            'small_forward_percentage': self.small_forward_percentage,
            'steal_percentage': self.steal_percentage,
            'steals': self.steals,
            'take_fouls': self.take_fouls,
            'team_abbreviation': self.team_abbreviation,
            'three_point_attempt_rate': self.three_point_attempt_rate,
            'three_point_attempts': self.three_point_attempts,
            'three_point_percentage': self.three_point_percentage,
            'three_point_shot_percentage_from_corner':
            self.three_point_shot_percentage_from_corner,
            'three_pointers': self.three_pointers,
            'three_pointers_assisted_percentage':
            self.three_pointers_assisted_percentage,
            'total_rebound_percentage': self.total_rebound_percentage,
            'total_rebounds': self.total_rebounds,
            'true_shooting_percentage': self.true_shooting_percentage,
            'turnover_percentage': self.turnover_percentage,
            'turnovers': self.turnovers,
            'two_point_attempts': self.two_point_attempts,
            'two_point_percentage': self.two_point_percentage,
            'two_pointers': self.two_pointers,
            'two_pointers_assisted_percentage':
            self.two_pointers_assisted_percentage,
            'usage_percentage': self.usage_percentage,
            'value_over_replacement_player':
            self.value_over_replacement_player,
            'weight': self.weight,
            'win_shares': self.win_shares,
            'win_shares_per_48_minutes': self.win_shares_per_48_minutes
        }
        return fields_to_include

    @property
    def dataframe(self):
        """
        Returns a ``pandas DataFrame`` containing all other relevant class
        properties and values where each index is a different season plus the
        career stats.
        """
        temp_index = self._index
        rows = []
        indices = []
        for season in self._season:
            self._index = self._season.index(season)
            rows.append(self._dataframe_fields())
            indices.append(season)
        self._index = temp_index
        return pd.DataFrame(rows, index=[indices])

    @property
    def season(self):
        """
        Returns a ``string`` of the season in the format 'YYYY-YY', such as
        '2017-18'. If no season was requested, the career stats will be
        returned for the player and the season will default to 'Career'.
        """
        return self._season[self._index]

    @property
    def team_abbreviation(self):
        """
        Returns a ``string`` of the abbrevation for the team the player plays
        for, such as 'HOU' for James Harden.
        """
        return self._team_abbreviation[self._index]

    @_most_recent_decorator
    def position(self):
        """
        Returns a ``string`` constant of the player's primary position.
        """
        return self._position

    @property
    def height(self):
        """
        Returns a ``string`` of the player's height in the format
        "feet-inches".
        """
        return self._height

    @property
    def weight(self):
        """
        Returns an ``int`` of the player's weight in pounds.
        """
        return int(self._weight.replace('lb', ''))

    @property
    def birth_date(self):
        """
        Returns a ``datetime`` object of the day and year the player was born.
        """
        return datetime.strptime(self._birth_date, '%Y-%m-%d')

    @property
    def nationality(self):
        """
        Returns a ``string`` constant denoting which country the player
        originates from.
        """
        return self._nationality

    @_int_property_decorator
    def games_played(self):
        """
        Returns an ``int`` of the number of games the player participated in.
        """
        return self._games_played

    @_int_property_decorator
    def games_started(self):
        """
        Returns an ``int`` of the number of games the player started.
        """
        return self._games_started

    @_int_property_decorator
    def two_pointers(self):
        """
        Returns an ``int`` of the total number of two point field goals the
        player made.
        """
        return self._two_pointers

    @_int_property_decorator
    def two_point_attempts(self):
        """
        Returns an ``int`` of the total number of two point field goals the
        player attempted during the season.
        """
        return self._two_point_attempts

    @_float_property_decorator
    def two_point_percentage(self):
        """
        Returns a ``float`` of the player's two point field goal percentage
        during the season. Percentage ranges from 0-1.
        """
        return self._two_point_percentage

    @_float_property_decorator
    def player_efficiency_rating(self):
        """
        Returns a ``float`` of the player's efficiency rating which represents
        the player's relative production level. An average player in the league
        has an efficiency rating of 15.
        """
        return self._player_efficiency_rating

    @_float_property_decorator
    def offensive_win_shares(self):
        """
        Returns a ``float`` of the number of wins the player contributed to the
        team as a result of his offensive plays.
        """
        return self._offensive_win_shares

    @_float_property_decorator
    def defensive_win_shares(self):
        """
        Returns a ``float`` of the number of wins the player contributed to the
        team as a result of his defensive plays.
        """
        return self._defensive_win_shares

    @_float_property_decorator
    def win_shares(self):
        """
        Returns a ``float`` of the number of wins the player contributed to the
        team as a result of his offensive and defensive plays.
        """
        return self._win_shares

    @_float_property_decorator
    def win_shares_per_48_minutes(self):
        """
        Returns a ``float`` of the number of wins the player contributed to the
        team per 48 minutes of playtime. An average player has a contribution
        of 0.100.
        """
        return self._win_shares_per_48_minutes

    @_float_property_decorator
    def offensive_box_plus_minus(self):
        """
        Returns a ``float`` of the number of offensive points per 100
        possessions the player contributed in comparison to an average player
        in the league.
        """
        return self._offensive_box_plus_minus

    @_float_property_decorator
    def defensive_box_plus_minus(self):
        """
        Returns a ``float`` of the number of defensive points per 100
        possessions the player contributed in comparison to an average player
        in the league.
        """
        return self._defensive_box_plus_minus

    @_float_property_decorator
    def value_over_replacement_player(self):
        """
        Returns a ``float`` of the total number of points per 100 team
        possessions the player contributed compared to a replacement-level
        player (who has an average score of -2.0). This value is prorated for
        an 82-game season.
        """
        return self._value_over_replacement_player

    @_float_property_decorator
    def shooting_distance(self):
        """
        Returns a ``float`` of the average distance the player takes a shot
        from in feet.
        """
        return self._shooting_distance

    @_float_property_decorator
    def percentage_shots_two_pointers(self):
        """
        Returns a ``float`` of the percentage of shots the player takes that
        are 2-pointers. Percentage ranges from 0-1.
        """
        return self._percentage_shots_two_pointers

    @_float_property_decorator
    def percentage_zero_to_three_footers(self):
        """
        Returns a ``float`` of the percentage of shots the player takes from
        zero to three feet from the basket. Percentage ranges from 0-1.
        """
        return self._percentage_zero_to_three_footers

    @_float_property_decorator
    def percentage_three_to_ten_footers(self):
        """
        Returns a ``float`` of the percentage of shots the player takes from
        three to ten feet from the basket. Percentage ranges from 0-1.
        """
        return self._percentage_three_to_ten_footers

    @_float_property_decorator
    def percentage_ten_to_sixteen_footers(self):
        """
        Returns a ``float`` of the percentage of shots the player takes from
        ten to sixteen feet from the basket. Percentage ranges from 0-1.
        """
        return self._percentage_ten_to_sixteen_footers

    @_float_property_decorator
    def percentage_sixteen_foot_plus_two_pointers(self):
        """
        Returns a ``float`` of the percentage of shots the player takes that
        are greater than sixteen feet from the basket, but in front of or on
        the three point arc. Percentage ranges from 0-1.
        """
        return self._percentage_sixteen_foot_plus_two_pointers

    @_float_property_decorator
    def percentage_shots_three_pointers(self):
        """
        Returns a ``float`` of the percentage of shots the player takes from
        beyond the three point arc. Percentage ranges from 0-1.
        """
        return self._percentage_shots_three_pointers

    @_float_property_decorator
    def field_goal_perc_zero_to_three_feet(self):
        """
        Returns a ``float`` of the player's field goal percentage for shots
        between zero and three feet from the basket. Percentage ranges from
        0-1.
        """
        return self._field_goal_perc_zero_to_three_feet

    @_float_property_decorator
    def field_goal_perc_three_to_ten_feet(self):
        """
        Returns a ``float`` of the player's field goal percentage for shots
        between three and ten feet from the basket. Percentage ranges from
        0-1.
        """
        return self._field_goal_perc_three_to_ten_feet

    @_float_property_decorator
    def field_goal_perc_ten_to_sixteen_feet(self):
        """
        Returns a ``float`` of the player's field goal percentage for shots
        between ten and sixteen feet from the basket. Percentage ranges from
        0-1.
        """
        return self._field_goal_perc_ten_to_sixteen_feet

    @_float_property_decorator
    def field_goal_perc_sixteen_foot_plus_two_pointers(self):
        """
        Returns a ``float`` of the player's field goal percentage for shots
        that are greater than sixteen feet from the basket, but in front
        of or on the three point arc. Percentage ranges from 0-1.
        """
        return self._field_goal_perc_sixteen_foot_plus_two_pointers

    @_float_property_decorator
    def two_pointers_assisted_percentage(self):
        """
        Returns a ``float`` of the percentage of 2-point field goals by the
        player that are assisted. Percentage ranges from 0-1.
        """
        return self._two_pointers_assisted_percentage

    @_float_property_decorator
    def percentage_field_goals_as_dunks(self):
        """
        Returns a ``float`` of the percentage of the player's shot attempts
        that are dunks. Percentage ranges from 0-1.
        """
        return self._percentage_field_goals_as_dunks

    @_int_property_decorator
    def dunks(self):
        """
        Returns an ``int`` of the total number of dunks the player made during
        the season.
        """
        return self._dunks

    @_float_property_decorator
    def three_pointers_assisted_percentage(self):
        """
        Returns a ``float`` of the percentage of 3-point field goals by the
        player that are assisted. Percentage ranges from 0-1.
        """
        return self._three_pointers_assisted_percentage

    @_float_property_decorator
    def percentage_of_three_pointers_from_corner(self):
        """
        Returns a ``float`` of the percentage of 3-point shots the player
        attempted from the corner. Percentage ranges from 0-1.
        """
        return self._percentage_of_three_pointers_from_corner

    @_float_property_decorator
    def three_point_shot_percentage_from_corner(self):
        """
        Returns a ``float`` of the percentage of 3-pointers from the corner
        that went in. Percentage ranges from 0-1.
        """
        return self._three_point_shot_percentage_from_corner

    @_int_property_decorator
    def half_court_heaves(self):
        """
        Returns an ``int`` of the number of shots the player took from beyond
        mid-court.
        """
        return self._half_court_heaves

    @_int_property_decorator
    def half_court_heaves_made(self):
        """
        Returns an ``int`` of the number of shots the player made from beyond
        mid-court.
        """
        return self._half_court_heaves_made

    @_int_property_decorator_default_zero
    def point_guard_percentage(self):
        """
        Returns an ``int`` of the percentage of time the player spent as a
        point guard. Percentage ranges from 0-100 and is rounded to the
        nearest whole number.
        """
        return self._point_guard_percentage

    @_int_property_decorator_default_zero
    def shooting_guard_percentage(self):
        """
        Returns an ``int`` of the percentage of time the player spent as a
        shooting guard. Percentage ranges from 0-100 and is rounded to the
        nearest whole number.
        """
        return self._shooting_guard_percentage

    @_int_property_decorator_default_zero
    def small_forward_percentage(self):
        """
        Returns an ``int`` of the percentage of time the player spent as a
        small forward. Percentage ranges from 0-100 and is rounded to the
        nearest whole number.
        """
        return self._small_forward_percentage

    @_int_property_decorator_default_zero
    def power_forward_percentage(self):
        """
        Returns an ``int`` of the percentage of time the player spent as a
        power forward. Percentage ranges from 0-100 and is rounded to the
        nearest whole number.
        """
        return self._power_forward_percentage

    @_int_property_decorator_default_zero
    def center_percentage(self):
        """
        Returns an ``int`` of the percentage of time the player spent as a
        center. Percentage ranges from 0-100 and is rounded to the nearest
        whole number.
        """
        return self._center_percentage

    @_float_property_decorator
    def on_court_plus_minus(self):
        """
        Returns a ``float`` of the number of points the player contributes to
        the team while on the court per 100 possessions.
        """
        return self._on_court_plus_minus

    @_float_property_decorator
    def net_plus_minus(self):
        """
        Returns a ``float`` of the net number of points the player contributes
        to the team per 100 possessions regardless of being on the floor or
        not.
        """
        return self._net_plus_minus

    @_int_property_decorator
    def passing_turnovers(self):
        """
        Returns an ``int`` of the total number of turnovers the player
        committed due to a bad pass.
        """
        return self._passing_turnovers

    @_int_property_decorator
    def lost_ball_turnovers(self):
        """
        Returns an ``int`` of the total number of turnovers the player
        committed due to losing the ball.
        """
        return self._lost_ball_turnovers

    @_int_property_decorator
    def other_turnovers(self):
        """
        Returns an ``int`` of the total number of all other non-passing/
        dribbling turnovers the player committed.
        """
        return self._other_turnovers

    @_int_property_decorator
    def shooting_fouls(self):
        """
        Returns an ``int`` of the total number of shooting fouls the player
        committed.
        """
        return self._shooting_fouls

    @_int_property_decorator
    def blocking_fouls(self):
        """
        Returns an ``int`` of the total number of blocking fouls the player
        committed.
        """
        return self._blocking_fouls

    @_int_property_decorator
    def offensive_fouls(self):
        """
        Returns an ``int`` of the total number of offensive fouls the player
        committed.
        """
        return self._offensive_fouls

    @_int_property_decorator
    def take_fouls(self):
        """
        Returns an ``int`` of the total number of take fouls the player
        committed by taking a foul before the offensive player has a chance to
        make a shooting motion.
        """
        return self._take_fouls

    @_int_property_decorator
    def points_generated_by_assists(self):
        """
        Returns an ``int`` of the total number of points the player generated
        as a result of him assisting the shooter.
        """
        return self._points_generated_by_assists

    @_int_property_decorator
    def shooting_fouls_drawn(self):
        """
        Returns an ``int`` of the total number of shooting fouls the player
        drew during the season.
        """
        return self._shooting_fouls_drawn

    @_int_property_decorator
    def and_ones(self):
        """
        Returns an ``int`` of the total number of times the player was fouled
        in the act of shooting and made the basket.
        """
        return self._and_ones

    @_int_property_decorator
    def shots_blocked(self):
        """
        Returns an ``int`` of the total number of shots the player took that
        were blocked by an opposing player.
        """
        return self._shots_blocked

    @_int_property_decorator
    def salary(self):
        """
        Returns an ``int`` of the player's annual salary rounded down.
        """
        return self._salary

    @property
    def contract(self):
        """
        Returns a ``dictionary`` of the player's contract details where the key
        is a ``string`` of the season, such as '2018-19', and the value is a
        ``string`` of the salary, such as '$40,000,000'.
        """
        return self._contract


class Roster:
    """
    Get stats for all players on a roster.

    Request a team's roster for a given season and create instances of the
    Player class for each player, containing a detailed list of the players
    statistics and information.

    Parameters
    ----------
    team : string
        The team's 3-letter abbreviation, such as 'HOU' for the Houston
        Rockets.
    year : string (optional)
        The 4-digit year to pull the roster from, such as '2018'. If left
        blank, defaults to the most recent season.
    slim : boolean (optional)
        Set to True to return a limited subset of player information including
        the name and player ID for each player as opposed to all of their
        respective stats which greatly reduces the time to return a response if
        just the names and IDs are desired. Defaults to False.
    """
    def __init__(self, team, year=None, slim=False):
        self._team = team
        self._slim = slim
        if slim:
            self._players = {}
        else:
            self._players = []

        self._find_players(year)

    def _pull_team_page(self, url):
        """
        Download the team page.

        Download the requested team's season page and create a PyQuery object.

        Parameters
        ----------
        url : string
            A string of the built URL for the requested team and season.

        Returns
        -------
        PyQuery object
            Returns a PyQuery object of the team's HTML page.
        """
        try:
            return pq(url)
        except HTTPError:
            return None

    def _create_url(self, year):
        """
        Build the team URL.

        Build a URL given a team's 3-letter abbreviation and the 4-digit year.

        Parameters
        ----------
        year : string
            The 4-digit string representing the year to pull the team's roster
            from.

        Returns
        -------
        string
            Returns a string of the team's season page for the requested team
            and year.
        """
        return ROSTER_URL % (self._team.upper(), year)

    def _get_id(self, player):
        """
        Parse the player ID.

        Given a PyQuery object representing a single player on the team roster,
        parse the player ID and return it as a string.

        Parameters
        ----------
        player : PyQuery object
            A PyQuery object representing the player information from the
            roster table.

        Returns
        -------
        string
            Returns a string of the player ID.
        """
        name_tag = player('td[data-stat="player"] a')
        name = re.sub(r'.*/players/./', '', str(name_tag))
        return re.sub(r'\.html.*', '', name)

    def _get_name(self, player):
        """
        Parse the player's name.

        Given a PyQuery object representing a single player on the team roster,
        parse the player ID and return it as a string.

        Parameters
        ----------
        player : PyQuery object
            A PyQuery object representing the player information from the
            roster table.

        Returns
        -------
        string
            Returns a string of the player's name.
        """
        name_tag = player('td[data-stat="player"] a')
        return name_tag.text()

    def _find_players(self, year):
        """
        Find all player IDs for the requested team.

        For the requested team and year (if applicable), pull the roster table
        and parse the player ID for all players on the roster and create an
        instance of the Player class for the player. All player instances are
        added to the 'players' property to get all stats for all players on a
        team.

        Parameters
        ----------
        year : string
            The 4-digit string representing the year to pull the team's roster
            from.
        """
        if not year:
            year = utils._find_year_for_season('nba')
            # If stats for the requested season do not exist yet (as is the
            # case right before a new season begins), attempt to pull the
            # previous year's stats. If it exists, use the previous year
            # instead.
            if not utils._url_exists(self._create_url(year)) and \
               utils._url_exists(self._create_url(str(int(year) - 1))):
                year = str(int(year) - 1)
        url = self._create_url(year)
        page = self._pull_team_page(url)
        if not page:
            output = ("Can't pull requested team page. Ensure the following "
                      "URL exists: %s" % url)
            raise ValueError(output)
        players = page('table#roster tbody tr').items()
        for player in players:
            player_id = self._get_id(player)
            if not player_id or player_id == '':
                continue  # pragma: no cover
            if self._slim:
                name = self._get_name(player)
                self._players[player_id] = name
            else:
                player_instance = Player(player_id)
                self._players.append(player_instance)

    @property
    def players(self):
        """
        Returns a ``list`` of player instances for each player on the requested
        team's roster if the ``slim`` property is False when calling the Roster
        class. If the ``slim`` property is True, returns a ``dictionary`` where
        each key is a string of the player's ID and each value is the player's
        first and last name as listed on the roster page.
        """
        return self._players
