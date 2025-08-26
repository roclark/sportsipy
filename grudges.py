from sportsipy.nba.roster import Roster as NBARoster
from sportsipy.nba.roster import Player as NBAPlayer
from sportsipy.nfl.roster import Roster as NFLRoster
from sportsipy.nfl.roster import Player as NFLPlayer
from time import sleep
import ast
import sqlite3

# COLORS
BOLD = '\033[1m'
RED = '\033[31m'
GREEN = '\033[32m'
GOLD = '\033[33m'
CYAN = '\033[36m'
RESET = '\033[0m'

# GLOBALS
sports = ["NBA", "NFL"]
teams = {"NBA":["ATL", "BOS", "BRK", "CHI", "CHO", "CLE", "DAL", "DEN", "DET", "GSW", 
                "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK", 
                "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"], 
         "NFL":["ATL", "BUF", "CAR", "CHI", "CIN", "CLE", "CLT", "CRD", "DAL", "DEN", 
                "DET", "GNB", "HTX", "JAX", "KAN", "MIA", "MIN", "NOR", "NWE", "NYG",
                "NYJ", "OTI", "PHI", "PIT", "RAI", "RAM", "RAV", "SDG", "SEA", "SFO", 
                "TAM", "WAS"]}
nfl_schedule = [{'Thursday, September 4th':[("8:20 PM", "DAL", "PHI")], 'Friday, September 5th':[("8:00 PM", "KAN", "SDG")], 
                 'Sunday, September 7th':[("1:00 PM", "TAM", "ATL"), ("1:00 PM", "CIN", "CLE"), 
                            ("1:00 PM", "MIA", "CLT"), ("1:00 PM", "CAR", "JAX"), 
                            ("1:00 PM", "RAI", "NWE"), ("1:00 PM", "CRD", "NOR"), 
                            ("1:00 PM", "PIT", "NYJ"), ("1:00 PM", "NYG", "WAS"),
                            ("4:05 PM", "OTI", "DEN"), ("4:05 PM", "SFO", "SEA"), 
                            ("4:25 PM", "DET", "GNB"), ("4:25 PM", "HTX", "RAM"), 
                            ("8:20 PM", "RAV", "BUF")],
                 'Monday, September 8th':[("8:15 PM", "MIN", "CHI")]}, # 1
                [("WAS", "GNB"), ("CLE", "RAV"), ("JAX", "CIN"), ("NYG", "DAL"), ("CHI", "DET"), # 2
                 ("NWE", "MIA"), ("SFO", "NOR"), ("BUF", "NYJ"), ("SEA", "PIT"), ("RAM", "OTI"),
                 ("CAR", "CRD"), ("DEN", "CLT"), ("PHI", "KAN"), ("ATL", "MIN"), ("TAM", "HTX"),
                 ("SDG", "RAI")],
                [("MIA", "BUF"), ("ATL", "CAR"), ("GNB", "CLE"), ("HTX", "JAX"), ("CIN", "MIN"), # 3
                 ("PIT", "NWE"), ("RAM", "PHI"), ("NYJ", "TAM"), ("CLT", "OTI"), ("RAI", "WAS"), 
                 ("DEN", "SDG"), ("NOR", "SEA"), ("DAL", "CHI"), ("CRD", "SFO"), ("KAN", "NYG"),
                 ("DET", "RAV")],
                [("SEA", "CRD"), ("MIN", "PIT"), ("WAS", "ATL"), ("NOR", "BUF"), ("CLE", "DET"), # 4
                 ("OTI", "HTX"), ("CAR", "NWE"), ("SDG", "NYG"), ("PHI", "TAM"), ("CLT", "RAM"), 
                 ("JAX", "SFO"), ("RAV", "KAN"), ("CHI", "RAI"), ("GNB", "DAL"), ("NYJ", "MIA"), 
                 ("CIN", "DEN")],
                [("SFO", "RAM"), ("MIN", "CLE"), ("HTX", "RAV"), ("MIA", "CAR"), ("RAI", "CLT"), # 5
                 ("NYG", "NOR"), ("DAL", "NYJ"), ("DEN", "PHI"), ("OTI", "CRD"), ("TAM", "SEA"), 
                 ("DET", "CIN"), ("WAS", "SDG"), ("NWE", "BUF"), ("KAN", "JAX")],
                [("PHI", "NYG"), ("DEN", "NYJ"), ("RAM", "RAV"), ("DAL", "CAR"), ("CRD", "CLT"), # 6
                 ("SEA", "JAX"), ("SDG", "MIA"), ("CLE", "PIT"), ("SFO", "TAM"), ("OTI", "RAI"), 
                 ("CIN", "GNB"), ("NWE", "NOR"), ("DET", "KAN"), ("BUF", "ATL"), ("CHI", "WAS")],
                [("PIT", "CIN"), ("RAM", "JAX"), ("NOR", "CHI"), ("MIA", "CLE"), ("RAI", "KAN"), # 7 
                 ("PHI", "MIN"), ("CAR", "NYJ"), ("NWE", "OTI"), ("NYG", "DEN"), ("CLT", "SDG"), 
                 ("GNB", "CRD"), ("WAS", "DAL"), ("ATL", "SFO"), ("TAM", "DET"), ("HTX", "SEA")],
                [("MIN", "SDG"), ("MIA", "ATL"), ("CHI", "RAV"), ("BUF", "CAR"), ("NYJ", "CIN"), # 8 
                 ("SFO", "HTX"), ("CLE", "NWE"), ("NYG", "PHI"), ("TAM", "NOR"), ("DAL", "DEN"), 
                 ("OTI", "CLT"), ("GNB", "PIT"), ("WAS", "KAN")],
                [("RAV", "MIA"), ("CHI", "CIN"), ("MIN", "DET"), ("CAR", "GNB"), ("DEN", "HTX"), # 9
                 ("ATL", "NWE"), ("SFO", "NYG"), ("CLT", "PIT"), ("SDG", "OTI"), ("NOR", "RAM"), 
                 ("JAX", "RAI"), ("KAN", "BUF"), ("SEA", "WAS"), ("CRD", "DAL")],
                [("RAI", "DEN"), ("ATL", "CLT"), ("NOR", "CAR"), ("NYG", "CHI"), ("JAX", "HTX"), # 10
                 ("BUF", "MIA"), ("RAV", "MIN"), ("CLE", "NYJ"), ("NWE", "TAM"), ("CRD", "SEA"), 
                 ("RAM", "SFO"), ("DET", "WAS"), ("PIT", "SDG"), ("PHI", "GNB")],
                [("NYJ", "NWE"), ("WAS", "MIA"), ("CAR", "ATL"), ("TAM", "BUF"), ("SDG", "JAX"), # 11 
                 ("CHI", "MIN"), ("GNB", "NYG"), ("CIN", "PIT"), ("HTX", "OTI"), ("SFO", "CRD"), 
                 ("SEA", "RAM"), ("RAV", "CLE"), ("KAN", "DEN"), ("DET", "PHI"), ("DAL", "RAI")], # 12
                [("BUF", "HTX"), ("NYJ", "RAV"), ("PIT", "CHI"), ("NWE", "CIN"), ("NYG", "DET"), 
                 ("MIN", "GNB"), ("CLT", "KAN"), ("SEA", "OTI"), ("JAX", "CRD"), ("CLE", "RAI"), 
                 ("PHI", "DAL"), ("ATL", "NOR"), ("TAM", "RAM"), ("CAR", "SFO")],
                [("GNB", "DET"), ("KAN", "DAL"), ("CIN", "RAV"), ("CHI", "PHI"), ("RAM", "CAR"), # 13
                 ("SFO", "CLE"), ("HTX", "CLT"), ("NOR", "MIA"), ("ATL", "NYJ"), ("CRD", "TAM"), 
                 ("JAX", "OTI"), ("MIN", "SEA"), ("RAI", "SDG"), ("BUF", "PIT"), ("DEN", "WAS"),
                 ("NYG", "NWE")],
                [("DAL", "DET"), ("SEA", "ATL"), ("PIT", "RAV"), ("OTI", "CLE"), ("CHI", "GNB"), # 14
                 ("CLT", "JAX"), ("WAS", "MIN"), ("MIA", "NYJ"), ("NOR", "TAM"), ("DEN", "RAI"), 
                 ("RAM", "CRD"), ("CIN", "BUF"), ("HTX", "KAN"), ("PHI", "SDG")],
                [("ATL", "TAM"), ("CLE", "CHI"), ("RAV", "CIN"), ("CRD", "HTX"), ("NYJ", "JAX"), # 15
                 ("SDG", "KAN"), ("BUF", "NWE"), ("WAS", "NYG"), ("RAI", "PHI"), ("GNB", "DEN"), 
                 ("DET", "RAM"), ("CAR", "NOR"), ("CLT", "SEA"), ("OTI", "SFO"), ("MIN", "DAL"),
                 ("MIA", "PIT")],
                [("RAM", "SEA"), ("NWE", "RAV"), ("TAM", "CAR"), ("BUF", "CLE"), ("SDG", "DAL"), # 16
                 ("NYJ", "NOR"), ("MIN", "NYG"), ("KAN", "OTI"), ("ATL", "CRD"), ("JAX", "DEN"), 
                 ("PIT", "DET"), ("RAI", "HTX"), ("CIN", "MIA"), ("SFO", "CLT"), ("GNB", "CHI"),
                 ("PHI", "WAS")],
                [("DAL", "WAS"), ("DET", "MIN"), ("DEN", "KAN"), ("PIT", "CLE"), ("JAX", "CLT"), # 17
                 ("TAM", "MIA"), ("NWE", "NYJ"), ("NOR", "OTI"), ("PHI", "BUF"), ("CHI", "SFO"), 
                 ("RAM", "ATL"), ("SEA", "CAR"), ("CRD", "CIN"), ("RAV", "GNB"), ("HTX", "SDG"),
                 ("NYG", "RAI")],
                [("NOR", "ATL"), ("NYJ", "BUF"), ("DET", "CHI"), ("CLE", "CIN"), ("SDG", "DEN"), # 18
                 ("CLT", "HTX"), ("OTI", "JAX"), ("CRD", "RAM"), ("KAN", "RAI"), ("GNB", "MIN"), 
                 ("MIA", "NWE"), ("DAL", "NYG"), ("WAS", "PHI"), ("RAV", "PIT"), ("SEA", "SFO"), 
                 ("CAR", "TAM")]]
