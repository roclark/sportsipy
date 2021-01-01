NFL Package
===========

The NFL package offers multiple modules which can be used to retrieve
information and statistics for the National Football League, such as team names,
season stats, game schedules, and boxscore metrics.

Boxscore
--------

The Boxscore module can be used to grab information from a specific game.
Metrics range from number of points scored to the number of passing yards, to
the number of yards lost from sacks and much more. The Boxscore can be easily
queried by passing a boxscore's URI on sports-reference.com which can be
retrieved from the ``Schedule`` class (see ``Schedule`` module below for more
information on retrieving game-specific information).

.. code-block:: python

    from sportsipy.nfl.boxscore import Boxscore

    game_data = Boxscore('201802040nwe')
    print(game_data.home_points)  # Prints 33
    print(game_data.away_points)  # Prints 41
    df = game_data.dataframe  # Returns a Pandas DataFrame of game metrics

The Boxscore module also contains a ``Boxscores`` class which searches for all
games played on a particular day and returns a dictionary of matchups between
all teams on the requested day. The dictionary includes the names and
abbreviations for each matchup as well as the boxscore link if applicable.

.. code-block:: python

    from sportsipy.nfl.boxscore import Boxscores

    games_today = Boxscores(1, 2017)
    # Prints a dictionary of all matchups for week 1 of 2017
    print(games_today.games)

The ``Boxscores`` class also allows the ability to query over a range of dates
using a second optional parameter during instantiation of the class. To query a
range of dates, enter the start date as the first parameter and the inclusive
end date as the second parameter.

.. code-block:: python

    from sportsipy.nfl.boxscore import Boxscores

    # Pulls all games from weeks 7 and 8 in 2017
    games = Boxscores(7, 2017, 8)
    # Prints a dictionary of all games from weeks 7 and 8 in 2017
    print(games.games)

.. automodule:: sportsipy.nfl.boxscore
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

.. automodule:: sportsipy.nfl.player
    :members:
    :undoc-members:
    :show-inheritance:

Roster
------

The Roster module contains detailed player information, allowing each player to
be queried by their player ID using the ``Player`` class which has detailed
information ranging from career touchdowns to single-season stats and player
height, weight, and nationality. The following is an example on collecting
career information for Drew Brees.

.. code-block:: python

    from sportsipy.nfl.roster import Player

    brees = Player('BreeDr00')
    print(brees.name)  # Prints 'Drew Brees'
    print(brees.passing_yards)  # Prints Brees' career passing yards
    # Prints a Pandas DataFrame of all relevant stats per season for Brees
    print(brees.dataframe)

By default, the player's career stats are returned whenever a property is
called. To get stats for a specific team, call the class instance with the
season string. All future property requests will return the season-specific
stats.

.. code-block:: python

    from sportsipy.nfl.roster import Player

    brees = Player('BreeDr00')  # Currently pulling career stats
    print(brees.passing_yards)  # Prints Brees' CAREER passing yards total
    # Prints Brees' passing yards total only for the 2017 season
    print(brees('2017').passing_yards)
    # Prints Brees' passing touchdowns for the 2017 season only
    print(brees.passing_touchdowns)

After requesting single-season stats, the career stats can be requested again
by calling the class without arguments or with the 'Career' string passed.

.. code-block:: python

    from sportsipy.nfl.roster import Player

    brees = Player('BreeDr00')  # Currently pulling career stats
    # Prints Brees' passing yards total only for the 2017 season
    print(brees('2017').passing_yards)
    print(brees('Career').passing_yards)  # Prints Brees' career passing yards

In addition, the Roster module also contains the ``Roster`` class which can be
used to pull all players on a team's roster during a given season and creates
instances of the Player class for each team member and adds them to a list to be
easily queried.

.. code-block:: python

    from sportsipy.nfl.roster import Roster

    saints = Roster('NOR')
    for player in saints.players:
        # Prints the name of all players who played for the New Orleans Saints
        # in the most recent season.
        print(player.name)

.. automodule:: sportsipy.nfl.roster
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

    from sportsipy.nfl.schedule import Schedule

    houston_schedule = Schedule('HTX')
    for game in houston_schedule:
        print(game.date)  # Prints the date the game was played
        print(game.result)  # Prints whether the team won or lost
        # Creates an instance of the Boxscore class for the game.
        boxscore = game.boxscore

.. automodule:: sportsipy.nfl.schedule
    :members:
    :undoc-members:
    :show-inheritance:

Teams
-----

The Teams module exposes information for all MLB teams including the team name
and abbreviation, the number of games they won during the season, the average
margin of victory, and much more.

.. code-block:: python

    from sportsipy.nfl.teams import Teams

    teams = Teams()
    for team in teams:
        print(team.name)  # Prints the team's name
        # Prints the team's average margin of victory
        print(team.margin_of_victory)

A team can also be requested directly by calling the ``Team`` class which
returns a Team instance identical to the one in each element in the loop above.
To request a specific team, use the 3-letter abbreviation for the team while
calling Team class.

.. code-block:: python

    from sportsipy.nfl.teams import Team

    kansas = Team('KAN')

Each Team instance contains a link to the ``Schedule`` class which enables easy
iteration over all games for a particular team. A Pandas DataFrame can also be
queried to easily grab all stats for all games.

.. code-block:: python

    from sportsipy.nfl.teams import Teams

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

    from sportsipy.nfl.teams import Teams

    for team in Teams():
        roster = team.roster  # Gets each team's roster
        for player in roster.players:
                print(player.name)  # Prints each players name on the roster

.. automodule:: sportsipy.nfl.teams
    :members:
    :undoc-members:
    :show-inheritance:
