from difflib import get_close_matches
from .squad_ids import SQUAD_IDS


def _parse_squad_name(team_id):
    """
    Parse and clean the team's name.

    To try and match requested team names with the master squad ID list, passed
    names should be parsed to remove the common 'FC' and 'CF' tags, as well as
    force all strings to be lowercase and excess whitespace removed.

    Parameters
    ----------
    team_id : string
        The requested team's name to be parsed.

    Returns
    -------
    string
        Returns a ``string`` of the parsed team's name.
    """
    irrelevant = [' FC', ' CF', 'FC ', 'CF ']
    for val in irrelevant:
        team_id = team_id.replace(val, '')
    name = team_id.lower().strip()
    return name


def lookup_squad_id(name, quiet=False):
    """
    Attempt to match a team name with a squad ID.

    A simple utility to make it easier to find squad IDs given a team name.
    By supplying a team name, this function will return the squad ID if a
    match can be found, or return a dictionary of the top 5 closest teams if a
    match cannot be made. For example, specifying 'Tottenham Hotspur' will
    return Tottenham's squad ID of '361ca564'. However, specifying 'Tottenham'
    doesn't technically match an official team name, and the closest matches
    will be returned instead, with Tottenham Hotspur being the first result.

    Due to the massive number of teams listed on fbref.com, the incorrect team
    could be accidently pulled by what appears to be the proper name. For
    example, 'Barcelona' is the name of one of the largest clubs in the world,
    located in Barcelona, Spain. However, 'Barcelona' could also refer to
    Barcelona Sporting Club (commonly referred to as just 'Barcelona' locally)
    who competes in the Ecuadorian Serie A. By using the squad ID, the intended
    team is guaranteed to be used.

    This helper function does not rely on case for the words, so 'Tottenham
    Hotspur' will return the same result as 'tottenham hotspur'. Also, common
    tags such as 'FC' and 'CF' are removed, so there is no need to specify
    those components.

    In the case a match can't be made, a dictionary of suggestions will be
    returned instead of the squad ID. The dictionary is intended to be used
    to find the best alternatives for later use. The keys are the suggested
    names and values are the squad IDs. This allows direct usage of a squad ID
    in subsequent calls to various classes in the Football module in
    sportsipy instead of attempting to lookup a name. As there can be
    multiple return types, it is recommended to check the type of the returned
    value before further calculations. If the return is of type ``string``, it
    is the 8-digit squad ID. If it is of type ``dictionary``, it is a key-value
    object containing suggestions.

    Parameters
    ----------
    name : string
        A ``string`` of the name of a squad to lookup, such as 'Tottenham
        Hotspur'.
    quiet : boolean
        A ``boolean`` value which suppresses text output while True.

    Returns
    -------
    string or dictionary
        Returns a ``string`` of the squad's 8-digit ID if a match could be
        found for the requested team. If a match could not be found, a
        ``dictionary`` is returned with the key-value pairs for the top 5
        closest teams as keys and their respective IDs as values.
    """
    filtered_name = _parse_squad_name(name)
    if filtered_name in SQUAD_IDS:
        return SQUAD_IDS[filtered_name]
    closest_matches = get_close_matches(filtered_name, SQUAD_IDS.keys(), 5)
    squad_match_ids = {}
    output = 'Exact match not found - Printing closest matches:\n'
    print(closest_matches)
    for team in closest_matches:
        output += team.title() + ' - ' + SQUAD_IDS[team] + '\n'
        squad_match_ids[team.title()] = SQUAD_IDS[team]
    if not quiet:
        print(output)
    return squad_match_ids


def _lookup_team(team_id):
    """
    Find the squad ID for the requested team.

    Every team on fbref.com has its own unique squad ID, which is a 8-digit
    code containing alphanumeric numbers. The user can either supply the
    8-digit code as-is, or provide the team's full name. If the squad ID is
    provided and matches a master list of IDs, the squad ID will be returned
    as-is for later use in the class. If the name is passed, it will first be
    parsed to try and match the team with a team in the master squad ID list.
    If no squad is found, an error will be raised indicating the requested team
    cannot be found.

    Parameters
    ----------
    team_id : string
        A ``string`` of either the team's ID or the name of the team.

    Returns
    -------
    string
        Returns a ``string`` of the squad's 8-digit ID.
    """
    if team_id.lower() in SQUAD_IDS.values():
        return team_id.lower()
    name = lookup_squad_id(team_id)
    if type(name) == str:
        return name
    error_message = ('Team ID of "%s" not found. Did you mean one of the '
                     'following?\n%s' % (team_id, name))
    raise ValueError(error_message)
