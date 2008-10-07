import re
import csv
import urllib
import datetime
from django.utils.encoding import smart_unicode, force_unicode
from time import strptime, strftime
import time
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
from fumblerooski.college.models import State, College, Game, Coach, Position, Player, PlayerOffense, PlayerDefense, PlayerSpecial, PlayerSummary, CollegeYear, Conference, GameOffense, GameDefense, Week, GameDrive, DriveOutcome


def update_college_year(year):
    teams = College.objects.all()
    for team in teams:
        games = Game.objects.filter(team1=team, season=year)
        results = {'W':0, 'L':0, 'T':0}
        for game in games:
            results[game.t1_result] = results.get(game.t1_result, 0) +1            
        if team.conference:
            conf = Conference.objects.get(id = team.conference_id)
            conf_games = Game.objects.select_related().filter(team1=team, season=year, team2__conference=conf)
            conf_results = {'W':0, 'L':0, 'T':0}
            for conf_game in conf_games:
                conf_results[conf_game.t1_result] = conf_results.get(conf_game.t1_result, 0) +1
            conf_wins = conf_results['W']
            conf_losses = conf_results['L']
            conf_ties = conf_results['T']
        else:
            conf_wins = 0
            conf_losses = 0
            conf_ties = 0
        record, created = CollegeYear.objects.get_or_create(college=team, year=year)
        record.wins=results['W']
        record.losses=results['L']
        record.ties=results['T']
        record.conference_wins=conf_wins
        record.conference_losses=conf_losses
        record.conference_ties=conf_ties
        
        record.save()

def game_updater(year, teams, date=None):
    
    if not teams:
        teams = College.objects.filter(updated=True).order_by('id')
    
    games = []
    
    for team in teams:
        url = "http://web1.ncaa.org/football/exec/rankingSummary?org=%s&year=%s&week=15" % (team.id, year)
        html = urllib.urlopen(url).read()
        soup = BeautifulSoup(html)
        try:
            t = soup.findAll('table')[2]
            rows = t.findAll('tr')[2:]
            base_url = "http://web1.ncaa.org/d1mfb/%s/Internet/worksheets/" % year
            for row in rows:
                try:
                    game_file = row.findAll('td')[0].find('a')['href'].split('game=')[1]
                    stringdate = row.findAll('td')[0].find('a').contents[0]
                    team1_score = int(row.findAll('td')[3].contents[0])
                    team2_score = int(row.findAll('td')[4].contents[0])
                    try:
                        t1_result, ot = row.findAll('td')[5].contents[0].strip().split(' ')
                    except:
                        t1_result = row.findAll('td')[5].contents[0].strip()
                        ot = None
                except:
                    game_file = None
                    stringdate = row.findAll('td')[0].contents[0]
                    team1_score = None
                    team2_score = None
                    t1_result = None
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
                print team, team2, date, team1_score, team2_score, t1_result
                g, new_game = Game.objects.get_or_create(season=year, team1=team, team2=team2, date=date)
                g.team1_score = team1_score
                g.team2_score=team2_score
                g.t1_result=t1_result
                g.ncaa_xml = game_file.split('.xml')[0].strip()
                if ot:
                    g.ot = 't'
                try:
                    if row.findAll('td')[1].contents[0] == '+':
                        g.t1_game_type = 'H'
                    elif row.findAll('td')[1].contents[0] == '*+':
                        g.t1_game_type = 'H'
                    elif row.findAll('td')[1].contents[0] == '*':
                        g.t1_game_type = 'A'
                    elif row.findAll('td')[1].contents[0] == '^':
                        g.t1_game_type = 'N'
                    elif row.findAll('td')[1].contents[0] == '*^':
                        g.t1_game_type = 'N'
                except:
                    g.t1_game_type = 'A'
                g.save()
                game_drive_loader(g)
                games.append(base_url + game_file)
        except:
            pass
    update_college_year(year)
    return games


"""
Loader for NCAA game summaries pre-2008
url format:

http://web1.ncaa.org/d1mfb/2000/Internet/worksheets/DIVISION1.HTML
http://web1.ncaa.org/d1mfb/2000/Internet/worksheets/1200020000827.HTML
"""

