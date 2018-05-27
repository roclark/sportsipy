PARSING_SCHEME = {
    'name': 'a',
    'average_age': 'td[data-stat="average_age"]:first',
    'games_played': 'td[data-stat="games"]:first',
    'wins': 'td[data-stat="wins"]:first',
    'losses': 'td[data-stat="losses"]:first',
    'overtime_losses': 'td[data-stat="losses_ot"]:first',
    'points': 'td[data-stat="points"]:first',
    'points_percentage': 'td[data-stat="points_pct"]:first',
    'goals_for': 'td[data-stat="goals"]:first',
    'goals_against': 'td[data-stat="opp_goals"]:first',
    'simple_rating_system': 'td[data-stat="srs"]:first',
    'strength_of_schedule': 'td[data-stat="sos"]:first',
    'total_goals_per_game': 'td[data-stat="total_goals_per_game"]:first',
    'power_play_goals': 'td[data-stat="goals_pp"]:first',
    'power_play_opportunities': 'td[data-stat="chances_pp"]:first',
    'power_play_percentage': 'td[data-stat="power_play_pct"]:first',
    'power_play_goals_against': 'td[data-stat="opp_goals_pp"]:first',
    'power_play_opportunities_against': 'td[data-stat="opp_chances_pp"]:first',
    'penalty_killing_percentage': 'td[data-stat="pen_kill_pct"]:first',
    'short_handed_goals': 'td[data-stat="goals_sh"]:first',
    'short_handed_goals_against': 'td[data-stat="opp_goals_sh"]:first',
    'shots_on_goal': 'td[data-stat="shots"]:first',
    'shooting_percentage': 'td[data-stat="shot_pct"]:first',
    'shots_against': 'td[data-stat="shots_against"]:first',
    'save_percentage': 'td[data-stat="save_pct"]:first',
    'pdo_at_even_strength': 'td[data-stat="pdo"]:first'
}

SCHEDULE_SCHEME = {
    'game': 'th[data-stat="games"]:first',
    'date': 'td[data-stat="date_game"]:first',
    'time': 'td[data-stat="time_game"]:first',
    'location': 'td[data-stat="game_location"]:first',
    'opponent_abbr': 'td[data-stat="opp_name"]:first',
    'opponent_name': 'td[data-stat="opp_name"]:first',
    'goals_scored': 'td[data-stat="goals"]:first',
    'goals_allowed': 'td[data-stat="opp_goals"]:first',
    'result': 'td[data-stat="game_outcome"]:first',
    'overtime': 'td[data-stat="overtimes"]:first',
    'wins': 'td[data-stat="wins"]:first',
    'losses': 'td[data-stat="losses"]:first',
    'overtime_losses': 'td[data-stat="losses_ot"]:first',
    'streak': 'td[data-stat="game_streak"]:first',
    'shots_on_goal': 'td[data-stat="shots"]:first',
    'penalties_in_minutes': 'td[data-stat="pen_min"]:first',
    'power_play_goals': 'td[data-stat="goals_pp"]:first',
    'power_play_opportunities': 'td[data-stat="chances_pp"]:first',
    'short_handed_goals': 'td[data-stat="goals_sh"]:first',
    'attendance': 'td[data-stat="attendance"]:first',
    'length_of_game': 'td[data-stat="game_duration"]:first'
}

SEASON_PAGE_URL = 'http://www.hockey-reference.com/leagues/NHL_%s.html'

SCHEDULE_URL = 'https://www.hockey-reference.com/teams/%s/%s_games.html'

SHOOTOUT = -1
OVERTIME_LOSS = 'OTL'
