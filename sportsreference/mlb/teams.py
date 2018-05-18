import re
from .constants import (ELEMENT_INDEX,
                        PARSING_SCHEME,
                        STANDINGS_URL,
                        TEAM_STATS_URL)
from pyquery import PyQuery as pq
from .. import utils


class Team:
    """
    An object containing all of a team's season information.

    Finds and parses all team stat information and identifiers, such as rank,
    name, and abbreviation, and sets them as properties which can be directly
    read from for easy reference.
    """
    def __init__(self, team_data, rank):
        """
        Parse all of the attributes located in the HTML data.

        Once Team is invoked, it parses all of the listed attributes for the
        team which can be found in the passed HTML data. All attributes below
        are properties which can be directly read for easy reference.

        Parameters
        ----------
        team_data : string
            A string containing all of the rows of stats for a given team. If
            multiple tables are being referenced, this will be comprised of
            multiple rows in a single string.
        rank : int
            A team's position in the league based on the number of points they
            obtained during the season.
        """
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
            if field == '_rank':
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
            value = utils.parse_field(PARSING_SCHEME,
                                      team_data,
                                      short_field,
                                      index)
            setattr(self, field, value)

    @property
    def rank(self):
        """
        Returns an int of the team's rank based on their win percentage.
        """
        return int(self._rank)

    @property
    def abbreviation(self):
        """
        Returns a string of the team's abbreviation, such as 'HOU' for the
        Houston Astros.
        """
        return self._abbreviation

    @property
    def name(self):
        """
        Returns a string of the team's full name, such as 'Houston Astros'.
        """
        return self._name

    @property
    def league(self):
        """
        Returns a string of the two letter abbreviation of the league, such as
        'AL' for the American League.
        """
        return self._league

    @property
    def games(self):
        """
        Returns an int of the number of games the team has played during the
        season.
        """
        return int(self._games)

    @property
    def wins(self):
        """
        Returns an int of the total number of games the team won during the
        season.
        """
        return int(self._wins)

    @property
    def losses(self):
        """
        Returns an int of the total number of games the team lost during the
        season.
        """
        return int(self._losses)

    @property
    def win_percentage(self):
        """
        Returns a float of the number of wins divided by the number of games
        played during the season. Percentage ranges from 0-1.
        """
        return float(self._win_percentage)

    @property
    def streak(self):
        """
        Returns a string of the team's current winning or losing streak, such
        as 'W 3' for a team on a 3-game winning streak.
        """
        return self._streak

    @property
    def runs(self):
        """
        Returns a float of the average number of runs scored per game by the
        team.
        """
        return float(self._runs)

    @property
    def runs_against(self):
        """
        Returns a float of the average number of runs scored per game by the
        opponent.
        """
        return float(self._runs_against)

    @property
    def run_difference(self):
        """
        Returns a float of the difference between the number of runs scored
        and the number of runs given up per game. Positive numbers indicate
        the team scores more per game than they are scored on.
        """
        return float(self._run_difference)

    @property
    def strength_of_schedule(self):
        """
        Returns a float denoting a team's strength of schedule, based on runs
        scores and conceded. Higher values result in more challenging schedules
        while 0.0 is an average schedule.
        """
        return float(self._strength_of_schedule)

    @property
    def simple_rating_system(self):
        """
        Returns a float of the average number of runs per game a team scores
        compared to average.
        """
        return float(self._simple_rating_system)

    @property
    def pythagorean_win_loss(self):
        """
        Returns a string of the team's expected win-loss record based on the
        runs scored and allowed. Record is in the format 'W-L'.
        """
        return self._pythagorean_win_loss

    @property
    def luck(self):
        """
        Returns an integer of the difference between the current wins and
        losses compared to the pythagorean wins and losses.
        """
        return int(self._luck)

    @property
    def interleague_record(self):
        """
        Returns a string of the team's interleague record. Record is in the
        format 'W-L'.
        """
        return self._interleague_record

    @property
    def home_record(self):
        """
        Returns a string of the team's home record. Record is in the format
        'W-L'.
        """
        return self._home_record

    @property
    def home_wins(self):
        """
        Returns an int of the number of wins at home during the season.
        """
        return int(self._home_record.split('-')[0])

    @property
    def home_losses(self):
        """
        Returns an int of the number of losses at home during the season.
        """
        return int(self._home_record.split('-')[1])

    @property
    def away_record(self):
        """
        Returns a string of the team's away record. Record is in the format
        'W-L'.
        """
        return self._away_record

    @property
    def away_wins(self):
        """
        Returns an int of the number of away wins during the season.
        """
        return int(self._away_record.split('-')[0])

    @property
    def away_losses(self):
        """
        Returns an int of the number of away losses during the season.
        """
        return int(self._away_record.split('-')[1])

    @property
    def extra_inning_record(self):
        """
        Returns a string of the team's record when the game has gone to extra
        innings. Record is in the format 'W-L'.
        """
        return self._extra_inning_record

    @property
    def extra_inning_wins(self):
        """
        Returns an int of the number of wins the team has when the game has
        gone to extra innings.
        """
        return int(self._extra_inning_record.split('-')[0])

    @property
    def extra_inning_losses(self):
        """
        Returns an int of the number of losses the team has when the game has
        gone to extra innings.
        """
        return int(self._extra_inning_record.split('-')[1])

    @property
    def single_run_record(self):
        """
        Returns a string of the team's record when only one run is scored.
        Record is in the format 'W-L'.
        """
        return self._single_run_record

    @property
    def single_run_wins(self):
        """
        Returns an int of the number of wins the team has when only one run is
        scored.
        """
        return int(self._single_run_record.split('-')[0])

    @property
    def single_run_losses(self):
        """
        Returns an int of the number of losses the team has when only one run
        is scored.
        """
        return int(self._single_run_record.split('-')[1])

    @property
    def record_vs_right_handed_pitchers(self):
        """
        Returns a string of the team's record against right-handed pitchers.
        Record is in the format 'W-L'.
        """
        return self._record_vs_right_handed_pitchers

    @property
    def wins_vs_right_handed_pitchers(self):
        """
        Returns an int of the number of wins against right-handed pitchers.
        """
        return int(self._record_vs_right_handed_pitchers.split('-')[0])

    @property
    def losses_vs_right_handed_pitchers(self):
        """
        Returns an int of the number of losses against right-handed pitchers.
        """
        return int(self._record_vs_right_handed_pitchers.split('-')[1])

    @property
    def record_vs_left_handed_pitchers(self):
        """
        Returns a string of the team's record against left-handed pitchers.
        Record is in the format 'W-L'.
        """
        return self._record_vs_left_handed_pitchers

    @property
    def wins_vs_left_handed_pitchers(self):
        """
        Returns an int of number of wins against left-handed pitchers.
        """
        return int(self._record_vs_left_handed_pitchers.split('-')[0])

    @property
    def losses_vs_left_handed_pitchers(self):
        """
        Returns an int of number of losses against left-handed pitchers.
        """
        return int(self._record_vs_left_handed_pitchers.split('-')[1])

    @property
    def record_vs_teams_over_500(self):
        """
        Returns a string of the team's record against teams with a win
        percentage over 500. Record is in the format 'W-L'.
        """
        return self._record_vs_teams_over_500

    @property
    def wins_vs_teams_over_500(self):
        """
        Returns an int of the number of wins against teams over 500.
        """
        return int(self._record_vs_teams_over_500.split('-')[0])

    @property
    def losses_vs_teams_over_500(self):
        """
        Returns an int of the number of losses against teams over 500.
        """
        return int(self._record_vs_teams_over_500.split('-')[1])

    @property
    def record_vs_teams_under_500(self):
        """
        Returns a string of the team's record against teams with a win
        percentage under 500. Record is in the format 'W-L'.
        """
        return self._record_vs_teams_under_500

    @property
    def wins_vs_teams_under_500(self):
        """
        Returns an int of the number of wins against teams under 500.
        """
        return int(self._record_vs_teams_under_500.split('-')[0])

    @property
    def losses_vs_teams_under_500(self):
        """
        Returns an int of the number of losses against teams under 500.
        """
        return int(self._record_vs_teams_under_500.split('-')[1])

    @property
    def last_ten_games_record(self):
        """
        Returns a string of the team's record over the last ten games. Record
        is in the format 'W-L'.
        """
        return self._last_ten_games_record

    @property
    def wins_last_ten_games(self):
        """
        Returns an int of the number of wins in the last 10 games.
        """
        try:
            return int(self._last_ten_games_record.split('-')[0])
        except AttributeError:
            return None

    @property
    def losses_last_ten_games(self):
        """
        Returns an int of the number of losses in the last 10 games.
        """
        try:
            return int(self._last_ten_games_record.split('-')[1])
        except AttributeError:
            return None

    @property
    def last_twenty_games_record(self):
        """
        Returns a string of the team's record over the last twenty games.
        Record is in the format 'W-L'.
        """
        return self._last_twenty_games_record

    @property
    def wins_last_twenty_games(self):
        """
        Returns an int of the number of wins in the last 20 games.
        """
        try:
            return int(self._last_twenty_games_record.split('-')[0])
        except AttributeError:
            return None

    @property
    def losses_last_twenty_games(self):
        """
        Returns an int of the number of losses in the last 20 games.
        """
        try:
            return int(self._last_twenty_games_record.split('-')[1])
        except AttributeError:
            return None

    @property
    def last_thirty_games_record(self):
        """
        Returns a string of the team's record over the last thirty games.
        Record is in the format 'W-L'.
        """
        return self._last_thirty_games_record

    @property
    def wins_last_thirty_games(self):
        """
        Returns an int of the number of wins in the last 30 games.
        """
        try:
            return int(self._last_thirty_games_record.split('-')[0])
        except AttributeError:
            return None

    @property
    def losses_last_thirty_games(self):
        """
        Returns an int of the number of losses in the last 30 games.
        """
        try:
            return int(self._last_thirty_games_record.split('-')[1])
        except AttributeError:
            return None

    @property
    def number_players_used(self):
        """
        Returns an int of the number of different players used during the
        season.
        """
        return int(self._number_players_used)

    @property
    def average_batter_age(self):
        """
        Returns a float of the average batter age weighted by their number of
        at bats plus the number of games participated in.
        """
        return float(self._average_batter_age)

    @property
    def plate_appearances(self):
        """
        Returns an int of the total number of plate appearances for the team.
        """
        return int(self._plate_appearances)

    @property
    def at_bats(self):
        """
        Returns an int of the total number of at bats for the team.
        """
        return int(self._at_bats)

    @property
    def total_runs(self):
        """
        Returns an int of the total number of runs scored during the season.
        """
        return int(self._total_runs)

    @property
    def hits(self):
        """
        Returns an int of the total number of hits during the season.
        """
        return int(self._hits)

    @property
    def doubles(self):
        """
        Returns an int of the total number of doubles hit by the team.
        """
        return int(self._doubles)

    @property
    def triples(self):
        """
        Returns an int of the total number of tripes hit by the team.
        """
        return int(self._triples)

    @property
    def home_runs(self):
        """
        Returns an int of the total number of home runs hit by the team.
        """
        return int(self._home_runs)

    @property
    def runs_batted_in(self):
        """
        Returns an int of the total number of runs batted in by the team.
        """
        return int(self._runs_batted_in)

    @property
    def stolen_bases(self):
        """
        Returns an int of the total number of bases stolen by the team.
        """
        return int(self._stolen_bases)

    @property
    def times_caught_stealing(self):
        """
        Returns an int of the number of times a player was caught stealing.
        """
        return int(self._times_caught_stealing)

    @property
    def bases_on_balls(self):
        """
        Returns an int of the number of bases on walks.
        """
        return int(self._bases_on_balls)

    @property
    def times_struck_out(self):
        """
        Returns an int of the total number of times the team struck out.
        """
        return int(self._times_struck_out)

    @property
    def batting_average(self):
        """
        Returns a float of the batting average for the team. Percentage ranges
        from 0-1.
        """
        return float(self._batting_average)

    @property
    def on_base_percentage(self):
        """
        Returns a float of the percentage of at bats that result in a player
        taking a base. Percentage ranges from 0-1.
        """
        return float(self._on_base_percentage)

    @property
    def slugging_percentage(self):
        """
        Returns a float of the ratio of total bases gained per at bat.
        """
        return float(self._slugging_percentage)

    @property
    def on_base_plus_slugging_percentage(self):
        """
        Returns a float of the sum of the on base percentage plus the slugging
        percentage.
        """
        return float(self._on_base_plus_slugging_percentage)

    @property
    def on_base_plus_slugging_percentage_plus(self):
        """
        Returns an int of the on base percentage plus the slugging percentage,
        adjusted to the team's home ballpark.
        """
        return int(self._on_base_plus_slugging_percentage_plus)

    @property
    def total_bases(self):
        """
        Returns an int of the total number of bases a team has gained during
        the season.
        """
        return int(self._total_bases)

    @property
    def grounded_into_double_plays(self):
        """
        Returns an int of the total number double plays grounded into by the
        team.
        """
        return int(self._grounded_into_double_plays)

    @property
    def times_hit_by_pitch(self):
        """
        Returns an int of the total number of times a batter was hit by an
        opponent's pitch.
        """
        return int(self._times_hit_by_pitch)

    @property
    def sacrifice_hits(self):
        """
        Returns an int of the total number of sacrifice hits the team made
        during the season.
        """
        return int(self._sacrifice_hits)

    @property
    def sacrifice_flies(self):
        """
        Returns an int of the total number of sacrifice flies the team made
        during the season.
        """
        return int(self._sacrifice_flies)

    @property
    def intentional_bases_on_balls(self):
        """
        Returns an int of the total number of times a player took a base from
        an intentional walk.
        """
        return int(self._intentional_bases_on_balls)

    @property
    def runners_left_on_base(self):
        """
        Returns an int of the total number of runners left on base at the end
        of an inning.
        """
        return int(self._runners_left_on_base)

    @property
    def number_of_pitchers(self):
        """
        Returns an int of the total number of pitchers used during a season.
        """
        return int(self._number_of_pitchers)

    @property
    def average_pitcher_age(self):
        """
        Returns a float of the average pitcher age weighted by the number of
        games started, followed by the number of games played and saves.
        """
        return float(self._average_pitcher_age)

    @property
    def runs_allowed_per_game(self):
        """
        Returns a float of the average number of runs a team has allowed per
        game.
        """
        return float(self._runs_allowed_per_game)

    @property
    def earned_runs_against(self):
        """
        Returns a float of the average number of earned runs against for a
        team.
        """
        return float(self._earned_runs_against)

    @property
    def games_finished(self):
        """
        Returns an int of the number of games finished which is equivalent to
        the number of games played minus the number of complete games during
        the season.
        """
        return int(self._games_finished)

    @property
    def complete_games(self):
        """
        Returns an int of the total number of complete games a team has
        accumulated during the season.
        """
        return int(self._complete_games)

    @property
    def shutouts(self):
        """
        Returns an int of the total number of shutouts a team has accumulated
        during the season.
        """
        return int(self._shutouts)

    @property
    def complete_game_shutouts(self):
        """
        Returns an int of the total number of complete games where the opponent
        scored zero runs.
        """
        return int(self._complete_game_shutouts)

    @property
    def saves(self):
        """
        Returns an int of the total number of saves a team has accumulated
        during the season.
        """
        return int(self._saves)

    @property
    def innings_pitched(self):
        """
        Returns a float of the total number of innings pitched by a team during
        the season.
        """
        return float(self._innings_pitched)

    @property
    def hits_allowed(self):
        """
        Returns an int of the total number of hits allowed during the season.
        """
        return int(self._hits_allowed)

    @property
    def home_runs_against(self):
        """
        Returns an int of the total number of home runs given up during the
        season.
        """
        return int(self._home_runs_against)

    @property
    def bases_on_walks_given(self):
        """
        Returns an int of the total number of bases from walks given up by a
        team during the season.
        """
        return int(self._bases_on_walks_given)

    @property
    def strikeouts(self):
        """
        Returns an int of the total number of times a team has struck out an
        opponent.
        """
        return int(self._strikeouts)

    @property
    def hit_pitcher(self):
        """
        Returns an int of the total number of times a pitcher has hit an
        opposing batter.
        """
        return int(self._hit_pitcher)

    @property
    def balks(self):
        """
        Returns an int of the total number of times a pitcher has balked.
        """
        return int(self._balks)

    @property
    def wild_pitches(self):
        """
        Returns an int of the total number of wild pitches thrown by a team
        during a season.
        """
        return int(self._wild_pitches)

    @property
    def batters_faced(self):
        """
        Returns an int of the total number of batters all pitchers have faced
        during a season.
        """
        return int(self._batters_faced)

    @property
    def earned_runs_against_plus(self):
        """
        Returns an int of the team's average earned runs against, adjusted for
        the home ballpark.
        """
        return int(self._earned_runs_against_plus)

    @property
    def fielding_independent_pitching(self):
        """
        Returns a float of the team's effectiveness at preventing home runs,
        walks, batters being hit by pitches, and strikeouts.
        """
        return float(self._fielding_independent_pitching)

    @property
    def whip(self):
        """
        Returns a float of the average number of walks plus hits by the
        opponent per inning.
        """
        return float(self._whip)

    @property
    def hits_per_nine_innings(self):
        """
        Returns a float of the average number of hits per nine innings by the
        opponent.
        """
        return float(self._hits_per_nine_innings)

    @property
    def home_runs_per_nine_innings(self):
        """
        Returns a float of the average number of home runs per nine innings by
        the opponent.
        """
        return float(self._home_runs_per_nine_innings)

    @property
    def bases_on_walks_given_per_nine_innings(self):
        """
        Returns a float of the average number of walks conceded per nine
        innings.
        """
        return float(self._bases_on_walks_given_per_nine_innings)

    @property
    def strikeouts_per_nine_innings(self):
        """
        Returns a float of the average number of strikeouts a team throws per
        nine innings.
        """
        return float(self._strikeouts_per_nine_innings)

    @property
    def strikeouts_per_base_on_balls(self):
        """
        Returns a float of the average number of strikeouts per walk thrown
        by a team.
        """
        return float(self._strikeouts_per_base_on_balls)

    @property
    def opposing_runners_left_on_base(self):
        """
        Returns an int of the total number of opponents a team has left on
        bases at the end of an inning.
        """
        return int(self._opposing_runners_left_on_base)


