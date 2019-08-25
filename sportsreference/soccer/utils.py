import re


def _parse_club_id(uri_link):
    """
    Returns a team's club id

    A team's club id is embedded in a URI link

    Parameters
    ----------
    uri_link : string
        A URI link which contains a team's club id within other link
        contents.

    Returns
    -------
    string
        The shortened club id
    """
    club_id = re.sub(r'/en/squads/', '', uri_link)
    club_id = re.sub(r'/.*', '', club_id)
    return club_id


def _parse_field_link(parsing_scheme, html_data, field, index=0):
    """
    Parse an HTML table to find the requested field's value.

    All of the values are passed in an HTML table row instead of as individual
    items. The values need to be parsed by matching the requested attribute
    with a parsing scheme that sports-reference uses to differentiate stats.
    This function returns a single value for the given attribute.

    Parameters
    ----------
    parsing_scheme : dict
        A dictionary of the parsing scheme to be used to find the desired
        field. The key corresponds to the attribute name to parse, and the
        value is a PyQuery-readable parsing scheme as a string (such as
        'td[data-stat="wins"]').
    html_data : string
        A string containing all of the rows of stats for a given team. If
        multiple tables are being referenced, this will be comprised of
        multiple rows in a single string.
    field : string
        The name of the attribute to match. Field must be a key in
        parsing_scheme.
    index : int (optional)
        An optional index if multiple fields have the same attribute name. For
        example, 'HR' may stand for the number of home runs a baseball team has
        hit, or the number of home runs a pitcher has given up. The index
        aligns with the order in which the attributes are recevied in the
        html_data parameter.

    Returns
    -------
    string
        The value at the specified index for the requested field. If no value
        could be found, returns None.
    """

    scheme = parsing_scheme[field]
    items = [i.attr('href') for i in html_data(scheme).items()]
    # Stats can be added and removed on a yearly basis. If not stats are found,
    # return None and have the be the value.
    if len(items) == 0:
        return None
    # Default to returning the first element. Optionally return another element
    # if multiple fields have the same tag attribute.
    try:
        return items[index]
    except IndexError:
        return None
