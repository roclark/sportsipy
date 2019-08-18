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


class Game:
    """
    A representation of a matchup between two teams.

    Stores all relevant high-level match information for a game in a team's
    schedule including date, time, opponent, and result.

    Parameters
    ----------
    game_data : string
        The row containing the specified game information.
    """
    def __init__(self, game_data, playoffs=False):
        self._game = None
        self._date = None
        self._time = None
        self._datetime = None
        self._boxscore = None
        self._location = None
        self._opponent_abbr = None
        self._opponent_name = None
        self._result = None
        self._points_scored = None
        self._points_allowed = None
        self._wins = None
        self._losses = None
        self._streak = None
        self._playoffs = playoffs

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
        boxscore = game_data('td[data-stat="box_score_text"]:first')
        boxscore = re.sub(r'.*/boxscores/', '', str(boxscore))
        boxscore = re.sub(r'\.html.*', '', boxscore)
        setattr(self, '_boxscore', boxscore)

    def _parse_opponent_abbr(self, game_data):
        """
        Parses the opponent's abbreviation for the game.

        The opponent's 3-letter abbreviation is embedded within the HTML tag
        and needs a special parsing scheme in order to be extracted.

        Parameters
        ----------
        game_data : PyQuery object
            A PyQuery object containing the information specific to a game.
        """
        opponent = game_data('td[data-stat="opp_name"]:first')
        opponent = re.sub(r'.*/teams/', '', str(opponent))
        opponent = re.sub(r'\/.*.html.*', '', opponent)
        setattr(self, '_opponent_abbr', opponent)

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
            if short_name == 'datetime' or short_name == 'playoffs':
                continue
            elif short_name == 'boxscore':
                self._parse_boxscore(game_data)
                continue
            elif short_name == 'opponent_abbr':
                self._parse_opponent_abbr(game_data)
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
            'boxscore_index': self.boxscore_index,
            'date': self.date,
            'datetime': self.datetime,
            'game': self.game,
            'location': self.location,
            'losses': self.losses,
            'opponent_abbr': self.opponent_abbr,
            'opponent_name': self.opponent_name,
            'playoffs': self.playoffs,
            'points_allowed': self.points_allowed,
            'points_scored': self.points_scored,
            'result': self.result,
            'streak': self.streak,
            'time': self.time,
            'wins': self.wins
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
    def time(self):
        """
        Returns a ``string`` of the time the game started in Eastern Time, such
        as '8:01p'.
        """
        return self._time

    @property
    def datetime(self):
        """
        Returns a datetime object to indicate the month, day, and year the game
        took place.
        """
        return datetime.strptime(self._date, '%a, %b %d, %Y')

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
    def opponent_name(self):
        """
        Returns a ``string`` of the opponent's name, such as 'Chicago Bulls'.
        """
        return self._opponent_name

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
    def wins(self):
        """
        Returns an ``int`` of the number of wins the team has in the season
        after the completion of the listed game.
        """
        return self._wins

    @int_property_decorator
    def losses(self):
        """
        Returns an ``int`` of the number of losses the team has in the season
        after the completion of the listed game.
        """
        return self._losses

    @property
    def streak(self):
        """
        Returns a ``string`` of the team's current streak after the conclusion
        of the listed game, such as 'W 3' for a 3-game winning streak.
        """
        return self._streak

    @property
    def playoffs(self):
        """
        Returns a ``boolean`` variable which evalutes to True when the game was
        played in the playoffs and returns False if the game took place in the
        regular season.
        """
        return self._playoffs


class Schedule:
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

    def _add_games_to_schedule(self, schedule, playoff=False):
        """
        Add game information to list of games.

        Create a Game instance for the given game in the schedule and add it to
        the list of games the team has or will play during the season.

        Parameters
        ----------
        schedule : PyQuery object
            A PyQuery object pertaining to a team's schedule table.
        playoff : boolean
            Evaluates to True if the game took place in the playoffs.
        """
        for item in schedule:
            if 'class="thead"' in str(item) or \
               'class="over_header thead"' in str(item):
                continue  # pragma: no cover
            game = Game(item, playoff)
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
            # If stats for the requested season do not exist yet (as is the
            # case right before a new season begins), attempt to pull the
            # previous year's stats. If it exists, use the previous year
            # instead.
            if not utils._url_exists(SCHEDULE_URL % (abbreviation.lower(),
                                                     year)) and \
               utils._url_exists(SCHEDULE_URL % (abbreviation.lower(),
                                                 str(int(year) - 1))):
                year = str(int(year) - 1)
        doc = pq(SCHEDULE_URL % (abbreviation, year))
        schedule = utils._get_stats_table(doc, 'table#games')
        if not schedule:
            utils._no_data_found()
            return
        self._add_games_to_schedule(schedule)
        if 'id="games_playoffs"' in str(doc):
            playoffs = utils._get_stats_table(doc, 'table#games_playoffs')
            self._add_games_to_schedule(playoffs, True)

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
