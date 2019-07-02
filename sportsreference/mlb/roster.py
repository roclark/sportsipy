import pandas as pd
import re
from functools import wraps
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from .constants import (NATIONALITY,
                        PLAYER_ELEMENT_INDEX,
                        PLAYER_SCHEME,
                        PLAYER_URL,
                        ROSTER_URL)
from .player import AbstractPlayer


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
        try:
            value = _cleanup(prop[index][element_ind])
            return float(value)
        except (ValueError, TypeError, IndexError):
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
        element_ind = 0
        try:
            return prop[index][element_ind]
        except (TypeError, IndexError):
            # If there is no value, default to None
            return None
    return wrapper


class Player(AbstractPlayer):
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
        self._contract = None
        self._games = None
        self._games_started = None
        self._plate_appearances = None
        self._at_bats = None
        self._runs = None
        self._hits = None
        self._doubles = None
        self._triples = None
        self._home_runs = None
        self._runs_batted_in = None
        self._stolen_bases = None
        self._times_caught_stealing = None
        self._bases_on_balls = None
        self._times_struck_out = None
        self._batting_average = None
        self._on_base_percentage = None
        self._slugging_percentage = None
        self._on_base_plus_slugging_percentage = None
        self._on_base_plus_slugging_percentage_plus = None
        self._total_bases = None
        self._grounded_into_double_plays = None
        self._times_hit_by_pitch = None
        self._sacrifice_hits = None
        self._sacrifice_flies = None
        self._intentional_bases_on_balls = None
        self._complete_games = None
        self._innings_played = None
        self._defensive_chances = None
        self._putouts = None
        self._assists = None
        self._errors = None
        self._double_plays_turned = None
        self._fielding_percentage = None
        self._total_fielding_runs_above_average = None
        self._defensive_runs_saved_above_average = None
        self._total_fielding_runs_above_average_per_innings = None
        self._defensive_runs_saved_above_average_per_innings = None
        self._range_factor_per_nine_innings = None
        self._range_factor_per_game = None
        self._league_fielding_percentage = None
        self._league_range_factor_per_nine_innings = None
        self._league_range_factor_per_game = None
        self._games_in_batting_order = None
        self._games_in_defensive_lineup = None
        self._games_pitcher = None
        self._games_catcher = None
        self._games_first_baseman = None
        self._games_second_baseman = None
        self._games_third_baseman = None
        self._games_shortstop = None
        self._games_left_fielder = None
        self._games_center_fielder = None
        self._games_right_fielder = None
        self._games_outfielder = None
        self._games_designated_hitter = None
        self._games_pinch_hitter = None
        self._games_pinch_runner = None
        # Stats specific to pitchers
        self._wins = None
        self._losses = None
        self._win_percentage = None
        self._era = None
        self._games_finished = None
        self._shutouts = None
        self._saves = None
        self._hits_allowed = None
        self._runs_allowed = None
        self._earned_runs_allowed = None
        self._home_runs_allowed = None
        self._bases_on_balls_given = None
        self._intentional_bases_on_balls_given = None
        self._strikeouts = None
        self._times_hit_player = None
        self._balks = None
        self._wild_pitches = None
        self._batters_faced = None
        self._era_plus = None
        self._fielding_independent_pitching = None
        self._whip = None
        self._hits_against_per_nine_innings = None
        self._home_runs_against_per_nine_innings = None
        self._bases_on_balls_given_per_nine_innings = None
        self._batters_struckout_per_nine_innings = None
        self._strikeouts_thrown_per_walk = None

        player_data = self._pull_player_data()
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
            A string representation of the season in the format 'YYYY', such as
            '2017'.
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
            season ``string``, such as '2017', and the value is a
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
            # For now, remove minor-league stats
            if 'class="minors_table hidden"' in str(row) or \
               'class="spacer partial_table"' in str(row) or \
               'class="partial_table"' in str(row):
                continue
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

        for table_id in ['batting_standard', 'standard_fielding',
                         'appearances', 'pitching_standard']:
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

    def _parse_team_name(self, team):
        """
        Parse the team name in the contract table.

        The team names in the contract table should be pulled in plain text and
        returned as a string.

        Parameters
        ----------
        team : string
            A string representing the team_name tag in a row in the player's
            contract table.

        Returns
        -------
        string
            A string of the team's name, such as 'Houston Astros'.
        """
        team = team.replace('\xa0', ' ')
        team_html = pq(team)
        return team_html.text()

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
        contract = {}

        salary_table = player_info('table#br-salaries')
        for row in salary_table('tbody tr').items():
            if 'class="spacer partial_table"' in str(row):
                continue
            year = row('th[data-stat="year_ID"]').text()
            if year.strip() == '':
                continue
            age = row('td[data-stat="age"]').text()
            team = self._parse_team_name(str(row('td[data-stat="team_name"]')))
            salary = row('td[data-stat="Salary"]').text()
            contract[year] = {
                'age': age,
                'team': team,
                'salary': salary
            }
        setattr(self, '_contract', contract)

    def _parse_value(self, html_data, field):
        """
        Parse the HTML table to find the requested field's value.

        All of the values are passed in an HTML table row instead of as
        individual items. The values need to be parsed by matching the
        requested attribute with a parsing scheme that sports-reference uses
        to differentiate stats. This function returns a single value for the
        given attribute.

        Parameters
        ----------
        html_data : string
            A string containing all of the rows of stats for a given team. If
            multiple tables are being referenced, this will be comprised of
            multiple rows in a single string.
        field : string
            The name of the attribute to match. Field must be a key in the
            PLAYER_SCHEME dictionary.

        Returns
        -------
        list
            A list of all values that match the requested field. If no value
            could be found, returns None.
        """
        scheme = PLAYER_SCHEME[field]
        items = [i.text() for i in html_data(scheme).items()]
        # Stats can be added and removed on a yearly basis. If no stats are
        # found, return None and have that be the value.
        if len(items) == 0:
            return None
        return items

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
        self._parse_player_information(player_info)
        self._parse_nationality(player_info)
        self._parse_birth_date(player_info)
        self._parse_contract(player_info)
        all_stats = self._combine_all_stats(player_info)
        setattr(self, '_season', list(all_stats.keys()))
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
            # The career stats default to Nonetype
            if season is None or season == 'Career':
                self._index = index
                self._season[index] = 'Career'
                break
            index += 1

    def __call__(self, requested_season=''):
        """
        Specify a different season to pull stats from.

        A different season can be requested by passing the season string, such
        as '2017' to the class instance.

        Parameters
        ----------
        requested_season : string (optional)
            A string of the requested season to query, such as '2017'. If left
            blank or 'Career' is passed, the career stats will be used for
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
            'assists': self.assists,
            'at_bats': self.at_bats,
            'bases_on_balls': self.bases_on_balls,
            'batting_average': self.batting_average,
            'birth_date': self.birth_date,
            'complete_games': self.complete_games,
            'defensive_chances': self.defensive_chances,
            'defensive_runs_saved_above_average':
            self.defensive_runs_saved_above_average,
            'defensive_runs_saved_above_average_per_innings':
            self.defensive_runs_saved_above_average_per_innings,
            'double_plays_turned': self.double_plays_turned,
            'doubles': self.doubles,
            'errors': self.errors,
            'fielding_percentage': self.fielding_percentage,
            'games': self.games,
            'games_catcher': self.games_catcher,
            'games_center_fielder': self.games_center_fielder,
            'games_designated_hitter': self.games_designated_hitter,
            'games_first_baseman': self.games_first_baseman,
            'games_in_batting_order': self.games_in_batting_order,
            'games_in_defensive_lineup': self.games_in_defensive_lineup,
            'games_left_fielder': self.games_left_fielder,
            'games_outfielder': self.games_outfielder,
            'games_pinch_hitter': self.games_pinch_hitter,
            'games_pinch_runner': self.games_pinch_runner,
            'games_pitcher': self.games_pitcher,
            'games_right_fielder': self.games_right_fielder,
            'games_second_baseman': self.games_second_baseman,
            'games_shortstop': self.games_shortstop,
            'games_started': self.games_started,
            'games_third_baseman': self.games_third_baseman,
            'grounded_into_double_plays': self.grounded_into_double_plays,
            'height': self.height,
            'hits': self.hits,
            'home_runs': self.home_runs,
            'innings_played': self.innings_played,
            'intentional_bases_on_balls': self.intentional_bases_on_balls,
            'league_fielding_percentage': self.league_fielding_percentage,
            'league_range_factor_per_game': self.league_range_factor_per_game,
            'league_range_factor_per_nine_innings':
            self.league_range_factor_per_nine_innings,
            'name': self.name,
            'nationality': self.nationality,
            'on_base_percentage': self.on_base_percentage,
            'on_base_plus_slugging_percentage':
            self.on_base_plus_slugging_percentage,
            'on_base_plus_slugging_percentage_plus':
            self.on_base_plus_slugging_percentage_plus,
            'plate_appearances': self.plate_appearances,
            'player_id': self.player_id,
            'position': self.position,
            'putouts': self.putouts,
            'range_factor_per_game': self.range_factor_per_game,
            'range_factor_per_nine_innings':
            self.range_factor_per_nine_innings,
            'runs': self.runs,
            'runs_batted_in': self.runs_batted_in,
            'sacrifice_flies': self.sacrifice_flies,
            'sacrifice_hits': self.sacrifice_hits,
            'season': self.season,
            'slugging_percentage': self.slugging_percentage,
            'stolen_bases': self.stolen_bases,
            'team_abbreviation': self.team_abbreviation,
            'times_caught_stealing': self.times_caught_stealing,
            'times_hit_by_pitch': self.times_hit_by_pitch,
            'times_struck_out': self.times_struck_out,
            'total_bases': self.total_bases,
            'total_fielding_runs_above_average':
            self.total_fielding_runs_above_average,
            'total_fielding_runs_above_average_per_innings':
            self.total_fielding_runs_above_average_per_innings,
            'triples': self.triples,
            'weight': self.weight,
            # Properties specific to pitchers
            'balks': self.balks,
            'bases_on_balls_given': self.bases_on_balls_given,
            'bases_on_balls_given_per_nine_innings':
            self.bases_on_balls_given_per_nine_innings,
            'batters_faced': self.batters_faced,
            'batters_struckout_per_nine_innings':
            self.batters_struckout_per_nine_innings,
            'earned_runs_allowed': self.earned_runs_allowed,
            'era': self.era,
            'era_plus': self.era_plus,
            'fielding_independent_pitching':
            self.fielding_independent_pitching,
            'games_finished': self.games_finished,
            'hits_against_per_nine_innings':
            self.hits_against_per_nine_innings,
            'hits_allowed': self.hits_allowed,
            'home_runs_against_per_nine_innings':
            self.home_runs_against_per_nine_innings,
            'home_runs_allowed': self.home_runs_allowed,
            'intentional_bases_on_balls_given':
            self.intentional_bases_on_balls_given,
            'losses': self.losses,
            'runs_allowed': self.runs_allowed,
            'saves': self.saves,
            'shutouts': self.shutouts,
            'strikeouts': self.strikeouts,
            'strikeouts_thrown_per_walk': self.strikeouts_thrown_per_walk,
            'times_hit_player': self.times_hit_player,
            'whip': self.whip,
            'wild_pitches': self.wild_pitches,
            'win_percentage': self.win_percentage,
            'wins': self.wins
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
        Returns a ``string`` of the season in the format 'YYYY', such as
        '2017'. If no season was requsted, the career stats will be
        returned for the player and the season will default to 'Career'.
        """
        return self._season[self._index]

    @property
    def name(self):
        """
        Returns a ``string`` of the player's name, such as 'Jose Altuve'.
        """
        return self._name

    @_most_recent_decorator
    def team_abbreviation(self):
        """
        Returns a ``string`` of the team's abbreviation, such as 'HOU' for the
        Houston Astros.
        """
        return self._team_abbreviation

    @_most_recent_decorator
    def position(self):
        """
        Returns a ``string`` constant of the player's primary position.
        """
        return self._position

    @property
    def height(self):
        """
        Returns a ``string`` of the players height in the format "feet-inches".
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
        return self._birth_date

    @property
    def nationality(self):
        """
        Returns a ``string`` constant denoting which country the player
        originiates from.
        """
        return self._nationality

    @property
    def contract(self):
        """
        Returns a ``dictionary`` of the player's contract where each key is a
        ``string`` of the year, such as '2017' and each value is a
        ``dictionary`` with the ``string`` key-value pairs of the player's age,
        team name, and salary.
        """
        return self._contract

    @_int_property_decorator
    def games(self):
        """
        Returns an ``int`` of the number of games the player participated in.
        """
        return self._games

    @_int_property_decorator
    def games_started(self):
        """
        Returns an ``int`` of the number of games the player started.
        """
        return self._games_started

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
    def doubles(self):
        """
        Returns an ``int`` of the number of doubles the player hit.
        """
        return self._doubles

    @_int_property_decorator
    def triples(self):
        """
        Returns an ``int`` of the number of triples the player hit.
        """
        return self._triples

    @_int_property_decorator
    def home_runs(self):
        """
        Returns an ``int`` of the number of home runs the player hit.
        """
        return self._home_runs

    @_int_property_decorator
    def runs_batted_in(self):
        """
        Returns an ``int`` of the number of runs batted in the player
        registered.
        """
        return self._runs_batted_in

    @_int_property_decorator
    def stolen_bases(self):
        """
        Returns an ``int`` of the number of bases the player has stolen.
        """
        return self._stolen_bases

    @_int_property_decorator
    def times_caught_stealing(self):
        """
        Returns an ``int`` of the number of times the player was caught
        stealing.
        """
        return self._times_caught_stealing

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
    def on_base_plus_slugging_percentage_plus(self):
        """
        Returns an ``int`` of the on base percentage plus the slugging
        percentage, adjusted to the player's ballpark.
        """
        return self._on_base_plus_slugging_percentage_plus

    @_int_property_decorator
    def total_bases(self):
        """
        Returns an ``int`` of the number of bases the player has gained.
        """
        return self._total_bases

    @_int_property_decorator
    def grounded_into_double_plays(self):
        """
        Returns an ``int`` of the number of double plays the player grounded
        into.
        """
        return self._grounded_into_double_plays

    @_int_property_decorator
    def times_hit_by_pitch(self):
        """
        Returns an ``int`` of the number of times the player has been hit by a
        pitch.
        """
        return self._times_hit_by_pitch

    @_int_property_decorator
    def sacrifice_hits(self):
        """
        Returns an ``int`` of the number of sacrifice hits or sacrafice bunts
        the player made.
        """
        return self._sacrifice_hits

    @_int_property_decorator
    def sacrifice_flies(self):
        """
        Returns an ``int`` of the number of sacrifice flies the player hit.
        """
        return self._sacrifice_flies

    @_int_property_decorator
    def intentional_bases_on_balls(self):
        """
        Returns an ``int`` of the number of times the player has been
        intentionally walked by the opposition.
        """
        return self._intentional_bases_on_balls

    @_int_property_decorator
    def complete_games(self):
        """
        Returns an ``int`` of the number of complete games the player has
        participated in.
        """
        return self._complete_games

    @_float_property_decorator
    def innings_played(self):
        """
        Returns a ``float`` of the total number of innings the player has
        played in.
        """
        return self._innings_played

    @_int_property_decorator
    def defensive_chances(self):
        """
        Returns an ``int`` of the number of defensive chances (equal to the
        number of putouts + assists + errors) the player had.
        """
        return self._defensive_chances

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
    def errors(self):
        """
        Returns an ``int`` of the number of errors the player made.
        """
        return self._errors

    @_int_property_decorator
    def double_plays_turned(self):
        """
        Returns an ``int`` of the number of double plays the player was
        involved in.
        """
        return self._double_plays_turned

    @_float_property_decorator
    def fielding_percentage(self):
        """
        Returns a ``float`` of the players fielding percentage, equivalent to
        (putouts + assists) / (putouts + assists + errors). Percentage ranges
        from 0-1.
        """
        return self._fielding_percentage

    @_int_property_decorator
    def total_fielding_runs_above_average(self):
        """
        Returns an ``int`` of the number of runs the player was worth compared
        to an average player.
        """
        return self._total_fielding_runs_above_average

    @_int_property_decorator
    def defensive_runs_saved_above_average(self):
        """
        Returns an ``int`` of the number of defensive runs the player saved
        compared to an average player.
        """
        return self._defensive_runs_saved_above_average

    @_int_property_decorator
    def total_fielding_runs_above_average_per_innings(self):
        """
        Returns an ``int`` of the number of runs the player was worth per 1,200
        innings compared to an average player.
        """
        return self._total_fielding_runs_above_average_per_innings

    @_int_property_decorator
    def defensive_runs_saved_above_average_per_innings(self):
        """
        Returns an ``int`` of the number of defensive runs the player was worth
        per 1,200 innings compared to an average player.
        """
        return self._defensive_runs_saved_above_average_per_innings

    @_float_property_decorator
    def range_factor_per_nine_innings(self):
        """
        Returns a ``float`` of the players range factor per nine innings, equal
        to 9 * (putouts + assists) / innings_played.
        """
        return self._range_factor_per_nine_innings

    @_float_property_decorator
    def range_factor_per_game(self):
        """
        Returns a ``float`` of the players range factor per game, equal to 9 *
        (putouts + assists) / games_played.
        """
        return self._range_factor_per_game

    @_float_property_decorator
    def league_fielding_percentage(self):
        """
        Returns a ``float`` of the average fielding percentage for the league
        at the player's position. Percentage ranges from 0-1.
        """
        return self._league_fielding_percentage

    @_float_property_decorator
    def league_range_factor_per_nine_innings(self):
        """
        Returns a ``float`` of the average range factor for the league per nine
        innings, equal to 9 * (putouts + assists) / innings_played.
        """
        return self._league_range_factor_per_nine_innings

    @_float_property_decorator
    def league_range_factor_per_game(self):
        """
        Returns a ``float`` of the average range factor for the league per
        game, equal to (putouts + assists) / games_played.
        """
        return self._league_range_factor_per_game

    @_int_property_decorator
    def games_in_batting_order(self):
        """
        Returns an ``int`` of the number of games the player was in the batting
        lineup.
        """
        return self._games_in_batting_order

    @_int_property_decorator
    def games_in_defensive_lineup(self):
        """
        Returns an ``int`` of the number of games the player was in the
        defensive lineup.
        """
        return self._games_in_defensive_lineup

    @_int_property_decorator
    def games_pitcher(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a pitcher.
        """
        return self._games_pitcher

    @_int_property_decorator
    def games_catcher(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a catcher.
        """
        return self._games_catcher

    @_int_property_decorator
    def games_first_baseman(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a first baseman.
        """
        return self._games_first_baseman

    @_int_property_decorator
    def games_second_baseman(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a second baseman.
        """
        return self._games_second_baseman

    @_int_property_decorator
    def games_third_baseman(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a third baseman.
        """
        return self._games_third_baseman

    @_int_property_decorator
    def games_shortstop(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a shortstop.
        """
        return self._games_shortstop

    @_int_property_decorator
    def games_left_fielder(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a left fielder.
        """
        return self._games_left_fielder

    @_int_property_decorator
    def games_center_fielder(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a center fielder.
        """
        return self._games_center_fielder

    @_int_property_decorator
    def games_right_fielder(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a right fielder.
        """
        return self._games_right_fielder

    @_int_property_decorator
    def games_outfielder(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as an outfielder.
        """
        return self._games_outfielder

    @_int_property_decorator
    def games_designated_hitter(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a designated hitter.
        """
        return self._games_designated_hitter

    @_int_property_decorator
    def games_pinch_hitter(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a pinch hitter.
        """
        return self._games_pinch_hitter

    @_int_property_decorator
    def games_pinch_runner(self):
        """
        Returns an ``int`` of the number of games the player was in the lineup
        as a pinch runner.
        """
        return self._games_pinch_runner

    @_int_property_decorator
    def wins(self):
        """
        Returns an ``int`` of the number of games the player has won as a
        pitcher.
        """
        return self._wins

    @_int_property_decorator
    def losses(self):
        """
        Returns an ``int`` of the number of games the player has lost as a
        pitcher.
        """
        return self._losses

    @_float_property_decorator
    def win_percentage(self):
        """
        Returns a ``float`` of the players winning percentage as a pitcher.
        Percentage ranges from 0-1.
        """
        return self._win_percentage

    @_float_property_decorator
    def era(self):
        """
        Returns a ``float`` of the pitcher's Earned Runs Average.
        """
        return self._era

    @_int_property_decorator
    def games_finished(self):
        """
        Returns an ``int`` of the number of games the player finished as a
        pitcher.
        """
        return self._games_finished

    @_int_property_decorator
    def shutouts(self):
        """
        Returns an ``int`` of the number of times the player did not allow any
        runs and threw a complete game as a pitcher.
        """
        return self._shutouts

    @_int_property_decorator
    def saves(self):
        """
        Returns an ``int`` of the number of saves the player made as a pitcher.
        """
        return self._saves

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
    def home_runs_allowed(self):
        """
        Returns an ``int`` of the number of home runs a player has allowed as a
        pitcher.
        """
        return self._home_runs_allowed

    @_int_property_decorator
    def bases_on_balls_given(self):
        """
        Returns an ``int`` of the number of bases on balls the player has given
        as a pitcher.
        """
        return self._bases_on_balls_given

    @_int_property_decorator
    def intentional_bases_on_balls_given(self):
        """
        Returns an ``int`` of the number of bases the player has intentionally
        given as a pitcher.
        """
        return self._intentional_bases_on_balls_given

    @_int_property_decorator
    def strikeouts(self):
        """
        Returns an ``int`` of the number of strikeouts the player threw as a
        pitcher.
        """
        return self._strikeouts

    @_int_property_decorator
    def times_hit_player(self):
        """
        Returns an ``int`` of the number of times the pitcher hit a player with
        a pitch.
        """
        return self._times_hit_player

    @_int_property_decorator
    def balks(self):
        """
        Returns an ``int`` of the number of times the pitcher balked.
        """
        return self._balks

    @_int_property_decorator
    def wild_pitches(self):
        """
        Returns an ``int`` of the number of wild pitches the player has thrown.
        """
        return self._wild_pitches

    @_float_property_decorator
    def era_plus(self):
        """
        Returns a ``float`` of the pitcher's ERA while adjusted for the
        ballpark.
        """
        return self._era_plus

    @_float_property_decorator
    def fielding_independent_pitching(self):
        """
        Returns a ``float`` of the pitcher's effectiveness at preventing home
        runs, bases on balls, and hitting players with pitches, while causing
        strikeouts.
        """
        return self._fielding_independent_pitching

    @_float_property_decorator
    def whip(self):
        """
        Returns a ``float`` of the pitcher's WHIP score, equivalent to (bases
        on balls + hits) / innings played.
        """
        return self._whip

    @_float_property_decorator
    def hits_against_per_nine_innings(self):
        """
        Returns a ``float`` of the number of hits the player has given per nine
        innings played.
        """
        return self._hits_against_per_nine_innings

    @_float_property_decorator
    def home_runs_against_per_nine_innings(self):
        """
        Returns a ``float`` of the number of home runs the pitcher has given
        per nine innings played.
        """
        return self._home_runs_against_per_nine_innings

    @_float_property_decorator
    def bases_on_balls_given_per_nine_innings(self):
        """
        Returns a ``float`` of the number of bases on balls the pitcher has
        given per nine innings played.
        """
        return self._bases_on_balls_given_per_nine_innings

    @_float_property_decorator
    def batters_struckout_per_nine_innings(self):
        """
        Returns a ``float`` of the number of batters the pitcher has struck out
        per nine innings played.
        """
        return self._batters_struckout_per_nine_innings

    @_float_property_decorator
    def strikeouts_thrown_per_walk(self):
        """
        Returns a ``float`` of the number of batters the pitcher has struck out
        per the number of walks given.
        """
        return self._strikeouts_thrown_per_walk


class Roster:
    """
    Get stats for all players on a roster.

    Request a team's roster for a given season and create instances of the
    Player class for each player, containing a detailed list of the players
    statistics and information.

    Parameters
    ----------
    team : string
        The team's abbreviation, such as 'HOU' for the Houston Astros.
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

        Build a URL given a team's abbreviation and the 4-digit year.

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
        return re.sub(r'\.shtml.*', '', name)

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
            year = utils._find_year_for_season('mlb')
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
        players = page('table#team_batting tbody tr').items()
        players_parsed = []
        for player in players:
            if 'class="thead"' in str(player):
                continue
            player_id = self._get_id(player)
            if self._slim:
                name = self._get_name(player)
                self._players[player_id] = name
            else:
                player_instance = Player(player_id)
                self._players.append(player_instance)
            players_parsed.append(player_id)
        for player in page('table#team_pitching tbody tr').items():
            if 'class="thead"' in str(player):
                continue
            player_id = self._get_id(player)
            # Skip players that showup in both batting and pitching tables, as
            # is often the case with National League pitchers.
            if player_id in players_parsed:
                continue
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
