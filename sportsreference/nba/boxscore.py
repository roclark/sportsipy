import re
from pyquery import PyQuery as pq
from .. import utils
from .constants import BOXSCORE_ELEMENT_INDEX, BOXSCORE_SCHEME, BOXSCORE_URL
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError


class Boxscore(object):
    """
    Detailed information about the final statistics for a game.

    Stores all relevant metrics for a game such as the date, time, location,
    result, and more advanced metrics such as the effective field goal rate,
    the true shooting percentage, the game's pace, and much more.
    """
    def __init__(self, uri):
        """
        Parse all of the attributes located in the HTML data.

        Parameters
        ----------
        uri : string
            The relative link to the boxscore HTML page, such as
            '201710310LAL'.
        """
        self._date = None
        self._location = None
        self._home_name = None
        self._away_name = None
        self._winner = None
        self._winning_name = None
        self._winning_abbr = None
        self._losing_name = None
        self._losing_abbr = None
        self._pace = None
        self._away_record = None
        self._away_minutes_played = None
        self._away_field_goals = None
        self._away_field_goal_attempts = None
        self._away_field_goal_percentage = None
        self._away_three_point_field_goals = None
        self._away_three_point_field_goal_attempts = None
        self._away_three_point_field_goal_percentage = None
        self._away_free_throws = None
        self._away_free_throw_attempts = None
        self._away_free_throw_percentage = None
        self._away_offensive_rebounds = None
        self._away_defensive_rebounds = None
        self._away_total_rebounds = None
        self._away_assists = None
        self._away_steals = None
        self._away_blocks = None
        self._away_turnovers = None
        self._away_personal_fouls = None
        self._away_points = None
        self._away_true_shooting_percentage = None
        self._away_effective_field_goal_percentage = None
        self._away_three_point_attempt_rate = None
        self._away_free_throw_attempt_rate = None
        self._away_offensive_rebound_percentage = None
        self._away_defensive_rebound_percentage = None
        self._away_total_rebound_percentage = None
        self._away_assist_percentage = None
        self._away_steal_percentage = None
        self._away_block_percentage = None
        self._away_turnover_percentage = None
        self._away_offensive_rating = None
        self._away_defensive_rating = None
        self._home_record = None
        self._home_minutes_played = None
        self._home_field_goals = None
        self._home_field_goal_attempts = None
        self._home_field_goal_percentage = None
        self._home_three_point_field_goals = None
        self._home_three_point_field_goal_attempts = None
        self._home_three_point_field_goal_percentage = None
        self._home_free_throws = None
        self._home_free_throw_attempts = None
        self._home_free_throw_percentage = None
        self._home_offensive_rebounds = None
        self._home_defensive_rebounds = None
        self._home_total_rebounds = None
        self._home_assists = None
        self._home_steals = None
        self._home_blocks = None
        self._home_turnovers = None
        self._home_personal_fouls = None
        self._home_points = None
        self._home_true_shooting_percentage = None
        self._home_effective_field_goal_percentage = None
        self._home_three_point_attempt_rate = None
        self._home_free_throw_attempt_rate = None
        self._home_offensive_rebound_percentage = None
        self._home_defensive_rebound_percentage = None
        self._home_total_rebound_percentage = None
        self._home_assist_percentage = None
        self._home_steal_percentage = None
        self._home_block_percentage = None
        self._home_turnover_percentage = None
        self._home_offensive_rating = None
        self._home_defensive_rating = None

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
            '201710310LAL'.

        Returns
        -------
        PyQuery object
            The requested page is returned as a queriable PyQuery object with
            the comment tags removed.
        """
        url = BOXSCORE_URL % uri
        try:
            url_data = pq(url)
        except HTTPError:
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
        return game_info[BOXSCORE_ELEMENT_INDEX[field]]

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
            '201710310LAL'.
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
            if short_field == 'winner':
                continue
            if short_field == 'location' or \
               short_field == 'date':
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
    def location(self):
        """
        Returns a string of the name of the venue where the game was played.
        """
        return self._location

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
        Returns a string of the winning team's name, such as 'Detroit Pistons'.
        """
        if self.winner == HOME:
            return self._home_name.text()
        return self._away_name.text()

    @property
    def winning_abbr(self):
        """
        Returns a string of the winning team's abbreviation, such as 'DET'
        for the Detroit Pistons.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._home_name)
        return utils._parse_abbreviation(self._away_name)

    @property
    def losing_name(self):
        """
        Returns a string of the losing team's name, such as 'Phoenix Suns'.
        """
        if self.winner == HOME:
            return self._away_name.text()
        return self._home_name.text()

    @property
    def losing_abbr(self):
        """
        Returns a string of the losing team's abbreviation, such as 'PHO'
        for the Phoenix Suns.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._away_name)
        return utils._parse_abbreviation(self._home_name)

    @property
    def pace(self):
        """
        Returns a float of the game's overall pace, measured by the number of
        possessions per 40 minutes.
        """
        return float(self._pace)

    @property
    def away_wins(self):
        """
        Returns an int of the number of games the team has won after the
        conclusion of the game.
        """
        try:
            wins, losses = re.findall('\d+', self._away_record)
            return int(wins)
        except ValueError:
            return 0

    @property
    def away_losses(self):
        """
        Returns an int of the number of games the team has lost after the
        conclusion of the game.
        """
        try:
            wins, losses = re.findall('\d+', self._away_record)
            return int(losses)
        except ValueError:
            return 0

    @property
    def away_minutes_played(self):
        """
        Returns an int of the total number of minutes the team played during
        the game.
        """
        return int(self._away_minutes_played)

    @property
    def away_field_goals(self):
        """
        Returns an int of the total number of field goals made by the away
        team.
        """
        return int(self._away_field_goals)

    @property
    def away_field_goal_attempts(self):
        """
        Returns an int of the total number of field goal attempts by the away
        team.
        """
        return int(self._away_field_goal_attempts)

    @property
    def away_field_goal_percentage(self):
        """
        Returns a float of the number of field goals made divided by the total
        number of field goal attempts by the away team. Percentage ranges from
        0-1.
        """
        return float(self._away_field_goal_percentage)

    @property
    def away_three_point_field_goals(self):
        """
        Returns an int of the total number of three point field goals made
        by the away team.
        """
        return int(self._away_three_point_field_goals)

    @property
    def away_three_point_field_goal_attempts(self):
        """
        Returns an int of the total number of three point field goal attempts
        by the away team.
        """
        return int(self._away_three_point_field_goal_attempts)

    @property
    def away_three_point_field_goal_percentage(self):
        """
        Returns a float of the number of three point field goals made divided
        by the number of three point field goal attempts by the away team.
        Percentage ranges from 0-1.
        """
        return float(self._away_three_point_field_goal_percentage)

    @property
    def away_two_point_field_goals(self):
        """
        Returns an int of the total number of two point field goals made
        by the away team.
        """
        return self.away_field_goals - self.away_three_point_field_goals

    @property
    def away_two_point_field_goal_attempts(self):
        """
        Returns an int of the total number of two point field goal attempts
        by the away team.
        """
        return self.away_field_goal_attempts - \
            self.away_three_point_field_goal_attempts

    @property
    def away_two_point_field_goal_percentage(self):
        """
        Returns a float of the number of two point field goals made divided
        by the number of two point field goal attempts by the away team.
        Percentage ranges from 0-1.
        """
        result = float(self.away_two_point_field_goals) / \
            float(self.away_two_point_field_goal_attempts)
        return round(float(result), 3)

    @property
    def away_free_throws(self):
        """
        Returns an int of the total number of free throws made by the away
        team.
        """
        return int(self._away_free_throws)

    @property
    def away_free_throw_attempts(self):
        """
        Returns an int of the total number of free throw attempts by the away
        team.
        """
        return int(self._away_free_throw_attempts)

    @property
    def away_free_throw_percentage(self):
        """
        Returns a float of the number of free throws made divided by the number
        of free throw attempts  by the away team.
        """
        return float(self._away_free_throw_percentage)

    @property
    def away_offensive_rebounds(self):
        """
        Returns an int of the total number of offensive rebounds by the away
        team.
        """
        return int(self._away_offensive_rebounds)

    @property
    def away_defensive_rebounds(self):
        """
        Returns an int of the total number of defensive rebounds by the away
        team.
        """
        return int(self._away_defensive_rebounds)

    @property
    def away_total_rebounds(self):
        """
        Returns an int of the total number of rebounds by the away team.
        """
        return int(self._away_total_rebounds)

    @property
    def away_assists(self):
        """
        Returns an int of the total number of assists by the away team.
        """
        return int(self._away_assists)

    @property
    def away_steals(self):
        """
        Returns an int of the total number of steals by the away team.
        """
        return int(self._away_steals)

    @property
    def away_blocks(self):
        """
        Returns an int of the total number of blocks by the away team.
        """
        return int(self._away_blocks)

    @property
    def away_turnovers(self):
        """
        Returns an int of the total number of turnovers by the away team.
        """
        return int(self._away_turnovers)

    @property
    def away_personal_fouls(self):
        """
        Returns an int of the total number of personal fouls by the away team.
        """
        return int(self._away_personal_fouls)

    @property
    def away_points(self):
        """
        Returns an int of the number of points the away team scored.
        """
        return int(self._away_points)

    @property
    def away_true_shooting_percentage(self):
        """
        Returns a float of the away team's true shooting percentage which
        considers free throws, 2-point field goals, and 3-point field goals.
        Percentage ranges from 0-1.
        """
        return float(self._away_true_shooting_percentage)

    @property
    def away_effective_field_goal_percentage(self):
        """
        Returns a float of the away team's field goal percentage while giving
        extra weight to 3-point field goals. Percentage ranges from 0-1.
        """
        return float(self._away_effective_field_goal_percentage)

    @property
    def away_three_point_attempt_rate(self):
        """
        Returns a float of the percentage of field goal attempts from 3-point
        range by the away team. Percentage ranges from 0-1.
        """
        return float(self._away_three_point_attempt_rate)

    @property
    def away_free_throw_attempt_rate(self):
        """
        Returns a float of the average number of free throw attempts per field
        goal attempt by the away team.
        """
        return float(self._away_free_throw_attempt_rate)

    @property
    def away_offensive_rebound_percentage(self):
        """
        Returns a float of the percentage of available offensive rebounds the
        away team grabbed. Percentage ranges from 0-100.
        """
        return float(self._away_offensive_rebound_percentage)

    @property
    def away_defensive_rebound_percentage(self):
        """
        Returns a float of the percentage of available defensive rebounds the
        away team grabbed. Percentage ranges from 0-100.
        """
        return float(self._away_defensive_rebound_percentage)

    @property
    def away_total_rebound_percentage(self):
        """
        Returns a float of the percentage of available rebounds the away team
        grabbed. Percentage ranges from 0-100.
        """
        return float(self._away_total_rebound_percentage)

    @property
    def away_assist_percentage(self):
        """
        Returns a float of the percentage of the away team's field goals that
        were assisted. Percentage ranges from 0-100.
        """
        return float(self._away_assist_percentage)

    @property
    def away_steal_percentage(self):
        """
        Returns a float of the percentage of possessions that ended in a steal
        by the away team. Percentage ranges from 0-100.
        """
        return float(self._away_steal_percentage)

    @property
    def away_block_percentage(self):
        """
        Returns a float of the percentage of 2-point field goals that were
        blocked by the away team. Percentage ranges from 0-100.
        """
        return float(self._away_block_percentage)

    @property
    def away_turnover_percentage(self):
        """
        Returns a float of the number of times the away team turned the ball
        over per 100 possessions.
        """
        return float(self._away_turnover_percentage)

    @property
    def away_offensive_rating(self):
        """
        Returns a float of the average number of points scored per 100
        possessions by the away team.
        """
        return float(self._away_offensive_rating)

    @property
    def away_defensive_rating(self):
        """
        Returns a float of the average number of points scored per 100
        possessions by the away team.
        """
        return float(self._away_defensive_rating)

    @property
    def home_wins(self):
        """
        Returns an int of the number of games the home team won after the
        conclusion of the game.
        """
        try:
            wins, losses = re.findall('\d+', self._home_record)
            return int(wins)
        except ValueError:
            return 0

    @property
    def home_losses(self):
        """
        Returns an int of the number of games the home team lost after the
        conclusion of the game.
        """
        try:
            wins, losses = re.findall('\d+', self._home_record)
            return int(losses)
        except ValueError:
            return 0

    @property
    def home_minutes_played(self):
        """
        Returns an int of the total number of minutes the team played during
        the game.
        """
        return int(self._home_minutes_played)

    @property
    def home_field_goals(self):
        """
        Returns an int of the total number of field goals made by the home
        team.
        """
        return int(self._home_field_goals)

    @property
    def home_field_goal_attempts(self):
        """
        Returns an int of the total number of field goal attempts by the home
        team.
        """
        return int(self._home_field_goal_attempts)

    @property
    def home_field_goal_percentage(self):
        """
        Returns a float of the number of field goals made divided by the total
        number of field goal attempts by the home team. Percentage ranges from
        0-1.
        """
        return float(self._home_field_goal_percentage)

    @property
    def home_three_point_field_goals(self):
        """
        Returns an int of the total number of three point field goals made
        by the home team.
        """
        return int(self._home_three_point_field_goals)

    @property
    def home_three_point_field_goal_attempts(self):
        """
        Returns an int of the total number of three point field goal attempts
        by the home team.
        """
        return int(self._home_three_point_field_goal_attempts)

    @property
    def home_three_point_field_goal_percentage(self):
        """
        Returns a float of the number of three point field goals made divided
        by the number of three point field goal attempts by the home team.
        Percentage ranges from 0-1.
        """
        return float(self._home_three_point_field_goal_percentage)

    @property
    def home_two_point_field_goals(self):
        """
        Returns an int of the total number of two point field goals made
        by the home team.
        """
        return self.home_field_goals - self.home_three_point_field_goals

    @property
    def home_two_point_field_goal_attempts(self):
        """
        Returns an int of the total number of two point field goal attempts
        by the home team.
        """
        return self.home_field_goal_attempts - \
            self.home_three_point_field_goal_attempts

    @property
    def home_two_point_field_goal_percentage(self):
        """
        Returns a float of the number of two point field goals made divided
        by the number of two point field goal attempts by the home team.
        Percentage ranges from 0-1.
        """
        result = float(self.home_two_point_field_goals) / \
            float(self.home_two_point_field_goal_attempts)
        return round(float(result), 3)

    @property
    def home_free_throws(self):
        """
        Returns an int of the total number of free throws made by the home
        team.
        """
        return int(self._home_free_throws)

    @property
    def home_free_throw_attempts(self):
        """
        Returns an int of the total number of free throw attempts by the home
        team.
        """
        return int(self._home_free_throw_attempts)

    @property
    def home_free_throw_percentage(self):
        """
        Returns a float of the number of free throws made divided by the number
        of free throw attempts  by the home team.
        """
        return float(self._home_free_throw_percentage)

    @property
    def home_offensive_rebounds(self):
        """
        Returns an int of the total number of offensive rebounds by the home
        team.
        """
        return int(self._home_offensive_rebounds)

    @property
    def home_defensive_rebounds(self):
        """
        Returns an int of the total number of defensive rebounds by the home
        team.
        """
        return int(self._home_defensive_rebounds)

    @property
    def home_total_rebounds(self):
        """
        Returns an int of the total number of rebounds by the home team.
        """
        return int(self._home_total_rebounds)

    @property
    def home_assists(self):
        """
        Returns an int of the total number of assists by the home team.
        """
        return int(self._home_assists)

    @property
    def home_steals(self):
        """
        Returns an int of the total number of steals by the home team.
        """
        return int(self._home_steals)

    @property
    def home_blocks(self):
        """
        Returns an int of the total number of blocks by the home team.
        """
        return int(self._home_blocks)

    @property
    def home_turnovers(self):
        """
        Returns an int of the total number of turnovers by the home team.
        """
        return int(self._home_turnovers)

    @property
    def home_personal_fouls(self):
        """
        Returns an int of the total number of personal fouls by the home team.
        """
        return int(self._home_personal_fouls)

    @property
    def home_points(self):
        """
        Returns an int of the number of points the home team scored.
        """
        return int(self._home_points)

    @property
    def home_true_shooting_percentage(self):
        """
        Returns a float of the home team's true shooting percentage which
        considers free throws, 2-point field goals, and 3-point field goals.
        Percentage ranges from 0-1.
        """
        return float(self._home_true_shooting_percentage)

    @property
    def home_effective_field_goal_percentage(self):
        """
        Returns a float of the home team's field goal percentage while giving
        extra weight to 3-point field goals. Percentage ranges from 0-1.
        """
        return float(self._home_effective_field_goal_percentage)

    @property
    def home_three_point_attempt_rate(self):
        """
        Returns a float of the percentage of field goal attempts from 3-point
        range by the home team. Percentage ranges from 0-1.
        """
        return float(self._home_three_point_attempt_rate)

    @property
    def home_free_throw_attempt_rate(self):
        """
        Returns a float of the average number of free throw attempts per field
        goal attempt by the home team.
        """
        return float(self._home_free_throw_attempt_rate)

    @property
    def home_offensive_rebound_percentage(self):
        """
        Returns a float of the percentage of available offensive rebounds the
        home team grabbed. Percentage ranges from 0-100.
        """
        return float(self._home_offensive_rebound_percentage)

    @property
    def home_defensive_rebound_percentage(self):
        """
        Returns a float of the percentage of available defensive rebounds the
        home team grabbed. Percentage ranges from 0-100.
        """
        return float(self._home_defensive_rebound_percentage)

    @property
    def home_total_rebound_percentage(self):
        """
        Returns a float of the percentage of available rebounds the home team
        grabbed. Percentage ranges from 0-100.
        """
        return float(self._home_total_rebound_percentage)

    @property
    def home_assist_percentage(self):
        """
        Returns a float of the percentage of the home team's field goals that
        were assisted. Percentage ranges from 0-100.
        """
        return float(self._home_assist_percentage)

    @property
    def home_steal_percentage(self):
        """
        Returns a float of the percentage of possessions that ended in a steal
        by the home team. Percentage ranges from 0-100.
        """
        return float(self._home_steal_percentage)

    @property
    def home_block_percentage(self):
        """
        Returns a float of the percentage of 2-point field goals that were
        blocked by the home team. Percentage ranges from 0-100.
        """
        return float(self._home_block_percentage)

    @property
    def home_turnover_percentage(self):
        """
        Returns a float of the number of times the home team turned the ball
        over per 100 possessions.
        """
        return float(self._home_turnover_percentage)

    @property
    def home_offensive_rating(self):
        """
        Returns a float of the average number of points scored per 100
        possessions by the home team.
        """
        return float(self._home_offensive_rating)

    @property
    def home_defensive_rating(self):
        """
        Returns a float of the average number of points scored per 100
        possessions by the away team.
        """
        return float(self._home_defensive_rating)
