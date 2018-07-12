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
                                       POST_SEASON,
                                       REGULAR_SEASON,
                                       CONFERENCE_TOURNAMENT)
from sportsreference.nfl.boxscore import Boxscore
from sportsreference.nfl.constants import (CONF_CHAMPIONSHIP,
                                           DIVISION,
                                           SUPER_BOWL,
                                           WILD_CARD)


class Game(object):
    """
    A representation of a matchup between two teams.

    Stores all relevant high-level match information for a game in a team's
    schedule including date, time, opponent, and result.
    """
    def __init__(self, game_data, game_type, year):
        """
        Parse all of the attributes located in the HTML data.

        Parameters
        ----------
        game_data : string
            The row containing the specified game's information.
        game_type : string
            A constant to denote whether a game took place in the regular
            season or in the playoffs.
        year : string
            The year as a 4-digit string. Note that this is the year that the
            bulk of the season took place. For example the Super Bowl for the
            2017 season took place in early Feburary 2018, but 2017 should be
            passed as that was the year the bulk of the season was played in.
        """
        self._year = year
        self._week = None
        self._bye = None
        self._day = None
        self._date = None
        self._time = None
        self._boxscore = None
        self._type = game_type
        self._datetime = None
        self._result = None
        self._overtime = None
        self._record = None
        self._location = None
        self._opponent_abbr = None
        self._opponent_name = None
        self._points_scored = None
        self._points_allowed = None
        self._first_downs_gained = None
        self._yards_gained = None
        self._pass_yards = None
        self._rush_yards = None
        self._turnovers = None
        self._first_downs_allowed = None
        self._yards_allowed = None
        self._pass_yards_allowed = None
        self._rush_yards_allowed = None
        self._turnovers_forced = None
        self._expected_offensive_points = None
        self._expected_defensive_points = None
        self._expected_special_teams_points = None

        self._parse_game_data(game_data)

    def _parse_abbreviation(self, game_data):
        """
        Parses the opponent's abbreviation from their name.

        The opponent's abbreviation is embedded within the HTML tag and needs
        a special parsing scheme in order to be extracted.
        """
        name = game_data('td[data-stat="opp"]:first')
        name = re.sub(r'.*/teams/', '', str(name))
        name = re.sub('/.*', '', name).upper()
        setattr(self, '_opponent_abbr', name)

    def _parse_boxscore(self, game_data):
        """
        Parses the boxscore URI for the game.

        The boxscore is embedded within the HTML tag and needs a special
        parsing scheme in order to be extracted.
        """
        boxscore = game_data('td[data-stat="box_score_text"]:first')
        boxscore = re.sub(r'.*/boxscores/', '', str(boxscore))
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
               short_name == 'type' or \
               short_name == 'bye' or \
               short_name == 'year':
                continue
            if short_name == 'opponent_abbr':
                self._parse_abbreviation(game_data)
                continue
            elif short_name == 'boxscore':
                self._parse_boxscore(game_data)
                continue
            value = utils._parse_field(SCHEDULE_SCHEME, game_data, short_name)
            setattr(self, field, value)

    @property
    def week(self):
        """
        Returns an int of the week number in the season, such as 1 for the
        first week of the regular season.
        """
        if self._week.lower() == 'wild card':
            return WILD_CARD
        if self._week.lower() == 'division':
            return DIVISION
        if self._week.lower() == 'conf. champ.':
            return CONF_CHAMPIONSHIP
        if self._week.lower() == 'superbowl':
            return SUPER_BOWL
        return int(self._week)

    @property
    def bye(self):
        """
        Returns a boolean value that evaluates to True if the team had a week
        off during the requested week and False if they played.
        """
        if self._opponent_name == 'Bye Week':
            return True
        return False

    @property
    def day(self):
        """
        Returns a string of the day of the week the game was played as a
        3-letter abbreviation, such as 'Sun' for Sunday.
        """
        return self._day

    @property
    def date(self):
        """
        Returns a string of the month and day the game was played, such as
        'September 7'.
        """
        return self._date

    @property
    def time(self):
        """
        Returns a string of the time the game was played, such as '8:30PM ET'.
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
    def type(self):
        """
        Returns a string constant indicating whether the game is a regular
        season or playoff matchup.
        """
        return self._type

    @property
    def datetime(self):
        """
        Returns a datetime object representing the date and time the game was
        played.
        """
        time = re.sub(r' .*', '', self._time)
        date_string = '%s %s %s %s' % (self._day,
                                       self._date,
                                       self._year,
                                       time)
        return datetime.strptime(date_string, '%a %B %d %Y %I:%M%p')

    @property
    def result(self):
        """
        Returns a string constant indicating whether the team won or lost the
        game.
        """
        if self._result.lower() == 'l':
            return LOSS
        return WIN

    @property
    def overtime(self):
        """
        Returns a boolean value that evaluates to True if the game when to
        overtime and False if it ended in regulation.
        """
        if self._overtime != '':
            return True
        return False

    @property
    def record(self):
        """
        Returns a string of the team's record after the conclusion of the
        requested game. Record is in the format 'W-L'.
        """
        return self._record

    @property
    def location(self):
        """
        Returns a string constant indicating whether the game was played at
        home, away, or a neutral site, such as the Super Bowl.
        """
        if self._location.lower() == '@':
            return AWAY
        if self._location.lower() == 'n':
            return NEUTRAL
        return HOME

    @property
    def opponent_abbr(self):
        """
        Returns a string of the opponent's 3-letter abbreviation, such as 'NWE'
        for the New England Patriots.
        """
        return self._opponent_abbr

    @property
    def opponent_name(self):
        """
        Returns a string of the opponent's full name, such as the 'New England
        Patriots'.
        """
        return self._opponent_name

    @property
    def points_scored(self):
        """
        Returns an int of the number of points scored by the team.
        """
        return int(self._points_scored)

    @property
    def points_allowed(self):
        """
        Returns an int of the number of points allowed by the team.
        """
        return int(self._points_allowed)

    @property
    def first_downs_gained(self):
        """
        Returns an int of the number of first downs the team gained.
        """
        return int(self._first_downs_gained)

    @property
    def yards_gained(self):
        """
        Returns an int of the total number of yards the team gained.
        """
        return int(self._yards_gained)

    @property
    def pass_yards(self):
        """
        Returns an int of the number of yards from passing the team gained.
        """
        return int(self._pass_yards)

    @property
    def rush_yards(self):
        """
        Returns an int of the number of yards from rushing the team gained.
        """
        return int(self._rush_yards)

    @property
    def turnovers(self):
        """
        Returns an int of the number of times the team turned the ball over.
        """
        if self._turnovers == '':
            return 0
        return int(self._turnovers)

    @property
    def first_downs_allowed(self):
        """
        Returns an int of the total number of first downs the defense allowed.
        """
        return int(self._first_downs_allowed)

    @property
    def yards_allowed(self):
        """
        Returns an int of the total number of yards the defense allowed.
        """
        return int(self._yards_allowed)

    @property
    def pass_yards_allowed(self):
        """
        Returns an int of the total number of passing yards the defense
        allowed.
        """
        return int(self._pass_yards_allowed)

    @property
    def rush_yards_allowed(self):
        """
        Returns an int of the total number of rushing yards the defense
        allowed.
        """
        return int(self._rush_yards_allowed)

    @property
    def turnovers_forced(self):
        """
        Returns an int of the total number of turnovers the defense forced upon
        the opposing team.
        """
        if self._turnovers_forced == '':
            return 0
        return int(self._turnovers_forced)

    @property
    def expected_offensive_points(self):
        """
        Returns a float of the number of points the offense was expected to
        contribute to the score.
        """
        return float(self._expected_offensive_points)

    @property
    def expected_defensive_points(self):
        """
        Returns a float of the number of points the defense was expected to
        contribute to the score.
        """
        return float(self._expected_defensive_points)

    @property
    def expected_special_teams_points(self):
        """
        Returns a float of the number of points the special teams unit was
        expected to contribute to the score.
        """
        return float(self._expected_special_teams_points)


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
            A team's short name, such as 'NWE' for the New England Patriots.
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
            A team's short name, such as 'NWE' for the New England Patriots.
        year : string
            The requested year to pull stats from.
        """
        if not year:
            year = utils._find_year_for_season('nfl')
        doc = pq(SCHEDULE_URL % (year, abbreviation))
        schedule = utils._get_stats_table(doc, 'table#games')
        game_type = REGULAR_SEASON

        for item in schedule:
            game = Game(item, game_type, year)
            # Sportsreference indicates the playoffs as the 'Date' field in a
            # row but doesn't contain any actual data.
            if game.date == 'Playoffs':
                game_type = POST_SEASON
                continue
            self._games.append(game)
