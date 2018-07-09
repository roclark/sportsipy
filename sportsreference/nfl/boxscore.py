import pandas as pd
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
    location, result, and more advanced metrics such as the number of yards
    from sacks, a team's passing completion, rushing touchdowns and much more.
    """
    def __init__(self, uri):
        """
        Parse all of the attributes located in the HTML data.

        Parameters
        ----------
        uri : string
            The relative link to the boxscore HTML page, such as
            '201802040nwe'.
        """
        self._uri = uri
        self._date = None
        self._time = None
        self._stadium = None
        self._attendance = None
        self._duration = None
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
        self._away_times_sacked = None
        self._away_yards_lost_from_sacks = None
        self._away_net_pass_yards = None
        self._away_total_yards = None
        self._away_fumbles = None
        self._away_fumbles_lost = None
        self._away_turnovers = None
        self._away_penalties = None
        self._away_yards_from_penalties = None
        self._away_third_down_conversions = None
        self._away_third_down_attempts = None
        self._away_fourth_down_conversions = None
        self._away_fourth_down_attempts = None
        self._away_time_of_possession = None
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
        self._home_times_sacked = None
        self._home_yards_lost_from_sacks = None
        self._home_net_pass_yards = None
        self._home_total_yards = None
        self._home_fumbles = None
        self._home_fumbles_lost = None
        self._home_turnovers = None
        self._home_penalties = None
        self._home_yards_from_penalties = None
        self._home_third_down_conversions = None
        self._home_third_down_attempts = None
        self._home_fourth_down_conversions = None
        self._home_fourth_down_attempts = None
        self._home_time_of_possession = None

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
            '201802040nwe'.

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
        # For NFL, a 404 page doesn't actually raise a 404 error, so it needs
        # to be manually checked.
        if '404 error' in str(url_data):
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
            '201802040nwe'.
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
               short_field == 'losing_abbr' or \
               short_field == 'uri':
                continue
            if short_field == 'date' or \
               short_field == 'time' or \
               short_field == 'stadium' or \
               short_field == 'attendance' or \
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
            index = 0
            if short_field in BOXSCORE_ELEMENT_INDEX.keys():
                index = BOXSCORE_ELEMENT_INDEX[short_field]
            value = utils._parse_field(BOXSCORE_SCHEME,
                                       boxscore,
                                       short_field,
                                       index)
            setattr(self, field, value)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the string URI that is used to
        instantiate the class, such as '201802040nwe'.
        """
        if self._away_points is None and self._home_points is None:
            return None
        fields_to_include = {
            'attendance': self.attendance,
            'away_first_downs': self.away_first_downs,
            'away_fourth_down_attempts': self.away_fourth_down_attempts,
            'away_fourth_down_conversions': self.away_fourth_down_conversions,
            'away_fumbles': self.away_fumbles,
            'away_fumbles_lost': self.away_fumbles_lost,
            'away_interceptions': self.away_interceptions,
            'away_net_pass_yards': self.away_net_pass_yards,
            'away_pass_attempts': self.away_pass_attempts,
            'away_pass_completions': self.away_pass_completions,
            'away_pass_touchdowns': self.away_pass_touchdowns,
            'away_pass_yards': self.away_pass_yards,
            'away_penalties': self.away_penalties,
            'away_points': self.away_points,
            'away_rush_attempts': self.away_rush_attempts,
            'away_rush_touchdowns': self.away_rush_touchdowns,
            'away_rush_yards': self.away_rush_yards,
            'away_third_down_attempts': self.away_third_down_attempts,
            'away_third_down_conversions': self.away_third_down_conversions,
            'away_time_of_possession': self.away_time_of_possession,
            'away_times_sacked': self.away_times_sacked,
            'away_total_yards': self.away_total_yards,
            'away_turnovers': self.away_turnovers,
            'away_yards_from_penalties': self.away_yards_from_penalties,
            'away_yards_lost_from_sacks': self.away_yards_lost_from_sacks,
            'date': self.date,
            'duration': self.duration,
            'home_first_downs': self.home_first_downs,
            'home_fourth_down_attempts': self.home_fourth_down_attempts,
            'home_fourth_down_conversions': self.home_fourth_down_conversions,
            'home_fumbles': self.home_fumbles,
            'home_fumbles_lost': self.home_fumbles_lost,
            'home_interceptions': self.home_interceptions,
            'home_net_pass_yards': self.home_net_pass_yards,
            'home_pass_attempts': self.home_pass_attempts,
            'home_pass_completions': self.home_pass_completions,
            'home_pass_touchdowns': self.home_pass_touchdowns,
            'home_pass_yards': self.home_pass_yards,
            'home_penalties': self.home_penalties,
            'home_points': self.home_points,
            'home_rush_attempts': self.home_rush_attempts,
            'home_rush_touchdowns': self.home_rush_touchdowns,
            'home_rush_yards': self.home_rush_yards,
            'home_third_down_attempts': self.home_third_down_attempts,
            'home_third_down_conversions': self.home_third_down_conversions,
            'home_time_of_possession': self.home_time_of_possession,
            'home_times_sacked': self.home_times_sacked,
            'home_total_yards': self.home_total_yards,
            'home_turnovers': self.home_turnovers,
            'home_yards_from_penalties': self.home_yards_from_penalties,
            'home_yards_lost_from_sacks': self.home_yards_lost_from_sacks,
            'losing_abbr': self.losing_abbr,
            'losing_name': self.losing_name,
            'stadium': self.stadium,
            'time': self.time,
            'winner': self.winner,
            'winning_abbr': self.winning_abbr,
            'winning_name': self.winning_name
        }
        return pd.DataFrame([fields_to_include], index=[self._uri])

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
        return self._duration.replace('Time of Game: ', '')

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
        Returns a string of the winning team's name, such as 'New England
        Patriots'.
        """
        if self.winner == HOME:
            return self._home_name.text()
        return self._away_name.text()

    @property
    def winning_abbr(self):
        """
        Returns a string of the winning team's abbreviation, such as 'NWE'
        for the New England Patriots.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._home_name)
        return utils._parse_abbreviation(self._away_name)

    @property
    def losing_name(self):
        """
        Returns a string of the losing team's name, such as 'Kansas City
        Chiefs'.
        """
        if self.winner == HOME:
            return self._away_name.text()
        return self._home_name.text()

    @property
    def losing_abbr(self):
        """
        Returns a string of the losing team's abbreviation, such as 'KAN'
        for the Kansas City Chiefs.
        """
        if self.winner == HOME:
            return utils._parse_abbreviation(self._away_name)
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
    def away_times_sacked(self):
        """
        Returns an int of the number of times the away team was sacked.
        """
        # Sacks info is in the format 'Sacked-Yards'
        sacks_info = self._away_times_sacked.split('-')
        return int(sacks_info[0])

    @property
    def away_yards_lost_from_sacks(self):
        """
        Returns an int of the number of yards the away team lost as the result
        of a sack.
        """
        # Sacks info is in the format 'Sacked-Yards'
        sacks_info = self._away_yards_lost_from_sacks.split('-')
        return int(sacks_info[1])

    @property
    def away_net_pass_yards(self):
        """
        Returns an int of the net pass yards gained by the away team.
        """
        return int(self._away_net_pass_yards)

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
    def away_third_down_conversions(self):
        """
        Returns an int of the number of third down plays the away team
        successfully converted.
        """
        # Conversion info is in the format 'Conversions-Attempts'
        conversion_info = self._away_third_down_conversions.split('-')
        return int(conversion_info[0])

    @property
    def away_third_down_attempts(self):
        """
        Returns an int of the number of third down plays the away team
        attempted to convert.
        """
        # Conversion info is in the format 'Conversions-Attempts'
        conversion_info = self._away_third_down_attempts.split('-')
        return int(conversion_info[1])

    @property
    def away_fourth_down_conversions(self):
        """
        Returns an int of the number of fourth down plays the away team
        successfully converted.
        """
        # Conversion info is in the format 'Conversions-Attempts'
        conversion_info = self._away_fourth_down_conversions.split('-')
        return int(conversion_info[0])

    @property
    def away_fourth_down_attempts(self):
        """
        Returns an int of the number of fourth down plays the away team
        attempted to convert.
        """
        # Conversion info is in the format 'Conversions-Attempts'
        conversion_info = self._away_fourth_down_attempts.split('-')
        return int(conversion_info[1])

    @property
    def away_time_of_possession(self):
        """
        Returns a string of the amount of time the home team had possession of
        the football in the format 'MM:SS'.
        """
        return self._away_time_of_possession

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
    def home_times_sacked(self):
        """
        Returns an int of the number of times the home team was sacked.
        """
        # Sacks info is in the format 'Sacked-Yards'
        sacks_info = self._home_times_sacked.split('-')
        return int(sacks_info[0])

    @property
    def home_yards_lost_from_sacks(self):
        """
        Returns an int of the number of yards the home team lost as the result
        of a sack.
        """
        # Sacks info is in the format 'Sacked-Yards'
        fumble_info = self._home_yards_lost_from_sacks.split('-')
        return int(fumble_info[1])

    @property
    def home_net_pass_yards(self):
        """
        Returns an int of the net pass yards gained by the home team.
        """
        return int(self._home_net_pass_yards)

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

    @property
    def home_third_down_conversions(self):
        """
        Returns an int of the number of third down plays the home team
        successfully converted.
        """
        # Conversion info is in the format 'Conversions-Attempts'
        conversion_info = self._home_third_down_conversions.split('-')
        return int(conversion_info[0])

    @property
    def home_third_down_attempts(self):
        """
        Returns an int of the number of third down plays the home team
        attempted to convert.
        """
        # Conversion info is in the format 'Conversions-Attempts'
        conversion_info = self._home_third_down_attempts.split('-')
        return int(conversion_info[1])

    @property
    def home_fourth_down_conversions(self):
        """
        Returns an int of the number of fourth down plays the home team
        successfully converted.
        """
        # Conversion info is in the format 'Conversions-Attempts'
        conversion_info = self._home_fourth_down_conversions.split('-')
        return int(conversion_info[0])

    @property
    def home_fourth_down_attempts(self):
        """
        Returns an int of the number of fourth down plays the home team
        attempted to convert.
        """
        # Conversion info is in the format 'Conversions-Attempts'
        conversion_info = self._home_fourth_down_conversions.split('-')
        return int(conversion_info[1])

    @property
    def home_time_of_possession(self):
        """
        Returns a string of the amount of time the home team had possession of
        the football in the format 'MM:SS'.
        """
        return self._home_time_of_possession