class Teams:
    """
    A list of all MLB teams and their stats in a given year.

    Finds and retrieves a list of all MLB teams from www.baseball-reference.com
    and creates a Team instance for every team that participated in the league
    in a given year. The Team class comprises a list of all major stats and a
    few identifiers for the requested season.
    """
    def __init__(self, year=None):
        """
        Get a list of all Team instances

        Once Teams is invoked, it retrieves a list of all MLB teams in the
        desired season and adds them to the '_teams' attribute.

        Parameters
        ----------
        year : string (optional)
            The requested year to pull stats from.
        """
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
        """Returns a list of all MLB teams for the given season."""
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
            abbr = utils.parse_field(PARSING_SCHEME, team_data, 'abbreviation')
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
            year = utils.find_year_for_season('mlb')
        doc = pq(STANDINGS_URL % year)
        standings = utils.get_stats_table(doc, 'div#all_expanded_standings_overall')
        doc = pq(TEAM_STATS_URL % year)
        batting_stats = utils.get_stats_table(doc, 'div#all_teams_standard_batting')
        pitching_stats = utils.get_stats_table(doc, 'div#all_teams_standard_pitching')
        for stats_list in [standings, batting_stats, pitching_stats]:
            team_data_dict = self._add_stats_data(stats_list, team_data_dict)

        for team_data in team_data_dict.values():
            team = Team(team_data['data'], team_data['rank'])
            self._teams.append(team)
