
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
