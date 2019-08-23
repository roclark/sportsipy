PARSING_SCHEME = {
    'name': 'a',
    'games': 'td[data-stat="games"]:first',
    'wins': 'td[data-stat="wins"]:first',
    'draws': 'td[data-stat="draws"]:first',
    'losses': 'td[data-stat="losses"]:first',
    'goals_for': 'td[data-stat="goals_for"]:first',
    'goals_against': 'td[data-stat="goals_against"]:first',
    'goal_diff': 'td[data-stat="goal_diff"]:first',
    'points': 'td[data-stat="points"]:first',
    'attendance_per_game': 'td[data-stat="attendance_per_g"]:first',
    'top_team_scorers': 'td[data-stat="top_team_scorers"]:first',
    'top_keeper': 'td[data-stat="top_keeper"]:first',
    'notes': 'td[data-stat="notes"]:first',
}

FBREF_MLS_COMP_ID = 22

MLS_FIRST_YEAR = 1996
ID_MAP = {
    '1996': 30,
    '1997': 32,
    '1998': 34,
    '1999': 37,
    '2000': 44,
    '2001': 56,
    '2002': 75,
    '2003': 100,
    '2004': 133,
    '2005': 168,
    '2006': 211,
    '2007': 260,
    '2008': 316,
    '2009': 374,
    '2010': 442,
    '2011': 509,
    '2012': 577,
    '2013': 643,
    '2014': 708,
    '2015': 1369,
    '2016': 1503,
    '2017': 1558,
    '2018': 1759,
    '2019': 2798  # TODO
}


MLS_CURRENT_SEASON_URL = 'https://fbref.com/en/comps/22/Major-League-Soccer-Stats'
MLS_SEASON_URL = ('https://fbref.com/en/comps/22/'
                          '%s/%s-Major-League-Soccer-Stats')

