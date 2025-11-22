import re
import csv
import urllib.request
import datetime
from time import strptime, strftime
import time
from bs4 import BeautifulSoup
from fumblerooski.college.models import College, Game, CollegeYear, Player, Position
    

def load_skeds(year, teams):
    """
    Loads the game schedules for teams for a given year. Defaults to all teams where updated = True,
    but can be passed in a selection of teams.
    >>> teams = CollegeYear.objects.filter(college__id__IN=(123,345,435))
    >>> load_skeds(2009, teams)
    """
    if not teams:
        teams = CollegeYear.objects.filter(college__updated=True).order_by('id')
    
    for team in teams:
        url = "http://web1.ncaa.org/football/exec/rankingSummary?year=%s&org=%s" % (year, team.id)
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html)
        t = soup.findAll('table')[2]
        rows = t.findAll('tr')[2:]
        for row in rows:
            stringdate = row.findAll('td')[0].contents[0]
            date = datetime.date(*(time.strptime(stringdate, '%m/%d/%Y')[0:3]))
            try:
                t2 = int(row.findAll('td')[2].find('a')['href'].split('=')[1].split('&')[0])
                try:
                    team2 = CollegeYear.objects.get(college__id=t2, year=year)
                except:
                    name = row.findAll('td')[2].find('a').contents[0].strip()
                    slug = row.findAll('td')[2].find('a').contents[0].replace(' ','-').replace(',','').replace('.','').replace(')','').replace('(','').replace("'","").lower().strip()
                    c2, created = College.objects.get_or_create(name=name, slug=slug)
                    team2, created = CollegeYear.objects.get_or_create(college=c2, year=year)
            except:
                name = row.findAll('td')[2].contents[0].strip()
                slug = row.findAll('td')[2].contents[0].replace(' ','-').replace(',','').replace('.','').replace(')','').replace('(','').lower().strip()
                c2, created = College.objects.get_or_create(name=name, slug=slug)
                team2, created = CollegeYear.objects.get_or_create(college=c2, year=year)
            g, new_game = Game.objects.get_or_create(season=year, team1=team, team2=team2, date=date)
            if "@" in row.findAll('td')[1].find('a').contents[0]:
                g.t1_game_type = 'A'
            elif "^" in row.findAll('td')[1].find('a').contents[0]:
                g.t1_game_type = 'N'
            else:
                g.t1_game_type = 'H'
            g.save()


def load_rosters(year, teams=None):
    """
    Loader for NCAA roster information. Loops through all teams in the database and finds rosters for the given year, then populates Player table with
    information for each player for that year. Also adds aggregate class totals for team in CollegeYear model.
    """
    if not teams:
        teams = College.objects.filter(updated=True).order_by('id')
    for team in teams:
        load_team(team.id, year)

def load_team(team_id, year):
    """
    Loads information about a single team during a single year. Includes total number of players by class,
    and also gets/creates individual Player objects and updates with the number of games played.
    >>> load_team(235, 2009)
    """
    team = CollegeYear.objects.get(college__id=team_id, season=year)
    url = "http://web1.ncaa.org/football/exec/roster?year=%s&org=%s" % (year, team_id)
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html)
    try:
        classes = soup.find("th").contents[0].split(":")[1].split(',') # retrieve class numbers for team
        fr, so, jr, sr = [int(c.strip()[0:2]) for c in classes] # assign class numbers
        team.freshmen = fr
        team.sophomores = so
        team.juniors = jr
        team.seniors = sr
        team.save()
        rows = soup.findAll("tr")[5:]
        for row in rows:
            cells = row.findAll("td")
            unif = cells[0].contents[0].strip()
            name = cells[1].a.contents[0].strip()
            if cells[2].contents[0].strip() == '-':
                pos = Position.objects.get(id=17)
            else:
                pos, created = Position.objects.get_or_create(abbrev=cells[2].contents[0].strip())
            cl = cells[3].contents[0].strip()
            gp = int(cells[4].contents[0].strip())
            py, created = Player.objects.get_or_create(name=name, slug=name.lower().replace(' ','-').replace('.','').replace("'","-"), team=team, season=year, position=pos, number=unif, status=cl)
            py.games_played=gp
            py.save()
    except:
        team.college.updated = False
        team.college.save()
