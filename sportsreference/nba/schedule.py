import pandas as pd
import re
from ..decorators import float_property_decorator, int_property_decorator
from .constants import (SCHEDULE_SCHEME,
                        SCHEDULE_URL)
from datetime import datetime
from pyquery import PyQuery as pq
from sportsreference import utils
from sportsreference.constants import (WIN,
                                       LOSS,
                                       HOME,
                                       AWAY,
                                       NEUTRAL,
                                       REGULAR_SEASON,
                                       CONFERENCE_TOURNAMENT)
from sportsreference.nba.boxscore import Boxscore


class Game(object):
    """
    A representation of a matchup between two teams.

    Stores all relevant high-level match information for a game in a team's
    schedule including date, time, opponent, and result.

    Parameters
    ----------
    game_data : string
        The row containing the specified game information.
    """
    def __init__(self, game_data):
        self._game = None
        self._date = None
        self._datetime = None
        self._boxscore = None
        self._location = None
        self._opponent_abbr = None
        self._result = None
        self._points_scored = None
        self._points_allowed = None
        self._field_goals = None
        self._field_goal_attempts = None
        self._field_goal_percentage = None
        self._three_point_field_goals = None
        self._three_point_field_goal_attempts = None
        self._three_point_field_goal_percentage = None
        self._free_throws = None
        self._free_throw_attempts = None
        self._free_throw_percentage = None
        self._offensive_rebounds = None
        self._total_rebounds = None
        self._assists = None
        self._steals = None
        self._blocks = None
        self._turnovers = None
        self._personal_fouls = None
        self._opp_field_goals = None
        self._opp_field_goal_attempts = None
        self._opp_field_goal_percentage = None
        self._opp_three_point_field_goals = None
        self._opp_three_point_field_goal_attempts = None
        self._opp_three_point_field_goal_percentage = None
        self._opp_free_throws = None
        self._opp_free_throw_attempts = None
        self._opp_free_throw_percentage = None
        self._opp_offensive_rebounds = None
        self._opp_total_rebounds = None
        self._opp_assists = None
        self._opp_steals = None
        self._opp_blocks = None
        self._opp_turnovers = None
        self._opp_personal_fouls = None

        self._parse_game_data(game_data)

    def _parse_boxscore(self, game_data):
        """
        Parses the boxscore URI for the game.

        The boxscore is embedded within the HTML tag and needs a special
        parsing scheme in order to be extracted.

        Parameters
        ----------
        game_data : PyQuery object
            A PyQuery object containing the information specific to a game.
        """
        boxscore = game_data('td[data-stat="date_game"]:first')
        boxscore = re.sub(r'.*/boxscores/', '', str(boxscore))
        boxscore = re.sub(r'\.html.*', '', boxscore)
        setattr(self, '_boxscore', boxscore)

    def _parse_game_data(self, game_data):
        """
        Parses a value for every attribute.

        The function looks through every attribute with the exception of those
        listed below and retrieves the value according to the parsing scheme
        and index of the attribute from the passed HTML data. Once the value
        is retrieved, the attribute's value is updated with the returned
        result.

        Note that this method is called directory once Game is invoked and does
        not need to be called manually.

        Parameters
        ----------
        game_data : string
            A string containing all of the rows of stats for a given game.
        """
        for field in self.__dict__:
            # Remove the leading '_' from the name
            short_name = str(field)[1:]
            if short_name == 'datetime':
                continue
            elif short_name == 'boxscore':
                self._parse_boxscore(game_data)
                continue
            value = utils._parse_field(SCHEDULE_SCHEME, game_data, short_name)
            setattr(self, field, value)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the boxscore string.
        """
        if self._points_allowed is None and self._points_scored is None:
            return None
        fields_to_include = {
            'assists': self.assists,
            'blocks': self.blocks,
            'boxscore_index': self.boxscore_index,
            'date': self.date,
            'datetime': self.datetime,
            'field_goal_attempts': self.field_goal_attempts,
            'field_goal_percentage': self.field_goal_percentage,
            'field_goals': self.field_goals,
            'free_throw_attempts': self.free_throw_attempts,
            'free_throw_percentage': self.free_throw_percentage,
            'free_throws': self.free_throws,
            'game': self.game,
            'location': self.location,
            'offensive_rebounds': self.offensive_rebounds,
            'opp_assists': self.opp_assists,
            'opp_blocks': self.opp_blocks,
            'opp_field_goal_attempts': self.opp_field_goal_attempts,
            'opp_field_goal_percentage': self.opp_field_goal_percentage,
            'opp_field_goals': self.opp_field_goals,
            'opp_free_throw_attempts': self.opp_free_throw_attempts,
            'opp_free_throw_percentage': self.opp_free_throw_percentage,
            'opp_free_throws': self.opp_free_throws,
            'opp_offensive_rebounds': self.opp_offensive_rebounds,
            'opp_personal_fouls': self.opp_personal_fouls,
            'opp_steals': self.opp_steals,
            'opp_three_point_field_goal_attempts':
            self.opp_three_point_field_goal_attempts,
            'opp_three_point_field_goal_percentage':
            self.opp_three_point_field_goal_percentage,
            'opp_three_point_field_goals': self.opp_three_point_field_goals,
            'opp_total_rebounds': self.opp_total_rebounds,
            'opp_turnovers': self.opp_turnovers,
            'opponent_abbr': self.opponent_abbr,
            'personal_fouls': self.personal_fouls,
            'points_allowed': self.points_allowed,
            'points_scored': self.points_scored,
            'result': self.result,
            'steals': self.steals,
            'three_point_field_goal_attempts':
            self.three_point_field_goal_attempts,
            'three_point_field_goal_percentage':
            self.three_point_field_goal_percentage,
            'three_point_field_goals': self.three_point_field_goals,
            'total_rebounds': self.total_rebounds,
            'turnovers': self.turnovers
        }
        return pd.DataFrame([fields_to_include], index=[self._boxscore])

    @property
    def dataframe_extended(self):
        """
        Returns a pandas DataFrame representing the Boxscore class for the
        game. This property provides much richer context for the selected game,
        but takes longer to process compared to the lighter 'dataframe'
        property. The index for the DataFrame is the boxscore string.
        """
        return self.boxscore.dataframe

    @int_property_decorator
    def game(self):
        """
        Returns an ``int`` to indicate which game in the season was requested.
        The first game of the season returns 1.
        """
        return self._game

    @property
    def date(self):
        """
        Returns a ``string`` of the date the game took place at, such as 'Wed,
        Oct 18, 2017'.
        """
        return self._date

    @property
    def datetime(self):
        """
        Returns a datetime object to indicate the month, day, and year the game
        took place.
        """
        return datetime.strptime(self._date, '%Y-%m-%d')

    @property
    def boxscore(self):
        """
        Returns an instance of the Boxscore class containing more detailed
        stats on the game.
        """
        return Boxscore(self._boxscore)

    @property
    def boxscore_index(self):
        """
        Returns a ``string`` of the URI for a boxscore which can be used to
        access or index a game.
        """
        return self._boxscore

    @property
    def location(self):
        """
        Returns a ``string`` constant to indicate whether the game was played
        in the team's home arena or on the road.
        """
        if self._location.lower() == '@':
            return AWAY
        return HOME

    @property
    def opponent_abbr(self):
        """
        Returns a ``string`` of the opponent's 3-letter abbreviation, such as
        'CHI' for the Chicago Bulls.
        """
        return self._opponent_abbr

    @property
    def result(self):
        """
        Returns a ``string`` constant to indicate whether the team won or lost
        the game.
        """
        if self._result.lower() == 'l':
            return LOSS
        return WIN

    @int_property_decorator
    def points_scored(self):
        """
        Returns an ``int`` of the number of points the team scored during the
        game.
        """
        return self._points_scored

    @int_property_decorator
    def points_allowed(self):
        """
        Returns an ``int`` of the number of points the team allowed during the
        game.
        """
        return self._points_allowed

    @int_property_decorator
    def field_goals(self):
        """
        Returns an ``int`` of the total number of field goals made by the team.
        """
        return self._field_goals

    @int_property_decorator
    def field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of field goal attempts by the
        team.
        """
        return self._field_goal_attempts

    @float_property_decorator
    def field_goal_percentage(self):
        """
        Returns a ``float`` of the number of field goals made divided by the
        total number of field goal attempts by the team. Percentage ranges from
        0-1.
        """
        return self._field_goal_percentage

    @int_property_decorator
    def three_point_field_goals(self):
        """
        Returns an ``int`` of the total number of three point field goals made
        by the team.
        """
        return self._three_point_field_goals

    @int_property_decorator
    def three_point_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of three point field goal
        attempts by the team.
        """
        return self._three_point_field_goal_attempts

    @float_property_decorator
    def three_point_field_goal_percentage(self):
        """
        Returns a ``float`` of the number of three point field goals made
        divided by the number of three point field goal attempts by the team.
        Percentage ranges from 0-1.
        """
        return self._three_point_field_goal_percentage

    @int_property_decorator
    def free_throws(self):
        """
        Returns an ``int`` of the total number of free throws made by the team.
        """
        return self._free_throws

    @int_property_decorator
    def free_throw_attempts(self):
        """
        Returns an ``int`` of the total number of free throw attempts by the
        team.
        """
        return self._free_throw_attempts

    @float_property_decorator
    def free_throw_percentage(self):
        """
        Returns a ``float`` of the number of free throws made divided by the
        number of free throw attempts by the team.
        """
        return self._free_throw_percentage

    @int_property_decorator
    def offensive_rebounds(self):
        """
        Returns an ``int`` of the total number of offensive rebounds by the
        team.
        """
        return self._offensive_rebounds

    @int_property_decorator
    def total_rebounds(self):
        """
        Returns an ``int`` of the total number of rebounds by the team.
        """
        return self._total_rebounds

    @int_property_decorator
    def assists(self):
        """
        Returns an ``int`` of the total number of assists by the team.
        """
        return self._assists

    @int_property_decorator
    def steals(self):
        """
        Returns an ``int`` of the total number of steals by the team.
        """
        return self._steals

    @int_property_decorator
    def blocks(self):
        """
        Returns an ``int`` of the total number of blocks by the team.
        """
        return self._blocks

    @int_property_decorator
    def turnovers(self):
        """
        Returns an ``int`` of the total number of turnovers by the team.
        """
        return self._turnovers

    @int_property_decorator
    def personal_fouls(self):
        """
        Returns an ``int`` of the total number of personal fouls by the team.
        """
        return self._personal_fouls

    @int_property_decorator
    def opp_field_goals(self):
        """
        Returns an ``int`` of the total number of field goals made by the
        opponent.
        """
        return self._opp_field_goals

    @int_property_decorator
    def opp_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of field goal attempts by the
        opponent.
        """
        return self._opp_field_goal_attempts

    @float_property_decorator
    def opp_field_goal_percentage(self):
        """
        Returns a ``float`` of the number of field goals made divided by the
        total number of field goal attempts by the opponent. Percentage ranges
        from 0-1.
        """
        return self._opp_field_goal_percentage

    @int_property_decorator
    def opp_three_point_field_goals(self):
        """
        Returns an ``int`` of the total number of three point field goals made
        by the opponent.
        """
        return self._opp_three_point_field_goals

    @int_property_decorator
    def opp_three_point_field_goal_attempts(self):
        """
        Returns an ``int`` of the total number of three point field goal
        attempts by the opponent.
        """
        return self._opp_three_point_field_goal_attempts

    @float_property_decorator
    def opp_three_point_field_goal_percentage(self):
        """
        Returns a ``float`` of the number of three point field goals made
        divided by the number of three point field goal attempts by the
        opponent. Percentage ranges from 0-1.
        """
        return self._opp_three_point_field_goal_percentage

    @int_property_decorator
    def opp_free_throws(self):
        """
        Returns an ``int`` of the total number of free throws made by the
        opponent.
        """
        return self._opp_free_throws

    @int_property_decorator
    def opp_free_throw_attempts(self):
        """
        Returns an ``int`` of the total number of free throw attempts by the
        opponent.
        """
        return self._opp_free_throw_attempts

    @float_property_decorator
    def opp_free_throw_percentage(self):
        """
        Returns a ``float`` of the number of free throws made divided by the
        number of free throw attempts by the opponent.
        """
        return self._opp_free_throw_percentage

    @int_property_decorator
    def opp_offensive_rebounds(self):
        """
        Returns an ``int`` of the total number of offensive rebounds by the
        opponent.
        """
        return self._opp_offensive_rebounds

    @int_property_decorator
    def opp_total_rebounds(self):
        """
        Returns an ``int`` of the total number of rebounds by the opponent.
        """
        return self._opp_total_rebounds

    @int_property_decorator
    def opp_assists(self):
        """
        Returns an ``int`` of the total number of assists by the opponent.
        """
        return self._opp_assists

    @int_property_decorator
    def opp_steals(self):
        """
        Returns an ``int`` of the total number of steals by the opponent.
        """
        return self._opp_steals

    @int_property_decorator
    def opp_blocks(self):
        """
        Returns an ``int`` of the total number of blocks by the opponent.
        """
        return self._opp_blocks

    @int_property_decorator
    def opp_turnovers(self):
        """
        Returns an ``int`` of the total number of turnovers by the opponent.
        """
        return self._opp_turnovers

    @int_property_decorator
    def opp_personal_fouls(self):
        """
        Returns an ``int`` of the total number of personal fouls by the
        opponent.
        """
        return self._opp_personal_fouls


