import re
from datetime import datetime
from pyquery import PyQuery as pq


SEASON_START_MONTH = {
    'mlb': {'start': 4, 'wrap': False},
    'nba': {'start': 10, 'wrap': True},
    'ncaab': {'start': 11, 'wrap': True},
    'ncaaf': {'start': 8, 'wrap': False},
    'nfl': {'start': 9, 'wrap': False},
    'nhl': {'start': 10, 'wrap': True}
}


def _todays_date():
    return datetime.now()


def find_year_for_season(league):
    today = _todays_date()
    if league not in SEASON_START_MONTH:
        raise ValueError('"%s" league cannot be found!')
    start = SEASON_START_MONTH[league]['start']
    wrap = SEASON_START_MONTH[league]['wrap']
    if wrap and start - 1 <= today.month <= 12:
        return today.year + 1
    elif not wrap and start == 1 and today.month == 12:
        return today.year + 1
    elif not wrap and not start -1 <= today.month <= 12:
        return today.year - 1
    else:
        return today.year


def _parse_abbreviation(uri_link):
    abbr = re.sub(r'/[0-9]+\..*htm.*', '', uri_link('a').attr('href'))
    abbr = re.sub(r'/.*/schools/', '', abbr)
    abbr = re.sub(r'/teams/', '', abbr)
    return abbr.upper()


def parse_field(parsing_scheme, html_data, field):
    if field == 'abbreviation':
        return _parse_abbreviation(html_data)
    scheme = parsing_scheme[field]
    items = [i.text() for i in html_data(scheme).items()]
    # Return the first item. All others are duplicates.
    return items[0]


# Some pages embed the HTML contents in comments. Since the HTML contents are
# valid, removing the content tags (but not the actual code within the
# comments) will return the desired contents.
def _remove_html_comment_tags(html):
    return str(html).replace('<!--', '').replace('-->', '')


def get_stats_table(html_page, div):
    stats_html = html_page(div)
    stats_table = pq(_remove_html_comment_tags(stats_html))
    teams_list = stats_table('tbody tr').items()
    return teams_list
