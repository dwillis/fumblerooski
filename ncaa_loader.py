import re
import csv
import urllib
import datetime
import logging
from django.utils.encoding import smart_unicode, force_unicode
from time import strptime, strftime
import time
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
from fumblerooski.college.models import State, College, CollegeCoach, Game, Position, Player, PlayerGame, PlayerRush, PlayerPass,PlayerReceiving, PlayerFumble, PlayerScoring, PlayerTackle, PlayerTacklesLoss, PlayerPassDefense, PlayerReturn, PlayerSummary, CollegeYear, Conference, GameOffense, GameDefense, Week, GameDrive, DriveOutcome, Ranking, RankingType, RushingSummary, Coach, CoachingJob
from fumblerooski.utils import update_college_year
from django.template.defaultfilters import slugify

LOG_FILENAME = 'ncaa_log.txt'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)
CURRENT_SEASON = 2009

def load_skeds(year, teams):
    if not teams:
        teams = College.objects.filter(updated=True).order_by('id')
    
    for team in teams:
        print team.id
        url = "http://web1.ncaa.org/football/exec/rankingSummary?year=%s&org=%s" % (year, team.id)
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html)
        t = soup.findAll('table')[2]
        rows = t.findAll('tr')[2:]
        for row in rows:
            stringdate = row.findAll('td')[0].contents[0]
            date = datetime.date(*(time.strptime(stringdate, '%m/%d/%Y')[0:3]))
            try:
                t2 = int(row.findAll('td')[2].find('a')['href'].split('=')[1].split('&')[0])
                try:
                    team2 = College.objects.get(id=t2)
                except:
                    name = row.findAll('td')[2].find('a').contents[0].strip()
                    slug = row.findAll('td')[2].find('a').contents[0].replace(' ','-').replace(',','').replace('.','').replace(')','').replace('(','').replace("'","").lower().strip()
                    team2, created = College.objects.get_or_create(name=name, slug=slug)
            except:
                name = row.findAll('td')[2].contents[0].strip()
                slug = row.findAll('td')[2].contents[0].replace(' ','-').replace(',','').replace('.','').replace(')','').replace('(','').lower().strip()
                team2, created = College.objects.get_or_create(name=name, slug=slug)
            g, new_game = Game.objects.get_or_create(season=year, team1=team, team2=team2, date=date)
            if "@" in row.findAll('td')[1].find('a').contents[0]:
                g.t1_game_type = 'A'
            elif "^" in row.findAll('td')[1].find('a').contents[0]:
                g.t1_game_type = 'N'
            else:
                g.t1_game_type = 'H'
            g.save()


def game_updater(year, teams, week, nostats=False):
    
    if not teams:
        teams = College.objects.filter(updated=True).order_by('id')
    
    games = []
    
    for team in teams:
        url = "http://web1.ncaa.org/football/exec/rankingSummary?org=%s&year=%s&week=%s" % (team.id, year, week)
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html)
        try:
            t = soup.findAll('table')[2]
            rows = t.findAll('tr')[2:]
            base_url = "http://web1.ncaa.org/d1mfb/%s/Internet/worksheets/" % year
            for row in rows:
                try:
                    game_file = row.findAll('td')[0].find('a')['href'].split('game=')[1]
                    stringdate = row.findAll('td')[0].find('a').contents[0][4:]
                    team1_score, team2_score = [int(x) for x in row.findAll('td')[2].contents[0].split(' - ')]
                    if len(row.findAll('td')[3].contents[0].strip().split(' ')) == 2:
                        t1_result, ot = row.findAll('td')[3].contents[0].strip().split(' ')
                    else:
                        t1_result = row.findAll('td')[3].contents[0].strip()
                        ot = None

                except:
                    game_file = None
                    stringdate = row.findAll('td')[0].contents[0][4:]
                    team1_score = None
                    team2_score = None
                    t1_result = None
                date = datetime.date(*(time.strptime(stringdate, '%m/%d/%Y')[0:3]))
                try:
                    t2 = int(row.findAll('td')[1].find('a')['href'].split('=')[1].split('&')[0])
                    try:
                        if t2 == 523:
                            team2 = College.objects.get(id=30631)
                        elif t2 == 115:   # hack job to cover for ncaa change
                            team2 = College.objects.get(id=30416)
                        else:
                            team2 = College.objects.get(id=t2)
                    except:
                        name = row.findAll('td')[1].contents[0].replace("*","").strip().title()
                        slug = slugify(name)
                        team2, created = College.objects.get_or_create(name=name, slug=slug)
                except:
                    name = row.findAll('td')[1].contents[0].replace("*","").strip().title()
                    slug = slugify(name)
                    team2, created = College.objects.get_or_create(name=name, slug=slug)
                print team, team2, date, team1_score, team2_score, t1_result
                g, new_game = Game.objects.get_or_create(season=year, team1=team, team2=team2, date=date)
                g.team1_score = team1_score
                g.team2_score=team2_score
                g.t1_result=t1_result
                g.overtime=ot
                if game_file:
                    g.ncaa_xml = game_file.split('.xml')[0].strip()
                    games.append(g)
                    if not nostats:
                        load_ncaa_game_xml(g)
                        g.has_stats = True
                        player_game_stats(g)
                        g.has_player_stats = True
                        game_drive_loader(g)
                        g.has_drives = True
                else:
                    pass
                if ot:
                    g.ot = 't'
                if "@" in row.findAll('td')[1].contents[0]:
                    g.t1_game_type = 'A'
                elif "^" in row.findAll('td')[1].contents[0]:
                    g.t1_game_type = 'N'
                elif row.findAll('td')[1].find('a') and "@" in row.findAll('td')[1].find('a').contents[0]:
                    g.t1_game_type = 'A'
                elif row.findAll('td')[1].find('a') and "^" in row.findAll('td')[1].find('a').contents[0]:
                    g.t1_game_type = 'N'
                else:
                    g.t1_game_type = 'H'
                g.save()
        except:
            raise
            logging.debug("Error in game")
    update_college_year(year)


