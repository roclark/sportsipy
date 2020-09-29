from sportsreference.nfl.teams import Teams
from sklearn.linear_model import LinearRegression
import numpy as np

starting_year = 1970
wins = []
years = []
ending_year = 2020

for i in range(starting_year, ending_year):
    teams = Teams(i)
    lions = teams('DET')
    wins.append([lions.wins])
    years.append([i])

years = np.array(years)
wins = np.array(wins)

LR = LinearRegression()
LR.fit(years, wins)
