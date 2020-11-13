Sportsipy: A free sports API written for python
###############################################

Sportsipy is a free python API that pulls the stats from
www.sports-reference.com and allows them to be easily be used in python-based
applications, especially ones involving data analytics and machine learning.

Sportsipy exposes a plethora of sports information from major sports
leagues in North America, such as the MLB, NBA, College Football and Basketball,
NFL, and NHL. Every sport has its own set of valid API queries ranging from the
list of teams in a league, to the date and time of a game, to the total number
of wins a team has secured during the season, and many, many more metrics that
paint a more detailed picture of how a team has performed during a game or
throughout a season.

Examples
========

The following are a few examples showcasing how easy it can be to collect
an abundance of metrics and information from all of the tracked leagues. The
examples below are only a miniscule subset of the total number of statistics
that can be pulled using sportsipy. Visit the documentation on
`Read The Docs <http://sportsipy.readthedocs.io/en/latest/>`_ for a
complete list of all information exposed by the API.

Get instances of all NHL teams for the 2018 season
--------------------------------------------------

.. code-block:: python

    from sportsipy.nhl.teams import Teams

    teams = Teams(2018)

Print every NBA team's name and abbreviation
--------------------------------------------

.. code-block:: python

    from sportsipy.nba.teams import Teams

    teams = Teams()
    for team in teams:
        print(team.name, team.abbreviation)

Get a specific NFL team's season information
--------------------------------------------

.. code-block:: python

    from sportsipy.nfl.teams import Teams

    teams = Teams()
    lions = teams('DET')

Print the date of every game for a NCAA Men's Basketball team
-------------------------------------------------------------

.. code-block:: python

    from sportsipy.ncaab.schedule import Schedule

    purdue_schedule = Schedule('purdue')
    for game in purdue_schedule:
        print(game.date)

Print the number of interceptions by the away team in a NCAA Football game
--------------------------------------------------------------------------

.. code-block:: python

    from sportsipy.ncaaf.boxscore import Boxscore

    championship_game = Boxscore('2018-01-08-georgia')
    print(championship_game.away_interceptions)

Get a Pandas DataFrame of all stats for a MLB game
--------------------------------------------------

.. code-block:: python

    from sportsipy.mlb.boxscore import Boxscore

    game = Boxscore('BOS201806070')
    df = game.dataframe

Find the number of goals a football team has scored
---------------------------------------------------

.. code-block:: python

    from sportsipy.fb.team import Team

    tottenham = Team('Tottenham Hotspur')
    print(tottenham.goals_scored)

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   sportsipy
   examples
   installation
   testing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