def update_player_game_stats(s):
    games = Game.objects.filter(has_player_stats=False, season=s, ncaa_xml__startswith=s)
    for game in games:
        player_game_stats(game)
        game.has_player_stats = True
        game.save()


"""
Loader for NCAA game summaries pre-2008
url format:

http://web1.ncaa.org/d1mfb/2000/Internet/worksheets/DIVISION1.HTML
http://web1.ncaa.org/d1mfb/2000/Internet/worksheets/1200020000827.HTML
"""

def get_summary_links(year):
    """
    Given a year, retrieves urls for weekly game lists and returns all games in a list. Do NOT use for 2008 - it displays 2007 links.
    """
    base_url='http://web1.ncaa.org/d1mfb/%s/Internet/worksheets/' % year
    url = "http://web1.ncaa.org/d1mfb/%s/Internet/worksheets/DIVISION1.HTML" % year
    doc = urllib.urlopen(url).read()
    soup = BeautifulSoup(doc)
    links = soup.findAll("a")[13:]
    link_list = []
    for link in links:
        link_list.append(urljoin(base_url,link['href']))
    l2 = set(link_list)
    newlinks = list(l2)
    return newlinks


def get_game_xml_url(year, links):
    """
    Takes a list generated by get_summary_links() and retrieves the urls of individual game xml files.
    """
    games = []
    base_url = "http://web1.ncaa.org/d1mfb/%s/Internet/worksheets/" % year
    for link in links:
        doc = urllib.urlopen(link).read()
        soup = BeautifulSoup(doc)
        g_list = [a['href'].split("game=")[1] for a in soup.findAll("table")[3].findAll("a")]
        for game in g_list:
            games.append(urljoin(base_url,game))
    return games

