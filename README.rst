Sportsreference: A free sports API written for python
######################################################
.. image:: https://github.com/roclark/sportsreference/workflows/Sportsreference%20push%20tests/badge.svg
    :target: https://github.com/roclark/sportsreference/actions
.. image:: https://readthedocs.org/projects/sportsreference/badge/?version=latest
    :target: https://sportsreference.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://img.shields.io/pypi/v/sportsreference.svg
    :target: https://pypi.org/project/sportsreference

.. contents::

Sportsreference is a free python API that pulls the stats from
www.sports-reference.com and allows them to be easily be used in python-based
applications, especially ones involving data analytics and machine learning.

Sportsreference exposes a plethora of sports information from major sports
leagues in North America, such as the MLB, NBA, College Football and Basketball,
NFL, and NHL. Every sport has its own set of valid API queries ranging from the
list of teams in a league, to the date and time of a game, to the total number
of wins a team has secured during the season, and many, many more metrics that
paint a more detailed picture of how a team has performed during a game or
throughout a season.

Installation
============

The easiest way to install `sportsreference` is by downloading the latest
released binary from PyPI using PIP. For instructions on installing PIP, visit
`PyPA.io <https://pip.pypa.io/en/stable/installing/>`_ for detailed steps on
installing the package manager for your local environment.

Next, run::

    pip install sportsreference

to download and install the latest official release of `sportsreference` on
your machine. You now have the latest stable version of `sportsreference`
installed and can begin using it following the examples below!

If the bleeding-edge version of `sportsreference` is desired, clone this
repository using git and install all of the package requirements with PIP::

    git clone https://github.com/roclark/sportsreference
    cd sportsreference
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
that can be pulled using sportsreference. Visit the documentation on
`Read The Docs <http://sportsreference.readthedocs.io/en/latest/>`_ for a
complete list of all information exposed by the API.

Get instances of all NHL teams for the 2018 season
--------------------------------------------------

.. code-block:: python

    from sportsreference.nhl.teams import Teams

    teams = Teams(2018)

Print every NBA team's name and abbreviation
--------------------------------------------

.. code-block:: python

    from sportsreference.nba.teams import Teams

    teams = Teams()
    for team in teams:
        print(team.name, team.abbreviation)

Get a specific NFL team's season information
--------------------------------------------

.. code-block:: python

    from sportsreference.nfl.teams import Teams

    teams = Teams()
    lions = teams('DET')

Print the date of every game for a NCAA Men's Basketball team
-------------------------------------------------------------

.. code-block:: python

    from sportsreference.ncaab.schedule import Schedule

    purdue_schedule = Schedule('purdue')
    for game in purdue_schedule:
        print(game.date)

Print the number of interceptions by the away team in a NCAA Football game
--------------------------------------------------------------------------

.. code-block:: python

    from sportsreference.ncaaf.boxscore import Boxscore

    championship_game = Boxscore('2018-01-08-georgia')
    print(championship_game.away_interceptions)

Get a Pandas DataFrame of all stats for a MLB game
--------------------------------------------------

.. code-block:: python

    from sportsreference.mlb.boxscore import Boxscore

    game = Boxscore('BOS201806070')
    df = game.dataframe

Documentation
=============

Two blog posts detailing the creation and basic usage of `sportsreference` can
be found on The Medium at the following links:

- `Part 1: Creating a public sports API <https://medium.com/clarktech-sports/python-sports-analytics-made-simple-part-1-14569d6e9a86>`_
- `Part 2: Pull any sports metric in 10 lines of Python <https://medium.com/clarktech-sports/python-sports-analytics-made-simple-part-2-40e591a7f3db>`_

The second post in particular is a great guide for getting started with
`sportsreference` and is highly recommended for anyone who is new to the
package.

Complete documentation is hosted on
`readthedocs.org <http://sportsreference.readthedocs.io/en/latest>`_. Refer to
the documentation for a full list of all metrics and information exposed by
sportsreference. The documentation is auto-generated using Sphinx based on the
docstrings in the sportsreference package.

Testing
=======

Sportsreference contains a testing suite which aims to test all major portions
of code for proper functionality. To run the test suite against your
environment, ensure all of the requirements are installed by running::

    pip install -r requirements.txt

Next, start the tests by running py.test while optionally including coverage
flags which identify the amount of production code covered by the testing
framework::

    py.test --cov=sportsreference --cov-report term-missing tests/

If the tests were successful, it will return a green line will show a message at
the end of the output similar to the following::

    ======================= 380 passed in 245.56 seconds =======================

If a test failed, it will show the number of failed and what went wrong within
the test output. If that's the case, ensure you have the latest version of code
and are in a supported environment. Otherwise, create an issue on GitHub to
attempt to get the issue resolved.
