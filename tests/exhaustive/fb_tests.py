import sys, os
sys.path.append(os.path.dirname(os.path.dirname(sys.path[0])))
from sportsipy.fb.team import Team
from sportsipy.fb.squad_ids import SQUAD_IDS

for team in list(set(SQUAD_IDS.values())):
    squad = Team(team)
    print(squad.name.encode('utf-8'))
    for game in squad.schedule:
        print(game.date)
    for player in squad.roster:
        print(player.name.encode('utf-8'))
