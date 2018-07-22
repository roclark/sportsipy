import re
from pyquery import PyQuery as pq
from .. import utils
from .constants import BOXSCORE_ELEMENT_INDEX, BOXSCORE_SCHEME, BOXSCORE_URL
from sportsreference import utils
from sportsreference.constants import AWAY, HOME


class Boxscore(object):
    """
    Detailed information about the final statistics for a game.

    Stores all relevant information for a game such as the date, time,
    location, result, and more advanced metrics such as the number of fumbles
    from sacks, a team's passing completion, rushing touchdowns and much more.
    """
    def __init__(self, uri):
        """
        Parse all of the attributes located in the HTML data.

        Parameters
        ----------
        uri : string
            The relative link to the boxscore HTML page, such as
            '2018-01-08-georgia'.
        """
        self._date = None
        self._time = None
        self._stadium = None
        self._away_name = None
        self._home_name = None
        self._winner = None
        self._winning_name = None
        self._winning_abbr = None
        self._losing_name = None
        self._losing_abbr = None
        self._away_points = None
        self._away_first_downs = None
        self._away_rush_attempts = None
        self._away_rush_yards = None
        self._away_rush_touchdowns = None
        self._away_pass_completions = None
        self._away_pass_attempts = None
        self._away_pass_yards = None
        self._away_pass_touchdowns = None
        self._away_interceptions = None
        self._away_total_yards = None
        self._away_fumbles = None
        self._away_fumbles_lost = None
        self._away_turnovers = None
        self._away_penalties = None
        self._away_yards_from_penalties = None
        self._home_points = None
        self._home_first_downs = None
        self._home_rush_attempts = None
        self._home_rush_yards = None
        self._home_rush_touchdowns = None
        self._home_pass_completions = None
        self._home_pass_attempts = None
        self._home_pass_yards = None
        self._home_pass_touchdowns = None
        self._home_interceptions = None
        self._home_total_yards = None
        self._home_fumbles = None
        self._home_fumbles_lost = None
        self._home_turnovers = None
        self._home_penalties = None
        self._home_yards_from_penalties = None

        self._parse_game_data(uri)

    def _retrieve_html_page(self, uri):
        """
        Download the requested HTML page.

        Given a relative link, download the requested page and strip it of all
        comment tags before returning a pyquery object which will be used to
        parse the data.

        Parameters
        ----------
        uri : string
            The relative link to the boxscore HTML page, such as
            '2018-01-08-georgia'.

        Returns
        -------
        PyQuery object
            The requested page is returned as a queriable PyQuery object with
            the comment tags removed.
        """
        url = BOXSCORE_URL % uri
        try:
            url_data = pq(url)
        except:
            return None
        return pq(utils._remove_html_comment_tags(url_data))

    def _parse_game_date_and_location(self, field, boxscore):
        """
        Retrieve the game's date and location.

        The date and location of the game follow a more complicated parsing
        scheme and should be handled differently from other tags. Both fields
        are separated by a newline character ('\n') with the first line being
        the date and the second being the location.

        Parameters
        ----------
        field : string
            The name of the attribute to parse
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.

        Returns
        -------
        string
            Depending on the requested field, returns a text representation of
            either the date or location of the game.
        """
        scheme = BOXSCORE_SCHEME[field]
        items = [i.text() for i in boxscore(scheme).items()]
        game_info = items[0].split('\n')
        index = BOXSCORE_ELEMENT_INDEX[field]
        # If the game is a bowl game or a championship game, it will have a
        # different layout for the game information where the specific game
        # title, such as the name of the bowl game, will be the first line of
        # text. All other matchers should have the index matcher increased by
        # 1.
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                    'saturday', 'sunday']:
            # The day info is generally the first line in text for non-special
            # games.
            if day in game_info[0].lower():
                return game_info[index]
        index += 1
        return game_info[index]

    def _parse_name(self, field, boxscore):
        """
        Retrieve the team's complete name tag.

        Both the team's full name (embedded in the tag's text) and the team's
        abbreviation are stored in the name tag which can be used to parse
        the winning and losing team's information.

        Parameters
        ----------
        field : string
            The name of the attribute to parse
        boxscore : PyQuery object
            A PyQuery object containing all of the HTML data from the boxscore.

        Returns
        -------
        PyQuery object
            The complete text for the requested tag.
        """
        scheme = BOXSCORE_SCHEME[field]
        return boxscore(scheme)

    def _parse_game_data(self, uri):
        """
        Parses a value for every attribute.

        This function looks through every attribute and retrieves the value
        according to the parsing scheme and index of the attribute from the
        passed HTML data. Once the value is retrieved, the attribute's value is
        updated with the returned result.

        Note that this method is called directly once Boxscore is invoked and
        does not need to be called manually.

        Parameters
        ----------
        uri : string
            The relative link to the boxscore HTML page, such as
            '2018-01-08-georgia'.
        """
        boxscore = self._retrieve_html_page(uri)
        # If the boxscore is None, the game likely hasn't been played yet and
        # no information can be gathered. As there is nothing to grab, the
        # class instance should just be empty.
        if not boxscore:
            return

        for field in self.__dict__:
            # Remove the '_' from the name
            short_field = str(field)[1:]
            if short_field == 'winner' or \
               short_field == 'winning_name' or \
               short_field == 'winning_abbr' or \
               short_field == 'losing_name' or \
               short_field == 'losing_abbr':
                continue
            if short_field == 'date' or \
               short_field == 'time' or \
               short_field == 'stadium':
                value = self._parse_game_date_and_location(short_field,
                                                           boxscore)
                setattr(self, field, value)
                continue
            if short_field == 'away_name' or \
               short_field == 'home_name':
                value = self._parse_name(short_field, boxscore)
                setattr(self, field, value)
                continue
            index = 0
            if short_field in BOXSCORE_ELEMENT_INDEX.keys():
                index = BOXSCORE_ELEMENT_INDEX[short_field]
            value = utils._parse_field(BOXSCORE_SCHEME,
                                       boxscore,
                                       short_field,
                                       index)
            setattr(self, field, value)

    @property
    def date(self):
        """
        Returns a string of the date the game took place.
        """
        return self._date

    @property
    def time(self):
        """
        Returns a string of the time the game started.
        """
        return self._time.replace('Start Time: ', '')

    @property
    def stadium(self):
        """
        Returns a string of the name of the stadium where the game was played.
        """
        return self._stadium.replace('Stadium: ', '')

    @property
    def winner(self):
        """
        Returns a string constant indicating whether the home or away team won.
        """
        if self.home_points > self.away_points:
            return HOME
        return AWAY

    @property
    def winning_name(self):
        """
        Returns a string of the winning team's name, such as 'Alabama'.
        """
        if self.winner == HOME:
            return self._home_name.text()
        return self._away_name.text()

    @property
    def winning_abbr(self):
        """
        Returns a string of the winning team's abbreviation, such as 'ALABAMA'
        for the Alabama Crimson Tide.
        """
        if self.winner == HOME:
            if 'cfb/schools' not in str(self._home_name):
                return self._home_name.text()
            return utils._parse_abbreviation(self._home_name)
        if 'cfb/schools' not in str(self._away_name):
            return self._away_name.text()
        return utils._parse_abbreviation(self._away_name)

    @property
    def losing_name(self):
        """
        Returns a string of the losing team's name, such as 'Georgia'.
        """
        if self.winner == HOME:
            return self._away_name.text()
        return self._home_name.text()

    @property
    def losing_abbr(self):
        """
        Returns a string of the losing team's abbreviation, such as 'GEORGIA'
        for the Georgia Bulldogs.
        """
        if self.winner == HOME:
            if 'cfb/schools' not in str(self._away_name):
                return self._away_name.text()
            return utils._parse_abbreviation(self._away_name)
        if 'cfb/schools' not in str(self._home_name):
            return self._home_name.text()
        return utils._parse_abbreviation(self._home_name)

    @property
    def away_points(self):
        """
        Returns an int of the number of points the away team scored.
        """
        return int(self._away_points)

    @property
    def away_first_downs(self):
        """
        Returns an int of the number of first downs the away team gained.
        """
        return int(self._away_first_downs)

    @property
    def away_rush_attempts(self):
        """
        Returns an int of the number of rushing plays the away team made.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._away_rush_attempts.split('-')
        return int(rush_info[0])

    @property
    def away_rush_yards(self):
        """
        Returns an int of the number of rushing yards the away team gained.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._away_rush_yards.split('-')
        return int(rush_info[1])

    @property
    def away_rush_touchdowns(self):
        """
        Returns an int of the number of rushing touchdowns the away team
        scored.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._away_rush_touchdowns.split('-')
        return int(rush_info[2])

    @property
    def away_pass_completions(self):
        """
        Returns an int of the number of completed passes the away team made.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._away_pass_completions.split('-')
        return int(pass_info[0])

    @property
    def away_pass_attempts(self):
        """
        Returns an int of the number of passes that were thrown by the away
        team.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._away_pass_attempts.split('-')
        return int(pass_info[1])

    @property
    def away_pass_yards(self):
        """
        Returns an int of the number of passing yards the away team gained.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._away_pass_yards.split('-')
        return int(pass_info[2])

    @property
    def away_pass_touchdowns(self):
        """
        Returns an int of the number of passing touchdowns the away team
        scored.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._away_pass_touchdowns.split('-')
        return int(pass_info[3])

    @property
    def away_interceptions(self):
        """
        Returns an int of the number of interceptions the away team threw.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._away_interceptions.split('-')
        return int(pass_info[4])

    @property
    def away_total_yards(self):
        """
        Returns an int of the total number of yards the away team gained.
        """
        return int(self._away_total_yards)

    @property
    def away_fumbles(self):
        """
        Returns an int of the number of times the away team fumbled the ball.
        """
        # Fumble info is in the format 'Fumbles-Lost'
        fumble_info = self._away_fumbles.split('-')
        return int(fumble_info[0])

    @property
    def away_fumbles_lost(self):
        """
        Returns an int of the number of times the away team turned the ball
        over as the result of a fumble.
        """
        # Fumble info is in the format 'Fumbles-Lost'
        fumble_info = self._away_fumbles.split('-')
        return int(fumble_info[1])

    @property
    def away_turnovers(self):
        """
        Returns an int of the number of times the away team turned the ball
        over.
        """
        return int(self._away_turnovers)

    @property
    def away_penalties(self):
        """
        Returns an int of the number of penalties called on the away team.
        """
        # Penalties info is in the format 'Penalties-Yards'
        penalties_info = self._away_penalties.split('-')
        return int(penalties_info[0])

    @property
    def away_yards_from_penalties(self):
        """
        Returns an int of the number of yards gifted as a result of penalties
        called on the away team.
        """
        # Penalties info is in the format 'Penalties-Yards'
        penalties_info = self._away_yards_from_penalties.split('-')
        return int(penalties_info[1])

    @property
    def home_points(self):
        """
        Returns an int of the number of points the home team scored.
        """
        return int(self._home_points)

    @property
    def home_first_downs(self):
        """
        Returns an int of the number of first downs the home team gained.
        """
        return int(self._home_first_downs)

    @property
    def home_rush_attempts(self):
        """
        Returns an int of the number of rushing plays the home team made.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._home_rush_attempts.split('-')
        return int(rush_info[0])

    @property
    def home_rush_yards(self):
        """
        Returns an int of the number of rushing yards the home team gained.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._home_rush_yards.split('-')
        return int(rush_info[1])

    @property
    def home_rush_touchdowns(self):
        """
        Returns an int of the number of rushing touchdowns the home team
        scored.
        """
        # Rush info is in the format 'Rush-Yds-TDs'
        rush_info = self._home_rush_touchdowns.split('-')
        return int(rush_info[2])

    @property
    def home_pass_completions(self):
        """
        Returns an int of the number of completed passes the home team made.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._home_pass_completions.split('-')
        return int(pass_info[0])

    @property
    def home_pass_attempts(self):
        """
        Returns an int of the number of passes that were thrown by the home
        team.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._home_pass_attempts.split('-')
        return int(pass_info[1])

    @property
    def home_pass_yards(self):
        """
        Returns an int of the number of passing yards the home team gained.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._home_pass_yards.split('-')
        return int(pass_info[2])

    @property
    def home_pass_touchdowns(self):
        """
        Returns an int of the number of passing touchdowns the home team
        scored.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._home_pass_touchdowns.split('-')
        return int(pass_info[3])

    @property
    def home_interceptions(self):
        """
        Returns an int of the number of interceptions the home team threw.
        """
        # Pass info is in the format 'Cmp-Att-Yd-TD-INT'
        pass_info = self._home_pass_touchdowns.split('-')
        return int(pass_info[4])

    @property
    def home_total_yards(self):
        """
        Returns an int of the total number of yards the home team gained.
        """
        return int(self._home_total_yards)

    @property
    def home_fumbles(self):
        """
        Returns an int of the number of times the home team fumbled the ball.
        """
        # Fumble info is in the format 'Fumbles-Lost'
        fumble_info = self._home_fumbles.split('-')
        return int(fumble_info[0])

    @property
    def home_fumbles_lost(self):
        """
        Returns an int of the number of times the home team turned the ball
        over as the result of a fumble.
        """
        # Fumble info is in the format 'Fumbles-Lost'
        fumble_info = self._home_fumbles_lost.split('-')
        return int(fumble_info[1])

    @property
    def home_turnovers(self):
        """
        Returns an int of the number of times the home team turned the ball
        over.
        """
        return int(self._home_turnovers)

    @property
    def home_penalties(self):
        """
        Returns an int of the number of penalties called on the home team.
        """
        # Penalties info is in the format 'Penalties-Yards'
        penalties_info = self._home_penalties.split('-')
        return int(penalties_info[0])

    @property
    def home_yards_from_penalties(self):
        """
        Returns an int of the number of yards gifted as a result of penalties
        called on the home team.
        """
        # Penalties info is in the format 'Penalties-Yards'
        penalties_info = self._home_yards_from_penalties.split('-')
        return int(penalties_info[1])
