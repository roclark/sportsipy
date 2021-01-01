Examples
========

Thanks to the broad range of metrics that are pulled from sports-reference.com,
there are multiple ways you can use the `sportsipy` package. This page has
multiple examples beyond those listed on the home page to demonstrate some cool
things you can do which leverage the tool. This page is by no means exhaustive
and the examples aren't necessarily the most efficient in the hope of providing
the most clarity.

In general, most examples shown for a specific sport are applicable for all
sports currently supported by `sportsipy`.

Finding Tallest Players
-----------------------
For each team, find the tallest player on the roster and print out their name
and height in inches.

.. code-block:: python

    from sportsipy.nba.teams import Teams

    def get_height_in_inches(height):
        feet, inches = height.split('-')
        return int(feet) * 12 + int(inches)

    def print_tallest_player(team_heights):
        tallest_player = max(team_heights, key=team_heights.get)
        print('%s: %s in.' % (tallest_player, team_heights[tallest_player]))

    for team in Teams():
        print('=' * 80)
        print(team.name)
        team_heights = {}
        for player in team.roster.players:
            height = get_height_in_inches(player.height)
            team_heights[player.name] = height
        print_tallest_player(team_heights)

Writing To CSV and Pickle
-------------------------
To prevent re-pulling data from datasets that won't change, such as completed
games with fixed statistics, the pandas DataFrame can be saved to the local
filesystem for re-use later on. Two common file types for this are CSV files and
the high-performing Pickle files. CSV files are a common file type that many
tools and editors support and save an interpretation of the DataFrame, while a
Pickle file is a special file that saves the DataFrame exactly as-is. Pickle
files are faster to read and write compared to CSV files and don't pose a risk
of missing or altered data compared to CSV files.

Save the combined stats for each team to both a CSV and Pickle file.

.. code-block:: python

    from sportsipy.ncaab.teams import Teams

    for team in Teams():
        team.dataframe.to_csv('%s.csv' % team.abbreviation.lower())
        team.dataframe.to_pickle('%s.pkl' % team.abbreviation.lower())

Finding Top Win Percentage By Year
----------------------------------
For each year in a range, find the team with the most wins during the season and
print their name and the win total.

.. code-block:: python

    from sportsipy.mlb.teams import Teams

    def print_most_wins(year, wins):
        most_wins = max(wins, key=wins.get)
        print('%s: %s - %s' % (year, wins[most_wins], most_wins))

    for year in range(2000, 2019):
        wins = {}
        for team in Teams(year):
            wins[team.name] = team.wins
        print_most_wins(year, wins)
