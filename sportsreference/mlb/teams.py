import pandas as pd
import re
from .constants import (ELEMENT_INDEX,
                        PARSING_SCHEME,
                        STANDINGS_URL,
                        TEAM_ELEMENT,
                        TEAM_STATS_URL)
from functools import wraps
from pyquery import PyQuery as pq
from .. import utils
from ..decorators import float_property_decorator, int_property_decorator
from .roster import Roster
from .schedule import Schedule


def mlb_int_property_decorator(func):
    @property
    @wraps(func)
    def wrapper(*args):
        value = func(*args)
        # Equivalent to the calling property's method name
        field = func.__name__
        try:
            record = value.split('-')
        except AttributeError:
            return None
        try:
            return int(record[TEAM_ELEMENT[field]])
        except (TypeError, ValueError, IndexError):
            return None
    return wrapper


class Team(object):
    """
    An object containing all of a team's season information.

    Finds and parses all team stat information and identifiers, such as rank,
    name, and abbreviation, and sets them as properties which can be directly
    read from for easy reference.

    Parameters
    ----------
    team_data : string
        A string containing all of the rows of stats for a given team. If
        multiple tables are being referenced, this will be comprised of
        multiple rows in a single string.
    rank : int
        A team's position in the league based on the number of points they
        obtained during the season.
    year : string (optional)
        The requested year to pull stats from.
    """
    def __init__(self, team_data, rank, year=None):
        self._year = year
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
        self._bases_on_balls = None
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
        """
        Parses the team's name.

        On the pages being parsed, the team's name doesn't follow the standard
        parsing algorithm that we use for the fields, and requires a special
        one-off algorithm. The name is attached in the 'title' attribute from
        within 'team_ID'. A few simple regex subs captures the team name. The
        '_name' attribute is applied with the captured team name from this
        function.

        Parameters
        ----------
        team_data : string
            A string containing all of the rows of stats for a given team. If
            multiple tables are being referenced, this will be comprised of
            multiple rows in a single string.
        """
        name = team_data('td[data-stat="team_ID"]:first')
        name = re.sub(r'.*title="', '', str(name))
        name = re.sub(r'".*', '', name)
        setattr(self, '_name', name)

    def _parse_team_data(self, team_data):
        """
        Parses a value for every attribute.

        This function looks through every attribute with the exception of
        '_rank' and retrieves the value according to the parsing scheme and
        index of the attribute from the passed HTML data. Once the value is
        retrieved, the attribute's value is updated with the returned result.

        Note that this method is called directly once Team is invoked and does
        not need to be called manually.

        Parameters
        ----------
        team_data : string
            A string containing all of the rows of stats for a given team. If
            multiple tables are being referenced, this will be comprised of
            multiple rows in a single string.
        """
        for field in self.__dict__:
            # The short field truncates the leading '_' in the attribute name.
            short_field = str(field)[1:]
            # The rank attribute is passed directly to the class during
            # instantiation.
            if field == '_rank' or \
               field == '_year':
                continue
            elif field == '_name':
                self._parse_name(team_data)
                continue
            # Default to returning the first element returned unless a
            # subsequent element is desired. For example, total runs and
            # runs per game are two different fields, but they both share
            # the same attribute of 'R' in the HTML tables.
            index = 0
            if short_field in ELEMENT_INDEX.keys():
                index = ELEMENT_INDEX[short_field]
            value = utils._parse_field(PARSING_SCHEME,
                                       team_data,
                                       short_field,
                                       index)
            setattr(self, field, value)

    @property
    def dataframe(self):
        """
        Returns a pandas DataFrame containing all other class properties and
        values. The index for the DataFrame is the string abbreviation of the
        team, such as 'HOU'.
        """
        fields_to_include = {
            'abbreviation': self.abbreviation,
            'at_bats': self.at_bats,
            'average_batter_age': self.average_batter_age,
            'average_pitcher_age': self.average_pitcher_age,
            'away_losses': self.away_losses,
            'away_record': self.away_record,
            'away_wins': self.away_wins,
            'balks': self.balks,
            'bases_on_balls': self.bases_on_balls,
            'bases_on_walks_given': self.bases_on_walks_given,
            'bases_on_walks_given_per_nine_innings':
            self.bases_on_walks_given_per_nine_innings,
            'batters_faced': self.batters_faced,
            'batting_average': self.batting_average,
            'complete_game_shutouts': self.complete_game_shutouts,
            'complete_games': self.complete_games,
            'doubles': self.doubles,
            'earned_runs_against': self.earned_runs_against,
            'earned_runs_against_plus': self.earned_runs_against_plus,
            'extra_inning_losses': self.extra_inning_losses,
            'extra_inning_record': self.extra_inning_record,
            'extra_inning_wins': self.extra_inning_wins,
            'fielding_independent_pitching':
            self.fielding_independent_pitching,
            'games': self.games,
            'games_finished': self.games_finished,
            'grounded_into_double_plays': self.grounded_into_double_plays,
            'hit_pitcher': self.hit_pitcher,
            'hits': self.hits,
            'hits_allowed': self.hits_allowed,
            'hits_per_nine_innings': self.hits_per_nine_innings,
            'home_losses': self.home_losses,
            'home_record': self.home_record,
            'home_runs': self.home_runs,
            'home_runs_against': self.home_runs_against,
            'home_runs_per_nine_innings': self.home_runs_per_nine_innings,
            'home_wins': self.home_wins,
            'innings_pitched': self.innings_pitched,
            'intentional_bases_on_balls': self.intentional_bases_on_balls,
            'interleague_record': self.interleague_record,
            'last_ten_games_record': self.last_ten_games_record,
            'last_thirty_games_record': self.last_thirty_games_record,
            'last_twenty_games_record': self.last_twenty_games_record,
            'league': self.league,
            'losses': self.losses,
            'losses_last_ten_games': self.losses_last_ten_games,
            'losses_last_thirty_games': self.losses_last_thirty_games,
            'losses_last_twenty_games': self.losses_last_twenty_games,
            'losses_vs_left_handed_pitchers':
            self.losses_vs_left_handed_pitchers,
            'losses_vs_right_handed_pitchers':
            self.losses_vs_right_handed_pitchers,
            'losses_vs_teams_over_500': self.losses_vs_teams_over_500,
            'losses_vs_teams_under_500': self.losses_vs_teams_under_500,
            'luck': self.luck,
            'name': self.name,
            'number_of_pitchers': self.number_of_pitchers,
            'number_players_used': self.number_players_used,
            'on_base_percentage': self.on_base_percentage,
            'on_base_plus_slugging_percentage':
            self.on_base_plus_slugging_percentage,
            'on_base_plus_slugging_percentage_plus':
            self.on_base_plus_slugging_percentage_plus,
            'opposing_runners_left_on_base':
            self.opposing_runners_left_on_base,
            'plate_appearances': self.plate_appearances,
            'pythagorean_win_loss': self.pythagorean_win_loss,
            'rank': self.rank,
            'record_vs_left_handed_pitchers':
            self.record_vs_left_handed_pitchers,
            'record_vs_right_handed_pitchers':
            self.record_vs_right_handed_pitchers,
            'record_vs_teams_over_500': self.record_vs_teams_over_500,
            'record_vs_teams_under_500': self.record_vs_teams_under_500,
            'run_difference': self.run_difference,
            'runners_left_on_base': self.runners_left_on_base,
            'runs': self.runs,
            'runs_against': self.runs_against,
            'runs_allowed_per_game': self.runs_allowed_per_game,
            'runs_batted_in': self.runs_batted_in,
            'sacrifice_flies': self.sacrifice_flies,
            'sacrifice_hits': self.sacrifice_hits,
            'saves': self.saves,
            'shutouts': self.shutouts,
            'simple_rating_system': self.simple_rating_system,
            'single_run_losses': self.single_run_losses,
            'single_run_record': self.single_run_record,
            'single_run_wins': self.single_run_wins,
            'slugging_percentage': self.slugging_percentage,
            'stolen_bases': self.stolen_bases,
            'streak': self.streak,
            'strength_of_schedule': self.strength_of_schedule,
            'strikeouts': self.strikeouts,
            'strikeouts_per_base_on_balls': self.strikeouts_per_base_on_balls,
            'strikeouts_per_nine_innings': self.strikeouts_per_nine_innings,
            'times_caught_stealing': self.times_caught_stealing,
            'times_hit_by_pitch': self.times_hit_by_pitch,
            'times_struck_out': self.times_struck_out,
            'total_bases': self.total_bases,
            'total_runs': self.total_runs,
            'triples': self.triples,
            'whip': self.whip,
            'wild_pitches': self.wild_pitches,
            'win_percentage': self.win_percentage,
            'wins': self.wins,
            'wins_last_ten_games': self.wins_last_ten_games,
            'wins_last_thirty_games': self.wins_last_thirty_games,
            'wins_last_twenty_games': self.wins_last_twenty_games,
            'wins_vs_left_handed_pitchers': self.wins_vs_left_handed_pitchers,
            'wins_vs_right_handed_pitchers':
            self.wins_vs_right_handed_pitchers,
            'wins_vs_teams_over_500': self.wins_vs_teams_over_500,
            'wins_vs_teams_under_500': self.wins_vs_teams_under_500
        }
        return pd.DataFrame([fields_to_include], index=[self._abbreviation])

    @int_property_decorator
    def rank(self):
        """
        Returns an ``int`` of the team's rank based on their win percentage.
        """
        return self._rank

    @property
    def abbreviation(self):
        """
        Returns a ``string`` of the team's abbreviation, such as 'HOU' for the
        Houston Astros.
        """
        return self._abbreviation

    @property
    def schedule(self):
        """
        Returns an instance of the Schedule class containing the team's
        complete schedule for the season.
        """
        return Schedule(self._abbreviation, self._year)

    @property
    def roster(self):
        """
        Returns an instance of the Roster class containing all players for the
        team during the season with all career stats.
        """
        return Roster(self._abbreviation, self._year)

    @property
    def name(self):
        """
        Returns a ``string`` of the team's full name, such as 'Houston Astros'.
        """
        return self._name

    @property
    def league(self):
        """
        Returns a ``string`` of the two letter abbreviation of the league, such
        as 'AL' for the American League.
        """
        return self._league

    @int_property_decorator
    def games(self):
        """
        Returns an ``int`` of the number of games the team has played during
        the season.
        """
        return self._games

    @int_property_decorator
    def wins(self):
        """
        Returns an ``int`` of the total number of games the team won during the
        season.
        """
        return self._wins

    @int_property_decorator
    def losses(self):
        """
        Returns an ``int`` of the total number of games the team lost during
        the season.
        """
        return self._losses

    @float_property_decorator
    def win_percentage(self):
        """
        Returns a ``float`` of the number of wins divided by the number of
        games played during the season. Percentage ranges from 0-1.
        """
        return self._win_percentage

    @property
    def streak(self):
        """
        Returns a ``string`` of the team's current winning or losing streak,
        such as 'W 3' for a team on a 3-game winning streak.
        """
        return self._streak

    @float_property_decorator
    def runs(self):
        """
        Returns a ``float`` of the average number of runs scored per game by
        the team.
        """
        return self._runs

    @float_property_decorator
    def runs_against(self):
        """
        Returns a ``float`` of the average number of runs scored per game by
        the opponent.
        """
        return self._runs_against

    @float_property_decorator
    def run_difference(self):
        """
        Returns a ``float`` of the difference between the number of runs scored
        and the number of runs given up per game. Positive numbers indicate
        the team scores more per game than they are scored on.
        """
        return self._run_difference

    @float_property_decorator
    def strength_of_schedule(self):
        """
        Returns a ``float`` denoting a team's strength of schedule, based on
        runs scores and conceded. Higher values result in more challenging
        schedules while 0.0 is an average schedule.
        """
        return self._strength_of_schedule

    @float_property_decorator
    def simple_rating_system(self):
        """
        Returns a ``float`` of the average number of runs per game a team
        scores compared to average.
        """
        return self._simple_rating_system

    @property
    def pythagorean_win_loss(self):
        """
        Returns a ``string`` of the team's expected win-loss record based on
        the runs scored and allowed. Record is in the format 'W-L'.
        """
        return self._pythagorean_win_loss

    @int_property_decorator
    def luck(self):
        """
        Returns an ``int`` of the difference between the current wins and
        losses compared to the pythagorean wins and losses.
        """
        return self._luck

    @property
    def interleague_record(self):
        """
        Returns a ``string`` of the team's interleague record. Record is in the
        format 'W-L'.
        """
        return self._interleague_record

    @property
    def home_record(self):
        """
        Returns a ``string`` of the team's home record. Record is in the format
        'W-L'.
        """
        return self._home_record

    @mlb_int_property_decorator
    def home_wins(self):
        """
        Returns an ``int`` of the number of wins at home during the season.
        """
        return self._home_record

    @mlb_int_property_decorator
    def home_losses(self):
        """
        Returns an ``int`` of the number of losses at home during the season.
        """
        return self._home_record

    @property
    def away_record(self):
        """
        Returns a ``string`` of the team's away record. Record is in the format
        'W-L'.
        """
        return self._away_record

    @mlb_int_property_decorator
    def away_wins(self):
        """
        Returns an ``int`` of the number of away wins during the season.
        """
        return self._away_record

    @mlb_int_property_decorator
    def away_losses(self):
        """
        Returns an ``int`` of the number of away losses during the season.
        """
        return self._away_record

    @property
    def extra_inning_record(self):
        """
        Returns a ``string`` of the team's record when the game has gone to
        extra innings. Record is in the format 'W-L'.
        """
        return self._extra_inning_record

    @mlb_int_property_decorator
    def extra_inning_wins(self):
        """
        Returns an ``int`` of the number of wins the team has when the game has
        gone to extra innings.
        """
        return self._extra_inning_record

    @mlb_int_property_decorator
    def extra_inning_losses(self):
        """
        Returns an ``int`` of the number of losses the team has when the game
        has gone to extra innings.
        """
        return self._extra_inning_record

    @property
    def single_run_record(self):
        """
        Returns a ``string`` of the team's record when only one run is scored.
        Record is in the format 'W-L'.
        """
        return self._single_run_record

    @mlb_int_property_decorator
    def single_run_wins(self):
        """
        Returns an ``int`` of the number of wins the team has when only one run
        is scored.
        """
        return self._single_run_record

    @mlb_int_property_decorator
    def single_run_losses(self):
        """
        Returns an ``int`` of the number of losses the team has when only one
        run is scored.
        """
        return self._single_run_record

    @property
    def record_vs_right_handed_pitchers(self):
        """
        Returns a ``string`` of the team's record against right-handed
        pitchers.
        Record is in the format 'W-L'.
        """
        return self._record_vs_right_handed_pitchers

    @mlb_int_property_decorator
    def wins_vs_right_handed_pitchers(self):
        """
        Returns an ``int`` of the number of wins against right-handed pitchers.
        """
        return self._record_vs_right_handed_pitchers

    @mlb_int_property_decorator
    def losses_vs_right_handed_pitchers(self):
        """
        Returns an ``int`` of the number of losses against right-handed
        pitchers.
        """
        return self._record_vs_right_handed_pitchers

    @property
    def record_vs_left_handed_pitchers(self):
        """
        Returns a ``string`` of the team's record against left-handed pitchers.
        Record is in the format 'W-L'.
        """
        return self._record_vs_left_handed_pitchers

    @mlb_int_property_decorator
    def wins_vs_left_handed_pitchers(self):
        """
        Returns an ``int`` of number of wins against left-handed pitchers.
        """
        return self._record_vs_left_handed_pitchers

    @mlb_int_property_decorator
    def losses_vs_left_handed_pitchers(self):
        """
        Returns an ``int`` of number of losses against left-handed pitchers.
        """
        return self._record_vs_left_handed_pitchers

    @property
    def record_vs_teams_over_500(self):
        """
        Returns a ``string`` of the team's record against teams with a win
        percentage over 500. Record is in the format 'W-L'.
        """
        return self._record_vs_teams_over_500

    @mlb_int_property_decorator
    def wins_vs_teams_over_500(self):
        """
        Returns an ``int`` of the number of wins against teams over 500.
        """
        return self._record_vs_teams_over_500

    @mlb_int_property_decorator
    def losses_vs_teams_over_500(self):
        """
        Returns an ``int`` of the number of losses against teams over 500.
        """
        return self._record_vs_teams_over_500

    @property
    def record_vs_teams_under_500(self):
        """
        Returns a ``string`` of the team's record against teams with a win
        percentage under 500. Record is in the format 'W-L'.
        """
        return self._record_vs_teams_under_500

    @mlb_int_property_decorator
    def wins_vs_teams_under_500(self):
        """
        Returns an ``int`` of the number of wins against teams under 500.
        """
        return self._record_vs_teams_under_500

    @mlb_int_property_decorator
    def losses_vs_teams_under_500(self):
        """
        Returns an ``int`` of the number of losses against teams under 500.
        """
        return self._record_vs_teams_under_500

    @property
    def last_ten_games_record(self):
        """
        Returns a ``string`` of the team's record over the last ten games.
        Record is in the format 'W-L'.
        """
        return self._last_ten_games_record

    @mlb_int_property_decorator
    def wins_last_ten_games(self):
        """
        Returns an ``int`` of the number of wins in the last 10 games.
        """
        return self._last_ten_games_record

    @mlb_int_property_decorator
    def losses_last_ten_games(self):
        """
        Returns an ``int`` of the number of losses in the last 10 games.
        """
        return self._last_ten_games_record

    @property
    def last_twenty_games_record(self):
        """
        Returns a ``string`` of the team's record over the last twenty games.
        Record is in the format 'W-L'.
        """
        return self._last_twenty_games_record

    @mlb_int_property_decorator
    def wins_last_twenty_games(self):
        """
        Returns an ``int`` of the number of wins in the last 20 games.
        """
        return self._last_twenty_games_record

    @mlb_int_property_decorator
    def losses_last_twenty_games(self):
        """
        Returns an ``int`` of the number of losses in the last 20 games.
        """
        return self._last_twenty_games_record

    @property
    def last_thirty_games_record(self):
        """
        Returns a ``string`` of the team's record over the last thirty games.
        Record is in the format 'W-L'.
        """
        return self._last_thirty_games_record

    @mlb_int_property_decorator
    def wins_last_thirty_games(self):
        """
        Returns an ``int`` of the number of wins in the last 30 games.
        """
        return self._last_thirty_games_record

    @mlb_int_property_decorator
    def losses_last_thirty_games(self):
        """
        Returns an ``int`` of the number of losses in the last 30 games.
        """
        return self._last_thirty_games_record

    @int_property_decorator
    def number_players_used(self):
        """
        Returns an ``int`` of the number of different players used during the
        season.
        """
        return self._number_players_used

    @float_property_decorator
    def average_batter_age(self):
        """
        Returns a ``float`` of the average batter age weighted by their number
        of at bats plus the number of games participated in.
        """
        return self._average_batter_age

    @int_property_decorator
    def plate_appearances(self):
        """
        Returns an ``int`` of the total number of plate appearances for the
        team.
        """
        return self._plate_appearances

    @int_property_decorator
    def at_bats(self):
        """
        Returns an ``int`` of the total number of at bats for the team.
        """
        return self._at_bats

    @int_property_decorator
    def total_runs(self):
        """
        Returns an ``int`` of the total number of runs scored during the
        season.
        """
        return self._total_runs

    @int_property_decorator
    def hits(self):
        """
        Returns an ``int`` of the total number of hits during the season.
        """
        return self._hits

    @int_property_decorator
    def doubles(self):
        """
        Returns an ``int`` of the total number of doubles hit by the team.
        """
        return self._doubles

    @int_property_decorator
    def triples(self):
        """
        Returns an ``int`` of the total number of tripes hit by the team.
        """
        return self._triples

    @int_property_decorator
    def home_runs(self):
        """
        Returns an ``int`` of the total number of home runs hit by the team.
        """
        return self._home_runs

    @int_property_decorator
    def runs_batted_in(self):
        """
        Returns an ``int`` of the total number of runs batted in by the team.
        """
        return self._runs_batted_in

    @int_property_decorator
    def stolen_bases(self):
        """
        Returns an ``int`` of the total number of bases stolen by the team.
        """
        return self._stolen_bases

    @int_property_decorator
    def times_caught_stealing(self):
        """
        Returns an ``int`` of the number of times a player was caught stealing.
        """
        return self._times_caught_stealing

    @int_property_decorator
    def bases_on_balls(self):
        """
        Returns an ``int`` of the number of bases on walks.
        """
        return self._bases_on_balls

    @int_property_decorator
    def times_struck_out(self):
        """
        Returns an ``int`` of the total number of times the team struck out.
        """
        return self._times_struck_out

    @float_property_decorator
    def batting_average(self):
        """
        Returns a ``float`` of the batting average for the team. Percentage
        ranges from 0-1.
        """
        return self._batting_average

    @float_property_decorator
    def on_base_percentage(self):
        """
        Returns a ``float`` of the percentage of at bats that result in a
        player taking a base. Percentage ranges from 0-1.
        """
        return self._on_base_percentage

    @float_property_decorator
    def slugging_percentage(self):
        """
        Returns a ``float`` of the ratio of total bases gained per at bat.
        """
        return self._slugging_percentage

    @float_property_decorator
    def on_base_plus_slugging_percentage(self):
        """
        Returns a ``float`` of the sum of the on base percentage plus the
        slugging percentage.
        """
        return self._on_base_plus_slugging_percentage

    @int_property_decorator
    def on_base_plus_slugging_percentage_plus(self):
        """
        Returns an ``int`` of the on base percentage plus the slugging
        percentage, adjusted to the team's home ballpark.
        """
        return self._on_base_plus_slugging_percentage_plus

    @int_property_decorator
    def total_bases(self):
        """
        Returns an ``int`` of the total number of bases a team has gained
        during the season.
        """
        return self._total_bases

    @int_property_decorator
    def grounded_into_double_plays(self):
        """
        Returns an ``int`` of the total number double plays grounded into by
        the team.
        """
        return self._grounded_into_double_plays

    @int_property_decorator
    def times_hit_by_pitch(self):
        """
        Returns an ``int`` of the total number of times a batter was hit by an
        opponent's pitch.
        """
        return self._times_hit_by_pitch

    @int_property_decorator
    def sacrifice_hits(self):
        """
        Returns an ``int`` of the total number of sacrifice hits the team made
        during the season.
        """
        return self._sacrifice_hits

    @int_property_decorator
    def sacrifice_flies(self):
        """
        Returns an ``int`` of the total number of sacrifice flies the team made
        during the season.
        """
        return self._sacrifice_flies

    @int_property_decorator
    def intentional_bases_on_balls(self):
        """
        Returns an ``int`` of the total number of times a player took a base
        from an intentional walk.
        """
        return self._intentional_bases_on_balls

    @int_property_decorator
    def runners_left_on_base(self):
        """
        Returns an ``int`` of the total number of runners left on base at the
        end of an inning.
        """
        return self._runners_left_on_base

    @int_property_decorator
    def number_of_pitchers(self):
        """
        Returns an ``int`` of the total number of pitchers used during a
        season.
        """
        return self._number_of_pitchers

    @float_property_decorator
    def average_pitcher_age(self):
        """
        Returns a ``float`` of the average pitcher age weighted by the number
        of games started, followed by the number of games played and saves.
        """
        return self._average_pitcher_age

    @float_property_decorator
    def runs_allowed_per_game(self):
        """
        Returns a ``float`` of the average number of runs a team has allowed
        per game.
        """
        return self._runs_allowed_per_game

    @float_property_decorator
    def earned_runs_against(self):
        """
        Returns a ``float`` of the average number of earned runs against for a
        team.
        """
        return self._earned_runs_against

    @int_property_decorator
    def games_finished(self):
        """
        Returns an ``int`` of the number of games finished which is equivalent
        to the number of games played minus the number of complete games during
        the season.
        """
        return self._games_finished

    @int_property_decorator
    def complete_games(self):
        """
        Returns an ``int`` of the total number of complete games a team has
        accumulated during the season.
        """
        return self._complete_games

    @int_property_decorator
    def shutouts(self):
        """
        Returns an ``int`` of the total number of shutouts a team has
        accumulated during the season.
        """
        return self._shutouts

    @int_property_decorator
    def complete_game_shutouts(self):
        """
        Returns an ``int`` of the total number of complete games where the
        opponent scored zero runs.
        """
        return self._complete_game_shutouts

    @int_property_decorator
    def saves(self):
        """
        Returns an ``int`` of the total number of saves a team has accumulated
        during the season.
        """
        return self._saves

    @float_property_decorator
    def innings_pitched(self):
        """
        Returns a ``float`` of the total number of innings pitched by a team
        during the season.
        """
        return self._innings_pitched

    @int_property_decorator
    def hits_allowed(self):
        """
        Returns an ``int`` of the total number of hits allowed during the
        season.
        """
        return self._hits_allowed

    @int_property_decorator
    def home_runs_against(self):
        """
        Returns an ``int`` of the total number of home runs given up during the
        season.
        """
        return self._home_runs_against

    @int_property_decorator
    def bases_on_walks_given(self):
        """
        Returns an ``int`` of the total number of bases from walks given up by
        a team during the season.
        """
        return self._bases_on_walks_given

    @int_property_decorator
    def strikeouts(self):
        """
        Returns an ``int`` of the total number of times a team has struck out
        an opponent.
        """
        return self._strikeouts

    @int_property_decorator
    def hit_pitcher(self):
        """
        Returns an ``int`` of the total number of times a pitcher has hit an
        opposing batter.
        """
        return self._hit_pitcher

    @int_property_decorator
    def balks(self):
        """
        Returns an ``int`` of the total number of times a pitcher has balked.
        """
        return self._balks

    @int_property_decorator
    def wild_pitches(self):
        """
        Returns an ``int`` of the total number of wild pitches thrown by a team
        during a season.
        """
        return self._wild_pitches

    @int_property_decorator
    def batters_faced(self):
        """
        Returns an ``int`` of the total number of batters all pitchers have
        faced during a season.
        """
        return self._batters_faced

    @int_property_decorator
    def earned_runs_against_plus(self):
        """
        Returns an ``int`` of the team's average earned runs against, adjusted
        for the home ballpark.
        """
        return self._earned_runs_against_plus

    @float_property_decorator
    def fielding_independent_pitching(self):
        """
        Returns a ``float`` of the team's effectiveness at preventing home
        runs, walks, batters being hit by pitches, and strikeouts.
        """
        return self._fielding_independent_pitching

    @float_property_decorator
    def whip(self):
        """
        Returns a ``float`` of the average number of walks plus hits by the
        opponent per inning.
        """
        return self._whip

    @float_property_decorator
    def hits_per_nine_innings(self):
        """
        Returns a ``float`` of the average number of hits per nine innings by
        the opponent.
        """
        return self._hits_per_nine_innings

    @float_property_decorator
    def home_runs_per_nine_innings(self):
        """
        Returns a ``float`` of the average number of home runs per nine innings
        by the opponent.
        """
        return self._home_runs_per_nine_innings

    @float_property_decorator
    def bases_on_walks_given_per_nine_innings(self):
        """
        Returns a ``float`` of the average number of walks conceded per nine
        innings.
        """
        return self._bases_on_walks_given_per_nine_innings

    @float_property_decorator
    def strikeouts_per_nine_innings(self):
        """
        Returns a ``float`` of the average number of strikeouts a team throws
        per nine innings.
        """
        return self._strikeouts_per_nine_innings

    @float_property_decorator
    def strikeouts_per_base_on_balls(self):
        """
        Returns a ``float`` of the average number of strikeouts per walk thrown
        by a team.
        """
        return self._strikeouts_per_base_on_balls

    @int_property_decorator
    def opposing_runners_left_on_base(self):
        """
        Returns an ``int`` of the total number of opponents a team has left on
        bases at the end of an inning.
        """
        return self._opposing_runners_left_on_base


