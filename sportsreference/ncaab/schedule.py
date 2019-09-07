import pandas as pd
import re
from ..decorators import int_property_decorator
from .constants import (SCHEDULE_SCHEME,
                        SCHEDULE_URL,
                        NCAA_TOURNAMENT,
                        NIT_TOURNAMENT,
                        CBI_TOURNAMENT,
                        CIT_TOURNAMENT)
from datetime import datetime
from pyquery import PyQuery as pq
from sportsreference import utils
from sportsreference.constants import (WIN,
                                       LOSS,
                                       HOME,
                                       AWAY,
                                       NEUTRAL,
                                       NON_DI,
                                       REGULAR_SEASON,
                                       CONFERENCE_TOURNAMENT)
from sportsreference.ncaab.boxscore import Boxscore


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
    def __init__(self, game_data):
        self._game = None
        self._date = None
        self._datetime = None
        self._time = None
        self._boxscore = None
        self._type = None
        self._location = None
        self._opponent_abbr = None
        self._opponent_name = None
        self._opponent_rank = None
        self._opponent_conference = None
        self._result = None
        self._points_for = None
        self._points_against = None
        self._overtimes = None
        self._season_wins = None
        self._season_losses = None
        self._streak = None
        self._arena = None

        self._parse_game_data(game_data)

    def _parse_abbreviation(self, game_data):
        """
        Parses the opponent's abbreviation from their name.

        The opponent's abbreviation is embedded within the HTML tag and needs
        a special parsing scheme in order to be extracted. For non-DI schools,
        the team's name should be used as the abbreviation.

        Parameters
        ----------
        game_data : PyQuery object
            A PyQuery object containing the information specific to a game.
        """
        name = game_data('td[data-stat="opp_name"]:first')
        # Non-DI schools do not have abbreviations and should be handled
        # differently by just using the team's name as the abbreviation.
        if 'cbb/schools' not in str(name):
            setattr(self, '_opponent_abbr', name.text())
            return
        name = re.sub(r'.*/cbb/schools/', '', str(name))
        name = re.sub('/.*', '', name)
        setattr(self, '_opponent_abbr', name)

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
        # Happens if the game hasn't been played yet as there is no boxscore
        # to display.
        if boxscore('a').text() == '':
            return
        boxscore = re.sub(r'.*/boxscores/', '', str(boxscore))
        boxscore = re.sub(r'\.html.*', '', str(boxscore))
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
            if short_name == 'datetime' or \
               short_name == 'opponent_rank':
                continue
            elif short_name == 'opponent_abbr':
                self._parse_abbreviation(game_data)
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
        if self._points_for is None and self._points_against is None:
            return None
        fields_to_include = {
            'arena': self.arena,
            'boxscore_index': self.boxscore_index,
            'date': self.date,
            'datetime': self.datetime,
            'game': self.game,
            'location': self.location,
            'opponent_abbr': self.opponent_abbr,
            'opponent_conference': self.opponent_conference,
            'opponent_name': self.opponent_name,
            'opponent_rank': self.opponent_rank,
            'overtimes': self.overtimes,
            'points_against': self.points_against,
            'points_for': self.points_for,
            'result': self.result,
            'season_losses': self.season_losses,
            'season_wins': self.season_wins,
            'streak': self.streak,
            'time': self.time,
            'type': self.type
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
        if self._points_for is None and self._points_against is None:
            return None
        return self.boxscore.dataframe

    @int_property_decorator
    def game(self):
        """
        Returns an ``int`` of the game's position in the season. The first game
        of the season returns 1.
        """
        return self._game

    @property
    def date(self):
        """
        Returns a ``string`` of the game's date, such as 'Fri, Nov 10, 2017'.
        """
        return self._date

    @property
    def datetime(self):
        """
        Returns a datetime object to indicate the month, day, year, and time
        the requested game took place.
        """
        # Sometimes, the time isn't displayed on the game page. In this case,
        # the time property will be empty, causing the time parsing to fail as
        # it can't match the expected format. To prevent the issue, and since
        # the time can't properly be parsed, a default start time of midnight
        # should be used in this scenario, allowing users to decide if and how
        # they want to handle the time being empty.
        if not self._time or self._time.upper() == '':
            time = '12:00A'
        else:
            time = self._time.upper()
        date_string = '%s %s' % (self._date, time)
        date_string = re.sub(r'/.*', '', date_string)
        date_string = re.sub(r' ET', '', date_string)
        date_string += 'M'
        date_string = re.sub(r'PMM', 'PM', date_string, flags=re.IGNORECASE)
        date_string = re.sub(r'AMM', 'AM', date_string, flags=re.IGNORECASE)
        date_string = re.sub(r' PM', 'PM', date_string, flags=re.IGNORECASE)
        date_string = re.sub(r' AM', 'AM', date_string, flags=re.IGNORECASE)
        return datetime.strptime(date_string, '%a, %b %d, %Y %I:%M%p')

    @property
    def time(self):
        """
        Returns a ``string`` to indicate the time the game started, such as
        '9:00 pm/est'.
        """
        return self._time

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
    def type(self):
        """
        Returns a ``string`` constant to indicate whether the game was played
        during the regular season or in the post season.
        """
        if self._type.lower() == 'reg':
            return REGULAR_SEASON
        if self._type.lower() == 'ctourn':
            return CONFERENCE_TOURNAMENT
        if self._type.lower() == 'ncaa':
            return NCAA_TOURNAMENT
        if self._type.lower() == 'nit':
            return NIT_TOURNAMENT
        if self._type.lower() == 'cbi':
            return CBI_TOURNAMENT
        if self._type.lower() == 'cit':
            return CIT_TOURNAMENT

    @property
    def location(self):
        """
        Returns a ``string`` constant to indicate whether the game was played
        at the team's home venue, the opponent's venue, or at a neutral site.
        """
        if self._location == '':
            return HOME
        if self._location == 'N':
            return NEUTRAL
        if self._location == '@':
            return AWAY

    @property
    def opponent_abbr(self):
        """
        Returns a ``string`` of the opponent's abbreviation, such as 'PURDUE'
        for the Purdue Boilermakers.
        """
        return self._opponent_abbr

    @property
    def opponent_name(self):
        """
        Returns a ``string`` of the opponent's name, such as the 'Purdue
        Boilermakers'.
        """
        name = re.sub(r'\(\d+\)', '', self._opponent_name)
        name = name.replace(u'\xa0', '')
        return name

    @property
    def opponent_rank(self):
        """
        Returns a ``string`` of the opponent's rank when the game was played
        and None if the team was unranked.
        """
        rank = re.findall(r'\d+', self._opponent_name)
        if len(rank) > 0:
            return int(rank[0])
        return None

    @property
    def opponent_conference(self):
        """
        Returns a ``string`` of the opponent's conference, such as 'Big Ten'
        for a team participating in the Big Ten Conference. If the team is not
        a Division-I school, a string constant for non-majors is returned.
        """
        if self._opponent_conference == '':
            return NON_DI
        return self._opponent_conference

    @property
    def result(self):
        """
        Returns a ``string`` constant to indicate whether the team won or lost
        the game.
        """
        if self._result.lower() == 'w':
            return WIN
        return LOSS

    @int_property_decorator
    def points_for(self):
        """
        Returns an ``int`` of the number of points the team scored during the
        game.
        """
        return self._points_for

    @int_property_decorator
    def points_against(self):
        """
        Returns an ``int`` of the number of points the team allowed during the
        game.
        """
        return self._points_against

    @property
    def overtimes(self):
        """
        Returns an ``int`` of the number of overtimes that were played during
        the game and 0 if the game finished at the end of regulation time.
        """
        if self._overtimes == '' or self._overtimes is None:
            return 0
        if self._overtimes.lower() == 'ot':
            return 1
        num_overtimes = re.findall(r'\d+', self._overtimes)
        try:
            return int(num_overtimes[0])
        except (ValueError, IndexError):
            return 0

    @int_property_decorator
    def season_wins(self):
        """
        Returns an ``int`` of the number of games the team has won after the
        conclusion of the requested game.
        """
        return self._season_wins

    @int_property_decorator
    def season_losses(self):
        """
        Returns an ``int`` of the number of games the team has lost after the
        conclusion of the requested game.
        """
        return self._season_losses

    @property
    def streak(self):
        """
        Returns a ``string`` of the team's win streak at the conclusion of the
        requested game. Streak is in the format '[W|L] #' (ie. 'W 3' indicates
        a 3-game winning streak while 'L 2' indicates a 2-game losing streak.
        """
        return self._streak

    @property
    def arena(self):
        """
        Returns a ``string`` of the name of the arena the game was played at.
        """
        return self._arena


class Schedule:
    """
    An object of the given team's schedule.

    Generates a team's schedule for the season including wins, losses, and
    scores if applicable.

    Parameters
    ----------
    abbreviation : string
        A team's short name, such as 'PURDUE' for the Purdue Boilermakers.
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
            A team's short name, such as 'PURDUE' for the Purdue Boilermakers.
        year : string
            The requested year to pull stats from.
        """
        if not year:
            year = utils._find_year_for_season('ncaab')
            # If stats for the requested season do not exist yet (as is the
            # case right before a new season begins), attempt to pull the
            # previous year's stats. If it exists, use the previous year
            # instead.
            if not utils._url_exists(SCHEDULE_URL % (abbreviation.lower(),
                                                     year)) and \
               utils._url_exists(SCHEDULE_URL % (abbreviation.lower(),
                                                 str(int(year) - 1))):
                year = str(int(year) - 1)
        doc = pq(SCHEDULE_URL % (abbreviation.lower(), year))
        schedule = utils._get_stats_table(doc, 'table#schedule')
        if not schedule:
            utils._no_data_found()
            return

        for item in schedule:
            if 'class="thead"' in str(item):
                continue
            game = Game(item)
            self._games.append(game)

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
