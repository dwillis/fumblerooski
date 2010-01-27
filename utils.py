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

def create_weeks(year):
    """
    Given a year with games in the db, creates weeks for that year.
    """
    
    min = Game.objects.filter(season=year).aggregate(Min('date'))['date__min']
    max = Game.objects.filter(season=year).aggregate(Max('date'))['date__max']
    date = min
    week = 1
    while date <= max:
        if date.weekday() < 5:
            dd = 5 - date.weekday()
            end_date = date + datetime.timedelta(days=dd)
        else:
            end_date = date
        new_week, created = Week.objects.get_or_create(year=min.year, week_num = week, end_date = end_date)
        date += datetime.timedelta(days=7)
        week += 1      

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

def advance_coaching_staff(team, year):
    """
    Takes an existing coaching staff, minus any who have an end_date value,
    and creates new CollegeCoach records for them in the provided year.

    Usage:    
    >>> from fumblerooski.utils import advance_coaching_staff
    >>> from fumblerooski.college.models import *
    >>> team = College.objects.get(id = 8)
    >>> advance_coaching_staff(team, 2010)
    """
    previous_year = int(year)-1
    college = College.objects.get(id=team.id)
    old_cy = CollegeYear.objects.get(college=college, year=previous_year)
    new_cy = CollegeYear.objects.get(college=college, year=year)
    old_staff = CollegeCoach.objects.filter(collegeyear=old_cy, end_date__isnull=True)
    for coach in old_staff:
        cc, created = CollegeCoach.objects.get_or_create(collegeyear=new_cy, coach=coach.coach)
        for job in coach.jobs.all():
            cc.jobs.add(job)
