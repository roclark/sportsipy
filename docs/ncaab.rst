NCAAB Package
=============

The NCAAB package offers multiple modules which can be used to retrieve
information and statistics for Men's Division I College Basketball, such as team
names, season stats, game schedules, and boxscore metrics.

Boxscore
--------

The Boxscore module can be used to grab information from a specific game.
Metrics range from number of points scored to the number of blocked shots, to
the assist percentage and much more. The Boxscore can be easily queried by
passing a boxscore's URI on sports-reference.com which can be retrieved from the
``Schedule`` class (see ``Schedule`` module below for more information on
retrieving game-specific information).

.. code-block:: python

    from sportsreference.ncaab.boxscore import Boxscore

    game_data = Boxscore('2018-04-02-21-villanova')
    print(game_data.home_points)  # Prints 79
    print(game_data.away_points)  # Prints 62
    df = game_data.dataframe  # Returns a Pandas DataFrame of game metrics

The Boxscore module also contains a ``Boxscores`` class which searches for all
games played on a particular day and returns a dictionary of matchups between
all teams on the requested day. The dictionary includes the names and
abbreviations for each matchup as well as the boxscore link if applicable.

.. code-block:: python

    from datetime import datetime
    from sportsreference.ncaab.boxscore import Boxscores

    games_today = Boxscores(datetime.today())
    print(games_today.games)  # Prints a dictionary of all matchups for today

.. automodule:: sportsreference.ncaab.boxscore
    :members:
    :undoc-members:
    :show-inheritance:

Conferences
-----------

The Conference module allows conferences to be pulled for any season using the
``Conferences`` class. Accessing the class properties exposes various
dictionaries containing the team and conference abbreviations as well as other
information. To get a list of conference abbreviations for each team, query the
``team_conference`` property.

.. code-block:: python

    from sportsreference.ncaab.conferences import Conferences

    conferences = Conferences()
    # Prints a dictionary of the team abbrevation as a key and conference
    # abbreviation as the value.
    print(conferences.team_conference)

The ``conferences`` property can also be queried by to provide more details on
the teams in every conference.

.. code-block:: python

    from sportsreference.ncaab.conferences import Conferences

    conferences = Conferences()
    # Prints a dictionary where each key is the conference abbreviation and
    # each value is a dictionary containing the full conference name as well as
    # another dictionary of all teams in the conference, including name and
    # abbreviation for each team.
    print(conferences.conferences)

.. automodule:: sportsreference.ncaab.conferences
    :members:
    :undoc-members:
    :show-inheritance:

Rankings
--------

The Rankings module includes the ``Rankings`` class which can be used to easily
query the NCAAB Men's Division-I Basketball rankings published by the Associated
Press on a week-by-week basis. Different formats can be referenced, ranging from
a lightweight dictionary of the most recent rankings containing only the team
abbreviation and rank, to a much larger dictionary of all rankings for an entire
season with results including full team name and abbreviation, current rank,
week number, previous rank, and movement.

.. code-block:: python

    from sportsreference.ncaab.rankings import Rankings

    rankings = Rankings()
    # Prints a dictionary of just the team abbreviation and rank for the current
    # week
    print(rankings.current)
    # Prints more detailed information including previous rank, full name, and
    # movement for all teams in current week
    print(rankings.current_extended)
    # Prints detailed information for all teams for all weeks where rankings
    # have been published for the requested season.
    print(rankings.complete)

.. automodule:: sportsreference.ncaab.rankings
    :members:
    :undoc-members:
    :show-inheritance:

Schedule
--------

The Schedule module can be used to iterate over all games in a team's schedule
to get game information such as the date, score, result, and more. Each game
also has a link to the ``Boxscore`` class which has much more detailed
information on the game metrics.

.. code-block:: python

    from sportsreference.ncaab.schedule import Schedule

    purdue_schedule = Schedule('PURDUE')
    for game in purdue_schedule:
        print(game.date)  # Prints the date the game was played
        print(game.result)  # Prints whether the team won or lost
        # Creates an instance of the Boxscore class for the game.
        boxscore = game.boxscore

.. automodule:: sportsreference.ncaab.schedule
    :members:
    :undoc-members:
    :show-inheritance:

Teams
-----

The Teams module exposes information for all NCAAB teams including the team name
and abbreviation, the number of games they won during the season, the total
number of shots they've blocked, and much more.

.. code-block:: python

    from sportsreference.ncaab.teams import Teams

    teams = Teams()
    for team in teams:
        print(team.name)  # Prints the team's name
        print(team.blocks)  # Prints the number of shots the team blocked

Each Team instance contains a link to the ``Schedule`` class which enables easy
iteration over all games for a particular team. A Pandas DataFrame can also be
queried to easily grab all stats for all games.

.. code-block:: python

    from sportsreference.ncaab.teams import Teams

    teams = Teams()
    for team in teams:
        schedule = team.schedule  # Returns a Schedule instance for each team
        # Returns a Pandas DataFrame of all metrics for all game Boxscores for
        # a season.
        df = team.schedule.dataframe_extended

.. automodule:: sportsreference.ncaab.teams
    :members:
    :undoc-members:
    :show-inheritance:
