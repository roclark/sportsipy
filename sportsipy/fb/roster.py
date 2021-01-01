import pandas as pd
import re
from .constants import ROSTER_SCHEME, SQUAD_URL
from ..decorators import float_property_decorator, int_property_decorator
from .fb_utils import _lookup_team
from .league_ids import LEAGUE_IDS
from pyquery import PyQuery as pq
from sportsipy.utils import (_get_stats_table,
                             _parse_field,
                             _remove_html_comment_tags)
from urllib.error import HTTPError


class SquadPlayer:
    """
    Get player information and stats.

    Given a player ID and data, capture all relevant stats and information for
    the player including name, nationality, goals, assists, expected goal
    difference, nutmegs, and much more.

    Parameters
    ----------
    player_data : PyQuery object
        A PyQuery object containing all fields of information for a single
        player, represented as one long row by concatenating all tables which
        hold values for the requested player.
    player_id : string
        A ``string`` representation of the player's unique 8-digit ID as shown
        on fbref.com.
    """
    def __init__(self, player_data, player_id):
        self._name = None
        self._player_id = player_id
        self._nationality = None
        self._position = None
        self._age = None
        self._matches_played = None
        self._starts = None
        self._minutes = None
        self._goals = None
        self._assists = None
        self._penalty_kicks = None
        self._penalty_kick_attempts = None
        self._yellow_cards = None
        self._red_cards = None
        self._goals_per_90 = None
        self._assists_per_90 = None
        self._goals_and_assists_per_90 = None
        self._goals_non_penalty_per_90 = None
        self._goals_and_assists_non_penalty_per_90 = None
        self._expected_goals = None
        self._expected_goals_non_penalty = None
        self._expected_assists = None
        self._expected_goals_per_90 = None
        self._expected_assists_per_90 = None
        self._expected_goals_and_assists_per_90 = None
        self._expected_goals_non_penalty_per_90 = None
        self._expected_goals_and_assists_non_penalty_per_90 = None
        self._own_goals = None
        # Goalkeeping stats
        self._goals_against = None
        self._own_goals_against = None
        self._goals_against_per_90 = None
        self._shots_on_target_against = None
        self._saves = None
        self._save_percentage = None
        self._wins = None
        self._draws = None
        self._losses = None
        self._clean_sheets = None
        self._clean_sheet_percentage = None
        self._penalty_kicks_attempted = None
        self._penalty_kicks_allowed = None
        self._penalty_kicks_saved = None
        self._penalty_kicks_missed = None
        # Advanced goalkeeping stats
        self._free_kick_goals_against = None
        self._corner_kick_goals_against = None
        self._post_shot_expected_goals = None
        self._post_shot_expected_goals_per_shot = None
        self._post_shot_expected_goals_minus_allowed = None
        self._post_shot_expected_goals_minus_allowed_per_90 = None
        self._launches_completed = None
        self._launches_attempted = None
        self._launch_completion_percentage = None
        self._keeper_passes_attempted = None
        self._throws_attempted = None
        self._launch_percentage = None
        self._average_keeper_pass_length = None
        self._goal_kicks_attempted = None
        self._goal_kick_launch_percentage = None
        self._average_goal_kick_length = None
        self._opponent_cross_attempts = None
        self._opponent_cross_stops = None
        self._opponent_cross_stop_percentage = None
        self._keeper_actions_outside_penalty_area = None
        self._keeper_actions_outside_penalty_area_per_90 = None
        self._average_keeper_action_outside_penalty_distance = None
        # Shooting stats
        self._shots = None
        self._shots_on_target = None
        self._free_kick_shots = None
        self._shots_on_target_percentage = None
        self._shots_per_90 = None
        self._shots_on_target_per_90 = None
        self._goals_per_shot = None
        self._goals_per_shot_on_target = None
        self._expected_goals_non_penalty_per_shot = None
        self._goals_minus_expected = None
        self._non_penalty_minus_expected_non_penalty = None
        # Passing stats
        self._assists_minus_expected = None
        self._key_passes = None
        self._passes_completed = None
        self._passes_attempted = None
        self._pass_completion = None
        self._short_passes_completed = None
        self._short_passes_attempted = None
        self._short_pass_completion = None
        self._medium_passes_completed = None
        self._medium_passes_attempted = None
        self._medium_pass_completion = None
        self._long_passes_completed = None
        self._long_passes_attempted = None
        self._long_pass_completion = None
        self._left_foot_passes = None
        self._right_foot_passes = None
        self._free_kick_passes = None
        self._through_balls = None
        self._corner_kicks = None
        self._throw_ins = None
        self._final_third_passes = None
        self._penalty_area_passes = None
        self._penalty_area_crosses = None
        # Playing time stats
        self._minutes_per_match = None
        self._minutes_played_percentage = None
        self._nineties_played = None
        self._minutes_per_start = None
        self._subs = None
        self._minutes_per_sub = None
        self._unused_sub = None
        self._points_per_match = None
        self._goals_scored_on_pitch = None
        self._goals_against_on_pitch = None
        self._goal_difference_on_pitch = None
        self._goal_difference_on_pitch_per_90 = None
        self._net_difference_on_pitch_per_90 = None
        self._expected_goals_on_pitch = None
        self._expected_goals_against_on_pitch = None
        self._expected_goal_difference = None
        self._expected_goal_difference_per_90 = None
        self._net_expected_goal_difference_per_90 = None
        # Miscellaneous stats
        self._soft_reds = None
        self._fouls_committed = None
        self._fouls_drawn = None
        self._offsides = None
        self._crosses = None
        self._tackles_won = None
        self._interceptions = None
        self._penalty_kicks_won = None
        self._penalty_kicks_conceded = None
        self._successful_dribbles = None
        self._attempted_dribbles = None
        self._dribble_success_rate = None
        self._players_dribbled_past = None
        self._nutmegs = None
        self._dribblers_tackled = None
        self._dribblers_contested = None
        self._tackle_percentage = None
        self._times_dribbled_past = None

        self._parse_player_stats(player_data)

    def __str__(self):
        """
        Return the string representation of the class.
        """
        return f'{self.name} ({self.player_id})'

    def __repr__(self):
        """
        Return the string representation of the class.
        """
        return self.__str__()

    def _parse_nationality(self, player_data):
        """
        Parse the player's nationality.

        If the nationality is listed for a player, it will contain a URI which
        includes the name of the country the player represents. For example, an
        English player would have a URI of the following:
        "/en/country/ENG/England-Football". Pulling out the country name and
        returning it as a string is a simple solution to pulling someone's
        nationality.

        Parameters
        ----------
        player_data : PyQuery object
            A PyQuery object representing all of the player's stats fields
            combined as a singular row.

        Returns
        -------
        string
            Returns a ``string`` of the player's home country, such as
            'England'.
        """
        country = player_data(ROSTER_SCHEME['nationality'])
        if not country:
            return None
        country = country.attr('href')
        country = re.sub(r'.*\/', '', country)
        country = country.replace('-Football', '')
        return country

    def _parse_player_stats(self, player_data):
        """
        Parse a value for every attribute.

        This method looks through every class attribute with a few exceptions
        and retrieves the value according to the parsing scheme and index of
        the attribute from the passed HTML data. Once the value is retrieved,
        the attribute's value is updated with the returned result.

        Parameters
        ----------
        player_data : string
            A ``string`` representation of all of the player's stats fields
            combined as a singular row.
        player_id : string
            A ``string`` of the player's unique 8-digit ID.
        """
        for field in self.__dict__:
            # The short field truncates the leading '_' in the attribute name.
            short_field = str(field)[1:]
            if short_field == 'player_id':
                continue
            if short_field == 'nationality':
                value = self._parse_nationality(player_data)
            else:
                value = _parse_field(ROSTER_SCHEME, player_data, short_field)
            setattr(self, field, value)

    @property
    def dataframe(self):
        """
        Returns a pandas ``DataFame`` containing all other class properties
        and values. The index for the DataFrame is the player ID.
        """
        fields_to_include = {
            'name': self.name,
            'player_id': self.player_id,
            'nationality': self.nationality,
            'position': self.position,
            'age': self.age,
            'matches_played': self.matches_played,
            'starts': self.starts,
            'minutes': self.minutes,
            'goals': self.goals,
            'assists': self.assists,
            'penalty_kicks': self.penalty_kicks,
            'penalty_kick_attempts': self.penalty_kick_attempts,
            'yellow_cards': self.yellow_cards,
            'red_cards': self.red_cards,
            'goals_per_90': self.goals_per_90,
            'assists_per_90': self.assists_per_90,
            'goals_and_assists_per_90': self.goals_and_assists_per_90,
            'goals_non_penalty_per_90': self.goals_non_penalty_per_90,
            'goals_and_assists_non_penalty_per_90':
            self.goals_and_assists_non_penalty_per_90,
            'expected_goals': self.expected_goals,
            'expected_goals_non_penalty': self.expected_goals_non_penalty,
            'expected_assists': self.expected_assists,
            'expected_goals_per_90': self.expected_goals_per_90,
            'expected_assists_per_90': self.expected_assists_per_90,
            'expected_goals_and_assists_per_90':
            self.expected_goals_and_assists_per_90,
            'expected_goals_non_penalty_per_90':
            self.expected_goals_non_penalty_per_90,
            'expected_goals_and_assists_non_penalty_per_90':
            self.expected_goals_and_assists_non_penalty_per_90,
            'own_goals': self.own_goals,
            'goals_against': self.goals_against,
            'own_goals_against': self.own_goals_against,
            'goals_against_per_90': self.goals_against_per_90,
            'shots_on_target_against': self.shots_on_target_against,
            'saves': self.saves,
            'save_percentage': self.save_percentage,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
            'clean_sheets': self.clean_sheets,
            'clean_sheet_percentage': self.clean_sheet_percentage,
            'penalty_kicks_attempted': self.penalty_kicks_attempted,
            'penalty_kicks_allowed': self.penalty_kicks_allowed,
            'penalty_kicks_saved': self.penalty_kicks_saved,
            'penalty_kicks_missed': self.penalty_kicks_missed,
            'free_kick_goals_against': self.free_kick_goals_against,
            'corner_kick_goals_against': self.corner_kick_goals_against,
            'post_shot_expected_goals': self.post_shot_expected_goals,
            'post_shot_expected_goals_per_shot':
            self.post_shot_expected_goals_per_shot,
            'post_shot_expected_goals_minus_allowed':
            self.post_shot_expected_goals_minus_allowed,
            'launches_completed': self.launches_completed,
            'launches_attempted': self.launches_attempted,
            'launch_completion_percentage': self.launch_completion_percentage,
            'keeper_passes_attempted': self.keeper_passes_attempted,
            'throws_attempted': self.throws_attempted,
            'launch_percentage': self.launch_percentage,
            'average_keeper_pass_length': self.average_keeper_pass_length,
            'goal_kicks_attempted': self.goal_kicks_attempted,
            'goal_kick_launch_percentage': self.goal_kick_launch_percentage,
            'average_goal_kick_length': self.average_goal_kick_length,
            'opponent_cross_attempts': self.opponent_cross_attempts,
            'opponent_cross_stops': self.opponent_cross_stops,
            'opponent_cross_stop_percentage':
            self.opponent_cross_stop_percentage,
            'keeper_actions_outside_penalty_area':
            self.keeper_actions_outside_penalty_area,
            'keeper_actions_outside_penalty_area_per_90':
            self.keeper_actions_outside_penalty_area_per_90,
            'average_keeper_action_outside_penalty_distance':
            self.average_keeper_action_outside_penalty_distance,
            'shots': self.shots,
            'shots_on_target': self.shots_on_target,
            'free_kick_shots': self.free_kick_shots,
            'shots_on_target_percentage': self.shots_on_target_percentage,
            'shots_per_90': self.shots_per_90,
            'shots_on_target_per_90': self.shots_on_target_per_90,
            'goals_per_shot': self.goals_per_shot,
            'goals_per_shot_on_target': self.goals_per_shot_on_target,
            'expected_goals_non_penalty_per_shot':
            self.expected_goals_non_penalty_per_shot,
            'goals_minus_expected': self.goals_minus_expected,
            'non_penalty_minus_expected_non_penalty':
            self.non_penalty_minus_expected_non_penalty,
            'assists_minus_expected': self.assists_minus_expected,
            'key_passes': self.key_passes,
            'passes_completed': self.passes_completed,
            'passes_attempted': self.passes_attempted,
            'pass_completion': self.pass_completion,
            'short_passes_completed': self.short_passes_completed,
            'short_passes_attempted': self.short_passes_attempted,
            'short_pass_completion': self.short_pass_completion,
            'medium_passes_completed': self.medium_passes_completed,
            'medium_passes_attempted': self.medium_passes_attempted,
            'medium_pass_completion': self.medium_pass_completion,
            'long_passes_completed': self.long_passes_completed,
            'long_passes_attempted': self.long_passes_attempted,
            'long_pass_completion': self.long_pass_completion,
            'left_foot_passes': self.left_foot_passes,
            'right_foot_passes': self.right_foot_passes,
            'free_kick_passes': self.free_kick_passes,
            'through_balls': self.through_balls,
            'corner_kicks': self.corner_kicks,
            'throw_ins': self.throw_ins,
            'final_third_passes': self.final_third_passes,
            'penalty_area_passes': self.penalty_area_passes,
            'penalty_area_crosses': self.penalty_area_crosses,
            'minutes_per_match': self.minutes_per_match,
            'minutes_played_percentage': self.minutes_played_percentage,
            'nineties_played': self.nineties_played,
            'minutes_per_start': self.minutes_per_start,
            'subs': self.subs,
            'minutes_per_sub': self.minutes_per_sub,
            'unused_sub': self.unused_sub,
            'points_per_match': self.points_per_match,
            'goals_scored_on_pitch': self.goals_scored_on_pitch,
            'goals_against_on_pitch': self.goals_against_on_pitch,
            'goal_difference_on_pitch': self.goal_difference_on_pitch,
            'goal_difference_on_pitch_per_90':
            self.goal_difference_on_pitch_per_90,
            'net_difference_on_pitch_per_90':
            self.net_difference_on_pitch_per_90,
            'expected_goals_on_pitch': self.expected_goals_on_pitch,
            'expected_goals_against_on_pitch':
            self.expected_goals_against_on_pitch,
            'expected_goal_difference': self.expected_goal_difference,
            'expected_goal_difference_per_90':
            self.expected_goal_difference_per_90,
            'net_expected_goal_difference_per_90':
            self.net_expected_goal_difference_per_90,
            'soft_reds': self.soft_reds,
            'fouls_committed': self.fouls_committed,
            'fouls_drawn': self.fouls_drawn,
            'offsides': self.offsides,
            'crosses': self.crosses,
            'tackles_won': self.tackles_won,
            'interceptions': self.interceptions,
            'penalty_kicks_won': self.penalty_kicks_won,
            'penalty_kicks_conceded': self.penalty_kicks_conceded,
            'successful_dribbles': self.successful_dribbles,
            'attempted_dribbles': self.attempted_dribbles,
            'dribble_success_rate': self.dribble_success_rate,
            'players_dribbled_past': self.players_dribbled_past,
            'nutmegs': self.nutmegs,
            'dribblers_tackled': self.dribblers_tackled,
            'dribblers_contested': self.dribblers_contested,
            'tackle_percentage': self.tackle_percentage,
            'times_dribbled_past': self.times_dribbled_past
        }
        return pd.DataFrame([fields_to_include], index=[self.player_id])

    @property
    def name(self):
        """
        Returns a ``string`` of the player's full name, such as 'Harry Kane'.
        """
        return self._name

    @property
    def player_id(self):
        """
        Returns a ``string`` of the player's 8-digit ID, such as '21a66f6a' for
        Harry Kane.
        """
        return self._player_id

    @property
    def nationality(self):
        """
        Returns a ``string`` of the player's home country, such as 'England'.
        """
        return self._nationality

    @property
    def position(self):
        """
        Returns a ``string`` of the player's primary position(s). Multiple
        positions are separated by commas.
        """
        return self._position

    @int_property_decorator
    def age(self):
        """
        Returns an ``int`` of the player's age as of August 1 for winter
        leagues and February 1 for summer leagues for the given season.
        """
        return self._age

    @int_property_decorator
    def matches_played(self):
        """
        Returns an ``int`` of the number of matches the player has participated
        in.
        """
        return self._matches_played

    @int_property_decorator
    def starts(self):
        """
        Returns an ``int`` of the number of games the player has started.
        """
        return self._starts

    @int_property_decorator
    def minutes(self):
        """
        Returns an ``int`` of the number of minutes the player has spent on the
        field in all competitions.
        """
        return self._minutes.replace(',', '')

    @int_property_decorator
    def goals(self):
        """
        Returns an ``int`` of the number of goals the player has scored.
        """
        return self._goals

    @int_property_decorator
    def assists(self):
        """
        Returns an ``int`` of the number of goals the player has assisted.
        """
        return self._assists

    @int_property_decorator
    def penalty_kicks(self):
        """
        Returns an ``int`` of the number of penalty kicks the player has scored
        during regular play.
        """
        return self._penalty_kicks

    @int_property_decorator
    def penalty_kick_attempts(self):
        """
        Returns an ``int`` of the number of penalty kicks the player has
        attempted.
        """
        return self._penalty_kick_attempts

    @int_property_decorator
    def yellow_cards(self):
        """
        Returns an ``int`` of the number of yellow cards the player has
        accumulated during the season.
        """
        return self._yellow_cards

    @int_property_decorator
    def red_cards(self):
        """
        Returns an ``int`` of the number of red cards the player has
        accumulated during the season.
        """
        return self._red_cards

    @float_property_decorator
    def goals_per_90(self):
        """
        Returns a ``float`` of the number of goals the player has scored per
        90 minutes on the field.
        """
        return self._goals_per_90

    @float_property_decorator
    def assists_per_90(self):
        """
        Returns a ``float`` of the number of goals the player has assisted per
        90 minutes on the field.
        """
        return self._assists_per_90

    @float_property_decorator
    def goals_and_assists_per_90(self):
        """
        Returns a ``float`` of the number of goals the player has either scored
        or assisted per 90 minutes on the field.
        """
        return self._goals_and_assists_per_90

    @float_property_decorator
    def goals_non_penalty_per_90(self):
        """
        Returns a ``float`` of the number of non-penalty goals the player has
        scored per 90 minutes on the field.
        """
        return self._goals_non_penalty_per_90

    @float_property_decorator
    def goals_and_assists_non_penalty_per_90(self):
        """
        Returns a ``float`` of the number of non-penalty goals the player has
        either scored or assisted per 90 minutes on the field.
        """
        return self._goals_and_assists_non_penalty_per_90

    @float_property_decorator
    def expected_goals(self):
        """
        Returns a ``float`` of the number of goals the player was expected to
        score based on the quality and quantity of shots taken.
        """
        return self._expected_goals

    @float_property_decorator
    def expected_goals_non_penalty(self):
        """
        Returns a ``float`` of the number of non-penalty goals the player was
        expected to score based on the quality and quantity of shots taken.
        """
        return self._expected_goals_non_penalty

    @float_property_decorator
    def expected_assists(self):
        """
        Returns a ``float`` of the number of goals the player was expected go
        assist based on the quality and quantity of teammate shots taken.
        """
        return self._expected_assists

    @float_property_decorator
    def expected_goals_per_90(self):
        """
        Returns a ``float`` of the player's expected goals per 90 minutes
        played.
        """
        return self._expected_goals_per_90

    @float_property_decorator
    def expected_assists_per_90(self):
        """
        Returns a ``float`` of the player's expected assists per 90 minutes
        played.
        """
        return self._expected_assists_per_90

    @float_property_decorator
    def expected_goals_and_assists_per_90(self):
        """
        Returns a ``float`` of the player's expected goals and assists per 90
        minutes played.
        """
        return self._expected_goals_and_assists_per_90

    @float_property_decorator
    def expected_goals_non_penalty_per_90(self):
        """
        Returns a ``float`` of the player's expected non-penalty goals per 90
        minutes played.
        """
        return self._expected_goals_non_penalty_per_90

    @float_property_decorator
    def expected_goals_and_assists_non_penalty_per_90(self):
        """
        Returns a ``float`` of the player's expected non-penalty goals and
        assists per 90 minutes played.
        """
        return self._expected_goals_and_assists_non_penalty_per_90

    @int_property_decorator
    def own_goals(self):
        """
        Returns an ``int`` of the number of own goals the player has conceded.
        """
        return self._own_goals

    @int_property_decorator
    def goals_against(self):
        """
        Returns an ``int`` of the number of goals a keeper has conceded.
        """
        return self._goals_against

    @int_property_decorator
    def own_goals_against(self):
        """
        Returns an ``int`` of the number of own goals the team scored on a
        keeper.
        """
        return self._own_goals_against

    @float_property_decorator
    def goals_against_per_90(self):
        """
        Returns a ``float`` of the number of goals a keeper has coneceded per
        90 minutes played.
        """
        return self._goals_against_per_90

    @int_property_decorator
    def shots_on_target_against(self):
        """
        Returns an ``int`` of the number of shots on target a keeper has faced.
        """
        return self._shots_on_target_against

    @int_property_decorator
    def saves(self):
        """
        Returns an ``int`` of the number of shots a keeper has saved.
        """
        return self._saves

    @float_property_decorator
    def save_percentage(self):
        """
        Returns a ``float`` of the percentage of shots the keeper saved.
        Percentage ranges from 0-1.
        """
        return self._save_percentage

    @int_property_decorator
    def wins(self):
        """
        Returns an ``int`` of the number of games a keeper has won.
        """
        return self._wins

    @int_property_decorator
    def draws(self):
        """
        Returns an ``int`` of the number of games a keeper has drawn.
        """
        return self._draws

    @int_property_decorator
    def losses(self):
        """
        Returns an ``int`` of the number of games a keeper has lost.
        """
        return self._losses

    @int_property_decorator
    def clean_sheets(self):
        """
        Returns an ``int`` of the number of clean sheets a keeper has
        registered.
        """
        return self._clean_sheets

    @float_property_decorator
    def clean_sheet_percentage(self):
        """
        Returns a ``float`` of the percentage of games a keeper has
        participated in that resulted in a clean sheet.
        """
        return self._clean_sheet_percentage

    @int_property_decorator
    def penalty_kicks_attempted(self):
        """
        Returns an ``int`` of the number of penalty kicks a keeper has faced
        during regular play.
        """
        return self._penalty_kicks_attempted

    @int_property_decorator
    def penalty_kicks_allowed(self):
        """
        Returns an ``int`` of the number of penalty kicks a keeper has conceded
        during regular play.
        """
        return self._penalty_kicks_allowed

    @int_property_decorator
    def penalty_kicks_saved(self):
        """
        Returns an ``int`` of the number of penalty kicks a keeper has saved
        during regular play.
        """
        return self._penalty_kicks_saved

    @int_property_decorator
    def penalty_kicks_missed(self):
        """
        Returns an ``int`` of the number of penalty kicks a keeper has faced
        where the opponent missed the goal.
        """
        return self._penalty_kicks_missed

    @int_property_decorator
    def free_kick_goals_against(self):
        """
        Returns an ``int`` of the number of goals a keeper conceded as a result
        of an opponent's free kick.
        """
        return self._free_kick_goals_against

    @int_property_decorator
    def corner_kick_goals_against(self):
        """
        Returns an ``int`` of the number of goals a keeper conceded as a result
        of an opponent's corner kick.
        """
        return self._corner_kick_goals_against

    @float_property_decorator
    def post_shot_expected_goals(self):
        """
        Returns a ``float`` of the number of goals a keeper was expected to
        concede.
        """
        return self._post_shot_expected_goals

    @float_property_decorator
    def post_shot_expected_goals_per_shot(self):
        """
        Returns a ``float`` of the number of goals a keeper was expected to
        concede per shot faced.
        """
        return self._post_shot_expected_goals_per_shot

    @float_property_decorator
    def post_shot_expected_goals_minus_allowed(self):
        """
        Returns a ``float`` of the number of goals a keeper was expected to
        concede minus the number of goals they actually conceded.
        """
        return self._post_shot_expected_goals_minus_allowed

    @float_property_decorator
    def post_shot_expected_goals_minus_allowed_per_90(self):
        """
        Returns a ``float`` of the number of goals a keeper was expected to
        concede minus the number of goals they actually conceded, per 90
        minutes played.
        """
        return self._post_shot_expected_goals_minus_allowed_per_90

    @int_property_decorator
    def launches_completed(self):
        """
        Returns an ``int`` of the number of passes longer than 40 yards a
        keeper completed.
        """
        return self._launches_completed

    @int_property_decorator
    def launches_attempted(self):
        """
        Returns an ``int`` of the number of passes longer than 40 yards a
        keeper attempted.
        """
        return self._launches_attempted

    @float_property_decorator
    def launch_completion_percentage(self):
        """
        Returns a ``float`` of the percentage of passes longer than 40 yards a
        keeper completed. Percentage ranges from 0-100.
        """
        return self._launch_completion_percentage

    @int_property_decorator
    def keeper_passes_attempted(self):
        """
        Returns an ``int`` of the number of non-goal kick passes a keeper
        attempted.
        """
        return self._keeper_passes_attempted

    @int_property_decorator
    def throws_attempted(self):
        """
        Returns an ``int`` of the number of throws a keeper attempted.
        """
        return self._throws_attempted

    @float_property_decorator
    def launch_percentage(self):
        """
        Returns a ``float`` of the percentage of passes a keeper makes longer
        than 40 yards excluding goal kicks. Percentage ranges from 0-100.
        """
        return self._launch_percentage

    @float_property_decorator
    def average_keeper_pass_length(self):
        """
        Returns a ``float`` of the average pass length for a keeper in yards
        excluding goal kicks.
        """
        return self._average_keeper_pass_length

    @int_property_decorator
    def goal_kicks_attempted(self):
        """
        Returns an ``int`` of the number of goal kicks a keeper attempted.
        """
        return self._goal_kicks_attempted

    @float_property_decorator
    def goal_kick_launch_percentage(self):
        """
        Returns a ``float`` of the percentage of goal kicks a keeper has
        launched further than 40 yards. Percentage ranges from 0-100.
        """
        return self._goal_kick_launch_percentage

    @float_property_decorator
    def average_goal_kick_length(self):
        """
        Returns a ``float`` of the average pass length for goal kicks in yards
        for a keeper.
        """
        return self._average_goal_kick_length

    @int_property_decorator
    def opponent_cross_attempts(self):
        """
        Returns an ``int`` of the number of crosses a keeper has faced.
        """
        return self._opponent_cross_attempts

    @int_property_decorator
    def opponent_cross_stops(self):
        """
        Returns an ``int`` of the number of crosses a keeper has successfully
        stopped.
        """
        return self._opponent_cross_stops

    @float_property_decorator
    def opponent_cross_stop_percentage(self):
        """
        Returns a ``float`` of the percentage of crosses the keeper has
        successfully stopped. Percentage ranges from 0-100.
        """
        return self._opponent_cross_stop_percentage

    @int_property_decorator
    def keeper_actions_outside_penalty_area(self):
        """
        Returns an ``int`` of the number of defensive actions a keeper made
        outside the penalty area.
        """
        return self._keeper_actions_outside_penalty_area

    @float_property_decorator
    def keeper_actions_outside_penalty_area_per_90(self):
        """
        Returns a ``float`` of the number of defensive actions a keeper made
        outside the penalty area per 90 minutes played.
        """
        return self._keeper_actions_outside_penalty_area_per_90

    @float_property_decorator
    def average_keeper_action_outside_penalty_distance(self):
        """
        Returns a ``float`` of the average distance from goal in yards a keeper
        performed a defensive action outside the penalty area.
        """
        return self._average_keeper_action_outside_penalty_distance

    @int_property_decorator
    def shots(self):
        """
        Returns an ``int`` of the number of shots the player has taken.
        """
        return self._shots

    @int_property_decorator
    def shots_on_target(self):
        """
        Returns an ``int`` of the number of shots on target the player has
        taken.
        """
        return self._shots_on_target

    @int_property_decorator
    def free_kick_shots(self):
        """
        Returns an ``int`` of the number of shots the player has taken from
        free kicks.
        """
        return self._free_kick_shots

    @float_property_decorator
    def shots_on_target_percentage(self):
        """
        Returns a ``float`` of the percentage of shots taken by the player that
        were on target. Percentage ranges from 0-100.
        """
        return self._shots_on_target_percentage

    @float_property_decorator
    def shots_per_90(self):
        """
        Returns a ``float`` of the number of shots the player has taken per 90
        minutes played.
        """
        return self._shots_per_90

    @float_property_decorator
    def shots_on_target_per_90(self):
        """
        Returns a ``float`` of the number of shots on target the player has
        taken per 90 minutes played.
        """
        return self._shots_on_target_per_90

    @float_property_decorator
    def goals_per_shot(self):
        """
        Returns a ``float`` of the average number of goals scored per shot
        taken by the player.
        """
        return self._goals_per_shot

    @float_property_decorator
    def goals_per_shot_on_target(self):
        """
        Returns a ``float`` of the average number of goals scored per shot on
        target by the player.
        """
        return self._goals_per_shot_on_target

    @float_property_decorator
    def expected_goals_non_penalty_per_shot(self):
        """
        Returns a ``float`` of the nuber of non-penalty goals the player was
        expected to score per shot.
        """
        return self._expected_goals_non_penalty_per_shot

    @float_property_decorator
    def goals_minus_expected(self):
        """
        Returns a ``float`` of the number of goals scored minus the number of
        goals the player was expected to score.
        """
        return self._goals_minus_expected

    @float_property_decorator
    def non_penalty_minus_expected_non_penalty(self):
        """
        Returns a ``float`` of the number of non-penalty goals scored minus the
        number of non-penalty goals the player was expected to score.
        """
        return self._non_penalty_minus_expected_non_penalty

    @float_property_decorator
    def assists_minus_expected(self):
        """
        Returns a ``float`` of the number of assists the player registered
        minus the actual number of assists the player tallied.
        """
        return self._assists_minus_expected

    @int_property_decorator
    def key_passes(self):
        """
        Returns an ``int`` of the number of passes the player made that
        directly lead to a shot.
        """
        return self._key_passes

    @int_property_decorator
    def passes_completed(self):
        """
        Returns an ``int`` of the total number of passes the player has
        completed.
        """
        return self._passes_completed

    @int_property_decorator
    def passes_attempted(self):
        """
        Returns an ``int`` of the total number of passes the player has
        attempted.
        """
        return self._passes_attempted

    @float_property_decorator
    def pass_completion(self):
        """
        Returns a ``float`` of the player's overall pass completion rating.
        Percentage ranges from 0-100.
        """
        return self._pass_completion

    @int_property_decorator
    def short_passes_completed(self):
        """
        Returns an ``int`` of the total number of passes under 5 yards the
        player has completed.
        """
        return self._short_passes_completed

    @int_property_decorator
    def short_passes_attempted(self):
        """
        Returns an ``int`` of the total number of passes under 5 yards the
        player has attempted.
        """
        return self._short_passes_attempted

    @float_property_decorator
    def short_pass_completion(self):
        """
        Returns a ``float`` of the player's overall pass completion rating for
        passes under 5 yards. Percentage ranges from 0-100.
        """
        return self._short_pass_completion

    @int_property_decorator
    def medium_passes_completed(self):
        """
        Returns an ``int`` of the total number of passes between 5 and 25 yards
        the player has completed.
        """
        return self._medium_passes_completed

    @int_property_decorator
    def medium_passes_attempted(self):
        """
        Returns an ``int`` of the total number of passes between 5 and 25 yards
        the player has attempted.
        """
        return self._medium_passes_attempted

    @float_property_decorator
    def medium_pass_completion(self):
        """
        Returns a ``float`` of the player's overall pass completion rating for
        passes between 5 and 25 yards. Percentage ranges from 0-100.
        """
        return self._medium_pass_completion

    @int_property_decorator
    def long_passes_completed(self):
        """
        Returns an ``int`` of the total number of passes greater than 25 yards
        the player has completed.
        """
        return self._long_passes_completed

    @int_property_decorator
    def long_passes_attempted(self):
        """
        Returns an ``int`` of the total number of passes greater than 25 yards
        the player has attempted.
        """
        return self._long_passes_attempted

    @float_property_decorator
    def long_pass_completion(self):
        """
        Returns a ``float`` of the player's overall pass completion rating for
        passes greater than 25 yards. Percentage ranges from 0-100.
        """
        return self._long_pass_completion

    @int_property_decorator
    def left_foot_passes(self):
        """
        Returns an ``int`` of the number of passes the player made with their
        left foot.
        """
        return self._left_foot_passes

    @int_property_decorator
    def right_foot_passes(self):
        """
        Returns an ``int`` of the number of passes the player made with their
        right foot.
        """
        return self._right_foot_passes

    @int_property_decorator
    def free_kick_passes(self):
        """
        Returns an ``int`` of the number of passes the player made from a free
        kick.
        """
        return self._free_kick_passes

    @int_property_decorator
    def through_balls(self):
        """
        Returns an ``int`` of the number of passes the player made between the
        last line of defenders into open space.
        """
        return self._through_balls

    @int_property_decorator
    def corner_kicks(self):
        """
        Returns an ``int`` of the number of corner kicks the player has taken.
        """
        return self._corner_kicks

    @int_property_decorator
    def throw_ins(self):
        """
        Returns an ``int`` of the number of throw-ins the player took.
        """
        return self._throw_ins

    @int_property_decorator
    def final_third_passes(self):
        """
        Returns an ``int`` of the number of passes the player made into the
        final third.
        """
        return self._final_third_passes

    @int_property_decorator
    def penalty_area_passes(self):
        """
        Returns an ``int`` of the number of passes the player made into the
        opposing penalty area.
        """
        return self._penalty_area_passes

    @int_property_decorator
    def penalty_area_crosses(self):
        """
        Returns an ``int`` of the number of non-set piece crosses the player
        made into the penalty area.
        """
        return self._penalty_area_crosses

    @int_property_decorator
    def minutes_per_match(self):
        """
        Returns an ``int`` of the average number of minutes the player played
        per match.
        """
        return self._minutes_per_match

    @float_property_decorator
    def minutes_played_percentage(self):
        """
        Returns a ``float`` of the percentage of time the player has been on
        the field for all games the team participated in. Percentage ranges
        from 0-100.
        """
        return self._minutes_played_percentage

    @float_property_decorator
    def nineties_played(self):
        """
        Returns a ``float`` of number of the number of minutes the player has
        played divided by 90.
        """
        return self._nineties_played

    @int_property_decorator
    def minutes_per_start(self):
        """
        Returns an ``int`` of the number of minutes the player plays on average
        per game started.
        """
        return self._minutes_per_start

    @int_property_decorator
    def subs(self):
        """
        Returns an ``int`` of the number of times the player has come on as a
        sub.
        """
        return self._subs

    @int_property_decorator
    def minutes_per_sub(self):
        """
        Returns an ``int`` of the average number of minutes the player has
        played per game after coming in as a sub.
        """
        return self._minutes_per_sub

    @int_property_decorator
    def unused_sub(self):
        """
        Returns an ``int`` of the number of times the player was an unused sub
        and spent the entirety of the game on the bench.
        """
        return self._unused_sub

    @float_property_decorator
    def points_per_match(self):
        """
        Returns a ``float`` of the average number of points the team has gained
        per game in which the player participated.
        """
        return self._points_per_match

    @int_property_decorator
    def goals_scored_on_pitch(self):
        """
        Returns an ``int`` of the number of goals the team has scored while the
        player was on the field.
        """
        return self._goals_scored_on_pitch

    @int_property_decorator
    def goals_against_on_pitch(self):
        """
        Returns an ``int`` of the number of goals the team has conceded while
        the player was on the field.
        """
        return self._goals_against_on_pitch

    @int_property_decorator
    def goal_difference_on_pitch(self):
        """
        Returns an ``int`` of the team's goal difference while the player is on
        the field.
        """
        return self._goal_difference_on_pitch

    @float_property_decorator
    def goal_difference_on_pitch_per_90(self):
        """
        Returns a ``float`` of the team's average goal difference while the
        player is on the field, per 90 minutes played.
        """
        return self._goal_difference_on_pitch_per_90

    @float_property_decorator
    def net_difference_on_pitch_per_90(self):
        """
        Returns a ``float`` of the team's goal difference while the player is
        on the pitch minus the team's goal difference while the player is off
        the pitch, per 90 minutes.
        """
        return self._net_difference_on_pitch_per_90

    @float_property_decorator
    def expected_goals_on_pitch(self):
        """
        Returns a ``float`` of the number of goals the team was expected to
        score while the player was on the pitch.
        """
        return self._expected_goals_on_pitch

    @float_property_decorator
    def expected_goals_against_on_pitch(self):
        """
        Returns a ``float`` of the number of goals the team was expected to
        concede while the player was on the pitch.
        """
        return self._expected_goals_against_on_pitch

    @float_property_decorator
    def expected_goal_difference(self):
        """
        Returns a ``float`` of the difference between expected team goals
        scored and conceded while the player was on the pitch.
        """
        return self._expected_goal_difference

    @float_property_decorator
    def expected_goal_difference_per_90(self):
        """
        Returns a ``float`` of the difference between expected team goals
        scored and conceded while the player was on the pitch, per 90 minutes.
        """
        return self._expected_goal_difference_per_90

    @float_property_decorator
    def net_expected_goal_difference_per_90(self):
        """
        Returns a ``float`` of the team's expected goal difference while the
        player is on the pitch minus the team's exepcted goal difference while
        the player is off the pitch, per 90 minutes.
        """
        return self._net_expected_goal_difference_per_90

    @int_property_decorator
    def soft_reds(self):
        """
        Returns an ``int`` of the number of games where the player received two
        yellow cards, resulting in a red, or a "soft red".
        """
        return self._soft_reds

    @int_property_decorator
    def fouls_committed(self):
        """
        Returns an ``int`` of the number of fouls the player has committed.
        """
        return self._fouls_committed

    @int_property_decorator
    def fouls_drawn(self):
        """
        Returns an ``int`` of the number of fouls the player has been the
        victim of.
        """
        return self._fouls_drawn

    @int_property_decorator
    def offsides(self):
        """
        Returns an ``int`` of the number of times the player has been called
        offside.
        """
        return self._offsides

    @int_property_decorator
    def crosses(self):
        """
        Returns an ``int`` of the number of times the player has crossed the
        ball.
        """
        return self._crosses

    @int_property_decorator
    def tackles_won(self):
        """
        Returns an ``int`` of the number of tackles the player has won.
        """
        return self._tackles_won

    @int_property_decorator
    def interceptions(self):
        """
        Returns an ``int`` of the number of times the player has intercepted
        the ball.
        """
        return self._interceptions

    @int_property_decorator
    def penalty_kicks_won(self):
        """
        Returns an ``int`` of the number of times the player has won a penalty
        kick for the team.
        """
        return self._penalty_kicks_won

    @int_property_decorator
    def penalty_kicks_conceded(self):
        """
        Returns an ``int`` of the number of times the player has conceded a
        penalty kick to the opposition.
        """
        return self._penalty_kicks_conceded

    @int_property_decorator
    def successful_dribbles(self):
        """
        Returns an ``int`` of the number of dribbles the player has completed
        successfully.
        """
        return self._successful_dribbles

    @int_property_decorator
    def attempted_dribbles(self):
        """
        Returns an ``int`` of the number of times the player has attempted a
        dribble.
        """
        return self._attempted_dribbles

    @float_property_decorator
    def dribble_success_rate(self):
        """
        Returns a ``float`` of the percentage of attempted dribbles the player
        has successfully completed. Percentage ranges from 0-100.
        """
        return self._dribble_success_rate

    @int_property_decorator
    def players_dribbled_past(self):
        """
        Returns an ``int`` of the number of opponents the player dribbled past.
        """
        return self._players_dribbled_past

    @int_property_decorator
    def nutmegs(self):
        """
        Returns an ``int`` of the number of opponents the player has nutmegged.
        """
        return self._nutmegs

    @int_property_decorator
    def dribblers_tackled(self):
        """
        Returns an ``int`` of the number of opponents who were attempting a
        dribble that the player tackled.
        """
        return self._dribblers_tackled

    @int_property_decorator
    def dribblers_contested(self):
        """
        Returns an ``int`` of the number of opponents who were attempting a
        dribble that the player contested.
        """
        return self._dribblers_contested

    @float_property_decorator
    def tackle_percentage(self):
        """
        Returns a ``float`` of the percentage of opposing dribblers the player
        has successfully tackled. Percentage ranges from 0-100.
        """
        return self._tackle_percentage

    @int_property_decorator
    def times_dribbled_past(self):
        """
        Returns an ``int`` of the number of times the player has been dribbled
        past.
        """
        return self._times_dribbled_past


