NBA Package
===========

The NBA package offers multiple modules which can be use to retrieve information
and statistics for the National Basketball Association, such as team names,
season stats, game schedules, and boxscore metrics.

Boxscore
--------

The Boxscore module can be used to grab information from a specific game.
Metrics range from number of points scored to the number of free throws made, to
the assist rate and much more. The Boxscore can be easily queried by passing a
boxscore's URI on sports-reference.com which can be retrieved from the
``Schedule`` class (see ``Schedule`` module below for more information on
retrieving game-specific information).

.. code-block:: python

    from sportsipy.nba.boxscore import Boxscore

    game_data = Boxscore('201806080CLE')
    print(game_data.away_points)  # Prints 108
    print(game_data.home_points)  # Prints 85
    df = game_data.dataframe  # Returns a Pandas DataFrame of game metrics

The Boxscore module also contains a ``Boxscores`` class which searches for all
games played on a particular day and returns a dictionary of matchups between
all teams on the requested day. The dictionary includes the names and
abbreviations for each matchup as well as the boxscore link if applicable.

.. code-block:: python

    from datetime import datetime
    from sportsipy.nba.boxscore import Boxscores

    games_today = Boxscores(datetime.today())
    print(games_today.games)  # Prints a dictionary of all matchups for today

The ``Boxscores`` class also allows the ability to query over a range of dates
using a second optional parameter during instantiation of the class. To query a
range of dates, enter the start date as the first parameter and the inclusive
end date as the second parameter.

.. code-block:: python

    from datetime import datetime
    from sportsipy.nba.boxscore import Boxscores

    # Pulls all games between and including January 1, 2018 and January 5, 2018
    games = Boxscores(datetime(2018, 1, 1), datetime(2018, 1, 5))
    # Prints a dictionary of all results from January 1, 2018 and January 5,
    # 2018
    print(games.games)

.. automodule:: sportsipy.nba.boxscore
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

.. automodule:: sportsipy.nba.player
    :members:
    :undoc-members:
    :show-inheritance:

Roster
------

The Roster module contains detailed player information, allowing each player to
be queried by their player ID using the ``Player`` class which has detailed
information ranging from career points totals to single-season stats and player
height, weight, and nationality. The following is an example on collecting
career information for James Harden:

.. code-block:: python

    from sportsipy.nba.roster import Player

    james_harden = Player('hardeja01')
    print(james_harden.name)  # Prints 'James Harden'
    print(james_harden.points)  # Prints Harden's career points total
    # Prints a Pandas DataFrame of all relevant Harden stats per season
    print(james_harden.dataframe)
    print(james_harden.salary)  # Prints Harden's career earnings
    print(james_harden.contract)  # Prints Harden's contract by yearly wages

By default, the player's career stats are returned whenever a property is
called. To get stats for a specific season, call the class instance with the
season string. All future property requests will return the season-specific
stats.

.. code-block:: python

    from sportsipy.nba.roster import Player

    james_harden = Player('hardeja01')  # Currently pulling career stats
    print(james_harden.points)  # Prints Harden's CAREER points total
    # Prints Harden's points total only for the 2017-18 season.
    print(james_harden('2017-18').points)
    # Prints the number of games Harden played in the 2017-18 season.
    print(james_harden.games_played)

After requesting single-season stats, the career stats can be requested again
by calling the class without arguments or with the 'Career' string passed.

.. code-block:: python

    from sportsipy.nba.roster import Player

    james_harden = Player('hardeja01')  # Currently pulling career stats
    # Prints Harden's points total only for the 2017-18 season.
    print(james_harden('2017-18').points)
    print(james_harden('Career').points) # Prints Harden's career points total

In addition, the Roster module also contains the ``Roster`` class which can be
used to pull all players on a team's roster during a given season and creates
instances of the Player class for each team member and adds them to a list to be
easily queried.

.. code-block:: python

    from sportsipy.nba.roster import Roster

    houston = Roster('HOU')
    for player in houston.players:
        # Prints the name of all players who played for Houston in the most
        # recent season.
        print(player.name)

.. automodule:: sportsipy.nba.roster
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

    from sportsipy.nba.schedule import Schedule

    houston_schedule = Schedule('HOU')
    for game in houston_schedule:
        print(game.date)  # Prints the date the game was played
        print(game.result)  # Prints whether the team won or lost
        # Creates an instance of the Boxscore class for the game.
        boxscore = game.boxscore

.. automodule:: sportsipy.nba.schedule
    :members:
    :undoc-members:
    :show-inheritance:

Teams
-----

The Teams module exposes information for all NBA teams including the team name
and abbreviation, the number of games they won during the season, the total
number of shots they've blocked, and much more.

.. code-block:: python

    from sportsipy.nba.teams import Teams

    teams = Teams()
    for team in teams:
        print(team.name)  # Prints the team's name
        print(team.blocks)  # Prints the team's total blocked shots

A team can also be requested directly by calling the ``Team`` class which
returns a Team instance identical to the one in each element in the loop above.
To request a specific team, use the 3-letter abbreviation for the team while
calling Team class.

.. code-block:: python

    from sportsipy.nba.teams import Team

    houston = Team('HOU')

Each Team instance contains a link to the ``Schedule`` class which enables easy
iteration over all games for a particular team. A Pandas DataFrame can also be
queried to easily grab all stats for all games.

.. code-block:: python

    from sportsipy.nba.teams import Teams

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

    from sportsipy.nba.teams import Teams

    teams = Teams()
    for team in teams:
        # Creates an instance of the roster class for each player on the team.
        roster = team.roster
        for player in roster.players:
            print(player.name)  # Prints the name of each player on the team.

.. automodule:: sportsipy.nba.teams
    :members:
    :undoc-members:
    :show-inheritance:
