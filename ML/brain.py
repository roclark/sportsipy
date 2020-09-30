# This imports the nfl teams which will serve as our data for our machine learning model
from sportsreference.nfl.teams import Teams
# We are importing a simple linear regression model from sklearn.Here are a few ref-
# sklearn - https://scikit-learn.org/stable/
# linear regression model (If you want to dig deep into the maths) - https://en.wikipedia.org/wiki/Linear_regression#:~:text=In%20statistics%2C%20linear%20regression%20is,is%20called%20simple%20linear%20regression.
# linear regression model (If you just want to wet your legs! ) - https://www.khanacademy.org/math/statistics-probability/describing-relationships-quantitative-data/introduction-to-trend-lines/a/linear-regression-review
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
