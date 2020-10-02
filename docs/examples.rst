Examples
========

Thanks to the broad range of metrics that are pulled from sports-reference.com,
there are multiple ways you can use the `sportsreference` package. This page has
multiple examples beyond those listed on the home page to demonstrate some cool
things you can do which leverage the tool. This page is by no means exhaustive
and the examples aren't necessarily the most efficient in the hope of providing
the most clarity.

In general, most examples shown for a specific sport are applicable for all
sports currently supported by `sportsreference`.

Finding Tallest Players
-----------------------
For each team, find the tallest player on the roster and print out their name
and height in inches.

.. code-block:: python

    from sportsreference.nba.teams import Teams

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

    from sportsreference.ncaab.teams import Teams

    for team in Teams():
        team.dataframe.to_csv('%s.csv' % team.abbreviation.lower())
        team.dataframe.to_pickle('%s.pkl' % team.abbreviation.lower())

Finding Top Win Percentage By Year
----------------------------------
For each year in a range, find the team with the most wins during the season and
print their name and the win total.

.. code-block:: python

    from sportsreference.mlb.teams import Teams

    def print_most_wins(year, wins):
        most_wins = max(wins, key=wins.get)
        print('%s: %s - %s' % (year, wins[most_wins], most_wins))

    for year in range(2000, 2019):
        wins = {}
        for team in Teams(year):
            wins[team.name] = team.wins
        print_most_wins(year, wins)

Predicting the Number of Wins By a Team In a Season
----------------------------------

.. |br| raw:: html

In order to predict the number of wins by a team, we are going to use a machine 
learning model- linear regression. If you don't know what is linear regression
here are a few links which will help you-<br/>
(If you want to dig deep into the maths) - https://en.wikipedia.org/wiki/Linear_regression#:~:text=In%20statistics%2C%20linear%20regression%20is,is%20called%20simple%20linear%20regression <br />
(If you just want to wet your legs! ) - https://www.khanacademy.org/math/statistics-probability/describing-relationships-quantitative-data/introduction-to-trend-lines/a/linear-regression-review <br />
This model will be imported from another package- sklearn(https://scikit-learn.org/stable/) <br />
We are going to iterate from 1970 to 2020 and store the number of wins each year
for the team lions(DET). Then we will train our model with this data.

.. code-block:: python

    # This imports the nfl teams which will serve as our data for our machine learning model
    from sportsreference.nfl.teams import Teams
    from sklearn.linear_model import LinearRegression
    # Importing numpy to reshape our array
    import numpy as np

    starting_year = 1970
    wins = []
    years = []
    ending_year = 2020

    # This loop itterates over our starting year(1970) till our ending year(2020) and appends the number of wins, for the team- lions, to our array wins
    for year in range(starting_year, ending_year):
        teams = Teams(year)
        lions = teams('DET')
        wins.append([lions.wins])
        # We also append the years(1970,1971,1972....2019)
        years.append([year])

    # We are using numpy to shape our array
    years = np.array(years)
    wins = np.array(wins)

    # Here we are declaring the model we are using
    LR = LinearRegression()
    # If you have visited the links for linear regression(I highly recommend you to do so!), you will know that we have to train our model. fit() does that for us
    LR.fit(years, wins)
    # This prints the slope of our model(If the value is 1 then we have a perfect model.The more deviated from 1 the less accurate.)
    print(LR.coef_)