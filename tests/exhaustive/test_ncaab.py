from sportsreference.ncaab.conferences import Conferences
from sportsreference.ncaab.rankings import Rankings
from sportsreference.ncaab.teams import Teams

for team in Teams():
    print(team.name)
    for player in team.roster:
        print(player.name)
    for game in schedule:
        print(game.dataframe)
        print(game.dataframe_extended)

conferences = Conferences()
print(conferences.conferences)
print(conferences.team_conference)

rankings = Rankings()
print(rankings.current)
print(rankings.current_extended)
print(rankings.complete)
