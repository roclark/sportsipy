import re
import urllib2
from constants import PARSING_SCHEME, STANDINGS_URL, TEAM_STATS_URL
from pyquery import PyQuery as pq
from .. import utils


class Team:
    def __init__(self, team_data, rank):
        self._rank = rank
        self._abbreviation = None
        self._name = None
        self._league = None
        self._games = None
        self._wins = None
        self._losses = None
        self._win_percentage = None
        self._streak = None
        self._runs = None
        self._runs_against = None
        self._run_difference = None
        self._strength_of_schedule = None
        self._simple_rating_system = None
        self._pythagorean_win_loss = None
        self._luck = None
        self._interleague_record = None
        self._home_record = None
        self._away_record = None
        self._extra_inning_record = None
        self._single_run_record = None
        self._record_vs_right_handed_pitchers = None
        self._record_vs_left_handed_pitchers = None
        self._record_vs_teams_over_500 = None
        self._record_vs_teams_under_500 = None
        self._last_ten_games_record = None
        self._last_twenty_games_record = None
        self._last_thirty_games_record = None
        self._number_players_used = None
        self._average_batter_age = None
        self._plate_appearances = None
        self._at_bats = None
        self._total_runs = None
        self._hits = None
        self._doubles = None
        self._triples = None
        self._home_runs = None
        self._runs_batted_in = None
        self._stolen_bases = None
        self._times_caught_stealing = None
        self._times_struck_out = None
        self._batting_average = None
        self._on_base_percentage = None
        self._slugging_percentage = None
        self._on_base_plus_slugging_percentage = None
        self._on_base_plus_slugging_percentage_plus = None
        self._total_bases = None
        self._grounded_into_double_plays = None
        self._times_hit_by_pitch = None
        self._sacrifice_hits = None
        self._sacrifice_flies = None
        self._intentional_bases_on_balls = None
        self._runners_left_on_base = None
        self._number_of_pitchers = None
        self._average_pitcher_age = None
        self._runs_allowed_per_game = None
        self._earned_runs_against = None
        self._games_finished = None
        self._complete_games = None
        self._shutouts = None
        self._complete_game_shutouts = None
        self._saves = None
        self._innings_pitched = None
        self._hits_allowed = None
        self._home_runs_against = None
        self._bases_on_walks_given = None
        self._strikeouts = None
        self._hit_pitcher = None
        self._balks = None
        self._wild_pitches = None
        self._batters_faced = None
        self._earned_runs_against_plus = None
        self._fielding_independent_pitching = None
        self._whip = None
        self._hits_per_nine_innings = None
        self._home_runs_per_nine_innings = None
        self._bases_on_walks_given_per_nine_innings = None
        self._strikeouts_per_nine_innings = None
        self._strikeouts_per_base_on_balls = None
        self._opposing_runners_left_on_base = None

        self._parse_team_data(team_data)

    def _parse_name(self, team_data):
        name = team_data('td[data-stat="team_ID"]:first')
        name = re.sub(r'.*title="', '', str(name))
        name = re.sub(r'".*', '', name)
        setattr(self, '_name', name)

    def _parse_team_data(self, team_data):
        for field in self.__dict__:
            # The rank attribute is passed directly to the class during
            # instantiation.
            if field == '_rank':
                continue
            elif field == '_name':
                self._parse_name(team_data)
                continue
            value = utils.parse_field(PARSING_SCHEME,
                                      team_data,
                                      str(field)[1:])
            setattr(self, field, value)

    @property
    def rank(self):
        return int(self._rank)

    @property
    def abbreviation(self):
        return self._abbreviation

    @property
    def name(self):
        return self._name

    @property
    def league(self):
        return self._league

    @property
    def games(self):
        return int(self._games)

    @property
    def wins(self):
        return int(self._wins)

    @property
    def losses(self):
        return int(self._losses)

    @property
    def win_percentage(self):
        return float(self._win_percentage)

    @property
    def streak(self):
        return self._streak

    @property
    def runs(self):
        return float(self._runs)

    @property
    def runs_against(self):
        return float(self._runs_against)

    @property
    def run_difference(self):
        return float(self._run_difference)

    @property
    def strength_of_schedule(self):
        return float(self._strength_of_schedule)

    @property
    def simple_rating_system(self):
        return float(self._simple_rating_system)

    @property
    def pythagorean_win_loss(self):
        return self._pythagorean_win_loss

    @property
    def luck(self):
        return int(self._luck)

    @property
    def interleague_record(self):
        return self._interleague_record

    @property
    def home_record(self):
        return self._home_record

    @property
    def home_wins(self):
        return int(self._home_record.split('-')[0])

    @property
    def home_losses(self):
        return int(self._home_losses.split('-')[1])

    @property
    def away_record(self):
        return self._away_record

    @property
    def away_wins(self):
        return int(self._away_wins.split('-')[0])

    @property
    def away_losses(self):
        return int(self._away_losses.split('-')[1])

    @property
    def extra_inning_record(self):
        return self._extra_inning_record

    @property
    def extra_inning_wins(self):
        return int(self._extra_inning_wins.split('-')[0])

    @property
    def extra_inning_losses(self):
        return int(self._extra_inning_losses.split('-')[1])

    @property
    def single_run_record(self):
        return self._single_run_record

    @property
    def single_run_wins(self):
        return int(self._single_run_wins.split('-')[0])

    @property
    def single_run_losses(self):
        return int(self._single_run_losses.split('-')[1])

    @property
    def record_vs_right_handed_pitchers(self):
        return self._record_vs_right_handed_pitchers

    @property
    def wins_vs_right_handed_pitchers(self):
        return int(self._wins_vs_right_handed_pitchers.split('-')[0])

    @property
    def losses_vs_right_handed_pitchers(self):
        return int(self._losses_vs_right_handed_pitchers.split('-')[1])

    @property
    def record_vs_left_handed_pitchers(self):
        return self._record_vs_left_handed_pitchers

    @property
    def wins_vs_left_handed_pitchers(self):
        return int(self._wins_vs_left_handed_pitchers.split('-')[0])

    @property
    def losses_vs_left_handed_pitchers(self):
        return int(self._losses_vs_left_handed_pitchers.split('-')[1])

    @property
    def record_vs_teams_over_500(self):
        return self._record_vs_teams_over_500

    @property
    def wins_vs_teams_over_500(self):
        return int(self._wins_vs_teams_over_500.split('-')[0])

    @property
    def losses_vs_teams_over_500(self):
        return int(self._losses_vs_teams_over_500.split('-')[1])

    @property
    def record_vs_teams_under_500(self):
        return self._record_vs_teams_under_500

    @property
    def wins_vs_teams_under_500(self):
        return int(self._wins_vs_teams_under_500.split('-')[0])

    @property
    def losses_vs_teams_under_500(self):
        return int(self._losses_vs_teams_under_500.split('-')[1])

    @property
    def last_ten_games_record(self):
        return self._last_ten_games_record

    @property
    def wins_last_ten_games(self):
        return int(self._wins_last_ten_games.split('-')[0])

    @property
    def losses_last_ten_games(self):
        return int(self._losses_last_ten_games.split('-')[1])

    @property
    def last_twenty_games_record(self):
        return self._last_twenty_games_record

    @property
    def wins_last_twenty_games(self):
        return int(self._wins_last_twenty_games.split('-')[0])

    @property
    def losses_last_twenty_games(self):
        return int(self._losses_last_twenty_games.split('-')[1])

    @property
    def last_thirty_games_record(self):
        return self._last_thirty_games_record

    @property
    def wins_last_thirty_games(self):
        return int(self._wins_last_thirty_games.split('-')[0])

    @property
    def losses_last_thirty_games(self):
        return int(self._losses_last_thirty_games.split('-')[1])

    @property
    def number_players_used(self):
        return int(self._number_players_used)

    @property
    def average_batter_age(self):
        return float(self._average_batter_age)

    @property
    def plate_appearances(self):
        return int(self._plate_appearances)

    @property
    def at_bats(self):
        return int(self._at_bats)

    @property
    def total_runs(self):
        return int(self._total_runs)

    @property
    def hits(self):
        return int(self._hits)

    @property
    def doubles(self):
        return int(self._doubles)

    @property
    def triples(self):
        return int(self._triples)

    @property
    def home_runs(self):
        return int(self._home_runs)

    @property
    def runs_batted_in(self):
        return int(self._runs_batted_in)

    @property
    def stolen_bases(self):
        return int(self._stolen_bases)

    @property
    def times_caught_stealing(self):
        return int(self._times_caught_stealing)

    @property
    def times_struck_out(self):
        return int(self._times_struck_out)

    @property
    def batting_average(self):
        return float(self._batting_average)

    @property
    def on_base_percentage(self):
        return float(self._on_base_percentage)

    @property
    def slugging_percentage(self):
        return float(self._slugging_percentage)

    @property
    def on_base_plus_slugging_percentage(self):
        return float(self._on_base_plus_slugging_percentage)

    @property
    def on_base_plus_slugging_percentage_plus(self):
        return int(self._on_base_plus_slugging_percentage_plus)

    @property
    def total_bases(self):
        return int(self._total_bases)

    @property
    def grounded_into_double_plays(self):
        return int(self._grounded_into_double_plays)

    @property
    def times_hit_by_pitch(self):
        return int(self._times_hit_by_pitch)

    @property
    def sacrifice_hits(self):
        return int(self._sacrifice_hits)

    @property
    def sacrifice_flies(self):
        return int(self._sacrifice_flies)

    @property
    def intentional_bases_on_balls(self):
        return int(self._intentional_bases_on_balls)

    @property
    def runners_left_on_base(self):
        return int(self._runners_left_on_base)

    @property
    def number_of_pitchers(self):
        return int(self._number_of_pitchers)

    @property
    def average_pitcher_age(self):
        return float(self._average_pitcher_age)

    @property
    def runs_allowed_per_game(self):
        return float(self._runs_allowed_per_game)

    @property
    def earned_runs_against(self):
        return float(self._earned_runs_against)

    @property
    def games_finished(self):
        return int(self._games_finished)

    @property
    def complete_games(self):
        return int(self._complete_games)

    @property
    def shutouts(self):
        return int(self._shutouts)

    @property
    def complete_game_shutouts(self):
        return int(self._complete_game_shutouts)

    @property
    def saves(self):
        return int(self._saves)

    @property
    def innings_pitched(self):
        return float(self._innings_pitched)

    @property
    def hits_allowed(self):
        return int(self._hits_allowed)

    @property
    def home_runs_against(self):
        return int(self._home_runs_against)

    @property
    def bases_on_walks_given(self):
        return int(self._bases_on_walks_given)

    @property
    def strikeouts(self):
        return int(self._strikeouts)

    @property
    def hit_pitcher(self):
        return int(self._hit_pitcher)

    @property
    def balks(self):
        return int(self._balks)

    @property
    def wild_pitches(self):
        return int(self._wild_pitches)

    @property
    def batters_faced(self):
        return int(self._batters_faced)

    @property
    def earned_runs_against_plus(self):
        return int(self._earned_runs_against_plus)

    @property
    def fielding_independent_pitching(self):
        return float(self._fielding_independent_pitching)

    @property
    def whip(self):
        return float(self._whip)

    @property
    def hits_per_nine_innings(self):
        return float(self._hits_per_nine_innings)

    @property
    def home_runs_per_nine_innings(self):
        return float(self._home_runs_per_nine_innings)

    @property
    def bases_on_walks_given_per_nine_innings(self):
        return float(self._bases_on_walks_given_per_nine_innings)

    @property
    def strikeouts_per_nine_innings(self):
        return float(self._strikeouts_per_nine_innings)

    @property
    def strikeouts_per_base_on_balls(self):
        return float(self._strikeouts_per_base_on_balls)

    @property
    def opposing_runners_left_on_base(self):
        return int(self._opposing_runners_left_on_base)