fantasy_positions = ["QB", "RB", "WR", "TE", "D/ST", "K"]
defensive_positions = ['DE', 'DT', 'DL', 'LB', 'DB', 'CB', "S"]
offensive_line_positions = ["T", "G", "C", "OL"]
utility_positions = ["FB", "LS", "P"]
position_translator = {"EDGE":"DE", "SAF":"S", "OT":"T", "FS":"S", "SS":"S", "OLB":"LB",
                       "ILB":"LB", "OG":"G", "Unknown":"Unknown", "NT":"DT", "RILB":"LB",
                       "MLB":"LB", "LT":"T", "LG":"G", "RG":"G", "RT":"T"}
playersWithGrudges = {}
grudgesByMatchup = {}
final_positions = fantasy_positions + defensive_positions + offensive_line_positions + utility_positions
position_order = {"QB": 0, # fantasy
                  "RB": 1,
                  "WR": 2,
                  "TE": 3,
                  "K": 4,
                  "DE": 5, # defense
                  "DT": 6,
                  "DL": 7,
                  "OLB": 8,
                  "ILB": 9,
                  "LB": 10,
                  "CB": 11,
                  "FS": 12,
                  "SS": 13,
                  "S": 14,
                  "DB": 15,
                  "C": 16, # offensive line
                  "T": 17,
                  "G": 18,
                  "OL": 19,
                  "LS": 20, # utility
                  "P": 21,
                  "Unknown": 1000}

