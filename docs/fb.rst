Football Package
================

The Football (soccer) package offers multiple modules which can be used to
retrieve information and statistics for thousands of football teams around the
world, such as team names, season stats, game schedules, and competition
results.

Team
----
The Team module is used to grab high-level stats and information for a specific
team. Information ranges from the team's primary competition, their position and
point value in the league, plus goals scored, and much more. The easiest way to
instantiate a team object is to pass a squad's 8-digit ID number to the class.
Squad IDs can either be found in the ``sportsipy.fb.squad_ids``
dictionary, or by using one of the utility functions listed below.

Alternatively, the team name can be used while calling the class and the
corresponding squad ID will be retrieved if possible. The following is an
example of pulling information on Tottenham Hotspur.

.. code-block:: python

    from sportsipy.fb.team import Team

    tottenham = Team('Tottenham Hotspur')  # Equivalent to Team('361ca564')
    print(tottenham.league)  # Prints 'Premier League'
    print(tottenham.goals_scored)  # Prints 47
    print(tottenham.home_record)  # Prints 8-2-4

.. automodule:: sportsipy.fb.team
    :members:
    :undoc-members:
    :show-inheritance:

Schedule
--------
The Schedule module can be used to iterate over all games in a team's schedule
to get high-level game information such as the date, score, result, and more.
Either the full team name or, preferably, the team's 8-digit squad ID can be
used to pull a specific team's schedule. The following is an example of pulling
the schedule and iterating over the games for Tottenham Hotspur.

.. code-block:: python

    from sportsipy.fb.schedule import Schedule

    tottenham_schedule = Schedule('Tottenham Hotspur')
    print(len(tottenham_schedule))  # Prints 52 for the total number of games
    for game in tottenham_schedule:
        print(game.datetime)  # Prints the datetime for each game
        print(game.goals_scored)  # Prints the number of goals the team scored
        print(game.captain)  # Prints the primary captain's name for the game

The Schedule module can also be accessed from the Team class.

.. code-block:: python

    from sportsipy.fb.team import Team

    tottenham = Schedule('Tottenham Hotspur')
    for game in tottenham.schedule:
        print(game.datetime)  # Prints the datetime for each game

.. automodule:: sportsipy.fb.schedule
    :members:
    :undoc-members:
    :show-inheritance:

Roster
------
The Roster module contains detailed player information for every player on a
team's roster, allowing each player to be queried by either their name or
their unique player ID. Every player instantiates the ``SquadPlayer`` class
which includes further individual statistics, such as goals, shots, assists,
playtime, and much more. The following is an example on pulling the roster
for Tottenham Hotspur and querying stats:

.. code-block:: python

    from sportsipy.fb.roster import Roster

    tottenham = Roster('Tottenham Hotspur')
    for player in tottenham:
        print(player.name)  # Prints the name of each player on the roster
        print(player.goals)  # Prints the number of goals the player scored
        print(player.assists)  # Prints the number of assists for the player

A specific player can also be called from a ``Roster`` instance instead of
iterating through every member of the team by using either the player's name
or unique player ID:

.. code-block:: python

    from sportsipy.fb.roster import Roster

    tottenham = Roster('Tottenham Hotspur')
    harry_kane = tottenham('Harry Kane')  # Pulls Harry Kane's stats
    print(harry_kane.goals)  # Prints Harry's goals
    print(harry_kane.assists)  # Prints Harry's assists

.. automodule:: sportsipy.fb.roster
    :members:
    :undoc-members:
    :show-inheritance:
