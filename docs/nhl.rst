NHL Package
===========

The NHL package offers multiple modules which can be used to retrieve
information and statistics for the National Hockey League, such as team names,
season stats, game schedules, and boxscore metrics.

Boxscore
--------

The Boxscore module can be used to grab information from a specific game.
Metrics range from number of goals scored to the number of penalty minutes, to
the save percentage and much more. The Boxscore can be easily queried by
passing a boxscore's URI on sports-reference.com which can be retrieved from the
``Schedule`` class (see ``Schedule`` module below for more information on
retrieving game-specific information).

.. code-block:: python

    from sportsipy.nhl.boxscore import Boxscore

    game_data = Boxscore('201806070VEG')
    print(game_data.home_goals)  # Prints 3
    print(game_data.away_goals)  # Prints 4
    df = game_data.dataframe  # Returns a Pandas DataFrame of game metrics

The Boxscore module also contains a ``Boxscores`` class which searches for all
games played on a particular day and returns a dictionary of matchups between
all teams on the requested day. The dictionary includes the names and
abbreviations for each matchup as well as the boxscore link if applicable.

.. code-block:: python

    from datetime import datetime
    from sportsipy.nhl.boxscore import Boxscores

    games_today = Boxscores(datetime.today())
    print(games_today.games)  # Prints a dictionary of all matchups for today

The ``Boxscores`` class also allows the ability to query over a range of dates
using a second optional parameter during instantiation of the class. To query a
range of dates, enter the start date as the first parameter and the inclusive
end date as the second parameter.

.. code-block:: python

    from datetime import datetime
    from sportsipy.nhl.boxscore import Boxscores

    # Pulls all games between and including February 4, 2017 and February 5,
    # 2017
    games = Boxscores(datetime(2017, 2, 4), datetime(2017, 2, 5))
    # Prints a dictionary of all results from February 4, 2017 and February 5,
    # 2017
    print(games.games)

.. automodule:: sportsipy.nhl.boxscore
    :members:
    :undoc-members:
    :show-inheritance:

Player
------

The Player module contains an abstract base class that can be inherited by both
the ``BoxscorePlayer`` and ``Player`` classes in the ``Boxscore`` and ``Roster``
modules, respectively. All of the properties that appear in the
``AbstractPlayer`` class can be read from either of the two child classes
mentioned above.

.. automodule:: sportsipy.nhl.player
    :members:
    :undoc-members:
    :show-inheritance:

Roster
------

The Roster module contains detailed player information, allowing each player to
be queried by their player ID using the ``Player`` class which has detailed
information ranging from career points totals to single-season stats and player
height and weight. The following is an example on collecting career information
for Henrik Zetterberg:

.. code-block:: python

    from sportsipy.nhl.roster import Player

    zetterberg = Player('zettehe01')
    print(zetterberg.name)  # Prints 'Henrik Zetterberg'
    print(zetterberg.points)  # Prints Zetterberg's career points total
    # Prints a Pandas DataFrame of all relevant Zetterberg stats per season
    print(zetterberg.dataframe)

By default, the player's career stats are returned whenever a property is
called. To get stats for a specific season, call the class instance with the
season string. All future property requests will return the season-specific
stats.

.. code-block:: python

    from sportsipy.nhl.roster import Player

    zetterberg = Player('zettehe01')  # Currently pulling career stats
    print(zetterberg.points)  # Prints Zetterberg's CAREER points total
    # Prints Zetterberg's points total only for the 2017-18 season.
    print(zetterberg('2017-18').points)
    # Prints the number of games Zetterberg played in the 2017-18 season.
    print(zetterberg.games_played)

After requesting single-season stats, the career stats can be requested again
by calling the class without arguments or with the 'Career' string passed.

.. code-block:: python

    from sportsipy.nhl.roster import Player

    zetterberg = Player('zettehe01')  # Currently pulling career stats
    # Prints Zetterberg's points total only for the 2017-18 season.
    print(zetterberg('2017-18').points)
    print(zetterberg('Career').points) # Prints Zetterberg's career points total

In addition, the Roster module also contains the ``Roster`` class which can be
used to pull all players on a team's roster during a given season and creates
instances of the Player class for each team member and adds them to a list to be
easily queried.

.. code-block:: python

    from sportsipy.nhl.roster import Roster

    detroit = Roster('DET')
    for player in detroit.players:
        # Prints the name of all players who played for Houston in the most
        # recent season.
        print(player.name)

.. automodule:: sportsipy.nhl.roster
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

    from sportsipy.nhl.schedule import Schedule

    detroit_schedule = Schedule('DET')
    for game in detroit_schedule:
        print(game.date)  # Prints the date the game was played
        print(game.result)  # Prints whether the team won or lost
        # Creates an instance of the Boxscore class for the game.
        boxscore = game.boxscore

.. automodule:: sportsipy.nhl.schedule
    :members:
    :undoc-members:
    :show-inheritance:

Teams
-----

The Teams module exposes information for all NHL teams including the team name
and abbreviation, the number of games they won during the season, the total
number of shots on goal, and much more.

.. code-block:: python

    from sportsipy.nhl.teams import Teams

    teams = Teams()
    for team in teams:
        print(team.name)  # Prints the team's name
        print(team.shots_on_goal)  # Prints the team's total shots on goal

A team can also be requested directly by calling the ``Team`` class which
returns a Team instance identical to the one in each element in the loop above.
To request a specific team, use the 3-letter abbreviation for the team while
calling Team class.

.. code-block:: python

    from sportsipy.nhl.teams import Team

    detroit = Team('DET')

Each Team instance contains a link to the ``Schedule`` class which enables easy
iteration over all games for a particular team. A Pandas DataFrame can also be
queried to easily grab all stats for all games.

.. code-block:: python

    from sportsipy.nhl.teams import Teams

    teams = Teams()
    for team in teams:
        schedule = team.schedule  # Returns a Schedule instance for each team
        # Returns a Pandas DataFrame of all metrics for all game Boxscores for
        # a season.
        df = team.schedule.dataframe_extended

Lastly, each Team instance also contains a link to the ``Roster`` class which
enables players from the team to be easily queried. Each Roster instance
contains detailed stats and information for each player on the team.

.. code-block:: python

    from sportsipy.nhl.teams import Teams

    teams = Teams()
    for team in teams:
        # Creates an instance of the roster class for each player on the team.
        roster = team.roster
        for player in roster.players:
            print(player.name)  # Prints the name of each player on the team.

.. automodule:: sportsipy.nhl.teams
    :members:
    :undoc-members:
    :show-inheritance:
