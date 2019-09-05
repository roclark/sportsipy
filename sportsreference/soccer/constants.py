PARSING_SCHEME = {
    'id': 'a',
    'name': 'a',
    'games': 'td[data-stat="games"]:first',
    'wins': 'td[data-stat="wins"]:first',
    'wins_so': 'td[data-stat="wins_shootout"]:first',
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

PLAYER_SCHEME = {
    'name': 'h1',
    'nationality': 'td[data-stat="nationality"]',
    'position': 'td[data-stat="pos"]',
    'age': 'td[data-stat="age"]',
    'appearances': 'td[data-stat="games"]',
    'starts': 'td[data-stat="games_starts"]',
    'substitutions': 'td[data-stat="games_subs"]',
    'minutes_played': 'td[data-stat="minutes"]',
    'minutes_played_per_appearance': 'td[data-stat="minutes_per_game"]',
    'goals': 'td[data-stat="goals"]',
    'assists': 'td[data-stat="assists"]',
    'penalty_kicks_made': 'td[data-stat="pens_made"]',
    'penalty_kicks_attempted': 'td[data-stat="pens_att"]',
    'fouls_commited': 'td[data-stat="fouls"]',
    'yellow_cards': 'td[data-stat="cards_yellow"]',
    'red_cards': 'td[data-stat="cards_red"]',
    'shots_on_target': 'td[data-stat="shots_on_target"]',
    'goals_per90': 'td[data-stat="goals_per90"]',
    'goals_assists_per90': 'td[data-stat="goals_assists_per90"]',
    'goals_penalty_per90': 'td[data-stat="goals_pens_per90"]',
    'goals_assists_penalty_per90':
    'td[data-stat="goals_assists_penalty_per90"]',
    'shots_on_target_per90': 'td[data-stat="shots_on_target_per90"]',
    'fouls_commited_per90': 'td[data-stat="fouls_per_90"]',
    'cards_per90': 'td[data-stat="cards_per_90"]',
    'goals_against': 'td[data-stat="goals_against"]',
    'goals_against_per90': 'td[data-stat="goals_against_per90"]',
    'shots_on_target_against': 'td[data-stat="shots_on_target_against"]',
    'save_percentage': 'td[data-stat="save_perc"]',
    'wins': 'td[data-stat="wins"]',
    'draws': 'td[data-stat="draws"]',
    'losses': 'td[data-stat="losses"]',
    'clean_sheets': 'td[data-stat="clean_sheets"]',
    'clean_sheets_percentage': 'td[data-stat="clean_sheets_perc"]'
}

FBREF_MLS_COMP_ID = 22

MLS_FIRST_YEAR = 1996
ID_MAP = {
    '1996': '30',
    '1997': '32',
    '1998': '34',
    '1999': '37',
    '2000': '44',
    '2001': '56',
    '2002': '75',
    '2003': '100',
    '2004': '133',
    '2005': '168',
    '2006': '211',
    '2007': '260',
    '2008': '316',
    '2009': '374',
    '2010': '442',
    '2011': '509',
    '2012': '577',
    '2013': '643',
    '2014': '708',
    '2015': '1369',
    '2016': '1503',
    '2017': '1558',
    '2018': '1759',
    '2019': '2798'  # TODO
}

FBREF_URL = 'https://fbref.com'
MLS_CURRENT_SEASON_URL = FBREF_URL + '/en/comps/22/Major-League-Soccer-Stats'
MLS_SEASON_URL = (FBREF_URL + '/en/comps/22/'
                  '%s/%s-Major-League-Soccer-Stats')
CURRENT_ROSTER_URL = (FBREF_URL + '/en/squads/%s')
ROSTER_URL = (FBREF_URL + '/en/squads/%s/%s')
PLAYER_URL = (FBREF_URL + '/en/players/%s')
