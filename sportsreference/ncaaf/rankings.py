import re
from pyquery import PyQuery as pq
from urllib.error import HTTPError
from .. import utils
from .constants import RANKINGS_SCHEME, RANKINGS_URL


class Rankings:
    """
    Get all Associated Press (AP) rankings on a week-by-week basis.

    Grab a list of the rankings published by the Associated Press to easily
    query the hierarchy of teams each week. The results expose the current and
    previous rankings as well as the movement for each team in the list.

    Parameters
    ----------
    year : string (optional)
        A string of the requested year to pull rankings from. Defaults to the
        most recent season.
    """
    def __init__(self, year=None):
        self._rankings = {}

        self._find_rankings(year)

    def _pull_rankings_page(self, year):
        """
        Download the rankings page.

        Download the rankings page for the requested year and create a PyQuery
        object.

        Parameters
        ----------
        year : string
            A string of the requested year to pull rankings from.

        Returns
        -------
        PyQuery object
            Returns a PyQuery object of the rankings HTML page.
        """
        try:
            return pq(RANKINGS_URL % year)
        except HTTPError:
            return None

    def _get_team(self, team):
        """
        Retrieve team's name and abbreviation.

        The team's name and abbreviation are embedded within the 'school_name'
        tag and, in the case of the abbreviation, require special parsing as it
        is located in the middle of a URI. The name and abbreviation are
        returned for the requested school.

        Parameters
        ----------
        team : PyQuery object
            A PyQuery object representing a single row in a table on the
            rankings page.

        Returns
        -------
        tuple (string, string)
            Returns a tuple of two strings where the first string is the team's
            abbreviation, such as 'PURDUE' and the second string is the team's
            name, such as 'Purdue'.
        """
        name_tag = team('td[data-stat="school_name"]')
        abbreviation = re.sub(r'.*/cfb/schools/', '', str(name_tag('a')))
        abbreviation = re.sub(r'/.*', '', abbreviation)
        name = team('td[data-stat="school_name"] a').text()
        return abbreviation, name

    def _find_rankings(self, year):
        """
        Retrieve the rankings for each week.

        Find and retrieve all AP rankings for the requested year and combine
        them on a per-week basis. Each week contains information about the
        name, abbreviation, rank, movement, and previous rank for each team
        as well as the date and week number the results were published on.

        Parameters
        ----------
        year : string
            A string of the requested year to pull rankings from.
        """
        if not year:
            year = utils._find_year_for_season('ncaaf')
            # If stats for the requested season do not exist yet (as is the
            # case right before a new season begins), attempt to pull the
            # previous year's stats. If it exists, use the previous year
            # instead.
            if not utils._url_exists(RANKINGS_URL % year) and \
               utils._url_exists(RANKINGS_URL % str(int(year) - 1)):
                year = str(int(year) - 1)
        page = self._pull_rankings_page(year)
        if not page:
            output = ("Can't pull rankings page. Ensure the following URL "
                      "exists: %s" % RANKINGS_URL)
            raise ValueError(output)
        rankings = page('table#ap tbody tr').items()
        weekly_rankings = []
        week = 0
        for team in rankings:
            if 'class="thead"' in str(team):
                self._rankings[int(week)] = weekly_rankings
                weekly_rankings = []
                continue
            abbreviation, name = self._get_team(team)
            rank = utils._parse_field(RANKINGS_SCHEME, team, 'rank')
            week = utils._parse_field(RANKINGS_SCHEME, team, 'week')
            date = utils._parse_field(RANKINGS_SCHEME, team, 'date')
            previous = utils._parse_field(RANKINGS_SCHEME, team, 'previous')
            change = utils._parse_field(RANKINGS_SCHEME, team, 'change')
            if 'decrease' in str(team(RANKINGS_SCHEME['change'])):
                change = int(change) * -1
            elif 'increase' in str(team(RANKINGS_SCHEME['change'])):
                try:
                    change = int(change)
                except ValueError:
                    change = 0
            else:
                change = 0
            rank_details = {
                'abbreviation': abbreviation,
                'name': name,
                'rank': int(rank),
                'week': int(week),
                'date': date,
                'previous': previous,
                'change': change
            }
            weekly_rankings.append(rank_details)
        # Add the final rankings which is not terminated with another header
        # row and hence will not hit the first if statement in the loop above.
        self._rankings[int(week)] = weekly_rankings

    @property
    def current_extended(self):
        """
        Returns a ``list`` of ``dictionaries`` of the most recent AP rankings.
        The list is ordered in terms of the ranking so the #1 team will be in
        the first element and the #25 team will be the last element. Each
        dictionary has the following structure::

            {
                'abbreviation': Team's abbreviation, such as 'PURDUE' (str),
                'name': Team's full name, such as 'Purdue' (str),
                'rank': Team's rank for the current week (int),
                'week': Week number for the results, such as 19 (int),
                'date': Date the rankings were released, such as '2017-03-01'.
                        Can also be 'Final' for the final rankings or
                        'Preseason' for preseason rankings (str),
                'previous': The team's previous rank, if applicable (str),
                'change': The amount the team moved up or down the rankings.
                          Moves up the ladder have a positive number while
                          drops yield a negative number and teams that didn't
                          move have 0 (int)
            }
        """
        latest_week = max(self._rankings.keys())
        ordered_dict = sorted(self._rankings[latest_week],
                              key=lambda k: k['rank'])
        return ordered_dict

    @property
    def current(self):
        """
        Returns a ``dictionary`` of the most recent rankings from the
        Associated Press where each key is a ``string`` of the team's
        abbreviation and each value is an ``int`` of the team's rank for the
        current week.
        """
        rankings_dict = {}

        for team in self.current_extended:
            rankings_dict[team['abbreviation']] = team['rank']
        return rankings_dict

    @property
    def complete(self):
        """
        Returns a ``dictionary`` where each key is a week number as an ``int``
        and each value is a ``list`` of ``dictionaries`` containing the AP
        rankings for each week. Within each list is a dictionary of team
        information such as name, abbreviation, rank, and more. Note that the
        list might not necessarily be in the same order as the rankings.

        The overall dictionary has the following structure::

            {
                week number, ie 16 (int): [
                    {
                        'abbreviation': Team's abbreviation, such as 'PURDUE'
                                        (str),
                        'name': Team's full name, such as 'Purdue' (str),
                        'rank': Team's rank for the current week (int),
                        'week': Week number for the results, such as 16 (int),
                        'date': Date the rankings were released, such as
                                '2017-12-03'. Can also be 'Final' for the final
                                rankings or 'Preseason' for preseason rankings
                                (str),
                        'previous': The team's previous rank, if applicable
                                    (str),
                        'change': The amount the team moved up or down the
                                  rankings. Moves up the ladder have a positive
                                  number while drops yield a negative number
                                  and teams that didn't move have 0 (int)
                    },
                    ...
                ],
                ...
            }
        """
        return self._rankings