def load_ncaa_game_xml(game):
    """
    Loader for NCAA game xml files
    """
    doc = urllib.urlopen(game.get_ncaa_xml_url()).read()
    soup = BeautifulSoup(doc)
    # replace all interior spaces with 0
    f = soup.findAll(text="&#160;")
    for each in f:
        each.replaceWith("0")
    
    try:
        print "trying game # %s: %s-%s" % (game.id, soup.teams.home.orgid.contents[0], soup.teams.visitor.orgid.contents[0])
        try:
            t1 = College.objects.get(id = int(soup.teams.home.orgid.contents[0]))
        except College.DoesNotExist:
            if soup.teams.home.orgid.contents[0] == '505632':
                t1 = College.objects.get(id=30647)
        if soup.teams.visitor.orgid.contents[0] == '506027':
            t2 = College.objects.get(id=30504) # special case for ncaa error on southern oregon
        elif soup.teams.visitor.orgid.contents[0] == '505632':
            t2 = College.objects.get(id=30505)
        elif soup.teams.visitor.orgid.contents[0] == '506123':
            t2 = College.objects.get(id=30506)
        elif soup.teams.visitor.orgid.contents[0] == '500405':
            t2 = College.objects.get(id=30513)
        elif soup.teams.visitor.orgid.contents[0] == '30077':
            t2 = College.objects.get(id=1083)
        elif soup.teams.visitor.orgid.contents[0] == '506112':
            t2 = College.objects.get(id=30514)
        elif soup.teams.visitor.orgid.contents[0] == '501982':
            t2 = College.objects.get(id=30510)
        elif soup.teams.visitor.orgid.contents[0] == '505632':
            t2 = College.objects.get(id=30647)
        elif soup.teams.visitor.orgid.contents[0] == '506116':
            t2 = College.objects.get(id=30509)
        elif soup.teams.visitor.orgid.contents[0] == '506037':
            t2 = College.objects.get(id=30636)
        elif soup.teams.visitor.orgid.contents[0] == '506083':
            t2 = College.objects.get(id=30488)
        elif soup.teams.visitor.orgid.contents[0] == '506105':
            t2 = College.objects.get(id=30635)
        elif soup.teams.visitor.orgid.contents[0] == '505260':
            t2 = College.objects.get(id=30515)
        elif soup.teams.visitor.orgid.contents[0] == '504135':
            t2 = College.objects.get(id=30561)
        elif soup.teams.visitor.orgid.contents[0] == '501555':
            t2 = College.objects.get(id=30432)
        elif soup.teams.visitor.orgid.contents[0] == '115':
            t2 = College.objects.get(id=30416)
        elif soup.teams.visitor.orgid.contents[0] == '523':
            t2 = College.objects.get(id=30631)
        else:
            t2 = College.objects.get(id = int(soup.teams.visitor.orgid.contents[0]))
        d = strptime(soup.gamedate.contents[0], "%m/%d/%y")
        gd = datetime.date(d[0], d[1], d[2])
    except:
        print "Could not find one of the teams"
        raise
    try:
        game, created = Game.objects.get_or_create(team1=t1, team2=t2, date=gd, season=CURRENT_SEASON)
        game_v,created = Game.objects.get_or_create(team1=t2, team2=t1, date=gd,season=CURRENT_SEASON)
        try:
            game.attendance = soup.attendance.contents[0]
            game_v.attendance = soup.attendance.contents[0]
        except:
            raise
        try:
            duration = soup.duration.contents[0].split(":")
            game.duration = datetime.time(int(duration[0]), int(duration[1]), 0)
            game_v.duration = game.duration
        except:
            pass
        game.save()
        game_v.save()
        
        print "Saved %s" % game
        
        while not game.has_stats:
        
        
            home_time = soup.teams.home.top.contents[0].split(":") or None
            visitor_time = soup.teams.visitor.top.contents[0].split(":") or None
        
            # home team offense
            home_offense, created = GameOffense.objects.get_or_create(game=game, team=t1)
        
            if game.date.year > 2006:
                home_offense.time_of_possession=datetime.time(0, int(home_time[0]), int(home_time[1]))
            else:
                home_offense.time_of_possession = None
        
            home_offense.third_down_attempts=int(soup.teams.home.thirddowns.att.contents[0])
            home_offense.third_down_conversions=int(soup.teams.home.thirddowns.conv.contents[0])
            home_offense.fourth_down_attempts=int(soup.teams.home.fourthdowns.att.contents[0])
            home_offense.fourth_down_conversions=int(soup.teams.home.fourthdowns.conv.contents[0])
            home_offense.first_downs_rushing=int(soup.teams.home.firstdowns.rush.contents[0])
            home_offense.first_downs_passing=int(soup.teams.home.firstdowns.contents[3].contents[0]) # can't use "pass"
            home_offense.first_downs_penalty=int(soup.teams.home.firstdowns.penalty.contents[0])
            home_offense.first_downs_total=int(soup.teams.home.firstdowns.total.contents[0])
            home_offense.penalties=int(soup.teams.home.penalties.number.contents[0])
            home_offense.penalty_yards=int(soup.teams.home.penalties.yards.contents[0])
            home_offense.fumbles=int(soup.teams.home.fumbles.number.contents[0])
            home_offense.fumbles_lost=int(soup.teams.home.fumbles.lost.contents[0])
            home_offense.rushes=int(soup.teams.home.totals.rushing.number.contents[0])
            home_offense.rush_gain=int(soup.teams.home.totals.rushing.gain.contents[0])
            home_offense.rush_loss=int(soup.teams.home.totals.rushing.loss.contents[0])
            home_offense.rush_net=int(soup.teams.home.totals.rushing.net.contents[0])
            home_offense.rush_touchdowns=int(soup.teams.home.totals.rushing.td.contents[0])
            home_offense.total_plays=int(soup.teams.home.totals.rushing.totplays.contents[0])
            home_offense.total_yards=int(soup.teams.home.totals.rushing.totyards.contents[0])
            home_offense.pass_attempts=int(soup.teams.home.totals.passing.att.contents[0])
            home_offense.pass_completions=int(soup.teams.home.totals.passing.comp.contents[0])
            home_offense.pass_interceptions=int(soup.teams.home.totals.passing.int.contents[0])
            home_offense.pass_yards=int(soup.teams.home.totals.passing.yards.contents[0])
            home_offense.pass_touchdowns=int(soup.teams.home.totals.passing.td.contents[0])
            home_offense.receptions=int(soup.teams.home.totals.receiving.number.contents[0])
            home_offense.receiving_yards=int(soup.teams.home.totals.receiving.yards.contents[0])
            home_offense.receiving_touchdowns=int(soup.teams.home.totals.receiving.td.contents[0])
            home_offense.punts=int(soup.teams.home.totals.punt.number.contents[0])
            home_offense.punt_yards=int(soup.teams.home.totals.punt.yards.contents[0])
            home_offense.punt_returns=int(soup.teams.home.totals.returns.puntnumber.contents[0])
            home_offense.punt_return_yards=int(soup.teams.home.totals.returns.puntyards.contents[0])
            home_offense.punt_return_touchdowns=int(soup.teams.home.totals.returns.punttd.contents[0])
            home_offense.kickoff_returns=int(soup.teams.home.totals.returns.konumber.contents[0])
            home_offense.kickoff_return_yards=int(soup.teams.home.totals.returns.koyards.contents[0])
            home_offense.kickoff_return_touchdowns=int(soup.teams.home.totals.returns.kotd.contents[0])
            home_offense.touchdowns=int(soup.teams.home.totals.scoring.td.contents[0])
            home_offense.pat_attempts=int(soup.teams.home.totals.scoring.offkickatt.contents[0])
            home_offense.pat_made=int(soup.teams.home.totals.scoring.offkickmade.contents[0])
            home_offense.two_point_conversion_attempts=int(soup.teams.home.totals.scoring.offrpatt.contents[0])
            home_offense.two_point_conversions=int(soup.teams.home.totals.scoring.offrpmade.contents[0])
            home_offense.field_goal_attempts=int(soup.teams.home.totals.scoring.fgatt.contents[0])
            home_offense.field_goals_made=int(soup.teams.home.totals.scoring.fgmade.contents[0])
            home_offense.points=int(soup.teams.home.totals.scoring.pts.contents[0])
        
            home_offense.save()
            print "Home Offense: %s" % home_offense
    
            # home team defense
            home_defense, created = GameDefense.objects.get_or_create(game = game, team = t1)
        
            home_defense.safeties = int(soup.teams.home.totals.scoring.saf.contents[0])
            home_defense.unassisted_tackles = int(soup.teams.home.totals.tackles.uatackles.contents[0])
            home_defense.assisted_tackles = int(soup.teams.home.totals.tackles.atackles.contents[0])
            home_defense.unassisted_tackles_for_loss = int(soup.teams.home.totals.tfl.uatfl.contents[0])
            home_defense.assisted_tackles_for_loss = int(soup.teams.home.totals.tfl.atfl.contents[0])
            home_defense.tackles_for_loss_yards = int(soup.teams.home.totals.tfl.tflyards.contents[0])
            home_defense.unassisted_sacks = int(soup.teams.home.totals.tfl.uasacks.contents[0])
            home_defense.assisted_sacks = int(soup.teams.home.totals.tfl.asacks.contents[0])
            home_defense.sack_yards = int(soup.teams.home.totals.tfl.sackyards.contents[0])
            home_defense.defensive_interceptions = int(soup.teams.home.totals.passdefense.intnumber.contents[0])
            home_defense.defensive_interception_yards = int(soup.teams.home.totals.passdefense.intyards.contents[0])
            home_defense.defensive_interception_touchdowns = int(soup.teams.home.totals.passdefense.inttd.contents[0])
            home_defense.pass_breakups = int(soup.teams.home.totals.passdefense.passbreakups.contents[0])
            home_defense.fumbles_forced = int(soup.teams.home.totals.fumbles.fumblesforced.contents[0])
            home_defense.fumbles_number = int(soup.teams.home.totals.fumbles.fumblesnumber.contents[0])
            home_defense.fumbles_yards = int(soup.teams.home.totals.fumbles.fumblesyards.contents[0])
            home_defense.fumbles_touchdowns = int(soup.teams.home.totals.fumbles.fumblestd.contents[0])
        
            home_defense.save()
            print "Home Defense: %s" % home_defense
    
            # visiting team offense
            visiting_offense, created = GameOffense.objects.get_or_create(game=game_v, team=t2)
        
            if game.date.year > 2006:
                visiting_offense.time_of_possession=datetime.time(0, int(visitor_time[0]), int(visitor_time[1]))
            else:
                visiting_offense.time_of_possession=None
        
            visiting_offense.third_down_attempts=int(soup.teams.visitor.thirddowns.att.contents[0])
            visiting_offense.third_down_conversions=int(soup.teams.visitor.thirddowns.conv.contents[0])
            visiting_offense.fourth_down_attempts=int(soup.teams.visitor.fourthdowns.att.contents[0])
            visiting_offense.fourth_down_conversions=int(soup.teams.visitor.fourthdowns.conv.contents[0])
            visiting_offense.first_downs_rushing=int(soup.teams.visitor.firstdowns.rush.contents[0])
            visiting_offense.first_downs_passing=int(soup.teams.visitor.firstdowns.contents[3].contents[0]) # can't use "pass"
            visiting_offense.first_downs_penalty=int(soup.teams.visitor.firstdowns.penalty.contents[0])
            visiting_offense.first_downs_total=int(soup.teams.visitor.firstdowns.total.contents[0])
            visiting_offense.penalties=int(soup.teams.visitor.penalties.number.contents[0])
            visiting_offense.penalty_yards=int(soup.teams.visitor.penalties.yards.contents[0])
            visiting_offense.fumbles=int(soup.teams.visitor.fumbles.number.contents[0])
            visiting_offense.fumbles_lost=int(soup.teams.visitor.fumbles.lost.contents[0])
            visiting_offense.rushes=int(soup.teams.visitor.totals.rushing.number.contents[0])
            visiting_offense.rush_gain=int(soup.teams.visitor.totals.rushing.gain.contents[0])
            visiting_offense.rush_loss=int(soup.teams.visitor.totals.rushing.loss.contents[0])
            visiting_offense.rush_net=int(soup.teams.visitor.totals.rushing.net.contents[0])
            visiting_offense.rush_touchdowns=int(soup.teams.visitor.totals.rushing.td.contents[0])
            visiting_offense.total_plays=int(soup.teams.visitor.totals.rushing.totplays.contents[0])
            visiting_offense.total_yards=int(soup.teams.visitor.totals.rushing.totyards.contents[0])
            visiting_offense.pass_attempts=int(soup.teams.visitor.totals.passing.att.contents[0])
            visiting_offense.pass_completions=int(soup.teams.visitor.totals.passing.comp.contents[0])
            visiting_offense.pass_interceptions=int(soup.teams.visitor.totals.passing.int.contents[0])
            visiting_offense.pass_yards=int(soup.teams.visitor.totals.passing.yards.contents[0])
            visiting_offense.pass_touchdowns=int(soup.teams.visitor.totals.passing.td.contents[0])
            visiting_offense.receptions=int(soup.teams.visitor.totals.receiving.number.contents[0])
            visiting_offense.receiving_yards=int(soup.teams.visitor.totals.receiving.yards.contents[0])
            visiting_offense.receiving_touchdowns=int(soup.teams.visitor.totals.receiving.td.contents[0])
            visiting_offense.punts=int(soup.teams.visitor.totals.punt.number.contents[0])
            visiting_offense.punt_yards=int(soup.teams.visitor.totals.punt.yards.contents[0])
            visiting_offense.punt_returns=int(soup.teams.visitor.totals.returns.puntnumber.contents[0])
            visiting_offense.punt_return_yards=int(soup.teams.visitor.totals.returns.puntyards.contents[0])
            visiting_offense.punt_return_touchdowns=int(soup.teams.visitor.totals.returns.punttd.contents[0])
            visiting_offense.kickoff_returns=int(soup.teams.visitor.totals.returns.konumber.contents[0])
            visiting_offense.kickoff_return_yards=int(soup.teams.visitor.totals.returns.koyards.contents[0])
            visiting_offense.kickoff_return_touchdowns=int(soup.teams.visitor.totals.returns.kotd.contents[0])
            visiting_offense.touchdowns=int(soup.teams.visitor.totals.scoring.td.contents[0])
            visiting_offense.pat_attempts=int(soup.teams.visitor.totals.scoring.offkickatt.contents[0])
            visiting_offense.pat_made=int(soup.teams.visitor.totals.scoring.offkickmade.contents[0])
            visiting_offense.two_point_conversion_attempts=int(soup.teams.visitor.totals.scoring.offrpatt.contents[0])
            visiting_offense.two_point_conversions=int(soup.teams.visitor.totals.scoring.offrpmade.contents[0])
            visiting_offense.field_goal_attempts=int(soup.teams.visitor.totals.scoring.fgatt.contents[0])
            visiting_offense.field_goals_made=int(soup.teams.visitor.totals.scoring.fgmade.contents[0])
            visiting_offense.points=int(soup.teams.visitor.totals.scoring.pts.contents[0])
        
            visiting_offense.save()
            print "Visiting Offense: %s" % visiting_offense

            # visiting team defense
            visiting_defense, created = GameDefense.objects.get_or_create(game = game_v, team = t2)

            visiting_defense.safeties = int(soup.teams.visitor.totals.scoring.saf.contents[0])
            visiting_defense.unassisted_tackles = int(soup.teams.visitor.totals.tackles.uatackles.contents[0])
            visiting_defense.assisted_tackles = int(soup.teams.visitor.totals.tackles.atackles.contents[0])
            visiting_defense.unassisted_tackles_for_loss = int(soup.teams.visitor.totals.tfl.uatfl.contents[0])
            visiting_defense.assisted_tackles_for_loss = int(soup.teams.visitor.totals.tfl.atfl.contents[0])
            visiting_defense.tackles_for_loss_yards = int(soup.teams.visitor.totals.tfl.tflyards.contents[0])
            visiting_defense.unassisted_sacks = int(soup.teams.visitor.totals.tfl.uasacks.contents[0])
            visiting_defense.assisted_sacks = int(soup.teams.visitor.totals.tfl.asacks.contents[0])
            visiting_defense.sack_yards = int(soup.teams.visitor.totals.tfl.sackyards.contents[0])
            visiting_defense.defensive_interceptions = int(soup.teams.visitor.totals.passdefense.intnumber.contents[0])
            visiting_defense.defensive_interception_yards = int(soup.teams.visitor.totals.passdefense.intyards.contents[0])
            visiting_defense.defensive_interception_touchdowns = int(soup.teams.visitor.totals.passdefense.inttd.contents[0])
            visiting_defense.pass_breakups = int(soup.teams.visitor.totals.passdefense.passbreakups.contents[0])
            visiting_defense.fumbles_forced = int(soup.teams.visitor.totals.fumbles.fumblesforced.contents[0])
            visiting_defense.fumbles_number = int(soup.teams.visitor.totals.fumbles.fumblesnumber.contents[0])
            visiting_defense.fumbles_yards = int(soup.teams.visitor.totals.fumbles.fumblesyards.contents[0])
            visiting_defense.fumbles_touchdowns = int(soup.teams.visitor.totals.fumbles.fumblestd.contents[0])

            visiting_defense.save()
            print "Visiting Defense: %s" % visiting_defense
            
            game.has_stats = True
            game.save()
            game_v.has_stats = True
            game_v.save()
            
    except:
        pass
