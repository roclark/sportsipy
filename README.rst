Sportsipy: A free sports API written for python
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

Sportsipy exposes a plethora of sports information from major sports
leagues in North America, such as the MLB, NBA, College Football and Basketball,
NFL, and NHL. Sportsipy also now supports Professional Football (or
Soccer) for thousands of teams from leagues around the world. Every sport has
its own set of valid API queries ranging from the list of teams in a league, to
the date and time of a game, to the total number of wins a team has secured
during the season, and many, many more metrics that paint a more detailed
picture of how a team has performed during a game or throughout a season.

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

Examples
========

The following are a few examples showcasing how easy it can be to collect
an abundance of metrics and information from all of the tracked leagues. The
examples below are only a miniscule subset of the total number of statistics
that can be pulled using sportsipy. Visit the documentation on
`Read The Docs <http://sportsipy.readthedocs.io/en/latest/>`_ for a
complete list of all information exposed by the API.

Get stats of a specified NHL player
-----------------------------------

.. code-block:: python

    from sportsipy.nhl.roster import Player

    sidney_crosby = Player('crosbsi01')
    print(f"Career games played = {sidney_crosby.games_played}")
    print(f"Career goals scored = {sidney_crosby.goals}")
    print(f"Career assists = {sidney_crosby.assists}")

    """
    Expected output:
    Career games played = 1272
    Career goals scored = 592
    Career assists = 1004
    """

Print every NBA team's name and abbreviation
--------------------------------------------

.. code-block:: python

    from sportsipy.nba.teams import Teams

    teams = Teams()
    for team in teams:
        print(team.name, team.abbreviation)

    """
    Expected Output:
    Indiana Pacers IND
    Boston Celtics BOS
    Oklahoma City Thunder OKC
    Milwaukee Bucks MIL
    Atlanta Hawks ATL
    Los Angeles Lakers LAL
    Dallas Mavericks DAL
    Golden State Warriors GSW
    Sacramento Kings SAC
    Phoenix Suns PHO
    Utah Jazz UTA
    Los Angeles Clippers LAC
    New Orleans Pelicans NOP
    Denver Nuggets DEN
    Philadelphia 76ers PHI
    Houston Rockets HOU
    Washington Wizards WAS
    Minnesota Timberwolves MIN
    New York Knicks NYK
    Cleveland Cavaliers CLE
    Toronto Raptors TOR
    Chicago Bulls CHI
    San Antonio Spurs SAS
    Orlando Magic ORL
    Brooklyn Nets BRK
    Miami Heat MIA
    Detroit Pistons DET
    Charlotte Hornets CHO
    Portland Trail Blazers POR
    Memphis Grizzlies MEM
    """

Get a specific NFL team's wins and losses for the season
--------------------------------------------------------

.. code-block:: python

    from sportsipy.nfl.teams import Teams

    teams = Teams()
    lions = teams('DET')

    print(f"The Detriot Lions had {lions.wins} wins and {lions.losses} losses during their most recent season.")

    """
    Expected Output:
    The Detriot Lions had 12 wins and 5 losses during their most recent season.
    """

Print the date of every game for a NCAA Men's Basketball team
-------------------------------------------------------------

