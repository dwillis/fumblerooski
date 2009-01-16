import re
import csv
import urllib
import datetime
from django.utils.encoding import smart_unicode, force_unicode
from time import strptime, strftime
import time
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup
from fumblerooski.college.models import State, College, CollegeCoach, Game, Position, Player, PlayerGame, PlayerRush, PlayerPass,PlayerReceiving, PlayerFumble, PlayerScoring, PlayerTackle, PlayerTacklesLoss, PlayerPassDefense, PlayerReturn, PlayerSummary, CollegeYear, Conference, GameOffense, GameDefense, Week, GameDrive, DriveOutcome, Ranking, RankingType, RushingSummary
from fumblerooski.coaches.models import Coach, CoachingJob

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

def add_college_years(year):
    teams = College.objects.filter(updated=True).order_by('id')
    for team in teams:
        cy, created = CollegeYear.objects.get_or_create(year=year, college=team)

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
