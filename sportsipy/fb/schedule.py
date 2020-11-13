import pandas as pd
import re
from .constants import SCHEDULE_SCHEME, SQUAD_URL
from datetime import datetime
from ..decorators import float_property_decorator, int_property_decorator
from .fb_utils import _lookup_team
from pyquery import PyQuery as pq
from sportsipy import utils
from sportsipy.constants import (AWAY,
                                 DRAW,
                                 HOME,
                                 LOSS,
                                 NEUTRAL,
                                 WIN)
from urllib.error import HTTPError


class Game:
    """
    A representation of a matchup between two teams.

    Stores all relevant high-level match information for a game in a team's
    schedule including date, time, week, opponent, and score.

    Parameters
    ----------
    game_data : string
        The row containing the specified game information.
    """
    def __init__(self, game_data):
        self._competition = None
        self._matchweek = None
        self._day = None
        self._date = None
        self._time = None
        self._datetime = None
        self._venue = None
        self._result = None
        self._goals_for = None
        self._goals_against = None
        self._opponent = None
        self._opponent_id = None
        self._expected_goals = None
        self._expected_goals_against = None
        self._attendance = None
        self._captain = None
        self._captain_id = None
        self._formation = None
        self._referee = None
        self._match_report = None
        self._notes = None

        self._parse_game_data(game_data)

    def __str__(self):
        """
        Return the string representation of the class.
        """
        return f'{self.date} - {self.opponent}'

    def __repr__(self):
        """
        Return the string representation of the class.
        """
        return self.__str__()

    def _parse_opponent_id(self, game_data):
        """
        Parse the opponent's squad ID.

        The opponent field has a squad ID embedded in the URL which can be used
        to more directly lookup or match an opponent. By pulling the opponent
        field and removing all other unnecessary parts of the URL, the ID can
        be safely parsed and returned.

        Parameters
        ----------
        game_data : string
            A ``string`` containing all of the rows of stats for a given game.

        Returns
        -------
        string
            Returns a ``string`` of the opponent's squad ID.
        """
        opponent = game_data(SCHEDULE_SCHEME['opponent'])
        opponent_id = opponent('a').attr('href')
        try:
            opponent_id = re.sub(r'.*\/squads\/', '', opponent_id)
            opponent_id = re.sub(r'\/.*', '', opponent_id)
        except TypeError:
            opponent_id = None
        return opponent_id

    def _parse_captain_id(self, game_data):
        """
        Parse the captain's player ID.

        The captain field contains a link to the captain's unique player ID in
        the URL which can be used to more directly lookup or match the player.
        By pulling the captain field and removing all other unnecessary parts
        of the URL, the ID can be safely parsed and returned.

        Parameters
        ----------
        game_data : string
            A ``string`` containing all of the rows of stats for a given game.

        Returns
        -------
        string
            Returns a ``string`` of the player's unique ID.
        """
        captain = game_data(SCHEDULE_SCHEME['captain'])
        captain_id = captain('a').attr('href')
        try:
            captain_id = re.sub(r'.*\/players\/', '', captain_id)
            captain_id = re.sub(r'\/.*', '', captain_id)
        except TypeError:
            captain_id = None
        return captain_id

    def _parse_match_report(self, game_data):
        """
        Parse the match report ID.

        The match report field contains a link to the detailed match report via
        the match report ID which is embedded in the URL. By pulling the match
        report field and removing all other unnecessary parts of the URL, the
        ID can be safely parsed and returned.

        Parameters
        ----------
        game_data : string
            A ``string`` containing all of the rows of stats for a given game.

        Returns
        -------
        string
            Returns a ``string`` of the match report's unique ID.
        """
        match_report = game_data(SCHEDULE_SCHEME['match_report'])
        match_report_id = match_report('a').attr('href')
        try:
            match_report_id = re.sub(r'.*\/matches\/', '', match_report_id)
            match_report_id = re.sub(r'\/.*', '', match_report_id)
        except TypeError:
            match_report_id = None
        return match_report_id

    def _parse_game_data(self, game_data):
        """
        Parse a value for every attribute.

        The function looks through every attribute with the exception of those
        listed below and retrieves the value according to the parsing scheme
        and index of the attribute from the passed HTML data. Once the value
        is retrieved, the attribute's value is updated with the returned
        result.

        Note that this method is called directly once Game is invoked and does
        not need to be called manually.

        Parameters
        ----------
        game_data : string
            A ``string`` containing all of the rows of stats for a given game.
        """
        for field in self.__dict__:
            # Remove the leading '_' from the name
            short_name = str(field)[1:]
            if short_name == 'datetime':
                continue
            if short_name == 'opponent_id':
                value = self._parse_opponent_id(game_data)
                setattr(self, field, value)
                continue
            if short_name == 'captain_id':
                value = self._parse_captain_id(game_data)
                setattr(self, field, value)
                continue
            if short_name == 'match_report':
                value = self._parse_match_report(game_data)
                setattr(self, field, value)
                continue
            value = utils._parse_field(SCHEDULE_SCHEME, game_data, short_name)
            setattr(self, field, value)

    @property
    def dataframe(self):
        """
        Returns a pandas ``DataFrame`` containing all other class properties
        and values. The index for the DataFrame is the match report ID.
        """
        if self._goals_for is None and self._goals_against is None:
            return None
        fields_to_include = {
            'competition': self.competition,
            'matchweek': self.matchweek,
            'day': self.day,
            'date': self.date,
            'time': self.time,
            'datetime': self.datetime,
            'venue': self.venue,
            'result': self.result,
            'goals_for': self.goals_for,
            'goals_against': self.goals_against,
            'shootout_scored': self.shootout_scored,
            'shootout_against': self.shootout_against,
            'opponent': self.opponent,
            'opponent_id': self.opponent_id,
            'expected_goals': self.expected_goals,
            'expected_goals_against': self.expected_goals_against,
            'attendance': self.attendance,
            'captain': self.captain,
            'captain_id': self.captain_id,
            'formation': self.formation,
            'referee': self.referee,
            'match_report': self.match_report,
            'notes': self.notes
        }
        return pd.DataFrame([fields_to_include], index=[self.match_report])

    @property
    def competition(self):
        """
        Returns a ``string`` of the competitions name, such as 'Premier
        League' or 'Champions Lg'.
        """
        return self._competition

    @property
    def matchweek(self):
        """
        Returns a ``string`` of the matchweek the game was played in, such
        as 'Matchweek 1' or 'Group Stage'.
        """
        return self._matchweek

    @property
    def day(self):
        """
        Returns a ``string`` of the day of the week the game was played on.
        """
        return self._day

    @property
    def date(self):
        """
        Returns a ``string`` of the date the game was played in the format
        'YYYY-MM-DD'.
        """
        return self._date

    @property
    def time(self):
        """
        Returns a ``string`` of the time the game started in 24-hour
        format, local to the home venue.
        """
        return self._time

    @property
    def datetime(self):
        """
        Returns a ``datetime`` object representing the date and time the match
        started. If the time is not present, the default time of midnight on
        the given day will be used instead.
        """
        try:
            date = self.date.split('-')
        except AttributeError:
            return None
        try:
            time = re.sub(' .*', '', self.time)
            time = time.split(':')
        except TypeError:
            time = None
        if len(date) != 3:
            return None
        year, month, day = date
        hour, minute = 0, 0
        if time and len(time) == 2:
            hour, minute = time
        else:
            time = None
        try:
            year = int(year)
            month = int(month)
            day = int(day)
        except ValueError:
            return None
        try:
            hour = int(hour)
            minute = int(minute)
        except ValueError:
            # As long as we have a valid date, we can still create a meaningful
            # datetime object, even if the time is invalid, so stick to the
            # default hour and minute in case they can't be parsed.
            hour = 0
            minute = 0
        datetime_ = datetime(year, month, day, hour, minute)
        return datetime_

    @property
    def venue(self):
        """
        Returns a ``string`` constant representing if the team played at
        home ('Home'), on the road ('Away'), or at a neutral site
        ('Neutral').
        """
        if not self._venue:
            return None
        if self._venue.upper() == 'HOME':
            return HOME
        if self._venue.upper() == 'AWAY':
            return AWAY
        if self._venue.upper() == 'NEUTRAL':
            return NEUTRAL

    @property
    def result(self):
        """
        Returns a ``string`` constant representing if the team won ('Win'),
        drew ('Draw'), or lost ('Loss').
        """
        if not self._result:
            return None
        if self._result.upper() == 'W':
            return WIN
        if self._result.upper() == 'D':
            return DRAW
        if self._result.upper() == 'L':
            return LOSS

    @int_property_decorator
    def goals_for(self):
        """
        Returns an ``int`` of the number of goals the team scored.
        """
        # If the game went to a shootout, remove the penalties.
        if '(' in self._goals_for and ')' in self._goals_for:
            return re.sub(' .*', '', self._goals_for)
        return self._goals_for

    @int_property_decorator
    def goals_against(self):
        """
        Returns an ``int`` of the number of goals the team conceded.
        """
        # If the game went to a shootout, remove the penalties.
        if '(' in self._goals_against and ')' in self._goals_against:
            return re.sub(' .*', '', self._goals_against)
        return self._goals_against

    @int_property_decorator
    def shootout_scored(self):
        """
        Returns an ``int`` of the number of penalties the team scored if the
        game went to a shootout after normal play.
        """
        penalties = re.findall(r'\(\d+\)', self._goals_for)
        if penalties:
            penalties = re.sub(r'\(|\)', '', penalties[0])
        return penalties

    @int_property_decorator
    def shootout_against(self):
        """
        Returns an ``int`` of the number of penalties the team conceded if the
        game went to a shootout after normal play.
        """
        penalties = re.findall(r'\(\d+\)', self._goals_against)
        if penalties:
            penalties = re.sub(r'\(|\)', '', penalties[0])
        return penalties

    @property
    def opponent(self):
        """
        Returns a ``string`` of the opponents name, such as 'Arsenal'.
        """
        return self._opponent

    @property
    def opponent_id(self):
        """
        Returns a ``string`` of the opponents squad ID, such as '18bb7c10'
        for Arsenal.
        """
        return self._opponent_id

    @float_property_decorator
    def expected_goals(self):
        """
        Returns a ``float`` of the number of goals the team was expected to
        score based on the quality of shots taken.
        """
        return self._expected_goals

    @float_property_decorator
    def expected_goals_against(self):
        """
        Returns a ``float`` of the number of goals the team was expected to
        concede based on the quality of shots taken.
        """
        return self._expected_goals_against

    @int_property_decorator
    def attendance(self):
        """
        Returns an ``int`` of the recorded attendance at the game.
        """
        try:
            return self._attendance.replace(',', '')
        except AttributeError:
            return None

    @property
    def captain(self):
        """
        Returns a ``string`` representing the captain's name, such as
        'Harry Kane'.
        """
        return self._captain

    @property
    def captain_id(self):
        """
        Returns a ``string`` of the captain's unique ID on fbref.com, such
        as '21a66f6a' for Harry Kane.
        """
        return self._captain_id

    @property
    def formation(self):
        """
        Returns a ``string`` of the formation the team started with during
        the game, such as '4-4-2'.
        """
        return self._formation

    @property
    def referee(self):
        """
        Returns a ``string`` of the first and last name of the referee for
        the match.
        """
        return self._referee

    @property
    def match_report(self):
        """
        Returns a ``string`` of the 8-digit match ID for the game.
        """
        return self._match_report

    @property
    def notes(self):
        """
        Returns a ``string`` of any notes that might be included with the
        game.
        """
        return self._notes