.. code-block:: python

    from sportsipy.ncaab.schedule import Schedule

    purdue_schedule = Schedule('purdue')
    for game in purdue_schedule:
        print(game.date)

    """
    Expected Output:
    Mon, Nov 6, 2023
    Fri, Nov 10, 2023
    Mon, Nov 13, 2023
    Mon, Nov 20, 2023
    Tue, Nov 21, 2023
    Wed, Nov 22, 2023
    Tue, Nov 28, 2023
    Fri, Dec 1, 2023
    Mon, Dec 4, 2023
    Sat, Dec 9, 2023
    Sat, Dec 16, 2023
    Thu, Dec 21, 2023
    Fri, Dec 29, 2023
    Tue, Jan 2, 2024
    Fri, Jan 5, 2024
    Tue, Jan 9, 2024
    Sat, Jan 13, 2024
    Tue, Jan 16, 2024
    Sat, Jan 20, 2024
    Tue, Jan 23, 2024
    Sun, Jan 28, 2024
    Wed, Jan 31, 2024
    Sun, Feb 4, 2024
    Sat, Feb 10, 2024
    Thu, Feb 15, 2024
    Sun, Feb 18, 2024
    Thu, Feb 22, 2024
    Sun, Feb 25, 2024
    Sat, Mar 2, 2024
    Tue, Mar 5, 2024
    Sun, Mar 10, 2024
    Fri, Mar 15, 2024
    Sat, Mar 16, 2024
    Fri, Mar 22, 2024
    Sun, Mar 24, 2024
    Fri, Mar 29, 2024
    Sun, Mar 31, 2024
    Sat, Apr 6, 2024
    Mon, Apr 8, 2024
    """

Print the number of interceptions by the away team in a NCAA Football game
--------------------------------------------------------------------------

.. code-block:: python

    from sportsipy.ncaaf.boxscore import Boxscore

    championship_game = Boxscore('2018-01-08-georgia')
    print(championship_game.away_interceptions)

    """
    Expected Output:
    1
    """

Get the batting average and home run total for each MLB team
------------------------------------------------------------

.. code-block:: python

    from sportsipy.mlb.teams import Teams

    teams = Teams()
    for team in teams:
        print(f"{team.name}, batting average: {team.batting_average}, home runs: {team.home_runs}")

    """
    Expected Output:
    Atlanta Braves, batting average: 0.283, home runs: 28
    Cleveland Guardians, batting average: 0.253, home runs: 25
    Milwaukee Brewers, batting average: 0.264, home runs: 31
    Baltimore Orioles, batting average: 0.26, home runs: 37
    New York Yankees, batting average: 0.239, home runs: 27
    Chicago Cubs, batting average: 0.245, home runs: 28
    Philadelphia Phillies, batting average: 0.249, home runs: 28
    Kansas City Royals, batting average: 0.237, home runs: 29
    Los Angeles Dodgers, batting average: 0.269, home runs: 31
    Cincinnati Reds, batting average: 0.222, home runs: 26
    Detroit Tigers, batting average: 0.221, home runs: 20
    New York Mets, batting average: 0.246, home runs: 26
    Boston Red Sox, batting average: 0.236, home runs: 33
    Seattle Mariners, batting average: 0.225, home runs: 24
    Texas Rangers, batting average: 0.25, home runs: 26
    San Diego Padres, batting average: 0.259, home runs: 28
    Pittsburgh Pirates, batting average: 0.237, home runs: 21
    Tampa Bay Rays, batting average: 0.244, home runs: 22
    Toronto Blue Jays, batting average: 0.231, home runs: 22
    Arizona Diamondbacks, batting average: 0.261, home runs: 26
    San Francisco Giants, batting average: 0.247, home runs: 23
    Minnesota Twins, batting average: 0.216, home runs: 26
    St. Louis Cardinals, batting average: 0.221, home runs: 16
    Washington Nationals, batting average: 0.231, home runs: 21
    Los Angeles Angels, batting average: 0.239, home runs: 27
    Oakland Athletics, batting average: 0.201, home runs: 28
    Houston Astros, batting average: 0.26, home runs: 26
    Colorado Rockies, batting average: 0.246, home runs: 21
    Miami Marlins, batting average: 0.216, home runs: 20
    Chicago White Sox, batting average: 0.192, home runs: 14
    """

Find the number of goals a football team has scored
---------------------------------------------------

.. code-block:: python

    from sportsipy.fb.team import Team

    tottenham = Team('Tottenham Hotspur')
    print(tottenham.goals_scored)

    """
    Expected Output:
    65
    """

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
