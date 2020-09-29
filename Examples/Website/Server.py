# importing flask framework to make a server
from sportsreference.nba.teams import Teams as TNBA
from sportsreference.nhl.teams import Teams as TNHL
from flask import Flask, render_template
# importing sportsreference


def getNameNBA():
    team_name = []
    teams = TNBA()
    for team in teams:
        team_name.append(team.name)
    return team_name[:5]


def getNameNHL():
    team_name_h = []
    teams = TNHL()
    for i in teams:
        team_name_h.append(i)
    return team_name_h[:5]


app = Flask(__name__)  # initializing flask


@app.route("/")
def home():
    names = str(getNameNBA())
    return render_template("index.html", name=names)


@app.route("/hockey")
def hockey():
    names = str(getNameNHL())
    return render_template("hockey.html", names=names)


@app.route("/basketball")
def basketball():
    return render_template("basketball.html")


if __name__ == "__main__":
    app.run()