#            print "Could not find game between %s and %s on %s" % (t1.name, t2.name, soup.gamedate.contents[0])
            
    

def game_drive_loader(game):
    while not game.has_drives:
        contents = urllib.urlopen(game.get_ncaa_drive_url().strip()).read()
        soup = BeautifulSoup(contents)
        rows = soup.findAll('table')[1].findAll("tr")[2:] # grabbing too many rows. need to tighten.
        for row in rows:
            cells = row.findAll('td')
            drive = int(cells[0].find("a").contents[0])
            print cells[2].contents[0]
            try:
                team = College.objects.get(slug=cells[2].contents[0].lower())
            except:
                team = College.objects.get(drive_slug=str(cells[2].contents[0]))
            quarter = int(cells[1].contents[0])
            start_how = cells[3].contents[0]
            start_time = datetime.time(0, int(cells[4].contents[0].split(":")[0]), int(cells[4].contents[0].split(":")[1][:2]))
            try:
                start_position = int(cells[5].contents[0])
                start_side = "O"
            except:
                try:
                    start_position = int(cells[5].contents[0].split(" ")[1])
                    start_side = 'P'
                except:
                    start_position = 0
                    start_side = 'O'
            try:
                end_result = DriveOutcome.objects.get(abbrev=str(cells[6].contents[0]))
            except:
                continue
            end_time = datetime.time(0, int(cells[7].contents[0].split(":")[0]), int(cells[7].contents[0].split(":")[1]))
            if cells[8].contents and str(cells[8].contents[0]) != 'null':
                try:
                    end_position = int(cells[8].contents[0])
                    end_side = "O"
                except:
                    end_position = int(cells[8].contents[0].split(" ")[1])
                    end_side = 'P'
            else:
                end_position = None
                end_side = 'P'
            plays = int(cells[9].contents[0])
            yards = int(cells[10].contents[0])
            time_of_possession = datetime.time(0, int(cells[11].contents[0].split(":")[0]), int(cells[11].contents[0].split(":")[1]))
            try:
                d, created = GameDrive.objects.get_or_create(game=game, drive=drive, team=team, quarter=quarter,start_how=str(start_how), start_time=start_time, start_position=start_position, start_side=start_side, end_result=end_result, end_time=end_time, end_position=end_position, end_side=end_side, plays=plays, yards=yards,time_of_possession=time_of_possession, season=game.season)
            except:
                print "Could not save drive %s, %s, %s" % (drive, game, team)