class Teams:
    """
    A list of all MLB teams and their stats in a given year.

    Finds and retrieves a list of all MLB teams from www.baseball-reference.com
    and creates a Team instance for every team that participated in the league
    in a given year. The Team class comprises a list of all major stats and a
    few identifiers for the requested season.

    Parameters
    ----------
    year : string (optional)
        The requested year to pull stats from.
    """
    def __init__(self, year=None):
        self._teams = []

        self._retrieve_all_teams(year)

    def __getitem__(self, abbreviation):
        """
        Return a specified team.

        Returns a team's instance in the Teams class as specified by the team's
        abbreviation.

        Parameters
        ----------
        abbreviation : string
            An MLB team's three letter abbreviation (ie. 'HOU' for Houston
            Astros).

        Returns
        -------
        Team instance
            If the requested team can be found, its Team instance is returned.

        Raises
        ------
        ValueError
            If the requested team is not present within the Teams list.
        """
        for team in self._teams:
            if team.abbreviation.upper() == abbreviation.upper():
                return team
        raise ValueError('Team abbreviation %s not found' % abbreviation)

    def __call__(self, abbreviation):
        """
        Return a specified team.

        Returns a team's instance in the Teams class as specified by the team's
        abbreviation. This method is a wrapper for __getitem__.

        Parameters
        ----------
        abbreviation : string
            An MLB team's three letter abbreviation (ie. 'HOU' for Houson
            Astros).

        Returns
        -------
        Team instance
            If the requested team can be found, its Team instance is returned.
        """
        return self.__getitem__(abbreviation)

    def __repr__(self):
        """Returns a ``list`` of all MLB teams for the given season."""
        return self._teams

    def __iter__(self):
        """Returns an iterator of all of the MLB teams for a given season."""
        return iter(self.__repr__())

    def __len__(self):
        """Returns the number of MLB teams for a given season."""
        return len(self.__repr__())

    def _add_stats_data(self, teams_list, team_data_dict):
        """
        Add a team's stats row to a dictionary.

        Pass table contents and a stats dictionary of all teams to accumulate
        all stats for each team in a single variable.

        Parameters
        ----------
        teams_list : generator
            A generator of all row items in a given table.
        team_data_dict : {str: {'data': str, 'rank': int}} dictionary
            A dictionary where every key is the team's abbreviation and every
            value is another dictionary with a 'data' key which contains the
            string version of the row data for the matched team, and a 'rank'
            key which is the rank of the team.

        Returns
        -------
        dictionary
            An updated version of the team_data_dict with the passed table row
            information included.
        """
        # Teams are listed in terms of rank with the first team being #1
        rank = 1
        for team_data in teams_list:
            # Skip the league average row
            if 'class="league_average_table"' in str(team_data):
                continue
            abbr = utils._parse_field(PARSING_SCHEME,
                                      team_data,
                                      'abbreviation')
            try:
                team_data_dict[abbr]['data'] += team_data
            except KeyError:
                team_data_dict[abbr] = {'data': team_data, 'rank': rank}
            rank += 1
        return team_data_dict

    def _retrieve_all_teams(self, year):
        """
        Find and create Team instances for all teams in the given season.

        For a given season, parses the specified MLB stats table and finds all
        requested stats. Each team then has a Team instance created which
        includes all requested stats and a few identifiers, such as the team's
        name and abbreviation. All of the individual Team instances are added
        to a list.

        Note that this method is called directly once Teams is invoked and does
        not need to be called manually.

        Parameters
        ----------
        year : string
            The requested year to pull stats from.
        """
        team_data_dict = {}

        if not year:
            year = utils._find_year_for_season('mlb')
        doc = pq(STANDINGS_URL % year)
        div_prefix = 'div#all_expanded_standings_overall'
        standings = utils._get_stats_table(doc, div_prefix)
        doc = pq(TEAM_STATS_URL % year)
        div_prefix = 'div#all_teams_standard_%s'
        batting_stats = utils._get_stats_table(doc, div_prefix % 'batting')
        pitching_stats = utils._get_stats_table(doc, div_prefix % 'pitching')
        for stats_list in [standings, batting_stats, pitching_stats]:
            team_data_dict = self._add_stats_data(stats_list, team_data_dict)

        for team_data in team_data_dict.values():
            team = Team(team_data['data'], team_data['rank'], year)
            self._teams.append(team)

    @property
    def dataframes(self):
        """
        Returns a pandas DataFrame where each row is a representation of the
        Team class. Rows are indexed by the team abbreviation.
        """
        frames = []
        for team in self.__iter__():
            frames.append(team.dataframe)
        return pd.concat(frames)
