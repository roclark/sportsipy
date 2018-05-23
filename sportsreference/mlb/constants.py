PARSING_SCHEME = {
    'name': 'a',
    'league': 'td[data-stat="lg_ID"]:first',
    'games': 'td[data-stat="G"]:first',
    'wins': 'td[data-stat="W"]:first',
    'losses': 'td[data-stat="L"]:first',
    'win_percentage': 'td[data-stat="win_loss_perc"]:first',
    'streak': 'td[data-stat="winning_streak"]:first',
    'runs': 'td[data-stat="R"]:first',
    'runs_against': 'td[data-stat="RA"]:first',
    'run_difference': 'td[data-stat="run_diff"]:first',
    'strength_of_schedule': 'td[data-stat="strength_of_schedule"]:first',
    'simple_rating_system': 'td[data-stat="simple_rating_system"]:first',
    'pythagorean_win_loss': 'td[data-stat="record_pythag"]:first',
    'luck': 'td[data-stat="luck_pythag"]:first',
    'interleague_record': 'td[data-stat="record_interleague"]:first',
    'home_record': 'td[data-stat="record_home"]:first',
    'away_record': 'td[data-stat="record_road"]:first',
    'extra_inning_record': 'td[data-stat="record_xinn"]:first',
    'single_run_record': 'td[data-stat="record_one_run"]:first',
    'record_vs_right_handed_pitchers': 'td[data-stat="record_vs_rhp"]:first',
    'record_vs_left_handed_pitchers': 'td[data-stat="record_vs_lhp"]:first',
    'record_vs_teams_over_500': 'td[data-stat="record_vs_over_500"]:first',
    'record_vs_teams_under_500': 'td[data-stat="record_vs_under_500"]:first',
    'last_ten_games_record': 'td[data-stat="record_last_10"]:first',
    'last_twenty_games_record': 'td[data-stat="record_last_20"]:first',
    'last_thirty_games_record': 'td[data-stat="record_last_30"]:first',
    'number_players_used': 'td[data-stat="batters_used"]:first',
    'average_batter_age': 'td[data-stat="age_bat"]:first',
    'plate_appearances': 'td[data-stat="PA"]:first',
    'at_bats': 'td[data-stat="AB"]:first',
    'total_runs': 'td[data-stat="R"]:first',
    'hits': 'td[data-stat="H"]:first',
    'doubles': 'td[data-stat="2B"]:first',
    'triples': 'td[data-stat="3B"]:first',
    'home_runs': 'td[data-stat="HR"]:first',
    'runs_batted_in': 'td[data-stat="RBI"]:first',
    'stolen_bases': 'td[data-stat="SB"]:first',
    'times_caught_stealing': 'td[data-stat="CS"]:first',
    'bases_on_balls': 'td[data-stat="BB"]:first',
    'times_struck_out': 'td[data-stat="SO"]:first',
    'batting_average': 'td[data-stat="batting_avg"]:first',
    'on_base_percentage': 'td[data-stat="onbase_perc"]:first',
    'slugging_percentage': 'td[data-stat="slugging_perc"]:first',
    'on_base_plus_slugging_percentage':
    'td[data-stat="onbase_plus_slugging"]:first',
    'on_base_plus_slugging_percentage_plus':
    'td[data-stat="onbase_plus_slugging_plus"]:first',
    'total_bases': 'td[data-stat="TB"]:first',
    'grounded_into_double_plays': 'td[data-stat="GIDP"]:first',
    'times_hit_by_pitch': 'td[data-stat="HBP"]:first',
    'sacrifice_hits': 'td[data-stat="SH"]:first',
    'sacrifice_flies': 'td[data-stat="SF"]:first',
    'intentional_bases_on_balls': 'td[data-stat="IBB"]:first',
    'runners_left_on_base': 'td[data-stat="LOB"]:first',
    'number_of_pitchers': 'td[data-stat="pitchers_used"]:first',
    'average_pitcher_age': 'td[data-stat="age_pitch"]:first',
    'runs_allowed_per_game': 'td[data-stat="runs_allowed_per_game"]:first',
    'earned_runs_against': 'td[data-stat="earned_run_avg"]:first',
    'games_finished': 'td[data-stat="GF"]:first',
    'complete_games': 'td[data-stat="CG"]:first',
    'shutouts': 'td[data-stat="SHO_team"]:first',
    'complete_game_shutouts': 'td[data-stat="SHO_cg"]:first',
    'saves': 'td[data-stat="SV"]:first',
    'innings_pitched': 'td[data-stat="IP"]:first',
    'hits_allowed': 'td[data-stat="H"]:first',
    'home_runs_against': 'td[data-stat="HR"]:first',
    'bases_on_walks_given': 'td[data-stat="BB"]:first',
    'strikeouts': 'td[data-stat="SO"]:first',
    'hit_pitcher': 'td[data-stat="HBP"]:first',
    'balks': 'td[data-stat="BK"]:first',
    'wild_pitches': 'td[data-stat="WP"]:first',
    'batters_faced': 'td[data-stat="batters_faced"]:first',
    'earned_runs_against_plus': 'td[data-stat="earned_run_avg_plus"]:first',
    'fielding_independent_pitching': 'td[data-stat="fip"]:first',
    'whip': 'td[data-stat="whip"]:first',
    'hits_per_nine_innings': 'td[data-stat="hits_per_nine"]:first',
    'home_runs_per_nine_innings': 'td[data-stat="home_runs_per_nine"]:first',
    'bases_on_walks_given_per_nine_innings':
    'td[data-stat="bases_on_balls_per_nine"]:first',
    'strikeouts_per_nine_innings': 'td[data-stat="strikeouts_per_nine"]:first',
    'strikeouts_per_base_on_balls':
    'td[data-stat="strikeouts_per_base_on_balls"]:first',
    'opposing_runners_left_on_base': 'td[data-stat="LOB"]:first'
}