class Roster:
    """
    Get stats for all players on a roster.

    Request a team's roster for a given season and create instances of the
    Player class for each player, containing a detailed list of the player's
    statistics and information for the season.

    Parameters
    ----------
    squad_id : string
        The team's 8-digit squad ID or the team's name, such as '361ca564' or
        'Tottenham Hotspur'.
    doc : PyQuery object (optional)
        If passed to the class instantiation, this will be used to pull all
        information instead of making another request to the website. If the
        document is not provided, it will be pulled during a later step.
    """
    def __init__(self, squad_id, doc=None):
        self._players = []

        self._squad_id = _lookup_team(squad_id)
        player_data_dict = self._pull_stats(doc)
        if not player_data_dict:
            return None
        self._instantiate_players(player_data_dict)

    def __call__(self, player):
        """
        Return a specified player on the roster.

        Returns a specific player as requested by the passed name or player ID.
        The input string must either match a player's 8-digit unique ID or the
        named listed on fbref.com for the player.

        Parameters
        ----------
        player : string
            A ``string`` of either the player's 8-digit unique ID or the name
            listed on fbref.com for the player.

        Returns
        -------
        Player instance
            If the requested player can be found, their Player instance is
            returned.

        Raises
        ------
        ValueError
            If the requested player cannot be matched with a player in the
            squad.
        """
        for player_instance in self._players:
            if not player_instance.name or not player_instance.player_id:
                continue  # pragma: no cover
            if player.lower() == player_instance.player_id.lower():
                return player_instance
            if player.lower().strip() == player_instance.name.lower().strip():
                return player_instance
        raise ValueError('No player found with the requested name or ID')

    def __str__(self):
        """
        Return the string representation of the class.
        """
        players = [f'{x.name} ({x.player_id})'.strip() for x in self._players]
        return '\n'.join(players)

    def __repr__(self):
        """
        Return the string representation of the class.
        """
        return self.__str__()

    def __iter__(self):
        """
        Returns an iterator of all of the players on the given team's roster.
        """
        return iter(self._players)

    def __len__(self):
        """
        Returns the number of player on the given team's roster.
        """
        return len(self._players)

    def _player_id(self, player_data):
        """
        Parse the player's ID from a row.

        The player ID is embedded within the header column of each individual
        player's row within a stats table. The specific ID is in a URL and can
        be easily parsed and returned.

        Parameters
        ----------
        player_data : PyQuery object
            A PyQuery object representing a single row in a stats table for a
            player.

        Returns
        -------
        string
            Returns a ``string`` of the player's unique 8-digit player ID.
        """
        player = player_data('th[data-stat="player"]')
        player_id = player('a').attr('href')
        try:
            player_id = re.sub(r'.*\/players\/', '', player_id)
            player_id = re.sub(r'\/.*', '', player_id)
        except TypeError:
            player_id = None
        return player_id

    def _add_stats_data(self, stats_table, player_data_dict):
        """
        Add each player's stats rows to a dictionary.

        Given the player stats are spread throughout many tables, they should
        be combined by player for a single reference for each player for easier
        lookups.

        Parameters
        ----------
        stats_table : generator
            A generator of all row items in a given table.
        player_data_dict : {str: {'data': str}} dictionary
            A dictionary where every key is the player's ID and every value is
            another dictionary with a 'data' key which contains the string
            version of the row data for the matched player.

        Returns
        -------
        dictionary
            An updated version of the player_data_dict with the passed table
            row information included.
        """
        for player_data in stats_table:
            if 'class="thead"' in str(player_data):
                continue  # pragma: no cover
            player_id = self._player_id(player_data)
            if not player_id:
                continue
            try:
                player_data_dict[player_id]['data'] += player_data
            except KeyError:
                player_data_dict[player_id] = {'data': player_data}
        return player_data_dict

    def _pull_stats(self, doc):
        """
        Download the team page and pull all stats.

        Download the requested team's season page and pull all of the relevant
        stats tables for later parsing.

        Parameters
        ----------
        doc : PyQuery object
            If passed to the class instantiation, this will be used to pull all
            information instead of making another request to the website. If
            the document is not provided, this value will be None.

        Returns
        -------
        dictionary
            Returns a ``dictionary`` where every key is the player's ID and
            every value is another dictionary with a 'data' key which contains
            the string version of the row data for the matched player.
        """
        if not doc:
            try:
                doc = pq(SQUAD_URL % self._squad_id)
                doc = pq(_remove_html_comment_tags(doc))
            except HTTPError:
                return None
        stats_table = []
        player_data_dict = {}

        # Some leagues have a special ID for the tables. First lookup that ID
        # if it exists, but if not, use 'ks_combined' as the default.
        postfix = LEAGUE_IDS.get(self._squad_id, 'ks_combined')

        for table_id in ['table#stats_standard_',
                         'table#stats_keeper_',
                         'table#stats_keeper_adv_',
                         'table#stats_shooting_',
                         'table#stats_passing_',
                         'table#stats_playing_time_',
                         'table#stats_misc_']:
            table = _get_stats_table(doc, table_id + 'ks_combined')
            if not table:
                table = _get_stats_table(doc, table_id + postfix)
                if not table:
                    continue
            player_data_dict = self._add_stats_data(table, player_data_dict)
        return player_data_dict

    def _instantiate_players(self, player_data_dict):
        """
        Create Player instances for each squad member.

        Given the stats information for all players, an instance of the Player
        class should be created and appended to the overall list of players for
        easy future reference.

        Parameters
        ----------
        player_data_dict : {str: {'data': str}} dictionary
            A dictionary where every key is the player's ID and every value is
            another dictionary with a 'data' key which contains the string
            version of the row data for the matched player.
        """
        for player_id, player_data in player_data_dict.items():
            player = SquadPlayer(player_data['data'], player_id)
            self._players.append(player)
