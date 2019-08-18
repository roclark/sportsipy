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
from sportsreference.nhl.boxscore import Boxscore
from sportsreference.nhl.constants import OVERTIME_LOSS, SHOOTOUT


class Game:
    """
    A representation of a matchup between two teams.

    Stores all relevant high-level match information for a game in a team's
    schedule including date, time, opponent, and result.

    Parameters
    ----------
    game_data : string
        The row containing the specified game information.
    year : string
        The year of the current season.
    """
    def __init__(self, game_data, year):
        self._game = None
        self._date = None
        self._boxscore = None
        self._location = None
        self._opponent_abbr = None
        self._opponent_name = None
        self._goals_scored = None
        self._goals_allowed = None
        self._result = None
        self._overtime = None
        self._shots_on_goal = None
        self._penalties_in_minutes = None
        self._power_play_goals = None
        self._power_play_opportunities = None
        self._short_handed_goals = None
        self._opp_shots_on_goal = None
        self._opp_penalties_in_minutes = None
        self._opp_power_play_goals = None
        self._opp_power_play_opportunities = None
        self._opp_short_handed_goals = None
        self._corsi_for = None
        self._corsi_against = None
        self._corsi_for_percentage = None
        self._fenwick_for = None
        self._fenwick_against = None
        self._fenwick_for_percentage = None
        self._faceoff_wins = None
        self._faceoff_losses = None
        self._faceoff_win_percentage = None
        self._offensive_zone_start_percentage = None
        self._pdo = None

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
        name = game_data('td[data-stat="opp_name"]:first')
        name = re.sub(r'.*/teams/', '', str(name))
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
        if self._goals_scored is None and self._goals_allowed is None:
            return None
        fields_to_include = {
            'boxscore_index': self.boxscore_index,
            'date': self.date,
            'datetime': self.datetime,
            'game': self.game,
            'goals_allowed': self.goals_allowed,
            'goals_scored': self.goals_scored,
            'location': self.location,
            'opponent_abbr': self.opponent_abbr,
            'opponent_name': self.opponent_name,
            'overtime': self.overtime,
            'penalties_in_minutes': self.penalties_in_minutes,
            'power_play_goals': self.power_play_goals,
            'power_play_opportunities': self.power_play_opportunities,
            'result': self.result,
            'short_handed_goals': self.short_handed_goals,
            'shots_on_goal': self.shots_on_goal,
            'opp_shots_on_goal': self.opp_shots_on_goal,
            'opp_penalties_in_minutes': self.opp_penalties_in_minutes,
            'opp_power_play_goals': self.opp_power_play_goals,
            'opp_power_play_opportunities': self.opp_power_play_opportunities,
            'opp_short_handed_goals': self.opp_short_handed_goals,
            'corsi_for': self.corsi_for,
            'corsi_against': self.corsi_against,
            'corsi_for_percentage': self.corsi_for_percentage,
            'fenwick_for': self.fenwick_for,
            'fenwick_against': self.fenwick_against,
            'fenwick_for_percentage': self.fenwick_for_percentage,
            'faceoff_wins': self.faceoff_wins,
            'faceoff_losses': self.faceoff_losses,
            'faceoff_win_percentage': self.faceoff_win_percentage,
            'offensive_zone_start_percentage':
            self.offensive_zone_start_percentage,
            'pdo': self.pdo
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
        return int(self._game)

    @property
    def date(self):
        """
        Returns a ``string`` of the date the game was played, such as
        '2017-10-05'.
        """
        return self._date

    @property
    def datetime(self):
        """
        Returns a datetime object to indicate the month, day, and year the game
        was played at.
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
        at home or away.
        """
        if self._location == '@':
            return AWAY
        return HOME

    @property
    def opponent_abbr(self):
        """
        Returns a ``string`` of the opponent's 3-letter abbreviation, such as
        'NYR' for the New York Rangers.
        """
        return self._opponent_abbr

    @property
    def opponent_name(self):
        """
        Returns a ``string`` of the opponent's name, such as 'New York
        Rangers'.
        """
        return self._opponent_name

    @int_property_decorator
    def goals_scored(self):
        """
        Returns an ``int`` of the number of goals the team scored during the
        game.
        """
        return self._goals_scored

    @int_property_decorator
    def goals_allowed(self):
        """
        Returns an ``int`` of the number of goals the team allowed during the
        game.
        """
        return self._goals_allowed

    @property
    def result(self):
        """
        Returns a ``string`` constant to indicate whether the team lost in
        regulation, lost in overtime, or won.
        """
        if self._result.lower() == 'w':
            return WIN
        if self._result.lower() == 'l' and \
           self.overtime != 0:
            return OVERTIME_LOSS
        return LOSS

    @int_property_decorator
    def overtime(self):
        """
        Returns an ``int`` of the number of overtimes that were played during
        the game, or an int constant if the game went to a shootout.
        """
        if self._overtime.lower() == 'ot':
            return 1
        if self._overtime.lower() == 'so':
            return SHOOTOUT
        if self._overtime == '':
            return 0
        num = re.findall(r'\d+', self._overtime)
        if len(num) > 0:
            return num[0]
        return 0

    @int_property_decorator
    def shots_on_goal(self):
        """
        Returns an ``int`` of the total number of shots on goal the team
        registered.
        """
        return self._shots_on_goal

    @int_property_decorator
    def penalties_in_minutes(self):
        """
        Returns an ``int`` of the total number of minutes the team served for
        penalties.
        """
        return self._penalties_in_minutes

    @int_property_decorator
    def power_play_goals(self):
        """
        Returns an ``int`` of the number of power play goals the team scored.
        """
        return self._power_play_goals

    @int_property_decorator
    def power_play_opportunities(self):
        """
        Returns an ``int`` of the number of power play opportunities the team
        had.
        """
        return self._power_play_opportunities

    @int_property_decorator
    def short_handed_goals(self):
        """
        Returns an ``int`` of the number of shorthanded goals the team scored.
        """
        return self._short_handed_goals

    @int_property_decorator
    def opp_shots_on_goal(self):
        """
        Returns an ``int`` of the total number of shots on goal the opponent
        registered.
        """
        return self._opp_shots_on_goal

    @int_property_decorator
    def opp_penalties_in_minutes(self):
        """
        Returns an ``int`` of the total number of minutes the opponent served
        for penalties.
        """
        return self._opp_penalties_in_minutes

    @int_property_decorator
    def opp_power_play_goals(self):
        """
        Returns an ``int`` of the number of power play goals the opponent
        scored.
        """
        return self._opp_power_play_goals

    @int_property_decorator
    def opp_power_play_opportunities(self):
        """
        Returns an ``int`` of the number of power play opportunities the
        opponent had.
        """
        return self._opp_power_play_opportunities

    @int_property_decorator
    def opp_short_handed_goals(self):
        """
        Returns an ``int`` of the number of shorthanded goals the opponent
        scored.
        """
        return self._opp_short_handed_goals

    @int_property_decorator
    def corsi_for(self):
        """
        Returns an ``int`` of the Corsi For at Even Strength metric which
        equals the number of shots + blocks + misses.
        """
        return self._corsi_for

    @int_property_decorator
    def corsi_against(self):
        """
        Returns an ``int`` of the Corsi Against at Even Strength metric which
        equals the number of shots + blocks + misses by the opponent.
        """
        return self._corsi_against

    @float_property_decorator
    def corsi_for_percentage(self):
        """
        Returns a ``float`` of the percentage of control a team had of the puck
        which is calculated by the corsi_for value divided by the sum of
        corsi_for and corsi_against. Values greater than 50.0 indicate the team
        had more control of the puck than their opponent. Percentage ranges
        from 0-100.
        """
        return self._corsi_for_percentage

    @int_property_decorator
    def fenwick_for(self):
        """
        Returns an ``int`` of the Fenwick For at Even Strength metric which
        equals the number of shots + misses.
        """
        return self._fenwick_for

    @int_property_decorator
    def fenwick_against(self):
        """
        Returns an ``int`` of the Fenwick Against at Even Strength metric which
        equals the number of shots + misses by the opponent.
        """
        return self._fenwick_against

    @float_property_decorator
    def fenwick_for_percentage(self):
        """
        Returns a ``float`` of the percentage of control a team had of the puck
        which is calculated by the fenwick_for value divided by the sum of
        fenwick_for and fenwick_against. Values greater than 50.0 indicate the
        team had more control of the puck than their opponent. Percentage
        ranges from 0-100.
        """
        return self._fenwick_for_percentage

    @int_property_decorator
    def faceoff_wins(self):
        """
        Returns an ``int`` of the number of faceoffs the team won at even
        strength.
        """
        return self._faceoff_wins

    @int_property_decorator
    def faceoff_losses(self):
        """
        Returns an ``int`` of the number of faceoffs the team lost at even
        strength.
        """
        return self._faceoff_losses

    @float_property_decorator
    def faceoff_win_percentage(self):
        """
        Returns a ``float`` of percentage of faceoffs the team won while at
        even strength. Percentage ranges from 0-100.
        """
        return self._faceoff_win_percentage

    @float_property_decorator
    def offensive_zone_start_percentage(self):
        """
        Returns a ``float`` of the percentage of stats that took place in the
        offensive half. Value is calculated by the number of offensive zone
        starts divided by the sum of offensive zone starts and defensive zone
        starts. Percentage ranges from 0-100.
        """
        return self._offensive_zone_start_percentage

    @float_property_decorator
    def pdo(self):
        """
        Returns a ``float`` of the team's PDO at Even Strength metric which is
        calculated by the sum of the shooting percentage and save percentage.
        Percentage ranges from 0-100.
        """
        return self._pdo


class Schedule:
    """
    An object of the given team's schedule.

    Generates a team's schedule for the season including wins, losses, and
    scores if applicable.

    Parameters
    ----------
    abbreviation : string
        A team's short name, such as 'NYR' for the New York Rangers.
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
            A team's short name, such as 'NYR' for the New York Rangers.
        year : string
            The requested year to pull stats from.
        """
        if not year:
            year = utils._find_year_for_season('nhl')
            # If stats for the requested season do not exist yet (as is the
            # case right before a new season begins), attempt to pull the
            # previous year's stats. If it exists, use the previous year
            # instead.
            if not utils._url_exists(SCHEDULE_URL % (abbreviation, year)) and \
               utils._url_exists(SCHEDULE_URL % (abbreviation,
                                                 str(int(year) - 1))):
                year = str(int(year) - 1)
        doc = pq(SCHEDULE_URL % (abbreviation, year))
        schedule = utils._get_stats_table(doc, 'table#tm_gamelog_rs')
        if not schedule:
            utils._no_data_found()
            return

        for item in schedule:
            if 'class="thead"' in str(item):
                continue
            game = Game(item, year)
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