def ranking_loader(year, week):
    teams = College.objects.filter(updated=True).order_by('id')
    for team in teams:
        cy = CollegeYear.objects.get(college=team, year=year)
        w = Week.objects.get(year=year, week_num=week)
        html = urllib.urlopen(cy.get_ncaa_week_url()+str(week)).read()
        soup = BeautifulSoup(html)
        try:
            rankings = soup.findAll('table')[4]
        except:
            rankings = None
        if rankings:
            rows = rankings.findAll('tr')[5:22]
            for row in rows:
                cells = row.findAll('td')
                rt = RankingType.objects.get(name=str(cells[0].find("a").contents[0]))
                try:
                    rk =int(cells[1].contents[0])
                    i_t = False
                except ValueError:
                    rk = int(cells[1].contents[0].split('T-')[1])
                    i_t = True
        
                try:
                    cr = int(cells[5].contents[0])
                    ic_t = False
                except ValueError:
                    cr = int(cells[5].contents[0].split('T-')[1])
                    ic_t = True
        
                r, created = Ranking.objects.get_or_create(ranking_type=rt, college=team, year=year, week=w, rank=rk, is_tied = i_t, actual=float(cells[2].contents[0]), conference_rank=cr, is_conf_tied=ic_t, division = cy.division)

def load_player_rushing(year):
    url = "http://web1.ncaa.org/mfb/natlRank.jsp?year=%s&div=B&rpt=IA_playerrush&site=org" % year
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)
    rankings = soup.find('table', {'class': 'statstable'})
    rows = rankings.findAll('tr')[1:]
    d = datetime.date.today()
    if year == '2008':
        w = Week.objects.filter(end_date__lte=d, year=d.year).order_by('-week_num')[0]
    else:
        w = Week.objects.filter(year=year).order_by('-week_num')[0]
    for row in rows:
        rank = int(row.findAll('td')[0].contents[0])
        year = int(row.findAll('td')[1].find('a')['href'].split('=')[1][:4])
        team_id = int(row.findAll('td')[1].find('a')['href'].split('=')[2].split('&')[0])
        p_num = str(row.findAll('td')[1].find('a')['href'].split('=')[3])
        pos = Position.objects.get(abbrev=str(row.findAll('td')[2].contents[0]))
        carries = int(row.findAll('td')[5].contents[0])
        net = int(row.findAll('td')[6].contents[0])
        td = int(row.findAll('td')[7].contents[0])
        avg = float(row.findAll('td')[8].contents[0])
        ypg = float(row.findAll('td')[9].contents[0])
        team = College.objects.get(id=team_id)
        player = Player.objects.get(team=team, number=p_num, year=year, position=pos)
        prs, created = RushingSummary.objects.get_or_create(player=player, year=year, week=w, rank=rank, carries=carries, net=net, td=td, average=avg, yards_per_game=ypg)

