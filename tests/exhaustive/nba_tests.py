from sportsreference.nba.teams import Teams
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(sys.path[0])))

for team in Teams():
    print(team.name)
    for player in team.roster.players:
        try:
            print(player.name)
        except UnicodeEncodeError:
            print(player.name.encode("utf-8"))
    for game in team.schedule:
        print(game.dataframe)
        print(game.dataframe_extended)