SCHEDULE_SCHEME = {
    'game': 'th[data-stat="team_game"]:first',
    'date': 'td[data-stat="date_game"]:first',
    'location': 'td[data-stat="homeORvis"]:first',
    'opponent_abbr': 'td[data-stat="opp_ID"]:first',
    'result': 'td[data-stat="win_loss_result"]:first',
    'runs_scored': 'td[data-stat="R"]:first',
    'runs_allowed': 'td[data-stat="RA"]:first',
    'innings': 'td[data-stat="extra_innings"]:first',
    'record': 'td[data-stat="win_loss_record"]:first',
    'rank': 'td[data-stat="rank"]:first',
    'games_behind': 'td[data-stat="games_back"]:first',
    'winner': 'td[data-stat="winning_pitcher"]:first',
    'loser': 'td[data-stat="losing_pitcher"]:first',
    'save': 'td[data-stat="saving_pitcher"]:first',
    'game_duration': 'td[data-stat="time_of_game"]:first',
    'day_or_night': 'td[data-stat="day_or_night"]:first',
    'attendance': 'td[data-stat="attendance"]:first',
    'streak': 'td[data-stat="win_loss_streak"]:first'
}

ELEMENT_INDEX = {
    'total_runs': 1,
    'bases_on_walks_given': 1,
    'hits_allowed': 1,
    'strikeouts': 1,
    'home_runs_against': 1,
    'opposing_runners_left_on_base': 1
}

STANDINGS_URL = ('https://www.baseball-reference.com/leagues/MLB/'
                 '%s-standings.shtml')
TEAM_STATS_URL = 'https://www.baseball-reference.com/leagues/MLB/%s.shtml'

SCHEDULE_URL = ('https://www.baseball-reference.com/teams/%s/'
                '%s-schedule-scores.shtml')

NIGHT = 'Night'
DAY = 'Day'
