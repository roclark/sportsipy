import pandas as pd
from functools import wraps
from lxml.etree import ParserError, XMLSyntaxError
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from .constants import PLAYER_SCHEME, PLAYER_URL, ROSTER_URL
from .player import AbstractPlayer


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


class Player(AbstractPlayer):
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
    """
    def __init__(self, player_id):
        self._most_recent_season = ''
        self._index = None
        self._player_id = player_id
        self._season = None
        self._name = None
        self._team_abbreviation = None
        self._height = None
        self._weight = None
        self._age = None
        self._league = None
        self._games_played = None
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
        self._total_shots = None
        self._time_on_ice = None
        self._average_time_on_ice = None
        self._faceoff_wins = None
        self._faceoff_losses = None
        self._faceoff_percentage = None
        self._blocks_at_even_strength = None
        self._hits_at_even_strength = None
        self._takeaways = None
        self._giveaways = None
        # Possession Metrics
        self._time_on_ice_even_strength = None
        self._corsi_for = None
        self._corsi_against = None
        self._corsi_for_percentage = None
        self._relative_corsi_for_percentage = None
        self._fenwick_for = None
        self._fenwick_against = None
        self._fenwick_for_percentage = None
        self._relative_fenwick_for_percentage = None
        self._goals_for_on_ice = None
        self._shooting_percentage_on_ice = None
        self._goals_against_on_ice = None
        self._save_percentage_on_ice = None
        self._pdo = None
        self._offensive_zone_start_percentage = None
        self._defensive_zone_start_percentage = None
        # Miscellaneous
        self._goals_created = None
        self._adjusted_goals = None
        self._adjusted_assists = None
        self._adjusted_points = None
        self._adjusted_goals_created = None
        self._total_goals_for_on_ice = None
        self._power_play_goals_for_on_ice = None
        self._total_goals_against_on_ice = None
        self._power_play_goals_against_on_ice = None
        self._offensive_point_shares = None
        self._defensive_point_shares = None
        self._point_shares = None
        self._shootout_attempts = None
        self._shootout_goals = None
        self._shootout_misses = None
        self._shootout_percentage = None
        # Goalie Metrics
        self._wins = None
        self._losses = None
        self._ties_plus_overtime_loss = None
        self._goals_against = None
        self._shots_against = None
        self._saves = None
        self._save_percentage = None
        self._goals_against_average = None
        self._shutouts = None
        self._minutes = None
        self._quality_starts = None
        self._quality_start_percentage = None
        self._really_bad_starts = None
        self._goal_against_percentage_relative = None
        self._goals_saved_above_average = None
        self._adjusted_goals_against_average = None
        self._goalie_point_shares = None
        self._even_strength_shots_faced = None
        self._even_strength_goals_allowed = None
        self._even_strength_save_percentage = None
        self._power_play_shots_faced = None
        self._power_play_goals_allowed = None
        self._power_play_save_percentage = None
        self._short_handed_shots_faced = None
        self._short_handed_goals_allowed = None
        self._short_handed_save_percentage = None

        player_data = self._pull_player_data()
        if not player_data:
            return
        self._find_initial_index()
        AbstractPlayer.__init__(self, player_id, self._name, player_data)

    def _build_url(self):
        """
        Create the player's URL to pull stats from.

        The player's URL requires the player ID.

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
        returning a PyQuery object which will be used to parse the data.
        Oftentimes, important data is contained in tables which are hidden in
        HTML comments and not accessible via PyQuery.

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
        and should be parsed to detonate which season metrics are being pulled
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
        season = utils._parse_field(PLAYER_SCHEME, row, 'season')
        return season.replace('*', '').replace('+', '')

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
        Pull stats from all tables into a single data structure.

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

        for table_id in ['stats_basic_plus_nhl', 'skaters_advanced',
                         'stats_misc_plus_nhl', 'stats_goalie_situational']:
            table_items = utils._get_stats_table(player_info,
                                                 'table#%s' % table_id)
            career_items = utils._get_stats_table(player_info,
                                                  'table#%s' % table_id,
                                                  footer=True)
            all_stats_dict = self._combine_season_stats(table_items,
                                                        career_items,
                                                        all_stats_dict)
        return all_stats_dict

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
        all_stats = self._combine_all_stats(player_info)
        setattr(self, '_season', list(all_stats.keys()))
        return all_stats

    def _find_initial_index(self):
        """
        Find the index of the career stats.

        When the Player class is instantiated, the default stats to pull are
        the player's career stats. Upon being called, the index of the 'Career'
        element should be the index value.
        """
        index = 0
        for season in self._season or season == 'Career':
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
            'adjusted_assists': self.adjusted_assists,
            'adjusted_goals': self.adjusted_goals,
            'adjusted_goals_against_average':
            self.adjusted_goals_against_average,
            'adjusted_goals_created': self.adjusted_goals_created,
            'adjusted_points': self.adjusted_points,
            'age': self.age,
            'assists': self.assists,
            'average_time_on_ice': self.average_time_on_ice,
            'blocks_at_even_strength': self.blocks_at_even_strength,
            'corsi_against': self.corsi_against,
            'corsi_for': self.corsi_for,
            'corsi_for_percentage': self.corsi_for_percentage,
            'defensive_point_shares': self.defensive_point_shares,
            'defensive_zone_start_percentage':
            self.defensive_zone_start_percentage,
            'even_strength_assists': self.even_strength_assists,
            'even_strength_goals': self.even_strength_goals,
            'even_strength_goals_allowed': self.even_strength_goals_allowed,
            'even_strength_save_percentage':
            self.even_strength_save_percentage,
            'even_strength_shots_faced': self.even_strength_shots_faced,
            'faceoff_losses': self.faceoff_losses,
            'faceoff_percentage': self.faceoff_percentage,
            'faceoff_wins': self.faceoff_wins,
            'fenwick_against': self.fenwick_against,
            'fenwick_for': self.fenwick_for,
            'fenwick_for_percentage': self.fenwick_for_percentage,
            'game_winning_goals': self.game_winning_goals,
            'games_played': self.games_played,
            'giveaways': self.giveaways,
            'goal_against_percentage_relative':
            self.goal_against_percentage_relative,
            'goalie_point_shares': self.goalie_point_shares,
            'goals': self.goals,
            'goals_against': self.goals_against,
            'goals_against_average': self.goals_against_average,
            'goals_against_on_ice': self.goals_against_on_ice,
            'goals_created': self.goals_created,
            'goals_for_on_ice': self.goals_for_on_ice,
            'goals_saved_above_average': self.goals_saved_above_average,
            'height': self.height,
            'hits_at_even_strength': self.hits_at_even_strength,
            'league': self.league,
            'losses': self.losses,
            'minutes': self.minutes,
            'name': self.name,
            'offensive_point_shares': self.offensive_point_shares,
            'offensive_zone_start_percentage':
            self.offensive_zone_start_percentage,
            'pdo': self.pdo,
            'penalties_in_minutes': self.penalties_in_minutes,
            'player_id': self.player_id,
            'plus_minus': self.plus_minus,
            'point_shares': self.point_shares,
            'points': self.points,
            'power_play_assists': self.power_play_assists,
            'power_play_goals': self.power_play_goals,
            'power_play_goals_against_on_ice':
            self.power_play_goals_against_on_ice,
            'power_play_goals_allowed': self.power_play_goals_allowed,
            'power_play_goals_for_on_ice': self.power_play_goals_for_on_ice,
            'power_play_save_percentage': self.power_play_save_percentage,
            'power_play_shots_faced': self.power_play_shots_faced,
            'quality_start_percentage': self.quality_start_percentage,
            'quality_starts': self.quality_starts,
            'really_bad_starts': self.really_bad_starts,
            'relative_corsi_for_percentage':
            self.relative_corsi_for_percentage,
            'relative_fenwick_for_percentage':
            self.relative_fenwick_for_percentage,
            'save_percentage': self.save_percentage,
            'save_percentage_on_ice': self.save_percentage_on_ice,
            'saves': self.saves,
            'season': self.season,
            'shooting_percentage': self.shooting_percentage,
            'shooting_percentage_on_ice': self.shooting_percentage_on_ice,
            'shootout_attempts': self.shootout_attempts,
            'shootout_goals': self.shootout_goals,
            'shootout_misses': self.shootout_misses,
            'shootout_percentage': self.shootout_percentage,
            'short_handed_assists': self.short_handed_assists,
            'short_handed_goals': self.short_handed_goals,
            'short_handed_goals_allowed': self.short_handed_goals_allowed,
            'short_handed_save_percentage': self.short_handed_save_percentage,
            'short_handed_shots_faced': self.short_handed_shots_faced,
            'shots_against': self.shots_against,
            'shots_on_goal': self.shots_on_goal,
            'shutouts': self.shutouts,
            'takeaways': self.takeaways,
            'team_abbreviation': self.team_abbreviation,
            'ties_plus_overtime_loss': self.ties_plus_overtime_loss,
            'time_on_ice': self.time_on_ice,
            'time_on_ice_even_strength': self.time_on_ice_even_strength,
            'total_goals_against_on_ice': self.total_goals_against_on_ice,
            'total_goals_for_on_ice': self.total_goals_for_on_ice,
            'total_shots': self.total_shots,
            'weight': self.weight,
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
        if not self._season:
            return None
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
    def name(self):
        """
        Returns a ``string`` of the player's name, such as 'Henrik Zetterberg'.
        """
        return self._name

    @property
    def team_abbreviation(self):
        """
        Returns a ``string`` of the team's abbreviation, such as 'DET' for the
        Detroit Red Wings.
        """
        # For career stats, skip the team abbreviation.
        if self._season[self._index].lower() == 'career':
            return None
        return self._team_abbreviation[self._index]

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

    @_int_property_decorator
    def age(self):
        """
        Returns an ``int`` of the player's age on February 1st of the season.
        """
        return self._age

    @property
    def league(self):
        """
        Returns a ``string`` of the league the player's team participates in.
        """
        return self._league[self._index]

    @_int_property_decorator
    def games_played(self):
        """
        Returns an ``int`` of the number of games the player participated in.
        """
        return self._games_played

    @_int_property_decorator
    def time_on_ice(self):
        """
        Returns an ``int`` of the total time the player has spent on ice in
        minutes.
        """
        return self._time_on_ice

    @property
    def average_time_on_ice(self):
        """
        Returns a ``string`` of the average time the player spends on the ice
        per game.
        """
        return self._average_time_on_ice[self._index]

    @_int_property_decorator
    def total_shots(self):
        """
        Returns an ``int`` of the total number of shots the player took
        regardless of them being on goal or not.
        """
        return self._total_shots

    @_int_property_decorator
    def faceoff_wins(self):
        """
        Returns an ``int`` of the number of faceoffs the player won.
        """
        return self._faceoff_wins

    @_int_property_decorator
    def faceoff_losses(self):
        """
        Returns an ``int`` of the number of faceoffs the player lost.
        """
        return self._faceoff_losses

    @_float_property_decorator
    def faceoff_percentage(self):
        """
        Returns a ``float`` of the percentage of faceoffs the player wins.
        Percentage ranges from 0-100.
        """
        return self._faceoff_percentage

    @_int_property_decorator
    def blocks_at_even_strength(self):
        """
        Returns an ``int`` of the number of shots the player blocks while at
        even strength.
        """
        return self._blocks_at_even_strength

    @_int_property_decorator
    def takeaways(self):
        """
        Returns an ``int`` of the number of times the player took the puck away
        from an opponent.
        """
        return self._takeaways

    @_int_property_decorator
    def giveaways(self):
        """
        Returns an ``int`` of the number of times the player gave the puck away
        to an opponent.
        """
        return self._giveaways

    @_float_property_decorator
    def time_on_ice_even_strength(self):
        """
        Returns a ``float`` of the amount of time the player spent on ice in
        minutes while at even strength.
        """
        return self._time_on_ice_even_strength

    @_float_property_decorator
    def corsi_for(self):
        """
        Returns a ``float`` of the player's 'Corsi For' factor at even
        strength, equal to shots + blocks + misses.
        """
        return self._corsi_for

    @_float_property_decorator
    def corsi_against(self):
        """
        Returns a ``float`` of the player's 'Corsi Against' factor at even
        strength, equal to shots + blocks + misses.
        """
        return self._corsi_against

    @_int_property_decorator
    def fenwick_for(self):
        """
        Returns an ``int`` of the player's 'Fenwick For' factor at even
        strength, equal to shots + misses.
        """
        return self._fenwick_for

    @_int_property_decorator
    def fenwick_against(self):
        """
        Returns an ``int`` of the player's 'Fenwick Against' factor at even
        strength, equal to shots + misses.
        """
        return self._fenwick_against

    @_float_property_decorator
    def fenwick_for_percentage(self):
        """
        Returns a ``float`` of the player's 'Fenwick For' percentage, equal to
        fenwick_for / (fenwick_for + fenwick_against). Percentage ranges from
        0-100.
        """
        return self._fenwick_for_percentage

    @_float_property_decorator
    def relative_fenwick_for_percentage(self):
        """
        Returns a ``float`` of the player's relative 'Fenwick For' percentage,
        equal to the difference between the player's on and off-ice Fenwick For
        percentage.
        """
        return self._relative_fenwick_for_percentage

    @_int_property_decorator
    def goals_for_on_ice(self):
        """
        Returns an ``int`` of the number of goals the team has scored while the
        player is on ice.
        """
        return self._goals_for_on_ice

    @_float_property_decorator
    def shooting_percentage_on_ice(self):
        """
        Returns a ``float`` of the team's shooting percentage while the player
        is on ice.
        """
        return self._shooting_percentage_on_ice

    @_int_property_decorator
    def goals_against_on_ice(self):
        """
        Returns an ``int`` of the number of times the team has been scored on
        while the player is on ice.
        """
        return self._goals_against_on_ice

    @_int_property_decorator
    def save_percentage_on_ice(self):
        """
        Returns an ``int`` of the team's save percentage while the player is on
        ice.
        """
        return self._save_percentage_on_ice

    @_float_property_decorator
    def pdo(self):
        """
        Returns a ``float`` of the team's PDO while the player is on ice at
        even strength, equal to the team's shooting percentage + save
        percentage. Percentage ranges from 0-100.
        """
        return self._pdo

    @_float_property_decorator
    def defensive_zone_start_percentage(self):
        """
        Returns a ``float`` of the percentage of faceoffs that occur in the
        defensive zone whil the player is on ice. Percentage ranges from
        0-100.
        """
        return self._defensive_zone_start_percentage

    @_int_property_decorator
    def goals_created(self):
        """
        Returns an ``int`` of the number of goals the player created, equal to
        (goals + assists * 0.5) * team_goals / (team_goals + team_assists *
        0.5).
        """
        return self._goals_created

    @_int_property_decorator
    def adjusted_goals(self):
        """
        Returns an ``int`` of the adjusted number of goals the player has
        scored.
        """
        return self._adjusted_goals

    @_int_property_decorator
    def adjusted_assists(self):
        """
        Returns an ``int`` of the adjusted number of goals the player has
        assisted.
        """
        return self._adjusted_assists

    @_int_property_decorator
    def adjusted_points(self):
        """
        Returns an ``int`` of the adjusted number of points the player has
        gained.
        """
        return self._adjusted_points

    @_int_property_decorator
    def adjusted_goals_created(self):
        """
        Returns an ``int`` of the adjusted number of goals the player created.
        """
        return self._adjusted_goals_created

    @_int_property_decorator
    def total_goals_for_on_ice(self):
        """
        Returns an ``int`` of the total number of goals for while the player
        was on ice.
        """
        return self._total_goals_for_on_ice

    @_int_property_decorator
    def power_play_goals_for_on_ice(self):
        """
        Returns an ``int`` of the total number of power play goals for while
        the player was on ice.
        """
        return self._power_play_goals_for_on_ice

    @_int_property_decorator
    def total_goals_against_on_ice(self):
        """
        Returns an ``int`` of the total number of goals against while the
        player was on ice.
        """
        return self._total_goals_against_on_ice

    @_int_property_decorator
    def power_play_goals_against_on_ice(self):
        """
        Returns an ``int`` of the total number of power play goals against
        while the player was on ice.
        """
        return self._power_play_goals_against_on_ice

    @_float_property_decorator
    def offensive_point_shares(self):
        """
        Returns a ``float`` of the player's offensive point share, equal to the
        approximate number of points the player contributed to while on
        offense.
        """
        return self._offensive_point_shares

    @_float_property_decorator
    def defensive_point_shares(self):
        """
        Returns a ``float`` of the player's denensive point share, equal to the
        approximate number of points the player contributed to while on
        defense.
        """
        return self._defensive_point_shares

    @_float_property_decorator
    def point_shares(self):
        """
        Returns a ``float`` of the player's total point share, equal to the sum
        of the player's offensive and defensive point share.
        """
        return self._point_shares

    @_int_property_decorator
    def shootout_attempts(self):
        """
        Returns an ``int`` of the number of shootouts the player attempted.
        """
        return self._shootout_attempts

    @_int_property_decorator
    def shootout_goals(self):
        """
        Returns an ``int`` of the number of shootout goals the player scored.
        """
        return self._shootout_goals

    @_int_property_decorator
    def shootout_misses(self):
        """
        Returns an ``int`` of the number of shootouts the player failed to
        score.
        """
        return self._shootout_misses

    @_float_property_decorator
    def shootout_percentage(self):
        """
        Returns a ``float`` of the percentage of shootouts the player scores
        in. Percentage ranges from 0-100.
        """
        return self._shootout_percentage

    @_int_property_decorator
    def wins(self):
        """
        Returns an ``int`` of the number of times the team won while the player
        is in goal.
        """
        return self._wins

    @_int_property_decorator
    def losses(self):
        """
        Returns an ``int`` of the number of times the team lost while the
        player is in goal.
        """
        return self._losses

    @_int_property_decorator
    def ties_plus_overtime_loss(self):
        """
        Returns an ``int`` of the number of times the team has either tied or
        lost in overtime or a shootout while the player is in goal.
        """
        return self._ties_plus_overtime_loss

    @_float_property_decorator
    def goals_against_average(self):
        """
        Returns a ``float`` of the average number of goals the opponent has
        scored per game while the player is in goal.
        """
        return self._goals_against_average

    @_int_property_decorator
    def minutes(self):
        """
        Returns an ``int`` of the total number of minutes the player has spent
        in goal.
        """
        return self._minutes

    @_int_property_decorator
    def quality_starts(self):
        """
        Returns an ``int`` of the number of quality starts the player has had,
        equal to starting out with an in-game save percentage greater than the
        player's average save percentage for the year.
        """
        return self._quality_starts

    @_float_property_decorator
    def quality_start_percentage(self):
        """
        Returns a ``float`` of the percentage of the player's starts that are
        considered quality starts while in goal. Percentage ranges from 0-1.
        """
        return self._quality_start_percentage

    @_int_property_decorator
    def really_bad_starts(self):
        """
        Returns an ``int`` of the number of really bad starts the player has
        had, equal to starting out with an in-game save percentage less than
        85%.
        """
        return self._really_bad_starts

    @_int_property_decorator
    def goal_against_percentage_relative(self):
        """
        Returns an ``int`` of the player's goals against average compared to
        the league average where 100 is an average player and 0 means the
        player saved every single shot.
        """
        return self._goal_against_percentage_relative

    @_float_property_decorator
    def goals_saved_above_average(self):
        """
        Returns a ``float`` of the number of goals the player saved above the
        league average.
        """
        return self._goals_saved_above_average

    @_float_property_decorator
    def adjusted_goals_against_average(self):
        """
        Returns a ``float`` of the adjusted goals against average for the
        player while in goal.
        """
        return self._adjusted_goals_against_average

    @_float_property_decorator
    def goalie_point_shares(self):
        """
        Returns a ``float`` of the player's point share while in goal.
        """
        return self._goalie_point_shares

    @_int_property_decorator
    def even_strength_shots_faced(self):
        """
        Returns an ``int`` of the number of shots the player has faced while at
        even strength.
        """
        return self._even_strength_shots_faced

    @_int_property_decorator
    def even_strength_goals_allowed(self):
        """
        Returns an ``int`` of the number of goals the player allowed in goal
        while at even strength.
        """
        return self._even_strength_goals_allowed

    @_float_property_decorator
    def even_strength_save_percentage(self):
        """
        Returns a ``float`` of the player's save percentage while at even
        strength.
        """
        return self._even_strength_save_percentage

    @_int_property_decorator
    def power_play_shots_faced(self):
        """
        Returns an ``int`` of the number of shots the player has faced while on
        a power play.
        """
        return self._power_play_shots_faced

    @_int_property_decorator
    def power_play_goals_allowed(self):
        """
        Returns an ``int`` of the number of goals the player allowed in goal
        while on a power play.
        """
        return self._power_play_goals_allowed

    @_float_property_decorator
    def power_play_save_percentage(self):
        """
        Returns a ``float`` of the player's save percentage while on a power
        play.
        """
        return self._power_play_save_percentage

    @_int_property_decorator
    def short_handed_shots_faced(self):
        """
        Returns an ``int`` of the number of shots the player has faced while
        short handed.
        """
        return self._short_handed_shots_faced

    @_int_property_decorator
    def short_handed_goals_allowed(self):
        """
        Returns an ``int`` of the number of goals the player allowed in goal
        while short handed.
        """
        return self._short_handed_goals_allowed

    @_float_property_decorator
    def short_handed_save_percentage(self):
        """
        Returns a ``float`` of the player's save percentage while short handed.
        """
        return self._short_handed_save_percentage


class Roster:
    """
    Get stats for all players on a roster.

    Request a team's roster for a given season and create instances of the
    Player class for each player, containing a detailed list of the player's
    statistics and information.

    Parameters
    ----------
    team : string
        The team's abbreviation, such as 'DET' for the Detroit Red Wings.
    year : string (optional)
        The 6-digit year to pull the roster from, such as '2017-18'. If left
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
            return pq(utils._remove_html_comment_tags(pq(url)))
        except HTTPError:
            return None

    def _create_url(self, year):
        """
        Build the team URL.

        Build a URL given a team's abbreviation and the 6-digit year.

        Parameters
        ----------
        year : string
            The 6-digit string representing the year to pull the team's roster
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
        return player('td[data-stat="player"]').attr('data-append-csv')

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
            The 6-digit string representing the year to pull the team's roster
            from.
        """
        if not year:
            year = utils._find_year_for_season('nhl')
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
        for player in page('table#roster tbody tr').items():
            player_id = self._get_id(player)
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