def player_game_stats(game):
    while not game.has_player_stats:
        html = urllib.urlopen(game.get_ncaa_xml_url()).read()
        soup = BeautifulSoup(html)
        f = soup.findAll(text="&#160;")
        for each in f:
            each.replaceWith("0")
        if game.t1_game_type != 'A':
            try:
                team = College.objects.get(id=int(soup.teams.home.orgid.contents[0]))
                players = soup.teams.home.players.findAll('player')
            except:
                players = None
                logging.debug("No home team players for %s" % game.id)
                pass
        else:
            try:
                team = College.objects.get(id=int(soup.teams.visitor.orgid.contents[0]))
                players = soup.teams.visitor.players.findAll('player')
            except:
                players = None
                logging.debug("No visiting team players for %s" % game.id)
                pass
        if players and team.updated == True:
            for p in players:
                uniform = str(p.find("uniform").contents[0])
                name = str(p.find("name").contents[0])
                try:
                    player = Player.objects.get(team=team, year=game.season, name=name, number=uniform)
                except:
                    logging.debug("Could not find %s player: %s (%s)" % (team.name, name, uniform))
                    player = None
                    pass
                if player:
                    if p.find("totplays"):
                        total_plays=p.find("totplays").contents[0]
                    else:
                        total_plays=None
                    if p.find("totyards"):
                        total_yards=p.find("totyards").contents[0]
                    else:
                        total_yards=None
                    pg, created = PlayerGame.objects.get_or_create(player=player, game=game, played=True, total_plays=total_plays, total_yards=total_yards)
                    if p.find("tackles"):
                        un_t = int(p.find("tackles").find("uatackles").contents[0])
                        a_t = int(p.find("tackles").find("atackles").contents[0])
                        pt, created = PlayerTackle.objects.get_or_create(player=player, game=game, unassisted_tackles=un_t, assisted_tackles=a_t)
                    if p.find("tfl"):
                        un_tfl = int(p.find("tfl").find("uatfl").contents[0])
                        a_tfl = int(p.find("tfl").find("atfl").contents[0])
                        tfl_yards = int(p.find("tfl").find("tflyards").contents[0])
                        un_sacks = int(p.find("tfl").find("uasacks").contents[0])
                        a_sacks = int(p.find("tfl").find("asacks").contents[0])
                        sack_yards = int(p.find("tfl").find("sackyards").contents[0])
                        ptfl, created = PlayerTacklesLoss.objects.get_or_create(player=player, game=game, unassisted_tackles_for_loss=un_tfl, assisted_tackles_for_loss=a_tfl, tackles_for_loss_yards=tfl_yards, unassisted_sacks=un_sacks, assisted_sacks=a_sacks,sack_yards=sack_yards)
                    if p.find("passdefense"):
                        int_no = int(p.find("passdefense").find("intnumber").contents[0])
                        int_yards = int(p.find("passdefense").find("intyards").contents[0])
                        int_td = int(p.find("passdefense").find("inttd").contents[0])
                        p_b = int(p.find("passdefense").find("passbreakups").contents[0])
                        pd, created = PlayerPassDefense.objects.get_or_create(player=player, game=game, interceptions=int_no, interception_yards=int_yards, interception_td=int_td, pass_breakups=p_b)
                    if p.find("fumbles"):
                        f_f = int(p.find("fumbles").find("fumblesforced").contents[0])
                        f_n = int(p.find("fumbles").find("fumblesnumber").contents[0])
                        f_y = int(p.find("fumbles").find("fumblesyards").contents[0])
                        f_t = int(p.find("fumbles").find("fumblestd").contents[0])
                        pf, created = PlayerFumble.objects.get_or_create(player=player, game=game, fumbles_forced=f_f, fumbles_number=f_n, fumbles_yards=f_y, fumbles_td=f_t)
                    if p.find("returns"):
                        p_r = int(p.find("returns").find("puntnumber").contents[0])
                        p_y = int(p.find("returns").find("puntyards").contents[0])
                        p_t = int(p.find("returns").find("punttd").contents[0])
                        ko_n = int(p.find("returns").find("konumber").contents[0])
                        ko_y = int(p.find("returns").find("koyards").contents[0])
                        ko_t = int(p.find("returns").find("kotd").contents[0])
                        pr, created = PlayerReturn.objects.get_or_create(player=player, game=game, punt_returns=p_r, punt_return_yards=p_y, punt_return_td=p_t, kickoff_returns=ko_n, kickoff_return_yards=ko_y, kickoff_return_td=ko_t)
                    if p.find("rushing"):
                        r_n = int(p.find("rushing").find("number").contents[0])
                        r_g = int(p.find("rushing").find("gain").contents[0])
                        r_l = int(p.find("rushing").find("loss").contents[0])
                        r_net = int(p.find("rushing").find("net").contents[0])
                        r_t = int(p.find("rushing").find("td").contents[0])
                        r_long = int(p.find("rushing").find("long").contents[0])
                        try:
                            r_avg = float(p.find("rushing").find("avg").contents[0])
                        except:
                            r_avg = None
                        r_tp = int(p.find("rushing").find("totplays").contents[0])
                        r_ty = int(p.find("rushing").find("totyards").contents[0])
                        pr, created = PlayerRush.objects.get_or_create(player=player, game=game, rushes=r_n, gain=r_g, loss=r_l, net=r_net, td=r_t, long_yards=r_long, average=r_avg, total_plays=r_tp, total_yards=r_ty)
                    if p.find("passing"):
                        p_att = int(p.find("passing").find("att").contents[0])
                        p_comp = int(p.find("passing").find("comp").contents[0])
                        p_int = int(p.find("passing").find("int").contents[0])
                        p_yards = int(p.find("passing").find("yards").contents[0])
                        p_td = int(p.find("passing").find("td").contents[0])
                        p_conv = int(p.find("passing").find("conv").contents[0])
                        p_tp = int(p.find("passing").find("totplays").contents[0])
                        p_ty = int(p.find("passing").find("totyards").contents[0])
                        p_eff = float(p.find("passing").find("passeff").contents[0])
                        pp, created = PlayerPass.objects.get_or_create(player=player, game=game, attempts=p_att, completions=p_comp, interceptions=p_int, yards=p_yards, td=p_td, conversions=p_conv, total_plays=p_tp, total_yards=p_ty, pass_efficiency=p_eff)
                    if p.find("receiving"):
                        r_number = int(p.find("receiving").find("number").contents[0])
                        r_yards = int(p.find("receiving").find("yards").contents[0])
                        r_td = int(p.find("receiving").find("td").contents[0])
                        r_lg = int(p.find("receiving").find("long").contents[0])
                        r_ag = float(p.find("receiving").find("avg").contents[0])
                        prr, created = PlayerReceiving.objects.get_or_create(player=player, game=game, receptions=r_number, yards=r_yards, td=r_td, long_yards=r_lg, average=r_ag)
                    if p.find("scoring"):
                        s_td = int(p.find("scoring").find("td").contents[0])
                        fg_att = int(p.find("scoring").find("fgatt").contents[0])
                        fg_made = int(p.find("scoring").find("fgmade").contents[0])
                        pat_att = int(p.find("scoring").find("offkickatt").contents[0])
                        pat_made = int(p.find("scoring").find("offkickmade").contents[0])
                        tpt_att = int(p.find("scoring").find("offrpatt").contents[0])
                        tpt_made = int(p.find("scoring").find("offrpmade").contents[0])
                        d_pat_att = int(p.find("scoring").find("defkickatt").contents[0])
                        d_pat_made = int(p.find("scoring").find("defkickmade").contents[0])
                        d_tpt_att = int(p.find("scoring").find("defrpatt").contents[0])
                        d_tpt_made = int(p.find("scoring").find("defrpmade").contents[0])
                        saf = int(p.find("scoring").find("saf").contents[0])
                        pts = int(p.find("scoring").find("pts").contents[0])
                        ps, created = PlayerScoring.objects.get_or_create(player=player, game=game, td=s_td, fg_att=fg_att, fg_made=fg_made, pat_att=pat_att, pat_made=pat_made, two_pt_att=tpt_att, two_pt_made=tpt_made,def_pat_att=d_pat_att, def_pat_made=d_pat_made, def_two_pt_att=d_tpt_att, def_two_pt_made=d_tpt_made, safeties=saf, points=pts)
        game.has_player_stats = True
        game.save()



