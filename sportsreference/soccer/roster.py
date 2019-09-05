import pandas as pd
import re
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .constants import PLAYER_SCHEME, CURRENT_ROSTER_URL, ROSTER_URL
from .player import AbstractPlayer
from sportsreference import utils
from sportsreference.decorators import int_property_decorator, \
    float_property_decorator


class RosterPlayerBase(AbstractPlayer):
    """[summary]
    """
    def __init__(self, player_id, name, player_data):

        self._appearances = None
        self._starts = None
        self._substitutions = None
        self._minutes_played = None
        self._minutes_played_per_appearance = None

        AbstractPlayer.__init__(self, player_id, name, player_data)

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
            field_stats = None
            stats = pq(player_data)
            value = self._parse_value(stats, short_field)
            field_stats = value
            setattr(self, field, field_stats)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the string abbreviation of the
        team, such as 'TODO'.
        """
        fields_to_include = {
            'name': self.name,
            'nationality': self.nationality,
            'position': self._position,
            'age': self.age,
            'appearances': self.appearances,
            'starts': self.starts,
            'substititions': self.substitutions,
            'minutes_played': self.minutes,
            'minutes_played_per_appereance': self.minutes_per_apperance
        }
        return pd.DataFrame([fields_to_include], index=[self._abbreviation])

    @int_property_decorator
    def appearances(self):
        """
        Returns a ``int`` of the number of apperances for the player
        """
        return self._appearances

    @int_property_decorator
    def starts(self):
        """
        Returns a ``int`` of the number of starts for the player
        """
        return self._goals

    @int_property_decorator
    def substitutions(self):
        """
        Returns a ``int`` of the number of substititions for the player
        """
        return self._substitutions

    @int_property_decorator
    def minutes(self):
        """
        Returns a ``int`` of the number of minutes for the player
        """
        return self._minutes_played

    @int_property_decorator
    def minutes_per_apperance(self):
        """
        Returns a ``int`` of the number of minutes per apperance for the player
        """
        return self._minutes_per_appreance


class RosterPlayer(RosterPlayerBase):
    """
    Get player information and stats for all seasons.

    Given a player ID capture all relevant stats and information.

    This class inherits the ``AbstractPlayer`` class. As a result, all
    properties associated with ``AbstractPlayer`` can also be read directly
    from this class.

    By default, the class instance will return the player's career stats, but
    single-season stats can be found by calling the instance with the requested
    season as denoted on sports-reference.com.

    Parameters
    ----------
    player_id : string
        A player's ID according to fbref.com. The player ID can be found by
        navigating to the player's stats page and getting the string between
        the final slash and the '.html' in the URL.
    """
    def __init__(self, player_id, name, player_data):

        # Performance
        self._goals = None
        self._assists = None
        self._penalty_kicks_made = None
        self._penalty_kicks_attempted = None
        self._fouls_commited = None
        self._yellow_cards = None
        self._red_cards = None
        self._shots_on_target = None

        # per 90 minutes
        self._goals_per90 = None
        self._goals_assists_per90 = None
        self._goals_penalty_per90 = None
        self._goals_assists_penalty_per90 = None
        self._shots_on_target_per90 = None
        self._fouls_commited_per90 = None
        self._cards_per90 = None

        RosterPlayerBase.__init__(self, player_id, name, player_data)

        self._parse_player_data(player_data)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the string abbreviation of the
        team, such as 'TODO'.
        """
        fields_to_include = {
            'goals': self.goals,
            'assists': self.assists,
            'penaltys_kicks_made': self.penalty_kicks_made,
            'penalty_kicks_attempted': self.penalty_kicks_attempted,
            'fouls': self.fouls,
            'yellow_cards': self.yellow_cards,
            'red_cards': self.red_cards,
            'shots_on_target': self.shots_on_target,
            'goals_per90': self.goals_per_90_minutes,
            'goals_assists_per90': self.goals_assists_per_90_minutes,
            'goals_penalty_kicks_made_per90':
            self.goals_penalty_kicks_made_per_90_minutes,
            'goals_assists_penalty_kicks_made_per90':
            self.goals_assists_penalty_kicks_made_per_90_minutes,
            'shots_on_target_per90': self.shots_on_target_per_90_minutes,
            'fouls_per90': self.fouls_per_90_minutes,
            'cards_per90': self.cards_per_90_minutes
        }
        return pd.DataFrame([fields_to_include], index=[self._abbreviation])

    @int_property_decorator
    def goals(self):
        """
        Returns a ``int`` of the number of goals for the player
        """
        return self._goals

    @int_property_decorator
    def assists(self):
        """
        Returns a ``int`` of the number of assists for the player
        """
        return self._assists

    @int_property_decorator
    def penalty_kicks_made(self):
        """
        Returns a ``int`` of the number of penalty kicks made for the player
        """
        return self._penalty_kicks_made

    @int_property_decorator
    def penalty_kicks_attempted(self):
        """
        Returns a ``int`` of the number of penalty kicks attempted for the
        player
        """
        return self._penalty_kicks_attempted

    @int_property_decorator
    def fouls(self):
        """
        Returns a ``int`` of the number of fouls for the player
        """
        return self._fouls_commited

    @int_property_decorator
    def yellow_cards(self):
        """
        Returns a ``int`` of the number of yellow cards for the player
        """
        return self._yellow_cards

    @int_property_decorator
    def red_cards(self):
        """
        Returns a ``int`` of the number of red cards for the player
        """
        return self._red_cards

    @int_property_decorator
    def shots_on_target(self):
        """
        Returns a ``int`` of the number of shots on target for the player
        """
        return self._shots_on_target

    @float_property_decorator
    def goals_per_90_minutes(self):
        """
        Returns a ``int`` of the number of goals for the player per 90 minutes
        """
        return self._goals_per90

    @float_property_decorator
    def goals_assists_per_90_minutes(self):
        """
        Returns a ``int`` of the number of goals and assists for the player
        per 90 minutes
        """
        return self._goals_assists_per90

    @float_property_decorator
    def goals_penalty_kicks_made_per_90_minutes(self):
        """
        Returns a ``int`` of the number of goals and penalty kicks made for
        the player per 90 minutes
        """
        return self._goals_penalty_made_per90

    @float_property_decorator
    def goals_assists_penalty_kicks_made_per_90_minutes(self):
        """
        Returns a ``int`` of the number of goals, assists, and penalty kicks
        made for the player per 90 minutes
        """
        return self._goals_assists_penalty_made_per90

    @float_property_decorator
    def shots_on_target_per_90_minutes(self):
        """
        Returns a ``int`` of the number of shots on target for the player
        per 90 minutes
        """
        return self._shots_on_target_per90

    @float_property_decorator
    def fouls_per_90_minutes(self):
        """
        Returns a ``int`` of the number of fouls commited for the player
        per 90 minutes
        """
        return self._fouls_commited_per90

    @float_property_decorator
    def cards_per_90_minutes(self):
        """
        Returns a ``int`` of the number of cards shown for the player
        per 90 minutes
        """
        return self._cards_per90


