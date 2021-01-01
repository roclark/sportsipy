import re
from .constants import SQUAD_URL
from ..decorators import float_property_decorator, int_property_decorator
from .fb_utils import _lookup_team
from pyquery import PyQuery as pq
from .roster import Roster
from .schedule import Schedule
from .squad_ids import SQUAD_IDS
from urllib.error import HTTPError
from .. import utils


class Team:
    """
    The high-level stats and information for a single professional team.

    By requesting a team via either a name or squad ID, an object will be
    created which contains high-level information and stats for that team, if
    found. The information ranges from the name of their primary competition,
    including their point-return, position, and place, plus the number of goals
    they have scored, and a pointer to the team roster and schedule.

    If a team cannot be identified for the given name or ID, a list of the
    closest matches will be returned as a dictionary instead.

    Parameters
    ----------
    team_id : string
        A string representing either the team's full name, such as 'Tottenham
        Hotspur', or the team's 8-digit squad ID, such as '361ca564' for
        Tottenham. If a team can't be found for the given name, a list of
        suggestions will be returned with corresponding squad IDs.
    squad_page : string (optional)
        Optionally specify the filename of a local file to use to pull data
        instead of downloading from sports-reference.com. This file should be
        of the Squad page for the designated year.
    """
    def __init__(self, team_id, squad_page=None):
        self._squad_id = None
        self._name = None
        self._season = None
        self._record = None
        self._position = None
        self._points = None
        self._league = None
        self._manager = None
        self._country = None
        self._gender = None
        self._goals_scored = None
        self._goals_against = None
        self._goal_difference = None
        self._expected_goals = None
        self._expected_goals_against = None
        self._expected_goal_difference = None
        self._home_record = None
        self._home_games = None
        self._away_record = None
        self._away_games = None
        self._home_wins = None
        self._home_draws = None
        self._home_losses = None
        self._away_wins = None
        self._away_draws = None
        self._away_losses = None
        self._home_points = None
        self._away_points = None

        self._squad_id = _lookup_team(team_id)
        self._pull_team_page(squad_page)

    def __str__(self):
        """
        Return the string representation of the class.
        """
        return f'{self.name} ({self.squad_id}) - {self.season}'

    def __repr__(self):
        """
        Return the string representation of the class.
        """
        return self.__str__()

    def _parse_name(self, doc):
        """
        Parse the team's name and season.

        The squad header includes both the season (in the format '2019-2020' or
        '2020') as well as the official team name, such as 'Tottenham Hotspur'.

        Parameters
        ----------
        doc : PyQuery object
            A PyQuery object of the squad's entire HTML page.
        """
        name = doc('h1[itemprop="name"]')
        name = name('span').text()
        # Name is in format "YYYY-YYYY Team Name Stats"
        # or "YYYY Team Name Stats"
        # ie. "2019-2020 Tottenham Hotspur Stats"
        # or "2020 Sporting KC Stats"
        # The season will always be the first part of the string.
        season = name.split(' ')[0]
        # The team's name will always be between the season and the string
        # "Stats", and therefore only those pieces should be pulled.
        name = ' '.join(name.split(' ')[1:-1])
        self._season = season
        self._name = name

    def _location_records(self, record_line):
        """
        Parse the team's home and away record.

        The squad's header contains information on the team's home and away
        record in the league, including the points gained both at home and on
        the road. Only the integer-based points as well as a string of the
        record should be parsed and returned for later use.

        Parameters
        ----------
        record_line : string
            A ``string`` representing the team's home and away record in as
            displayed in the squad team's header.

        Returns
        -------
        tuple
            Returns a ``tuple`` of the location-based records in the following
            format: (home record, away record, home points, away points).
        """
        home_record, away_record = None, None
        home_points, away_points = None, None
        records = record_line.lower().replace('home record: ', '')
        records = records.replace('away record: ', '')
        match_records = re.findall(r'\(.*?\)', records)
        p = re.compile(r'[\(\)]')
        if len(match_records) == 2:
            home_record, away_record = [p.sub(' ', x).strip()
                                        for x in match_records]
        points = re.sub(r'\(.*?\)', '', records)
        points = re.findall(r'\d+', points)
        if len(points) == 2:
            home_points, away_points = [int(p) for p in points]
        return home_record, away_record, home_points, away_points

    def _records(self, record_line):
        """
        Parse the team's record in their primary competition.

        The team's record line found on the header of their squad page includes
        the team's record, position in the league, points, and league name for
        their primary competition during the season.

        Parameters
        ----------
        record_line : string
            A ``string`` representing the first line of the team's header which
            contains information on the squad's record, position, and league.

        Returns
        -------
        tuple
            A ``tuple`` of the parsed results in the following format: (record,
            points, position, league name).
        """
        records = record_line.lower().replace('record: ', '')
        records_split = records.split(',')
        if len(records_split) != 3:
            return None, None, None, None
        record, points, position = records_split
        points = re.sub(' point.*', '', points).strip()
        position = re.sub(r'\(.*\)', '', position).strip()
        league = re.sub('.* in ', '', position).title()
        try:
            position = re.findall(r'\d+', position)[0]
        except IndexError:
            position = None
        return record, points, position, league

    def _goals(self, goals_line):
        """
        Parse the number of goals the team scored and conceded.

        The number of goals the team scored and conceded, along with the
        difference, can be found in the header. Only the integer point values
        should be parsed and returned.

        Parameters
        ----------
        goals_line : string
            A ``string`` representation of the HTML line for the goals scored
            and conceded by the team.

        Returns
        -------
        tuple
            Returns a ``tuple`` of the teams goals in the following format:
            (goals scored, goals against, goal difference).
        """
        goals = re.sub(r'\(.*?\)', '', goals_line.lower())
        goals = re.findall(r'\d+', goals)
        if len(goals) != 3:
            return None, None, None
        return goals

    def _parse_expected_goals(self, goals_line):
        """
        Parse the expected goals for the team.

        The expected goal values can be found in the header with the xG, xGA
        prefixes. This is the number of goals the team was expected to score
        and concede during the season, as opposed to the actual numbers they
        tallied. The line also includes the difference between the expected
        goals scored and conceded.

        Parameters
        ----------
        goals_line : string
            A ``string`` representation of the HTML line for the expected goals
            found in the squad's header.

        Returns
        -------
        tuple
            Returns a ``tuple`` of the team's expected goals in the following
            format: (expected goals scored, expected goals against, expected
            goal difference).
        """
        goals = goals_line.replace('xG: ', '')
        goals = goals.replace(', xGA: ', ' ')
        goals = goals.replace(', Diff: ', ' ')
        goals = goals.split(' ')
        if len(goals) != 3:
            return None, None, None
        return goals

    def _parse_header(self, doc):
        """
        Parse the various components on the squad's header.

        Each squad page contains information relevant to the team's selected
        year, including the season, record, goals, position in their league
        competition, manager, and more. Much of this information should be used
        to augment the squad class to provide further details and context on
        the team.

        The function pulls the header for the squad's page and parses
        information line-by-line to retrieve relevant values. Since various
        pages may have less information than others, a looping structure with
        an if-elif block to check the contents of the line is the best way to
        ensure only the expected information is collected in each part.

        Parameters
        ----------
        doc : PyQuery object
            A PyQuery object containing the entire HTML contents of the squad's
            home page.
        """
        header = doc('div[data-template="Partials/Teams/Summary"]')
        for header_line in header('p'):
            line = pq(header_line).text()
            if 'home record' in line.lower():
                # Returns in the format (home_record, away_record, home_points,
                # away_points).
                records = self._location_records(line)
                self._home_record = records[0]
                self._away_record = records[1]
                self._home_points = records[2]
                self._away_points = records[3]
            elif 'record' in line.lower():
                # Returns in format (record, points, position, league).
                records = self._records(line)
                self._record = records[0]
                self._points = records[1]
                self._position = records[2]
                self._league = records[3]
            elif 'goals' in line.lower():
                # Returns in format (scored, against, difference).
                goals = self._goals(line)
                self._goals_scored = goals[0]
                self._goals_against = goals[1]
                self._goal_difference = goals[2]
            elif 'xGA' in line and 'Diff' in line:
                # Returns in format (expected, against, difference).
                goals = self._parse_expected_goals(line)
                self._expected_goals = goals[0]
                self._expected_goals_against = goals[1]
                self._expected_goal_difference = goals[2]
            elif 'manager' in line.lower():
                self._manager = line.replace('Manager: ', '')
            elif 'governing country' in line.lower():
                self._country = pq(header_line)('a').text()
            elif 'gender' in line.lower():
                self._gender = line.replace('Gender: ', '')

    def _pull_team_page(self, squad_page=None):
        """
        Pull the team page and parse results.

        Using the requested squad ID, first pull the team page, then parse
        the header for relevant information on the team including records,
        goals, manager, league results, and more.

        Parameters
        ----------
        squad_page : string (optional)
            Optionally specify the filename of a local file to use to pull data
            instead of downloading from sports-reference.com. This file should
            be of the Squad page for the designated year.
        """
        try:
            doc = utils._pull_page(SQUAD_URL % self.squad_id, squad_page)
        except HTTPError:
            return
        self._doc = doc
        self._parse_name(doc)
        self._parse_header(doc)

    @property
    def squad_id(self):
        """
        Returns a ``string`` of the team's squad ID according to
        sports-reference.com, such as '361ca564' for Tottenham Hotspur.
        """
        return self._squad_id

    @property
    def name(self):
        """
        Returns a ``string`` of the team's full name, such as 'Tottenham
        Hotspur'.
        """
        return self._name

    @property
    def schedule(self):
        """
        Returns an instance of the Schedule class containing the team's
        complete schedule for the season.
        """
        if not hasattr(self, '_doc'):
            self._doc = None
        return Schedule(self.squad_id, self._doc)

    @property
    def roster(self):
        """
        Returns an instance of the Roster class containing instances of every
        player on the team.
        """
        if not hasattr(self, '_doc'):
            self._doc = None
        return Roster(self._squad_id, self._doc)

    @property
    def season(self):
        """
        Returns a ``string`` of the season's year(s) in the format YYYY or
        YYYY-YYYY. For example, '2020' or '2019-2020'.
        """
        return self._season

    @property
    def record(self):
        """
        Returns a ``string`` of the team's record during their primary
        competition (ie. Premier League) for the current season in the format
        'Wins-Draws-Losses'.
        """
        return self._record

    @int_property_decorator
    def position(self):
        """
        Returns an ``int`` of the team's place in the table (ie. 1 for first)
        for the current season in their primary competition (ie. Premier
        League).
        """
        return self._position

    @int_property_decorator
    def points(self):
        """
        Returns an ``int`` of the number of points the team has gained in their
        primary competition (ie. Premier League).
        """
        return self._points

    @property
    def league(self):
        """
        Returns a ``string`` of the team's primary competition, such as
        'Premier League'.
        """
        return self._league

    @property
    def manager(self):
        """
        Returns a ``string`` of the full name of the team's manager, such as
        'José Mourinho'.
        """
        return self._manager

    @property
    def country(self):
        """
        Returns a ``string`` of the team's governing country, such as
        'England'.
        """
        return self._country

    @property
    def gender(self):
        """
        Returns a ``string`` denoting which gender the team competes in (ie.
        'Female').
        """
        return self._gender

    @int_property_decorator
    def goals_scored(self):
        """
        Returns an ``int`` of the number of goals the team has scored during
        their primary competition (ie. Premier League).
        """
        return self._goals_scored

    @int_property_decorator
    def goals_against(self):
        """
        Returns an ``int`` of the number of goals the team has allowed during
        their primary competition (ie. Premier League).
        """
        return self._goals_against

    @int_property_decorator
    def goal_difference(self):
        """
        Returns an ``int`` of the team's goal difference during their primary
        competition (ie. Premier League).
        """
        return self._goal_difference

    @float_property_decorator
    def expected_goals(self):
        """
        Returns a ``float`` of the number of goals the team was expected to
        score during their primary competition (ie. Premier League).
        """
        return self._expected_goals

    @float_property_decorator
    def expected_goals_against(self):
        """
        Returns a ``float`` of the number of goals the team was expected to
        concede during their primary competition (ie. Premier League).
        """
        return self._expected_goals_against

    @float_property_decorator
    def expected_goal_difference(self):
        """
        Returns a ``float`` of the difference between the team's expected
        goals scored and conceded during their primary competition (ie. Premier
        League).
        """
        return self._expected_goal_difference

    @property
    def home_record(self):
        """
        Returns a ``string`` of the team's home record during their primary
        competition (ie. Premier League) for the current season in the format
        'Wins-Draws-Losses'.
        """
        return self._home_record

    @int_property_decorator
    def home_games(self):
        """
        Returns an ``int`` of the number of games the team has played at home
        during their primary competition (ie. Premier League).
        """
        try:
            return self.home_wins + self.home_draws + self.home_losses
        except TypeError:
            return None

    @property
    def away_record(self):
        """
        Returns a ``string`` of the team's away record during their primary
        competition (ie. Premier League) for the current season in the format
        'Wins-Draws-Losses'.
        """
        return self._away_record

    @int_property_decorator
    def away_games(self):
        """
        Returns an ``int`` of the number of games the team has played away
        during their primary competition (ie. Premier League).
        """
        try:
            return self.away_wins + self.away_draws + self.away_losses
        except TypeError:
            return None

    @int_property_decorator
    def home_wins(self):
        """
        Returns an ``int`` of the number of games the team has won at home
        during their primary competition (ie. Premier League) for the current
        season.
        """
        try:
            record = self._home_record.split('-')
            wins = record[0]
            wins = int(wins)
        except ValueError:
            return None
        except AttributeError:
            return None
        return wins

    @int_property_decorator
    def home_draws(self):
        """
        Returns an ``int`` of the number of games the team has drawn at home
        during their primary competition (ie. Premier League) for the current
        season.
        """
        try:
            record = self._home_record.split('-')
            draws = record[1]
            draws = int(draws)
        except IndexError:
            return None
        except ValueError:
            return None
        except AttributeError:
            return None
        return draws

    @int_property_decorator
    def home_losses(self):
        """
        Returns an ``int`` of the number of games the team has lost at home
        during their primary competition (ie. Premier League) for the current
        season.
        """
        try:
            record = self._home_record.split('-')
            losses = record[2]
            losses = int(losses)
        except IndexError:
            return None
        except ValueError:
            return None
        except AttributeError:
            return None
        return losses

    @int_property_decorator
    def away_wins(self):
        """
        Returns an ``int`` of the number of games the team has won while away
        during their primary competition (ie. Premier League) for the current
        season.
        """
        try:
            record = self._away_record.split('-')
            wins = record[0]
            wins = int(wins)
        except ValueError:
            return None
        except AttributeError:
            return None
        return wins

    @int_property_decorator
    def away_draws(self):
        """
        Returns an ``int`` of the number of games the team has drawn while away
        during their primary competition (ie. Premier League) for the current
        season.
        """
        try:
            record = self._away_record.split('-')
            draws = record[1]
            draws = int(draws)
        except IndexError:
            return None
        except ValueError:
            return None
        except AttributeError:
            return None
        return draws

    @int_property_decorator
    def away_losses(self):
        """
        Returns an ``int`` of the number of games the team has lost while away
        during their primary competition (ie. Premier League) for the current
        season.
        """
        try:
            record = self._away_record.split('-')
            losses = record[2]
            losses = int(losses)
        except IndexError:
            return None
        except ValueError:
            return None
        except AttributeError:
            return None
        return losses

    @int_property_decorator
    def home_points(self):
        """
        Returns an ``int`` of the number of points the team has gained while at
        home during their primary competition (ie. Premier League) for the
        current season.
        """
        return self._home_points

    @int_property_decorator
    def away_points(self):
        """
        Returns an ``int`` of the number of points the team has gained while
        away during their primary competition (ie. Premier League) for the
        current season.
        """
        return self._away_points