def stats_loader(year):
    # don't use for 2008
    l = get_summary_links(year)
    g = Game.objects.filter(season=year, has_stats=False, has_player_stats=False)
    for game in g:
        load_ncaa_game_xml(game)
        load_player_stats(game)

def partial_loader(year, id):
    teams = College.objects.filter(updated=True, id__gt=id).order_by('id')
    g = game_updater(2008, teams, 19)
    for game in g:
        load_ncaa_game_xml(g)
        load_player_stats(game)

def last_week_loader():
    week = Week.objects.filter(year=2008, end_date__lte=datetime.date.today()).order_by('end_date')[0]
    games = Game.objects.filter(week=week)
    teams = []
    for game in games:
        teams.append(game.team1)
    g = game_updater(2008, teams, week.week_num)
    for game in g:
        load_ncaa_game_xml(g)
        load_player_stats(game)

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
    team = College.objects.get(id=team_id)
    url = "http://web1.ncaa.org/football/exec/roster?year=%s&org=%s" % (year, team.id)
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)
    print team.id
    try:
        classes = soup.find("th").contents[0].split(":")[1].split(',') # retrieve class numbers for team
        fr, so, jr, sr = [int(c.strip()[0:2]) for c in classes] # assign class numbers
        t, created = CollegeYear.objects.get_or_create(college=team, year=year)
        t.freshmen = fr
        t.sophomores = so
        t.juniors = jr
        t.seniors = sr
        t.save()
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
            py, created = Player.objects.get_or_create(name=name, slug=name.lower().replace(' ','-').replace('.','').replace("'","-"), team=team, year=year, position=pos, number=unif, status=cl)
            py.games_played=gp
            py.save()
    except:
        logging.debug("No roster for %s" % team.name)
        team.updated = False
        team.save()

