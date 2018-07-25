import re
from pyquery import PyQuery as pq
from .. import utils
from .constants import BOXSCORE_ELEMENT_INDEX, BOXSCORE_SCHEME, BOXSCORE_URL
from sportsreference import utils
from sportsreference.constants import AWAY, HOME
from sportsreference.mlb.constants import DAY, NIGHT


class Boxscore(object):
    """
    Detailed information about the final statistics for a game.

    Stores all relevant information for a game such as the date, time,
    location, result, and more advanced metrics such as the number of goals
    scored, the number of points for a player, the amount of power play assists
    and much more.
    """
    def __init__(self, uri):
        """
        Parse all of the attributes located in the HTML data.

        Parameters
        ----------
        uri : string
            The relative link to the boxscore HTML page, such as
            '201806070VEG'.
        """
        self._date = None
        self._time = None
        self._arena = None
        self._attendance = None
        self._duration = None
        self._away_name = None
        self._home_name = None
        self._winner = None
        self._winning_name = None
        self._winning_abbr = None
        self._losing_name = None
        self._losing_abbr = None
        self._away_goals = None
        self._away_assists = None
        self._away_points = None
        self._away_penalties_in_minutes = None
        self._away_even_strength_goals = None
        self._away_power_play_goals = None
        self._away_short_handed_goals = None
        self._away_game_winning_goals = None
        self._away_even_strength_assists = None
        self._away_power_play_assists = None
        self._away_short_handed_assists = None
        self._away_shots_on_goal = None
        self._away_shooting_percentage = None
        self._away_saves = None
        self._away_save_percentage = None
        self._away_shutout = None
        self._home_goals = None
        self._home_assists = None
        self._home_points = None
        self._home_penalties_in_minutes = None
        self._home_even_strength_goals = None
        self._home_power_play_goals = None
        self._home_short_handed_goals = None
        self._home_game_winning_goals = None
        self._home_even_strength_assists = None
        self._home_power_play_assists = None
        self._home_short_handed_assists = None
        self._home_shots_on_goal = None
        self._home_shooting_percentage = None
        self._home_saves = None
        self._home_save_percentage = None
        self._home_shutout = None

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
            '201806070VEG'.

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
        # For playoff games, the second line (index 1) in the information block
        # of the boxscore contains the name of the round. If found, the index
        # will need to be updated by 1 to match the information.
        if 'eastern first round' in game_info[1].lower() or \
           'western first round' in game_info[1].lower() or \
           'eastern second round' in game_info[1].lower() or \
           'western second round' in game_info[1].lower() or \
           'eastern conference finals' in game_info[1].lower() or \
           'western conference finals' in game_info[1].lower() or \
           'stanley cup final' in game_info[1].lower():
            # The date and time fields will always be the first line of
            # information and should retain their original index.
            if field != 'date' and field != 'time':
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
            '201802040nwe'.
        """
        boxscore = self._retrieve_html_page(uri)
        # If the boxscore is None, the game likely hasn't been played yet and
        # no information can be gathered. As there is nothing to grab, the
        # class instance should just be empty.
        if not boxscore:
            return

        fields_to_special_parse = [
            'away_even_strength_assists',
            'away_power_play_assists',
            'away_short_handed_assists',
            'away_game_winning_goals',
            'home_even_strength_assists',
            'home_power_play_assists',
            'home_short_handed_assists',
            'home_game_winning_goals'
        ]

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
               short_field == 'arena' or \
               short_field == 'attendance' or \
               short_field == 'time_of_day' or \
               short_field == 'duration':
                value = self._parse_game_date_and_location(short_field,
                                                           boxscore)
                setattr(self, field, value)
                continue
            if short_field == 'away_name' or \
               short_field == 'home_name':
                value = self._parse_name(short_field, boxscore)
                setattr(self, field, value)
                continue
            if short_field in fields_to_special_parse:
                scheme = BOXSCORE_SCHEME[short_field]
                value = [i.text() for i in boxscore(scheme).items()]
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

        self._away_skaters = len(boxscore(BOXSCORE_SCHEME['away_skaters']))

    @property
    def date(self):
        """
        Returns a string of the date the game took place.
        """
        # Date is in the format 'Month Day, Year, Time'. Split the date into
        # the day and time by combining the text on both sides of the first
        # comma.
        date = self._date.split(',')
        return ','.join(date[:-1])

    @property
    def time(self):
        """
        Returns a string of the time the game started.
        """
        # Time is in the format 'Month Day, Year, Time'. Split the time into
        # the day and the time by taking the text after the last comma.
        time = self._time.split(',')
        return time[-1].strip()

    @property
    def arena(self):
        """
        Returns a string of the name of the ballpark where the game was played.
        """
        return self._arena.replace('Arena: ', '')

    @property
    def attendance(self):
        """
        Returns an int of the game's listed attendance.
        """
        attendance = self._attendance.replace('Attendance: ', '')
        return int(attendance.replace(',', ''))

    @property
    def duration(self):
        """
        Returns a string of the game's duration in the format 'H:MM'.
        """
        return self._duration.replace('Game Duration: ', '')

    @property
    def winner(self):
        """
        Returns a string constant indicating whether the home or away team won.
        """
        if self.home_goals > self.away_goals:
            return HOME
        return AWAY

    @property
    def winning_name(self):
        """
        Returns a string of the winning team's name, such as 'Vegas Golden
        Knights'.
        """
        if self.winner == HOME:
            return self._home_name.text()
        return self._away_name.text()

    @property
    def winning_abbr(self):
        """
        Returns a string of the winning team's abbreviation, such as 'VEG'
        for the Vegas Golden Knights.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._home_name)
        return utils._parse_abbreviation(self._away_name)

    @property
    def losing_name(self):
        """
        Returns a string of the losing team's name, such as 'Washington
        Capitals'.
        """
        if self.winner == HOME:
            return self._away_name.text()
        return self._home_name.text()

    @property
    def losing_abbr(self):
        """
        Returns a string of the losing team's abbreviation, such as 'WSH'
        for the Washington Capitals.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._away_name)
        return utils._parse_abbreviation(self._home_name)

    @property
    def away_goals(self):
        """
        Returns an int of the number of goals the away team scored.
        """
        return int(self._away_goals)

    @property
    def away_assists(self):
        """
        Returns an int of the number of assists the away team registered.
        """
        return int(self._away_assists)

    @property
    def away_points(self):
        """
        Returns an int of the number of points the away team registered.
        """
        return int(self._away_points)

    @property
    def away_penalties_in_minutes(self):
        """
        Returns an int of the length of time the away team spent in the penalty
        box.
        """
        return int(self._away_penalties_in_minutes)

    @property
    def away_even_strength_goals(self):
        """
        Returns an int of the number of goals the away team scored at even
        strength.
        """
        return int(self._away_even_strength_goals)

    @property
    def away_power_play_goals(self):
        """
        Returns an int of the number of goals the away team scored while on a
        power play.
        """
        return int(self._away_power_play_goals)

    @property
    def away_short_handed_goals(self):
        """
        Returns an int of the number of goals the away team scored while short
        handed.
        """
        return int(self._away_short_handed_goals)

    @property
    def away_game_winning_goals(self):
        """
        Returns an int of the number of game winning goals the away team
        scored.
        """
        goals = self._away_game_winning_goals[:self._away_skaters]
        num = 0
        for x in goals:
            try:
                num += int(x)
            except ValueError:
                continue
        return num

    @property
    def away_even_strength_assists(self):
        """
        Returns an int of the number of assists the away team registered while
        at even strength.
        """
        assists = self._away_even_strength_assists[:self._away_skaters]
        num = 0
        for x in assists:
            try:
                num += int(x)
            except ValueError:
                continue
        return num

    @property
    def away_power_play_assists(self):
        """
        Returns an int of the number of assists the away team registered while
        on a power play.
        """
        assists = self._away_power_play_assists[:self._away_skaters]
        num = 0
        for x in assists:
            try:
                num += int(x)
            except ValueError:
                continue
        return num

    @property
    def away_short_handed_assists(self):
        """
        Returns an int of the number of assists the away team registered while
        short handed.
        """
        assists = self._away_short_handed_assists[:self._away_skaters]
        num = 0
        for x in assists:
            try:
                num += int(x)
            except ValueError:
                continue
        return num

    @property
    def away_shots_on_goal(self):
        """
        Returns an int of the number of shots on goal the away team registered.
        """
        return int(self._away_shots_on_goal)

    @property
    def away_shooting_percentage(self):
        """
        Returns a float of the away team's shooting percentage. Percentage
        ranges from 0-100.
        """
        return float(self._away_shooting_percentage)

    @property
    def away_saves(self):
        """
        Returns an int of the number of saves the away team made.
        """
        return int(self._away_saves)

    @property
    def away_save_percentage(self):
        """
        Returns a float of the percentage of shots the away team saved.
        Percentage ranges from 0-1.
        """
        return float(self._away_save_percentage)

    @property
    def away_shutout(self):
        """
        Returns an int denoting whether or not the away team shutout the home
        team.
        """
        return int(self._away_shutout)

    @property
    def home_goals(self):
        """
        Returns an int of the number of goals the home team scored.
        """
        return int(self._home_goals)

    @property
    def home_assists(self):
        """
        Returns an int of the number of assists the home team registered.
        """
        return int(self._home_assists)

    @property
    def home_points(self):
        """
        Returns an int of the number of points the home team registered.
        """
        return int(self._home_points)

    @property
    def home_penalties_in_minutes(self):
        """
        Returns an int of the length of time the home team spent in the penalty
        box.
        """
        return int(self._home_penalties_in_minutes)

    @property
    def home_even_strength_goals(self):
        """
        Returns an int of the number of goals the home team scored at even
        strength.
        """
        return int(self._home_even_strength_goals)

    @property
    def home_power_play_goals(self):
        """
        Returns an int of the number of goals the home team scored while on a
        power play.
        """
        return int(self._home_power_play_goals)

    @property
    def home_short_handed_goals(self):
        """
        Returns an int of the number of goals the home team scored while short
        handed.
        """
        return int(self._home_short_handed_goals)

    @property
    def home_game_winning_goals(self):
        """
        Returns an int of the number of game winning goals the home team
        scored.
        """
        goals = self._home_game_winning_goals[self._away_skaters:]
        num = 0
        for x in goals:
            try:
                num += int(x)
            except ValueError:
                continue
        return num

    @property
    def home_even_strength_assists(self):
        """
        Returns an int of the number of assists the home team registered while
        at even strength.
        """
        assists = self._home_even_strength_assists[self._away_skaters:]
        num = 0
        for x in assists:
            try:
                num += int(x)
            except ValueError:
                continue
        return num

    @property
    def home_power_play_assists(self):
        """
        Returns an int of the number of assists the home team registered while
        on a power play.
        """
        assists = self._home_power_play_assists[self._away_skaters:]
        num = 0
        for x in assists:
            try:
                num += int(x)
            except ValueError:
                continue
        return num

    @property
    def home_short_handed_assists(self):
        """
        Returns an int of the number of assists the home team registered while
        short handed.
        """
        assists = self._home_short_handed_assists[self._away_skaters:]
        num = 0
        for x in assists:
            try:
                num += int(x)
            except ValueError:
                continue
        return num

    @property
    def home_shots_on_goal(self):
        """
        Returns an int of the number of shots on goal the home team registered.
        """
        return int(self._home_shots_on_goal)

    @property
    def home_shooting_percentage(self):
        """
        Returns a float of the home team's shooting percentage. Percentage
        ranges from 0-100.
        """
        return float(self._home_shooting_percentage)

    @property
    def home_saves(self):
        """
        Returns an int of the number of saves the home team made.
        """
        return int(self._home_saves)

    @property
    def home_save_percentage(self):
        """
        Returns a float of the percentage of shots the home team saved.
        Percentage ranges from 0-1.
        """
        return float(self._home_save_percentage)

    @property
    def home_shutout(self):
        """
        Returns an int denoting whether or not the home team shutout the home
        team.
        """
        return int(self._home_shutout)
