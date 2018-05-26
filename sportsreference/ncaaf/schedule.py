import re
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
                                       NON_DI,
                                       REGULAR_SEASON,
                                       CONFERENCE_TOURNAMENT)


class Game(object):
    """
    A representation of a matchup between two teams.

    Stores all relevant high-level match information for a game in a team's
    schedule including date, time, opponent, and result.
    """
    def __init__(self, game_data):
        """
        Parse all of the attributes located in the HTML data.

        Parameters
        ----------
        game_data : string
            The row containing the specified game information.
        """
        self._game = None
        self._date = None
        self._time = None
        self._day_of_week = None
        self._location = None
        self._rank = None
        self._opponent_rank = None
        self._opponent_name = None
        self._opponent_abbr = None
        self._opponent_conference = None
        self._result = None
        self._points_for = None
        self._points_against = None
        self._wins = None
        self._losses = None
        self._streak = None

        self._parse_game_data(game_data)

    def _parse_abbreviation(self, game_data):
        """
        Parses the opponent's abbreviation from their name.

        The opponent's abbreviation is embedded within the HTML tag and needs
        a special parsing scheme in order to be extracted. For non-DI schools,
        the team's name should be used as the abbreviation.
        """
        name = game_data('td[data-stat="opp_name"]:first')
        # Non-DI schools do not have abbreviations and should be handled
        # differently by just using the team's name as the abbreviation.
        if 'cfb/schools' not in str(name):
            setattr(self, '_opponent_abbr', name.text())
            return
        name = re.sub(r'.*/cfb/schools/', '', str(name))
        name = re.sub('/.*', '', name)
        setattr(self, '_opponent_abbr', name)

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
            if short_name == 'opponent_abbr':
                self._parse_abbreviation(game_data)
                continue
            value = utils.parse_field(SCHEDULE_SCHEME, game_data, short_name)
            setattr(self, field, value)

    @property
    def game(self):
        """
        Returns an int to indicate which game in the season was requested. The
        first game of the season returns 1.
        """
        return int(self._game)

    @property
    def date(self):
        """
        Returns a string of the date the game was played, such as 'Sep 2,
        2017'.
        """
        return self._date

    @property
    def time(self):
        """
        Returns a string of the time the game started, such as '12:00 PM'.
        """
        return self._time

    @property
    def datetime(self):
        """
        Returns a datetime object of the month, day, year, and time the game
        was played.
        """
        date_string = '%s %s' % (self._date, self._time)
        return datetime.strptime(date_string, '%b %d, %Y %I:%M %p')

    @property
    def day_of_week(self):
        """
        Returns a string of the 3-letter abbreviation of the day of the week
        the game was played on, such as 'Sat' for Saturday.
        """
        return self._day_of_week

    @property
    def location(self):
        """
        Returns a string constant to indicate whether the game was played at
        home, away, or in a neutral location.
        """
        if self._location.lower() == 'n':
            return NEUTRAL
        if self._location.lower() == '@':
            return AWAY
        return HOME

    @property
    def rank(self):
        """
        Returns an int of the team's rank at the time the game was played.
        """
        rank = re.findall('\d+', self._rank)
        if len(rank) == 0:
            return None
        return int(rank[0])

    @property
    def opponent_rank(self):
        """
        Returns an int of the opponent's rank at the time the game was played.
        """
        rank = re.findall('\d+', self._opponent_name)
        if len(rank) == 0:
            return None
        return int(rank[0])

    @property
    def opponent_name(self):
        """
        Returns a string of the opponent's name, such as 'Purdue Boilermakers'
        for the Purdue Boilermakers.
        """
        return self._opponent_name

    @property
    def opponent_abbr(self):
        """
        Returns a string of the opponent's abbreviation, such as 'PURDUE' for
        the Purdue Boilermakers.
        """
        return self._opponent_abbr

    @property
    def opponent_conference(self):
        """
        Returns a string of the conference the team participates in, such as
        'Big Ten' for the Big Ten Conference. If a team does not compete in
        Division-I, a string constant for the non-major school will be
        returned.
        """
        if self._opponent_conference.lower() == 'non-major':
            return NON_DI
        return self._opponent_conference

    @property
    def result(self):
        """
        Returns a string constant to indicate whether the team won or lost the
        game.
        """
        if self._result.lower() == 'l':
            return LOSS
        return WIN

    @property
    def points_for(self):
        """
        Returns an int of the number of points the team scored during the game.
        """
        return int(self._points_for)

    @property
    def points_against(self):
        """
        Returns an int of the number of points the team allowed during the
        game.
        """
        return int(self._points_against)

    @property
    def wins(self):
        """
        Returns an int of the number of games the team has won so far in the
        season at the conclusion of the requested game.
        """
        return int(self._wins)

    @property
    def losses(self):
        """
        Returns an int of the number of games the team has lost so far in the
        season at the conclusion of the requested game.
        """
        return int(self._losses)

    @property
    def streak(self):
        """
        Returns a string of the team's winning streak at the conclusion of the
        requested game. Streaks are listed in the format '[W|L] #' (ie. 'W 3'
        for a 3-game winning streak and 'L 2' for a 2-game losing streak).
        """
        return self._streak


class Schedule:
    """
    An object of the given team's schedule.

    Generates a team's schedule for the season including wins, losses, and
    scores if applicable.
    """
    def __init__(self, abbreviation, year=None):
        """
        Parameters
        ----------
        abbreviation : string
            A team's short name, such as 'MICHIGAN' for the Michigan
            Wolverines.
        year : string (optional)
            The requested year to pull stats from.
        """
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
        """Returns a list of all games scheduled for the given team."""
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
        Parameters
        ----------
        abbreviation : string
            A team's short name, such as 'MICHIGAN' for the Michigan
            Wolverines.
        year : string
            The requested year to pull stats from.
        """
        if not year:
            year = utils.find_year_for_season('ncaaf')
        doc = pq(SCHEDULE_URL % (abbreviation, year))
        schedule = utils.get_stats_table(doc, 'table#schedule')

        for item in schedule:
            game = Game(item)
            self._games.append(game)
