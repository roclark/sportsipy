from sportsreference.nhl.teams import Teams

for team in Teams():
    print(team.name)
    for player in team.roster:
        print(player.name)
    for game in schedule:
        print(game.dataframe)
        print(game.dataframe_extended)