def welcome():
    """
    Prints a instructional message upon running the script.
    """
    print("\n" + BOLD + "Welcome to Grudge Match Detector! " + RESET + "\n")
    print("When a player squares off against his/her previous team, " +
          "it is considered a \"grudge match.\"\n")
    print("Players with " + RED + "grudges" + RESET + " often perform better than " + 
          "what is usually expected of them.\n")
    print("Use this knowledge wisely!")

def ask(q, valid_options):
    """
    Prompts user for a specific sport/team/week.

    :param q: The question we are asking (e.g. sport/team/week).
    :type q: str
    :param valid_options: The acceptable answers to the question.
    :type valid_options: list
    :return: The user's answer.
    :rtype: str
    """
    deciding = True
    while deciding:
        ans = input("\n" + q.capitalize() + "?\n").upper()
        if ans in valid_options:
            deciding = False
        else:
            print(f"\n\'{ans}\' is not a valid {q}.")
    return ans

def update_roster(sport, team):
    """
    Updates roster based on latest information from sports-reference.com.

    :param team: The professional sports team abbreviation (e.g. ATL, BOS).
    :type team: str
    """
    print(f"Grabbing latest {team} roster...")
    if sport == "NBA":
        NBARoster(team)
    if sport == "NFL":
        NFLRoster(team)    

def update_all_rosters(sport):
    """
    Updates all rosters for a sports league.

    :param team: The professional sports league (e.g. NBA, NFL).
    :type team: str
    """
    for team in teams[sport]:
        update_roster(sport, team)
        print("Sleeping for 1 minute...")
        sleep(60)

