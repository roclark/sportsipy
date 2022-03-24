Sportsipy: A free sports API written for Python
###############################################
**Development Status: This project is no longer undergoing active development. Please consider
opening a pull request for any new features or bug fixes to be reviewed and
merged.**

.. image:: https://github.com/roclark/sportsipy/workflows/Sportsipy%20push%20tests/badge.svg
    :target: https://github.com/roclark/sportsipy/actions
.. image:: https://readthedocs.org/projects/sportsipy/badge/?version=latest
    :target: https://sportsipy.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://img.shields.io/pypi/v/sportsipy.svg
    :target: https://pypi.org/project/sportsipy

.. contents::

Sportsipy is a free python API that pulls the stats from
www.sports-reference.com and allows them to be easily be used in python-based
applications, especially ones involving data analytics and machine learning.

Sportsipy exposes a plethora of sports information from major sports leagues in North America, such as the MLB, NBA, College Football and Basketball, NFL, and NHL. Sportsipy also now supports Professional Football (or Soccer) for thousands of teams from leagues around the world. Every sport has its own set of valid API queries ranging from the list of teams in a league, to the date and time of a game, to the total number of wins a team has secured during the season, and many, many more metrics that paint a more detailed picture of how a team has performed during a game or throughout a season.

Installation
============

The easiest way to install `sportsipy` is by downloading the latest
released binary from PyPI using PIP. For instructions on installing PIP, visit
`PyPA.io <https://pip.pypa.io/en/stable/installing/>`_ for detailed steps on
installing the package manager for your local environment.

Next, run::

    pip install sportsipy

to download and install the latest official release of `sportsipy` on
your machine. You now have the latest stable version of `sportsipy`
installed and can begin using it following the examples below!

If the bleeding-edge version of `sportsipy` is desired, clone this
repository using git and install all of the package requirements with PIP::

    git clone https://github.com/roclark/sportsipy
    cd sportsipy
    pip install -r requirements.txt

Once complete, create a Python wheel for your default version of Python by
running the following command::

    python setup.py sdist bdist_wheel

This will create a `.whl` file in the `dist` directory which can be installed
with the following command::

    pip install dist/*.whl

Overview
===========

Sportsipy is currently available for Soccer, MLB, NBA, NFL, NHL, NCAAF, and NCAAB. This section serves as a brief overview of what Sportsipy has to offer. Almost any sport-related statistic for teams, leagues, and players can be found. You can use the search box in the 
`readthedocs.org <http://sportsipy.readthedocs.io/en/latest>`_  to track down what you are looking for.

Each module below is covered at a high level. Sportsipy makes heavy use of classes/modules and they are all interconnected. For example:

* NCAAB Package
    * Conference Module (Big 10)
        * Team Module (Purdue Basketball, 2019 - 2020)
            * Roster Module
                * Player Module (Carsen Edwards)
            * Schedule Module
                * Boxscore Module (Purdue vs. Indiana 2/19/19)

            
At each stage/module, almost any statistic you can think of is accessible. With that in mind, more information is covered below!

Team
--------

The Team module is used to grab high-level stats and information for a specific team such as record, ranking, games played, etc. Each Team instance can be used to access the Schedule and Roster classes.

Schedule
--------

The Schedule module can be used to iterate over all games in a team's schedule to get high-level game information such as the date, score, result, and more. Each game in the schedule is part of the Boxscore class, which contains detailed statistics for a specific game.

Roster
--------

The Roster module contains the players for a team, which you can use to access the Player module for each player to obtain player specific information.

Boxscore
--------

The Boxscore module is used to retrieve information for any given game such as player statistics, score, winner/loser, location, date, etc. You also can directly access the Player module for each player in the game.

Player
--------

The Player module contains player information and stats for all seasons. You can capture all relevant stats and information like name, team, height/weight, career stats, single-season stats, and much more.

Conferences
--------

The Conference module allows conference information to be accessed for any season. Accessing the class properties allows you to find teams by conference as well as conference specific stats and information.

Rankings
--------

The Rankings module is part of the NCAAF and NCAAB packages published by the Associated Press on a week-by-week basis. You can find things such as teams, current rank, week number, previous rank, and rankings movement.

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

Documentation
=============

Two blog posts detailing the creation and basic usage of `sportsipy` can
be found on The Medium at the following links:

- `Part 1: Creating a public sports API <https://medium.com/clarktech-sports/python-sports-analytics-made-simple-part-1-14569d6e9a86>`_
- `Part 2: Pull any sports metric in 10 lines of Python <https://medium.com/clarktech-sports/python-sports-analytics-made-simple-part-2-40e591a7f3db>`_

The second post in particular is a great guide for getting started with
`sportsipy` and is highly recommended for anyone who is new to the
package.

Complete documentation is hosted on
`readthedocs.org <http://sportsipy.readthedocs.io/en/latest>`_. Refer to
the documentation for a full list of all metrics and information exposed by
sportsipy. The documentation is auto-generated using Sphinx based on the
docstrings in the sportsipy package.

Testing
=======

Sportsipy contains a testing suite which aims to test all major portions
of code for proper functionality. To run the test suite against your
environment, ensure all of the requirements are installed by running::

    pip install -r requirements.txt

Next, start the tests by running py.test while optionally including coverage
flags which identify the amount of production code covered by the testing
framework::

    py.test --cov=sportsipy --cov-report term-missing tests/

If the tests were successful, it will return a green line will show a message at
the end of the output similar to the following::

    ======================= 380 passed in 245.56 seconds =======================

If a test failed, it will show the number of failed and what went wrong within
the test output. If that's the case, ensure you have the latest version of code
and are in a supported environment. Otherwise, create an issue on GitHub to
attempt to get the issue resolved.
