from sportsreference.fb.squad_ids import SQUAD_IDS
from sportsreference.fb.team import Team
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(sys.path[0])))

for team in list(set(SQUAD_IDS.values())):
    squad = Team(team)
    print(squad.name)
    for game in squad.schedule:
        print(game.date)
    for player in squad.roster:
        print(player.name)