def get_summary_links(year):
    """
    Given a year, retrieves urls for weekly game lists and returns all games in a list.
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

def load_ncaa_game_xml(urls):
    """
    Loader for NCAA game xml files
    url format:                year                     year000000tidyearmmdd
    http://web1.ncaa.org/d1mfb/2008/Internet/worksheets/200800000014720080830.xml
    """
    for url in urls:
        doc = urllib.urlopen(url).read()
        soup = BeautifulSoup(doc)
        # replace all interior spaces with 0
        f = soup.findAll(text="&#160;")
        for each in f:
            each.replaceWith("0")
        
        try:
            print "trying game: %s-%s" % (soup.teams.home.orgid.contents[0], soup.teams.visitor.orgid.contents[0])
            t1 = College.objects.get(id = int(soup.teams.home.orgid.contents[0]))
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
            else:
                t2 = College.objects.get(id = int(soup.teams.visitor.orgid.contents[0]))
            d = strptime(soup.gamedate.contents[0], "%m/%d/%y")
            gd = datetime.date(d[0], d[1], d[2])
        except:
            print "Could not find one of the teams"
        try:
            game, created = Game.objects.get_or_create(team1=t1, team2=t2, date=gd, season=gd.year)
            game_v,created = Game.objects.get_or_create(team1=t2, team2=t1, date=gd,season=gd.year)
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
            
        except:
            pass
#            print "Could not find game between %s and %s on %s" % (t1.name, t2.name, soup.gamedate.contents[0])
    

def game_drive_loader(game):
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
        start_time = datetime.time(0, int(cells[4].contents[0].split(":")[0]), int(cells[4].contents[0].split(":")[1]))
        try:
            start_position = int(cells[5].contents[0])
            start_side = "O"
        except:
            start_position = int(cells[5].contents[0].split(" ")[1])
            start_side = 'P'
        if start_position == '':
            start_position = 0
            start_side = 'O'
        end_result = DriveOutcome.objects.get(abbrev=str(cells[6].contents[0]))
        end_time = datetime.time(0, int(cells[7].contents[0].split(":")[0]), int(cells[7].contents[0].split(":")[1]))
        if cells[8].contents:
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
        print drive, team, quarter, start_how, start_time, start_position, start_side, end_result.abbrev, end_time, end_position, end_side, plays, yards, time_of_possession
        d, created = GameDrive.objects.get_or_create(game=game, drive=drive, team=team, quarter=quarter,start_how=str(start_how), start_time=start_time, start_position=start_position, start_side=start_side, end_result=end_result, end_time=end_time, end_position=end_position, end_side=end_side, plays=plays, yards=yards,time_of_possession=time_of_possession)
        if created:
            print "saved drive %s" % d.drive
    not_found = list(set(not_found))
    return not_found

def game_fetcher(year):
    l = get_summary_links(year)
    g = get_game_xml_url(year,l)
    for game in g:
        urllib.urlretrieve(game, game.split("worksheets/")[1])

def game_loader(year):
    l = get_summary_links(year)
    g = get_game_xml_url(year,l)
    load_ncaa_game_xml(g)

def partial_loader(year, id):
    teams = College.objects.filter(updated=True, id__gt=id).order_by('id')
    g = game_updater(2008, teams)
    load_ncaa_game_xml(g)

def last_week_updater():
    week = Week.objects.filter(year=2008, end_date__lte=datetime.date.today()).order_by('end_date')[0]
    games = Game.objects.filter(week=week)
    teams = []
    for game in games:
        teams.append(game.team1)
    g = game_updater(2008, teams)
    load_ncaa_game_xml(g)

def load_rosters(year):
    """
    Loader for NCAA roster information. Loops through all teams in the database and finds rosters for the given year, then populates Player table with
    information for each player for that year. Also adds aggregate class totals for team in CollegeYear model.
    """
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
        t = CollegeYear.objects.get(college=team, year=year)
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
        raise

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

def update_offense(yr='2007'):
    y = Year.objects.get(year=int(yr))
    py = PlayerYear.objects.select_related().filter(year=yr)
    cursor = connection.cursor()
    for player in py:
        ps = PlayerSummary.objects.get_or_create(playeryear=player)
        cursor.execute("""
            update football_playersummary 
            set rushes = (
                select sum(football_playeroffense.rushes)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            rush_gain = (
                select sum(football_playeroffense.rush_gain)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            rush_net = (
                select sum(football_playeroffense.rush_net)
                from football_playeroffense
                where football_playeroffense.playeryear_id = %s),
            rush_td = (
                select sum(football_playeroffense.rush_td)
                from football_playeroffense
                where football_playeroffense.playeryear_id = %s),
            pass_attempts = (
                select sum(football_playeroffense.pass_attempts)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            pass_complete = (
                select sum(football_playeroffense.pass_complete)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            pass_yards = (
                select sum(football_playeroffense.pass_yards)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            pass_td = (
                select sum(football_playeroffense.pass_td)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            receptions = (
                select sum(football_playeroffense.receptions)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            reception_yards = (
                select sum(football_playeroffense.reception_yards)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            reception_td = (
                select sum(football_playeroffense.reception_td)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            offense_plays = (
                select sum(football_playeroffense.offense_plays)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s),
            offense_yards = (
                select sum(football_playeroffense.offense_yards)
                from football_playeroffense 
                where football_playeroffense.playeryear_id = %s)
            where football_playersummary.playeryear_id = %s""", (player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id, player.id)
            )

def load_recruits():
    import csv
    reader = csv.reader(open("players2007.csv"))
    for row in reader:
        st = State.objects.get(id=row[5])
        p = Position.objects.get(abbrev=row[2])
        pl, created = Player.objects.get_or_create(first_name=row[0], last_name=row[1], pos=p, height=row[3], weight=row[4], home_state=st)
        pl.save()

def load_players(year):
    file = open('csv/DivIA.csv').readlines()
    file = file[1:]
    players = open('players.csv','w')
    for line in file:
        players.write(line)
    players.close()

    reader = csv.reader(open('players.csv'))
    for row in reader:
        y, created = Year.objects.get_or_create(id=year)
        t = College.objects.get(id=row[0])
        pos, created = Position.objects.get_or_create(abbrev=row[5])
        if row[4] == '':
            if row[3] != 'Team':
                first = raw_input("Enter a first name for %s on %s: " % (row[3], row[1]))
                p, created=Player.objects.get_or_create(ncaa_id=row[7], last_name=force_unicode(row[3].upper()), first_name='', first_name_fixed=force_unicode(first.upper()))
            else:
                pass
        else:
            # change to match on id and last_name only?
            p, created=Player.objects.get_or_create(ncaa_id=row[7], last_name=force_unicode(row[3].upper()), first_name=force_unicode(row[4].upper()), first_name_fixed=force_unicode(row[4].upper()))
        py, created = PlayerYear.objects.get_or_create(player=p, team=t, year=y, position=pos, number=row[2], ncaa_number=row[2], status=row[6])
