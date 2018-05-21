PARSING_SCHEME = {
    'name': 'a',
    'conference': 'td[data-stat="conf_abbr"] a',
    'games': 'td[data-stat="g"]:first',
    'wins': 'td[data-stat="wins"]:first',
    'losses': 'td[data-stat="losses"]:first',
    'win_percentage': 'td[data-stat="win_loss_pct"]:first',
    'conference_wins': 'td[data-stat="wins_conf"]:first',
    'conference_losses': 'td[data-stat="losses_conf"]:first',
    'conference_win_percentage': 'td[data-stat="win_loss_pct_conf"]:first',
    'points_per_game': 'td[data-stat="points_per_g"]:first',
    'points_against_per_game': 'td[data-stat="opp_points_per_g"]:first',
    'simple_rating_system': 'td[data-stat="srs"]:first',
    'strength_of_schedule': 'td[data-stat="sos"]:first',
    'current_rank': 'td[data-stat="rank_current"]:first',
    'preseason_rank': 'td[data-stat="rank_pre"]:first',
    'highest_rank': 'td[data-stat="rank_min"]:first',
    'pass_completions': 'td[data-stat="pass_cmp"]:first',
    'pass_attempts': 'td[data-stat="pass_att"]:first',
    'pass_completion_percentage': 'td[data-stat="pass_cmp_pct"]:first',
    'pass_yards': 'td[data-stat="pass_yds"]:first',
    'interceptions': 'td[data-stat="pass_int"]:first',
    'pass_touchdowns': 'td[data-stat="pass_td"]:first',
    'rush_attempts': 'td[data-stat="rush_att"]:first',
    'rush_yards': 'td[data-stat="rush_yds"]:first',
    'rush_yards_per_attempt': 'td[data-stat="rush_yds_per_att"]:first',
    'rush_touchdowns': 'td[data-stat="rush_td"]:first',
    'plays': 'td[data-stat="tot_plays"]:first',
    'yards': 'td[data-stat="tot_yds"]:first',
    'turnovers': 'td[data-stat="turnovers"]:first',
    'fumbles_lost': 'td[data-stat="fumbles_lost"]:first',
    'yards_per_play': 'td[data-stat="tot_yds_per_play"]:first',
    'pass_first_downs': 'td[data-stat="first_down_pass"]:first',
    'rush_first_downs': 'td[data-stat="first_down_rush"]:first',
    'first_downs_from_penalties': 'td[data-stat="first_down_penalty"]:first',
    'first_downs': 'td[data-stat="first_down"]:first',
    'penalties': 'td[data-stat="penalty"]:first',
    'yards_from_penalties': 'td[data-stat="penalty_yds"]:first'
}

SEASON_PAGE_URL = 'http://www.sports-reference.com/cfb/years/%s-standings.html'

OFFENSIVE_STATS_URL = ('https://www.sports-reference.com/cfb/years/'
                       '%s-team-offense.html')