def load_coaches():
    import xlrd
    url1 = 'http://www.ncaa.org/wps/wcm/connect/resources/file/ebbd654a53ad23b/d1a_birthdates.xls?MOD=AJPERES'
    file = urllib.urlretrieve(url1, 'csv/coaches.xls')
    book = xlrd.open_workbook('csv/coaches.xls')
    sh = book.sheet_by_index(0)
    for rx in range(1,sh.nrows):
        n = sh.cell_value(rowx=rx, colx=0).split(' (')
        date = datetime.date(xlrd.xldate_as_tuple(sh.cell_value(rowx=rx, colx=2),0)[0], xlrd.xldate_as_tuple(sh.cell_value(rowx=rx, colx=2),0)[1], xlrd.xldate_as_tuple(sh.cell_value(rowx=rx, colx=2),0)[2])
        c, created = Coach.objects.get_or_create(ncaa_name = sh.cell_value(rowx=rx, colx=0), name = n[0], alma_mater = n[1].split(')')[0], birth_date = date)
        c.slug = c.name.lower().replace(' ','-').replace(',','-').replace('.','-').replace('--','-')
        c.save()
    url2 = 'http://www.ncaa.org/wps/wcm/connect/resources/file/ebbd1b4a538e0d9/d1a.xls?MOD=AJPERES'
    file2 = urllib.urlretrieve(url2, 'csv/coaches2.xls')
    book2 = xlrd.open_workbook('csv/coaches2.xls')
    sh2 = book2.sheet_by_index(0)
    for rx in range(1, sh2.nrows):
        c = Coach.objects.get(ncaa_name = sh2.cell_value(rowx=rx, colx=0))
        c.years = sh2.cell_value(rowx=rx, colx=2)
        c.wins = sh2.cell_value(rowx=rx, colx=3)
        c.losses = sh2.cell_value(rowx=rx, colx=4)
        c.ties = sh2.cell_value(rowx=rx, colx=5)
        c.save()