def find_grudges(t1, t2):
    """
    1. Queries database for players which currently play for team `t1` and 
    have previously played for team `t2`.
     
    2. Stores matches into global `playersWithGrudges` according to position.

    :param t1: Current team.
    :type t1: str
    :param t2: Former team.
    :type t2: str
    :returns: The list of player grudges from t1 against t2.
    :rtype: list(dict)
    """
    #print(f"\nSeeking {t1} players who have previously played for {t2}...")
    playersWithGrudges.clear()
    conn = sqlite3.connect('sportsipy/' + sport.lower() + '/players2.db')
    c = conn.cursor()
    c.execute(f"""
              SELECT player_id, name, position, team, team_history, initial_team, fantasy_pos_rk, headshot_url FROM players2 WHERE 
              sport == '{sport}' AND team == '{t1}' AND instr(team_history, '{t2}') > 0""")
    rows = c.fetchall()
    grudgeList = []
    for row in rows:
        playerId, name, position, curr_team, team_history, initial_team, fantasy_pos_rk, headshot_url = row
        years_played = ast.literal_eval(team_history)[t2]
        # format headshot url
        if not headshot_url:
            headshot_url = 'None'
        # format position
        position = position.strip()
        # format grudge type
        grudgeType = 'Grudge'
        if t2 == initial_team:
            grudgeType = 'Primary Grudge'
        # format seasons
        years_played_str = ", ".join(years_played)
        # format pos rk
        if fantasy_pos_rk == None:
            fantasy_pos_rk = 'N/A'
        # populate data object
        grudgeDict = {'headshotUrl': headshot_url,
                      'name': name,
                      'position': position,
                      'grudgeType': grudgeType,
                      'seasons': years_played_str,
                      'positionRk': fantasy_pos_rk
                      }
        grudgeList.append(grudgeDict)
    if len(grudgeList) > 1:
        grudgeListSorted = sorted(grudgeList, key=lambda x: position_order[x['position']])
        return grudgeListSorted
    else:
        return grudgeList

def print_player_grudges_js():
    """
    Find all player grudges from a week's slate of matchups and print the complete data structure.
    """
    build_me = {}
    for day, gameList in nfl_schedule[int(week)-1].items(): # week 1
        for game in gameList:
            time, awayTeam, homeTeam = game
            awayGrudges = find_grudges(awayTeam, homeTeam)
            homeGrudges = find_grudges(homeTeam, awayTeam)
            team_name_map = {'SDG': 'LAC',
                             'OTI': 'TEN',
                             'NWE': 'NE'}
            if awayTeam in team_name_map.keys():
                awayTeam = team_name_map[awayTeam]
            if homeTeam in team_name_map.keys():
                homeTeam = team_name_map[homeTeam]
            try:
                build_me[day]
            except:
                build_me[day] = []
            build_me[day].append({'time': time,
                                  'awayTeam': awayTeam,
                                  'homeTeam': homeTeam,
                                  'awayGrudges': awayGrudges,
                                  'homeGrudges': homeGrudges})
    print(build_me)

# START
welcome()
update_roster('NFL', 'TAM')
sleep(60)
update_roster('NFL', 'ATL')
#update_all_rosters('NFL')
sport = ask("sport", sports)
week = ask("week", [str(i) for i in range(1, 19)])
print_player_grudges_js()

#### NFL DEBUG
## TODO
# player1 = NFLPlayer('PiniBr00')
# print(f"Name: {player1.name}")
# print(f"Player Id: {player1.player_id}")
# print(f"Headshot URL: {player1.headshot_url}")
# print(f"Position: {player1.position}")
# print(f"Height: {player1.height}")
# print(f"Weight: {player1.weight}")
# print(f"Current Team: {player1.team_abbreviation}")
# print(f"Birth Date: {player1.birth_date}")
# print(f"Experience: {player1.season}")
# print(f"Team History: {player1.team_history}")
# print(f"Initial Team: {player1.initial_team}")
# print(f"Position Rank (Fantasy): {player1.fantasy_pos_rk}")
# print(f"Weighted Career Average Value: {player1.weighted_career_av}")

#### CCBL? 
## TODO
# - Figure out how to write to database
# - Figure out how to host on github.io website
# - Figure out front end!

#### NBA DEBUG
## TODO
## - a player grudge against his/her original team is caled a 'primary grudge' 
##   (distinguish somehow!)
##   - for this we need to collect the player's drafted team and store in new column in DB
## - sort player grudges by highest to lowest career avg minutes per game
# player1 = NBAPlayer('armstta02')
# print(f"Name: {player1.name}")
# print(f"Season(s): {player1.season}")
# print(f"Height: {player1.height}")
# print(f"Weight: {player1.weight}")
# print(f"Position: {player1.position}")
# print(f"Birth Date: {player1.birth_date}")
# print(f"Nationality: {player1.nationality}")
# print(f"Team History: {player1.team_history}")
# print(f"Current Team: {player1.team_abbreviation}")
# print(f"Games Played: {player1.games_played}")
# print(f"Games Started: {player1.games_started}")
