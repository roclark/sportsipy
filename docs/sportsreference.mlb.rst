sportsreference.mlb package
===========================

The MLB package offers multiple modules which can be used to retrieve
information and statistics for Major League Baseball, such as team names,
season stats, game schedules, and boxscore metrics.

Submodules
----------

sportsreference.mlb.boxscore module
-----------------------------------

The Boxscore module can be used to grab information from a specific game.
Metrics range from number of runs scored to the number of sacrifice flies, to
the slugging percentage and much more. The Boxscore can be easily queried by
passing a boxscore's URI on sports-reference.com which can be retrieved from the
``Schedule`` class (see ``Schedule`` module below for more information on
retrieving game-specific information).

.. code-block:: python

    from sportsreference.mlb.boxscore import Boxscore

    game_data = Boxscore('BOS/BOS201808020')
    print(game_data.home_runs)  # Prints 15
    print(game_data.away_runs)  # Prints 7
    df = game_data.dataframe  # Returns a Pandas DataFrame of game metrics

The Boxscore module also contains a ``Boxscores`` class which searches for all
games played on a particular day and returns a dictionary of matchups between
all teams on the requested day. The dictionary includes the names and
abbreviations for each matchup as well as the boxscore link if applicable.

.. code-block:: python

    from datetime import datetime
    from sportsreference.mlb.boxscore import Boxscores

    games_today = Boxscores(datetime.today())
    print(games_today.games)  # Prints a dictionary of all matchups for today

.. automodule:: sportsreference.mlb.boxscore
    :members:
    :undoc-members:
    :show-inheritance:

sportsreference.mlb.schedule module
-----------------------------------

The Schedule module can be used to iterate over all games in a team's schedule
to get game information such as the date, score, result, and more. Each game
also has a link to the ``Boxscore`` class which has much more detailed
information on the game metrics.

.. code-block:: python

    from sportsreference.mlb.schedule import Schedule

    houston_schedule = Schedule('HOU')
    for game in houston_schedule:
        print(game.date)  # Prints the date the game was played
        print(game.result)  # Prints whether the team won or lost
        # Creates an instance of the Boxscore class for the game.
        boxscore = game.boxscore

.. automodule:: sportsreference.mlb.schedule
    :members:
    :undoc-members:
    :show-inheritance:

sportsreference.mlb.teams module
--------------------------------

The Teams module exposes information for all MLB teams including the team name
and abbreviation, the number of games they won during the season, the total
number of bases they've stolen, and much more.

.. code-block:: python

    from sportsreference.mlb.teams import Teams

    teams = Teams()
    for team in teams:
        print(team.name)  # Prints the team's name
        print(team.batting_average)  # Prints the team's season batting average

Each Team instance contains a link to the ``Schedule`` class which enables easy
iteration over all games for a particular team. A Pandas DataFrame can also be
queried to easily grab all stats for all games.

.. code-block:: python

    from sportsreference.mlb.teams import Teams

    teams = Teams()
    for team in teams:
        schedule = team.schedule  # Returns a Schedule instance for each team
        # Returns a Pandas DataFrame of all metrics for all game Boxscores for
        # a season.
        df = team.schedule.dataframe_extended

.. automodule:: sportsreference.mlb.teams
    :members:
    :undoc-members:
    :show-inheritance:
