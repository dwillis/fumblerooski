import re
import csv
import urllib
import datetime
from django.utils.encoding import smart_unicode, force_unicode
from django.db.models import Avg, Sum, Min, Max, Count
from time import strptime, strftime
import time
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
from fumblerooski.college.models import *
from fumblerooski.rankings.models import *

def next_coach_id():
    """
    Generates the next id for newly added coaches, since their slugs (which combine the id and name fields) 
    are added post-commit.
    """
    c = Coach.objects.aggregate(Max("id"))
    return c['id__max']+1

def update_conf_games(year):
    """
    Marks a game as being a conference game if teams are both in the same conference.
    """
    games = Game.objects.filter(season=year, team1__updated=True, team2__updated=True)
    for game in games:
        try:
            if game.team1.collegeyear_set.get(year=year).conference == game.team2.collegeyear_set.get(year=year).conference:
                game.is_conference_game = True
                game.save()
        except:
            pass

def update_quarter_scores(game):
    """
    Utility to update quarter scores for existing games. New games handled via ncaa_loader.
    """
    doc = urllib.urlopen(game.get_ncaa_xml_url()).read()
    soup = BeautifulSoup(doc)
    quarters = len(soup.findAll('score')[1:])/2
    t2_quarters = soup.findAll('score')[1:quarters+1] #visiting team
    t1_quarters = soup.findAll('score')[quarters+1:] #home team
    for i in range(quarters):
        vqs, created = QuarterScore.objects.get_or_create(game = game, team = game.team2, season=game.season, quarter = i+1, points = int(t2_quarters[i].contents[0]))
        hqs, created = QuarterScore.objects.get_or_create(game = game, team = game.team1, season=game.season, quarter = i+1, points = int(t1_quarters[i].contents[0]))
        
    

def update_college_year(year):
    """
    Updates season and conference records for teams. Run at the end of a game loader.
    """
    teams = CollegeYear.objects.select_related().filter(year=year, college__updated=True).order_by('college_college.id')
    for team in teams:
        games = Game.objects.filter(team1=team.college, season=year, t1_result__isnull=False).values("t1_result").annotate(count=Count("id")).order_by('t1_result')
        d = {}
        for i in range(len(games)):
            d[games[i]['t1_result']] = games[i]['count']
        try:
            wins = d['W']
        except KeyError:
            wins = 0
        try:
            losses = d['L']
        except KeyError:
            losses = 0
        try:
            ties = d['T']
        except KeyError:
            ties = 0
        if team.conference:
            conf_games = Game.objects.select_related().filter(team1=team.college, season=year, is_conference_game=True, t1_result__isnull=False).values("t1_result").annotate(count=Count("id")).order_by('t1_result')
            if conf_games:
                c = {}
                for i in range(len(conf_games)):
                    c[conf_games[i]['t1_result']] = conf_games[i]['count']
                try:
                    conf_wins = c['W']
                except KeyError:
                    conf_wins = 0
                try:
                    conf_losses = c['L']
                except KeyError:
                    conf_losses = 0
                try:
                    conf_ties = c['T']
                except KeyError:
                    conf_ties = 0
                team.conference_wins=conf_wins
                team.conference_losses=conf_losses
                team.conference_ties=conf_ties
        team.wins=wins
        team.losses=losses
        team.ties=ties
        team.save()

def add_college_years(year):
    """
    Creates college years for teams. Used at the beginning of a new season or to backfill.
    """
    teams = College.objects.filter(updated=True).order_by('id')
    for team in teams:
        cy, created = CollegeYear.objects.get_or_create(year=year, college=team)

def game_weeks(year):
    """
    Populates week foreign key for games.
    """
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
