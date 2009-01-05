import re
import csv
import urllib
import datetime
from django.utils.encoding import smart_unicode, force_unicode
from time import strptime, strftime
import time
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
from fumblerooski.college.models import State, College, Game, Position, Player, PlayerGame, PlayerRush, PlayerPass,PlayerReceiving, PlayerFumble, PlayerScoring, PlayerTackle, PlayerTacklesLoss, PlayerPassDefense, PlayerReturn, PlayerSummary, CollegeYear, Conference, GameOffense, GameDefense, Week, GameDrive, DriveOutcome, Ranking, RankingType, RushingSummary
from fumblerooski.coaches.models import Coach, CoachingJob, CollegeCoach

def update_conf_games(year):
    games = Game.objects.filter(season=year, team1__updated=True, team2__updated=True)
    for game in games:
        if game.team1.collegeyear_set.get(year=year).conference == game.team2.collegeyear_set.get(year=year).conference:
            game.is_conference_game = True
            game.save()

def update_college_year(year):
    teams = CollegeYear.objects.select_related().filter(year=year, college__updated=True).order_by('college_college.id')
    for team in teams:
        games = Game.objects.filter(team1=team.college, season=year)
        results = {'W':0, 'L':0, 'T':0}
        for game in games:
            results[game.t1_result] = results.get(game.t1_result, 0) +1
        if team.conference:
            conf_games = Game.objects.select_related().filter(team1=team.college, season=year, is_conference_game=True)
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
        team.wins=results['W']
        team.losses=results['L']
        team.ties=results['T']
        team.conference_wins=conf_wins
        team.conference_losses=conf_losses
        team.conference_ties=conf_ties
        
        team.save()

def game_updater(year, teams, week):
    
    if not teams:
        teams = College.objects.filter(updated=True).order_by('id')
    
    games = []
    
    for team in teams:
        print team.id
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
                    stringdate = row.findAll('td')[0].find('a').contents[0]
                    team1_score = int(row.findAll('td')[3].contents[0])
                    team2_score = int(row.findAll('td')[4].contents[0])
                    if len(row.findAll('td')[5].contents[0].strip().split(' ')) == 2:
                        t1_result, ot = row.findAll('td')[5].contents[0].strip().split(' ')
                    else:
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
                g.overtime=ot
                if game_file:
                    g.ncaa_xml = game_file.split('.xml')[0].strip()
                    games.append(g)
                    if not g.has_stats:
                        load_ncaa_game_xml(g)
                        g.has_stats = True
                    if not g.has_player_stats:
                        player_game_stats(g)
                        g.has_player_stats = True
                    if not g.has_drives:
                        game_drive_loader(g)
                        g.has_drives = True
                else:
                    pass
                if ot:
                    g.ot = 't'
                if len(row.findAll('td')[1].contents) > 0:
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
                else:
                    g.t1_game_type = 'A'
                g.save()
        except:
            raise
    update_college_year(year)



def game_weeks(year):
    weeks = Week.objects.filter(year=year).order_by('week_num')
    for week in weeks:
        games = Game.objects.filter(season=year, date__lte=week.end_date, week__isnull=True)
        for game in games:
            game.week = week
            game.save()


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
