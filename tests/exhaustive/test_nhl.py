import sys, os
sys.path.append(os.path.dirname(os.path.dirname(sys.path[0])))
from sportsreference.nhl.teams import Teams

for team in Teams():
    print(team.name)
    for player in team.roster.players:
        print(player.name)
    for game in team.schedule:
        print(game.dataframe)
        print(game.dataframe_extended)
