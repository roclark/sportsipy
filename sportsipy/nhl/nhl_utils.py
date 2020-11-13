from pyquery import PyQuery as pq
from sportsipy import utils
from .constants import SEASON_PAGE_URL


def _retrieve_all_teams(year, season_page=None):
    """
    Find and create Team instances for all teams in the given season.

    For a given season, parses the specified NHL stats table and finds all
    requested stats. Each team then has a Team instance created which includes
    all requested stats and a few identifiers, such as the team's name and
    abbreviation. All of the individual Team instances are added to a list.

    Note that this method is called directly once Teams is invoked and does not
    need to be called manually.

    Parameters
    ----------
    year : string
        The requested year to pull stats from.
    teams_file : string (optional)
        Link with filename to the local season page.

    Returns
    -------
    tuple
        Returns a ``tuple`` in the format of (teams_list, year) where the
        teams_list is the PyQuery data for every team in the given season, and
        the year is the request year for the season.
    """
    if not year:
        year = utils._find_year_for_season('nhl')
        # If stats for the requested season do not exist yet (as is the case
        # right before a new season begins), attempt to pull the previous
        # year's stats. If it exists, use the previous year instead.
        if not utils._url_exists(SEASON_PAGE_URL % year) and \
           utils._url_exists(SEASON_PAGE_URL % str(int(year) - 1)):
            year = str(int(year) - 1)
    doc = utils._pull_page(SEASON_PAGE_URL % year, season_page)
    teams_list = utils._get_stats_table(doc, 'div#all_stats')
    if not teams_list:
        utils._no_data_found()
        return None, None
    return teams_list, year