class Schedule:
    """
    An object of the given team's schedule.

    Generates a team's schedule for the season including wins, losses, draws,
    and scores if applicable.

    Parameters
    ----------
    team_id : string
        The team's 8-digit squad ID or the team's name, such as 'Tottenham
        Hotspur'.
    doc : PyQuery object (optional)
        If passed to the class instantiation, this will be used to pull all
        information instead of making another request to the website. If the
        document is not provided, it will be pulled during a later step.
    """
    def __init__(self, team_id, doc=None):
        self._games = []
        self._pull_schedule(team_id, doc)

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

        Raises
        ------
        IndexError
            If the requested index is not within the bounds of the schedule.
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
            if not game.datetime:
                continue  # pragma: no cover
            if game.datetime.year == date.year and \
               game.datetime.month == date.month and \
               game.datetime.day == date.day:
                return game
        raise ValueError('No games found for requested date')

    def __str__(self):
        """
        Return the string representation of the class.
        """
        games = [f'{game.date} - {game.opponent}'.strip()
                 for game in self._games]
        return '\n'.join(games)

    def __repr__(self):
        """
        Return the string representation of the class.
        """
        return self.__str__()

    def __iter__(self):
        """
        Returns an iterator of all of the games scheduled for the given team.
        """
        return iter(self._games)

    def __len__(self):
        """
        Returns the number of scheduled games for the given team.
        """
        return len(self._games)

    def _add_games_to_schedule(self, schedule):
        """
        Add game information to the list of games.

        Create a Game instance for the given game in the schedule and add it to
        the list of games the team has or will play during the season.

        Parameters
        ----------
        schedule : PyQuery object
            A PyQuery object pertaining to a team's schedule table.
        """
        for item in schedule:
            if 'class="thead"' in str(item):
                continue  # pragma: no cover
            game = Game(item)
            self._games.append(game)

    def _pull_schedule(self, team_id, doc):
        """
        Download and create objects for the team's schedule.

        Given the team's abbreviation, pull the squad page and parse all of the
        games on the list. If a document is already provided (occurs when
        called directly from the Team class), that can be used to save an extra
        call to the website and games can be parsed from that object.

        A Game instance is created for every item in the team's schedule and
        appended to the '_games' property.

        Parameters
        ----------
        team_id : string
            The team's 8-digit squad ID or the team's name, such as 'Tottenham
            Hotspur'.
        doc : PyQuery object
            If passed to the class instantiation, this will be used to pull all
            information instead of making another request to the website. If
            the document is not provided, this value will be None.
        """
        if not doc:
            squad_id = _lookup_team(team_id)
            try:
                doc = pq(SQUAD_URL % squad_id)
            except HTTPError:
                return
        schedule = utils._get_stats_table(doc, 'table#matchlogs_all')

        if not schedule:
            utils._no_data_found()
            return
        self._add_games_to_schedule(schedule)
