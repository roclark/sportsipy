from pyquery import PyQuery as pq
import re
from urllib.error import HTTPError
from .. import utils
from .constants import CONFERENCE_URL, CONFERENCES_URL


class Conference:
    """
    Find teams that participated in a particular conference.

    Create a dictionary which includes the names and abbreviations for all
    teams that participated in a conference during a given year.

    Parameters
    ----------
    conference_abbreviation : string
        A string of the requested conference's abbreviation, such as
        'big-12'.
    year : string (optional)
        A string of the requested year to pull conference information from.
        Defaults to the most recent season.
    """
    def __init__(self, conference_abbreviation, year=None):
        self._teams = {}

        self._find_conference_teams(conference_abbreviation, year)

    def _pull_conference_page(self, conference_abbreviation, year):
        """
        Download the conference page.

        Download the conference page for the requested conference and season
        and create a PyQuery object.

        Parameters
        ----------
        conference_abbreviation : string
            A string of the requested conference's abbreviation, such as
            'big-12'.
        year : string
            A string of the requested year to pull conference information from.
        """
        try:
            return pq(CONFERENCE_URL % (conference_abbreviation, year))
        except HTTPError:
            return None

    def _get_team_abbreviation(self, team):
        """
        Retrieve team's abbreviation.

        The team's abbreviation is embedded within the 'school_name' tag and
        requires special parsing as it is located in the middle of a URI. The
        abbreviation is returned for the requested school.

        Parameters
        ----------
        team : PyQuery object
            A PyQuery object representing a single row in a table on the
            conference page.

        Returns
        -------
        string
            Returns a string of the team's abbreviation, such as 'PURDUE'.
        """
        name_tag = team('td[data-stat="school_name"] a')
        team_abbreviation = re.sub(r'.*/cbb/schools/', '', str(name_tag))
        team_abbreviation = re.sub(r'/.*', '', team_abbreviation)
        return team_abbreviation

    def _find_conference_teams(self, conference_abbreviation, year):
        """
        Retrieve the teams in the conference for the requested season.

        Find and retrieve all teams that participated in a conference for a
        given season. The name and abbreviation for each team are parsed and
        recorded to enable easy queries of conference schools..

        Parameters
        ----------
        conference_abbreviation : string
            A string of the requested conference's abbreviation, such as
            'big-12'.
        year : string
            A string of the requested year to pull conference information from.
        """
        if not year:
            year = utils._find_year_for_season('ncaab')
            # If stats for the requested season do not exist yet (as is the
            # case right before a new season begins), attempt to pull the
            # previous year's stats. If it exists, use the previous year
            # instead.
            if not utils._url_exists(CONFERENCES_URL % year) and \
               utils._url_exists(CONFERENCES_URL % str(int(year) - 1)):
                year = str(int(year) - 1)
        page = self._pull_conference_page(conference_abbreviation, year)
        if not page:
            url = CONFERENCE_URL % (conference_abbreviation, year)
            output = ("Can't pull requested conference page. Ensure the "
                      "following URL exists: %s" % url)
            raise ValueError(output)
        conference = page('table#standings tbody tr').items()
        for team in conference:
            team_abbreviation = self._get_team_abbreviation(team)
            if team_abbreviation == '':
                continue
            team_name = team('td[data-stat="school_name"]').text()
            self._teams[team_abbreviation] = team_name

    @property
    def teams(self):
        """
        Returns a ``dictionary`` of team names and abbreviations where each key
        is a ``string`` of the team abbreviation and each value is a ``string``
        of the full team name.
        """
        return self._teams


class Conferences:
    """
    Get all conferences and teams for a season.

    Retrieve a list of all conferences and teams that participated in the
    conference for each team in the season. The included properties allow
    flexibility in queries to either get the conference abbreviation for a
    given team, or get more detailed information including all teams for each
    conference.

    Parameters
    ----------
    year : string (optional)
        A string of the requested year to pull conferences from. Defaults to
        the most recent season.
    """
    def __init__(self, year=None):
        self._conferences = {}
        self._team_conference = {}

        self._find_conferences(year)

    def _pull_conference_page(self, year):
        """
        Download the conference page.

        Download the conference page for the requested team and create a
        PyQuery object.

        Parameters
        ----------
        year : string
            A string of the requested year to pull rankings from.

        Returns
        -------
        PyQuery object
            Returns a PyQuery object of the conference HTML page.
        """
        try:
            return pq(CONFERENCES_URL % year)
        except HTTPError:
            return None

    def _get_conference_id(self, conference):
        """
        Get the conference abbreviation, such as 'big-12'.

        The conference abbreviation is embedded within the Conference Name
        tag and requires special parsing to extract. The abbreviation is
        returned as a string.

        Parameters
        ----------
        conference : PyQuery object
            A PyQuery object representing a single row in the conference table
            which can be used to find the conference abbreviation.

        Returns
        -------
        string
            Returns a string of the conference abbreviation, such as 'big-12'.
        """
        name_tag = conference('td[data-stat="conf_name"] a')
        conference_id = re.sub(r'.*/cbb/conferences/', '', str(name_tag))
        conference_id = re.sub(r'/.*', '', conference_id)
        return conference_id

    def _find_conferences(self, year):
        """
        Retrieve the conferences and teams for the requested season.

        Find and retrieve all conferences for a given season and parse all of
        the teams that participated in the conference during that year.
        Conference information includes abbreviation and full name for the
        conference as well as the abbreviation and full name for each team in
        the conference.

        Parameters
        ----------
        year : string
            A string of the requested year to pull conferences from.
        """
        if not year:
            year = utils._find_year_for_season('ncaab')
            # If stats for the requested season do not exist yet (as is the
            # case right before a new season begins), attempt to pull the
            # previous year's stats. If it exists, use the previous year
            # instead.
            if not utils._url_exists(CONFERENCES_URL % year) and \
               utils._url_exists(CONFERENCES_URL % str(int(year) - 1)):
                year = str(int(year) - 1)
        page = self._pull_conference_page(year)
        if not page:
            output = ("Can't pull requested conference page. Ensure the "
                      "following URL exists: %s" % (CONFERENCES_URL % year))
            raise ValueError(output)
        conferences = page('table#conference-summary tbody tr').items()
        for conference in conferences:
            conference_abbreviation = self._get_conference_id(conference)
            conference_name = conference('td[data-stat="conf_name"]').text()
            teams_dict = Conference(conference_abbreviation, year).teams
            conference_dict = {
                    'name': conference_name,
                    'teams': teams_dict
                }
            for team in teams_dict.keys():
                self._team_conference[team] = conference_abbreviation
            self._conferences[conference_abbreviation] = conference_dict

    @property
    def conferences(self):
        """
        Returns a ``dictionary`` of conference names and abbreviations where
        each key is a ``string`` of the abbreviation and each value is a
        ``dictionary`` containing the full conference name and another
        ``dictionary`` with individual team information. The overall dictionary
        is in the following structure::

            {
                abbreviation, ie 'big-12' (str): {
                    'name': Full conference name, such as 'Big 12 Conference'
                            (str),
                    'teams': {
                        team abbreviation, such as 'kansas' (str): Full team
                            name, such as 'Kansas' (str),
                        ...
                    }
                },
                ...
            }
        """
        return self._conferences

    @property
    def team_conference(self):
        """
        Returns a ``dictionary`` of conference abbreviations for each team
        where each key is a ``string`` of the team abbreviation and each value
        is a ``string`` of the conference abbreviation.
        """
        return self._team_conference