class RosterGoalkeepr(RosterPlayerBase):
    """
    Get player information and stats for all seasons.

    Given a player ID capture all relevant stats and information.

    This class inherits the ``AbstractPlayer`` class. As a result, all
    properties associated with ``AbstractPlayer`` can also be read directly
    from this class.

    By default, the class instance will return the player's career stats, but
    single-season stats can be found by calling the instance with the requested
    season as denoted on sports-reference.com.

    Parameters
    ----------
    player_id : string
        A player's ID according to fbref.com. The player ID can be found by
        navigating to the player's stats page and getting the string between
        the final slash and the '.html' in the URL.
    """
    def __init__(self, player_id, name, player_data):

        self._goals_against = None
        self._goals_against_per90 = None
        self._shots_on_target_against = None
        self._save_percentage = None
        self._wins = None
        self._draws = None
        self._losses = None
        self._clean_sheets = None
        self._clean_sheets_percentage = None

        RosterPlayerBase.__init__(self, player_id, name, player_data)

        self._parse_player_data(player_data)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the string abbreviation of the
        team, such as 'TODO'.
        """
        fields_to_include = {
            'goals_against': self.goals,
            'goals_against_per90': self.assists,
            'shots_on_target_against': self.penalty_kicks_made,
            'save_percentage': self.penalty_kicks_attempted,
            'wins': self.fouls,
            'draws': self.yellow_cards,
            'losses': self.red_cards,
            'clean_sheets': self.shots_on_target,
            'clean_sheets_percentage': self.goals_per_90_minutes
        }
        return pd.DataFrame([fields_to_include], index=[self._abbreviation])

    @int_property_decorator
    def goals_against(self):
        """
        Returns a ``int`` of the number of goals scored against the goalkeeper
        """
        return self._goals_against

    @float_property_decorator
    def goals_against_per90(self):
        """
        Returns a ``float`` of the number of goals scored against the
        goalkeeper per 90 minutes
        """
        return self._goals_against_per90

    @int_property_decorator
    def shots_on_target_against(self):
        """
        Returns a ``int`` of the number of shots on target against the
        goalkeeper
        """
        return self._shots_on_taget_against

    @float_property_decorator
    def save_percentage(self):
        """
        Returns a ``float`` of the save percentage of the goalkeeper
        player
        """
        return self._save_percentage

    @int_property_decorator
    def wins(self):
        """
        Returns a ``int`` of the number of wins for the goalkeeper
        """
        return self._wins

    @int_property_decorator
    def draws(self):
        """
        Returns a ``int`` of the number of draws for the goalkeeper
        """
        return self._draws

    @int_property_decorator
    def losses(self):
        """
        Returns a ``int`` of the number of losses for the goalkeeper
        """
        return self._losses

    @int_property_decorator
    def clean_sheets(self):
        """
        Returns a ``int`` of the number of clean sheets for the goalkeeper
        """
        return self._clean_sheets

    @float_property_decorator
    def clean_sheets_percentage(self):
        """
        Returns a ``int`` of the clean sheets percentage of the goalkeeper
        """
        return self._clean_sheets_percentage


class Roster:
    """
    Get stats for all players on a roster.

    Request a team's roster for a given season and create instances of the
    Player class for each player, containing a detailed list of the players
    statistics and information.

    Parameters
    ----------
    team : string
        The team's abbreviation
    year : string (optional)
        The 4-digit year to pull the roster from, such as '2018'. If left
        blank, defaults to the most recent season.
    slim : boolean (optional)
        Set to True to return a limited subset of player information including
        the name and player ID for each player as opposed to all of their
        respective stats which greatly reduces the time to return a response if
        just the names and IDs are desired. Defaults to False.
    """
    def __init__(self, team_id, team, year=None, slim=False):
        self._team_id = team_id
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
        if not year:
            return CURRENT_ROSTER_URL % (self._team_id)
        else:
            return ROSTER_URL % (self._team_id, year)

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
        name_tag = player('th[data-stat="player"] a')
        name = re.sub(r'.*/en/players/', '', str(name_tag))
        return re.sub(r'/.*', '', name)

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
        name_tag = player('th[data-stat="player"] a')
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

        url = self._create_url(year)
        page = self._pull_team_page(url)
        if not page:
            output = ("Can't pull requested team page. Ensure the follow "
                      "URL exists: %s" % url)
            raise ValueError(output)
        players = page('table#stats_player tbody tr').items()
        for player in players:
            player_id = self._get_id(player)
            name = self._get_name(player)
            if self._slim:
                self._players[player_id] = name
            else:
                player_instance = RosterPlayer(player_id, name, player)
                self._players.append(player_instance)

        goalkeepers = page('table#stats_keeper tbody tr').items()
        for goalkeeper in goalkeepers:
            player_id = self._get_id(goalkeeper)
            name = self._get_name(goalkeeper)
            if self._slim:
                self._players[player_id] = name
            else:
                player_instance = RosterGoalkeepr(player_id, name, goalkeeper)
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