class Teams:
    def __init__(self, year=None, short=False):
        self._teams = []

        self._retrieve_all_teams(year)

    def __getitem__(self, abbreviation):
        for team in self._teams:
            if team.abbreviation.upper() == abbreviation.upper():
                return team
        raise ValueError('Team abbreviation %s not found' % abbreviation)

    def __call__(self, abbreviation):
        return self.__getitem__(abbreviation)

    def __repr__(self):
        return self._teams

    def __iter__(self):
        return iter(self.__repr__())

    def _retrieve_all_teams(self, year):
        team_stats_dict = {}

        if not year:
            year = utils.find_year_for_season('mlb')
        doc = pq(STANDINGS_URL % year)
        standings = utils.get_stats_table(doc, 'div#all_expanded_standings_overall')
        doc = pq(TEAM_STATS_URL % year)
        batting_stats = utils.get_stats_table(doc, 'div#all_teams_standard_batting')
        pitching_stats = utils.get_stats_table(doc, 'div#all_teams_standard_pitching')
        # Teams are listed in terms of rank with the first team being #1
        rank = 1
        for team_data in standings:
            # Skip the leauge average row
            if 'class="league_average_table"' in str(team_data):
                continue
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            team_stats_dict[abbr] = {'data': team_data,
                                     'rank': rank}
            rank += 1

        for team_data in batting_stats:
            # Skip the league average row
            if 'class="league_average_table"' in str(team_data):
                continue
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            team_stats_dict[abbr]['data'] += team_data

        for team_data in pitching_stats:
            # Skip the league average row
            if 'class="league_average_table"' in str(team_data):
                continue
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
            data = team_stats_dict[abbr]['data'] + team_data
            team = Team(data, team_stats_dict[abbr]['rank'])
            self._teams.append(team)
