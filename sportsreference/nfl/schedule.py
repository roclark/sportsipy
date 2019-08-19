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
                                       POST_SEASON,
                                       REGULAR_SEASON,
                                       CONFERENCE_TOURNAMENT)
from sportsreference.nfl.boxscore import Boxscore
from sportsreference.nfl.constants import (CONF_CHAMPIONSHIP,
                                           DIVISION,
                                           SUPER_BOWL,
                                           WILD_CARD)


class Game:
    """
    A representation of a matchup between two teams.

    Stores all relevant high-level match information for a game in a team's
    schedule including date, time, opponent, and result.

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
    def __init__(self, game_data, game_type, year):
        self._year = year
        self._week = None
        self._day = None
        self._date = None
        self._boxscore = None
        self._type = game_type
        self._datetime = None
        self._result = None
        self._overtime = None
        self._location = None
        self._opponent_abbr = None
        self._opponent_name = None
        self._points_scored = None
        self._points_allowed = None
        self._pass_completions = None
        self._pass_attempts = None
        self._pass_yards = None
        self._pass_touchdowns = None
        self._interceptions = None
        self._times_sacked = None
        self._yards_lost_from_sacks = None
        self._pass_yards_per_attempt = None
        self._pass_completion_rate = None
        self._quarterback_rating = None
        self._rush_attempts = None
        self._rush_yards = None
        self._rush_yards_per_attempt = None
        self._rush_touchdowns = None
        self._field_goals_made = None
        self._field_goals_attempted = None
        self._extra_points_made = None
        self._extra_points_attempted = None
        self._punts = None
        self._punt_yards = None
        self._third_down_conversions = None
        self._third_down_attempts = None
        self._fourth_down_conversions = None
        self._fourth_down_attempts = None
        self._time_of_possession = None

        self._parse_game_data(game_data)

    def _parse_abbreviation(self, game_data):
        """
        Parses the opponent's abbreviation from their name.

        The opponent's abbreviation is embedded within the HTML tag and needs
        a special parsing scheme in order to be extracted.

        Parameters
        ----------
        game_data : PyQuery object
            A PyQuery object containing the information specific to a game.
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

        Parameters
        ----------
        game_data : PyQuery object
            A PyQuery object containing the information specific to a game.
        """
        boxscore = game_data('td[data-stat="boxscore_word"]:first')
        boxscore = re.sub(r'.*/boxscores/', '', str(boxscore))
        boxscore = re.sub(r'\.htm.*', '', str(boxscore))
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
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the boxscore string.
        """
        if self._points_scored is None and self._points_allowed is None:
            return None
        fields_to_include = {
            'boxscore_index': self.boxscore_index,
            'date': self.date,
            'datetime': self.datetime,
            'day': self.day,
            'extra_points_attempted': self.extra_points_attempted,
            'extra_points_made': self.extra_points_made,
            'field_goals_attempted': self.field_goals_attempted,
            'field_goals_made': self.field_goals_made,
            'fourth_down_attempts': self.fourth_down_attempts,
            'fourth_down_conversions': self.fourth_down_conversions,
            'interceptions': self.interceptions,
            'location': self.location,
            'opponent_abbr': self.opponent_abbr,
            'opponent_name': self.opponent_name,
            'overtime': self.overtime,
            'pass_attempts': self.pass_attempts,
            'pass_completion_rate': self.pass_completion_rate,
            'pass_completions': self.pass_completions,
            'pass_touchdowns': self.pass_touchdowns,
            'pass_yards': self.pass_yards,
            'pass_yards_per_attempt': self.pass_yards_per_attempt,
            'points_allowed': self.points_allowed,
            'points_scored': self.points_scored,
            'punt_yards': self.punt_yards,
            'punts': self.punts,
            'quarterback_rating': self.quarterback_rating,
            'result': self.result,
            'rush_attempts': self.rush_attempts,
            'rush_touchdowns': self.rush_touchdowns,
            'rush_yards': self.rush_yards,
            'rush_yards_per_attempt': self.rush_yards_per_attempt,
            'third_down_attempts': self.third_down_attempts,
            'third_down_conversions': self.third_down_conversions,
            'time_of_possession': self.time_of_possession,
            'times_sacked': self.times_sacked,
            'type': self.type,
            'week': self.week,
            'yards_lost_from_sacks': self.yards_lost_from_sacks
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
    def week(self):
        """
        Returns an ``int`` of the week number in the season, such as 1 for the
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
        return self._week

    @property
    def day(self):
        """
        Returns a ``string`` of the day of the week the game was played as a
        3-letter abbreviation, such as 'Sun' for Sunday.
        """
        return self._day

    @property
    def date(self):
        """
        Returns a ``string`` of the month and day the game was played, such as
        'September 7'.
        """
        return self._date

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
        Returns a ``string`` constant indicating whether the game is a regular
        season or playoff matchup.
        """
        return self._type

    @property
    def datetime(self):
        """
        Returns a datetime object representing the date the game was played.
        """
        date_string = '%s %s %s' % (self._day,
                                    self._date,
                                    self._year)
        return datetime.strptime(date_string, '%a %B %d %Y')

    @property
    def result(self):
        """
        Returns a ``string`` constant indicating whether the team won or lost
        the game.
        """
        if self._result.lower() == 'l':
            return LOSS
        return WIN

    @property
    def overtime(self):
        """
        Returns a ``boolean`` value that evaluates to True if the game when to
        overtime and False if it ended in regulation.
        """
        if self._overtime != '':
            return True
        return False

    @property
    def location(self):
        """
        Returns a ``string`` constant indicating whether the game was played at
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
        Returns a ``string`` of the opponent's 3-letter abbreviation, such as
        'NWE' for the New England Patriots.
        """
        return self._opponent_abbr

    @property
    def opponent_name(self):
        """
        Returns a ``string`` of the opponent's full name, such as the 'New
        England Patriots'.
        """
        return self._opponent_name

    @int_property_decorator
    def points_scored(self):
        """
        Returns an ``int`` of the number of points scored by the team.
        """
        return self._points_scored

    @int_property_decorator
    def points_allowed(self):
        """
        Returns an ``int`` of the number of points allowed by the team.
        """
        return self._points_allowed

    @int_property_decorator
    def pass_completions(self):
        """
        Returns an ``int`` of the number of completed passed by the team.
        """
        return self._pass_completions

    @int_property_decorator
    def pass_attempts(self):
        """
        Returns an ``int`` of the number of passes the team attempted during
        the game.
        """
        return self._pass_attempts

    @int_property_decorator
    def pass_yards(self):
        """
        Returns an ``int`` of the number of yards the team gained as a result
        of passing plays.
        """
        return self._pass_yards

    @int_property_decorator
    def pass_touchdowns(self):
        """
        Returns an ``int`` of the number of touchdowns the team scored as a
        result of passing plays.
        """
        return self._pass_touchdowns

    @int_property_decorator
    def interceptions(self):
        """
        Returns an ``int`` of the number of interceptions the team threw.
        """
        return self._interceptions

    @int_property_decorator
    def times_sacked(self):
        """
        Returns an ``int`` of the number of times the quarterback was sacked by
        the opponent.
        """
        return self._times_sacked

    @int_property_decorator
    def yards_lost_from_sacks(self):
        """
        Returns an ``int`` of the total number of yards lost as a result of a
        sack.
        """
        return self._yards_lost_from_sacks

    @float_property_decorator
    def pass_yards_per_attempt(self):
        """
        Returns a ``float`` of the average number of yards gained per passing
        play.
        """
        return self._pass_yards_per_attempt

    @float_property_decorator
    def pass_completion_rate(self):
        """
        Returns a ``float`` of the percentage of passes that were completed by
        the team. Percentage ranges from 0-100.
        """
        return self._pass_completion_rate

    @float_property_decorator
    def quarterback_rating(self):
        """
        Returns a ``float`` of the quarterback's rating for the game.
        """
        return self._quarterback_rating

    @int_property_decorator
    def rush_attempts(self):
        """
        Returns an ``int`` of the total number of times the team attempted a
        rushing play.
        """
        return self._rush_attempts

    @int_property_decorator
    def rush_yards(self):
        """
        Returns an ``int`` of the total number of yards the team gain as a
        result of rushing plays.
        """
        return self._rush_yards

    @float_property_decorator
    def rush_yards_per_attempt(self):
        """
        Returns a ``float`` of the average number of yards gained per rushing
        play.
        """
        return self._rush_yards_per_attempt

    @int_property_decorator
    def rush_touchdowns(self):
        """
        Returns an ``int`` of the number of touchdowns the team scored as a
        result of rushing plays.
        """
        return self._rush_touchdowns

    @int_property_decorator
    def field_goals_made(self):
        """
        Returns an ``int`` of the total number of field goals the team scored.
        """
        return self._field_goals_made

    @int_property_decorator
    def field_goals_attempted(self):
        """
        Returns an ``int`` of the total number of times the team attempted a
        field goal.
        """
        return self._field_goals_attempted

    @int_property_decorator
    def extra_points_made(self):
        """
        Returns an ``int`` of the number of extra points the team successfully
        converted after scoring a touchdown.
        """
        return self._extra_points_made

    @int_property_decorator
    def extra_points_attempted(self):
        """
        Returns an ``int`` of the number of times the team attempted to convert
        an extra point after scoring a touchdown.
        """
        return self._extra_points_attempted

    @int_property_decorator
    def punts(self):
        """
        Returns an ``int`` of the number of times the team punted the ball.
        """
        return self._punts

    @int_property_decorator
    def punt_yards(self):
        """
        Returns an ``int`` of the total number of yards the team punted the
        ball.
        """
        return self._punt_yards

    @int_property_decorator
    def third_down_conversions(self):
        """
        Returns an ``int`` of the number of third downs the team successfully
        converted.
        """
        return self._third_down_conversions

    @int_property_decorator
    def third_down_attempts(self):
        """
        Returns an ``int`` of the total number of third downs the team
        attempted to convert.
        """
        return self._third_down_attempts

    @int_property_decorator
    def fourth_down_conversions(self):
        """
        Returns an ``int`` of the number of fourth downs the team successfully
        converted.
        """
        return self._fourth_down_conversions

    @int_property_decorator
    def fourth_down_attempts(self):
        """
        Returns an ``int`` of the total number of fourth downs the team
        attempted to convert.
        """
        return self._fourth_down_attempts

    @property
    def time_of_possession(self):
        """
        Returns a ``string`` of the total time the team spent with the ball.
        Time is in the format 'MM:SS'.
        """
        return self._time_of_possession


class Schedule:
    """
    An object of the given team's schedule.

    Generates a team's schedule for the season including wins, losses, and
    scores if applicable.

    Parameters
    ----------
    abbreviation : string
        A team's short name, such as 'NWE' for the New England Patriots.
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

    def _add_games_to_schedule(self, schedule, game_type, year):
        """
        Add games instances to schedule.

        Create a Game instance for every applicable game in the season and
        append the instance to the '_game' property.

        Parameters
        ----------
        schedule : PyQuery object
            A PyQuery object pertaining to a team's schedule table.
        game_type : string
            A string constant denoting whether the game is being played as part
            of the regular season or the playoffs.
        year : string
            The requested year to pull stats from.
        """
        for item in schedule:
            game = Game(item, game_type, year)
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
            A team's short name, such as 'NWE' for the New England Patriots.
        year : string
            The requested year to pull stats from.
        """
        if not year:
            year = utils._find_year_for_season('nfl')
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
        schedule = utils._get_stats_table(doc, 'table#gamelog%s' % year)
        if not schedule:
            utils._no_data_found()
            return
        self._add_games_to_schedule(schedule, REGULAR_SEASON, year)
        if 'playoff_gamelog%s' % year in str(doc):
            playoffs = utils._get_stats_table(doc,
                                              'table#playoff_gamelog%s' % year)
            self._add_games_to_schedule(playoffs, POST_SEASON, year)

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