class Schedule(object):
    """
    An object of the given team's schedule.

    Generates a team's schedule for the season including wins, losses, and
    scores if applicable.

    Parameters
    ----------
    abbreviation : string
        A team's short name, such as 'PHO' for the Phoenix Suns.
    year : string (optional)
        The requested year to pull stats from.
    """
    def __init__(self, abbreviation, year=None):
        self._games = []
        self._pull_schedule(abbreviation, year)

    def __getitem__(self, index):
        """
        Return a specified game.

        Returns a specified game as requested by the index number in the array.
        The input index is 0-based and must be within the range of the schedule
        array.

        Parameters
        ----------
        index : int
            The 0-based index of the game to return.

        Returns
        -------
        Game instance
            If the requested game can be found, its Game instance is returned.
        """
        return self._games[index]

    def __call__(self, date):
        """
        Return a specified game.

        Returns a specific game as requested by the passed datetime. The input
        datetime must have the same year, month, and day, but can have any time
        be used to match the game.

        Parameters
        ----------
        date : datetime
            A datetime object of the month, day, and year to identify a
            particular game that was played.

        Returns
        -------
        Game instance
            If the requested game can be found, its Game instance is returned.

        Raises
        ------
        ValueError
            If the requested date cannot be matched with a game in the
            schedule.
        """
        for game in self._games:
            if game.datetime.year == date.year and \
               game.datetime.month == date.month and \
               game.datetime.day == date.day:
                return game
        raise ValueError('No games found for requested date')

    def __repr__(self):
        """Returns a ``list`` of all games scheduled for the given team."""
        return self._games

    def __iter__(self):
        """
        Returns an iterator of all of the games scheduled for the given team.
        """
        return iter(self.__repr__())

    def __len__(self):
        """Returns the number of scheduled games for the given team."""
        return len(self.__repr__())

    def _add_games_to_schedule(self, schedule):
        """
        Add game information to list of games.

        Create a Game instance for the given game in the schedule and add it to
        the list of games the team has or will play during the season.

        Parameters
        ----------
        schedule : PyQuery object
            A PyQuery object pertaining to a team's schedule table.
        year : string
            The requested year to pull stats from.
        """
        for item in schedule:
            if 'class="thead"' in str(item) or \
               'class="over_header thead"' in str(item):
                continue
            game = Game(item)
            self._games.append(game)

    def _pull_schedule(self, abbreviation, year):
        """
        Download and create objects for the team's schedule.

        Given a team abbreviation and season, first download the team's
        schedule page and convert to a PyQuery object, then create a Game
        instance for every game in the team's schedule and append it to the
        '_games' property.

        Parameters
        ----------
        abbreviation : string
            A team's short name, such as 'DET' for the Detroit Pistons.
        year : string
            The requested year to pull stats from.
        """
        if not year:
            year = utils._find_year_for_season('nba')
        doc = pq(SCHEDULE_URL % (abbreviation, year))
        schedule = utils._get_stats_table(doc, 'table#tgl_basic')
        self._add_games_to_schedule(schedule)
        if 'tgl_basic_playoffs' in str(doc):
            playoffs = utils._get_stats_table(doc,
                                              'div#all_tgl_basic_playoffs')
            self._add_games_to_schedule(playoffs)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame where each row is a representation of the
        Game class. Rows are indexed by the boxscore string.
        """
        frames = []
        for game in self.__iter__():
            df = game.dataframe
            if df is not None:
                frames.append(df)
        if frames == []:
            return None
        return pd.concat(frames)

    @property
    def dataframe_extended(self):
        """
        Returns a pandas DataFrame where each row is a representation of the
        Boxscore class for every game in the schedule. Rows are indexed by the
        boxscore string. This property provides much richer context for the
        selected game, but takes longer to process compared to the lighter
        'dataframe' property.
        """
        frames = []
        for game in self.__iter__():
            df = game.dataframe_extended
            if df is not None:
                frames.append(df)
        if frames == []:
            return None
        return pd.concat(frames)
