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

"""
The functions here are a collection of utilities that help with data loading 
or otherwise populate records that are not part of the scraping process.
"""

def create_missing_collegeyears(year):
    """
    Create collegeyears where they are missing (legacy data only).
    >>> create_missing_collegeyears(2009)
    """
    games = Game.objects.filter(season=year)
    for game in games:
        try:
            game.team1
        except CollegeYear.DoesNotExist:
            try:
                c = College.objects.get(pk=game.team1_id)
                cy, created = CollegeYear.objects.get_or_create(college=c, season=year)
                if created:
                    print "created CollegeYear for %s in %s" % (c, year)
            except:
                print "Could not find a college for %s" % game.team1_id

def opposing_coaches(coach):
    coach_list = Coach.objects.raw("SELECT college_coach.id, college_coach.slug, count(college_game.*) as games from college_coach inner join college_game on college_coach.id = college_game.coach2_id where coach1_id = %s group by 1,2 order by 3 desc", [coach.id])
    return coach_list

def calculate_team_year(year, month):
    if int(month) < 8:
        team_year = int(year)-1
    else:
        team_year = int(year)
    return team_year

def calculate_record(totals):
    """
    Given a dictionary of game results, calculates the W-L-T record from those games.
    Used to calculate records for team vs opponent and coach vs coach views.
    """
    d = {}
    for i in range(len(totals)):
        d[totals[i]['t1_result']] = totals[i]['count']
    try:
        wins = d['W']
    except KeyError:
        wins = 0
    try:
        losses = d['L'] or None
    except KeyError:
        losses = 0
    try:
        ties = d['T']
    except KeyError:
        ties = 0
    return wins, losses, ties

def last_home_loss_road_win(games):
    """
    Given a list of games, returns the most recent home loss and road win.
    """    
    try:
        last_home_loss = games.filter(t1_game_type='H', t1_result='L')[0]
    except:
        last_home_loss = None
    try:
        last_road_win = games.filter(t1_game_type='A', t1_result='W')[0]
    except:
        last_road_win = None
    return last_home_loss, last_road_win
    
    
def set_head_coaches():
    """
    One-time utility to add a boolean value to college coach records. Used to prepare
    the populate_head_coaches function for games. 
    """
    cc = CollegeCoach.objects.select_related().filter(jobs__name='Head Coach').update(is_head_coach=True)

def populate_head_coaches(game):
    """
    Given a game, tries to find and save the head coaches for that game. 
    If it cannot, it leaves the head coaching fields as 0. Can be run on
    an entire season or as part of the game loader. As college coach data
    grows, will need to be run periodically on games without head coaches:
    
    >>> games = Game.objects.filter(coach1__isnull=True, coach2__isnull=True)
    >>> for game in games:
    ...     populate_head_coaches(game)
    ...
    """
    try:
        hc = game.team1.collegecoach_set.filter(is_head_coach=True).order_by('-start_date')
        if hc.count() > 0:
            if hc.count() == 1:
                game.coach1 = hc[0].coach
            else:
                coach1, coach2 = [c for c in hc]
                if coach1.end_date:
                    if game.date < coach1.end_date:
                        game.coach1 = coach1.coach
                    elif game.date >= coach2.start_date:
                        game.coach1 = coach2.coach
                    else:
                        game.coach1_id = 0                
        else:
            game.coach1_id = 0
    except:
        game.coach1_id = 0
    game.save()
    
    try:
        hc2 = game.team2.collegecoach_set.filter(is_head_coach=True).order_by('-start_date')
        if hc2.count() > 0:
            if hc2.count() == 1:
                game.coach2 = hc2[0].coach
            else:
                coach1, coach2 = [c for c in hc2]
                if coach1.end_date:
                    if game.date < coach1.end_date:
                        game.coach2 = coach1.coach
                    elif game.date >= coach2.start_date:
                        game.coach2 = coach2.coach
                    else:
                        game.coach2_id = 0                
        else:
            game.coach2_id = 0
    except:
        game.coach2_id = 0
    game.save()

def next_coach_id():
    """
    Generates the next id for newly added coaches, since their slugs (which combine the id and name fields) 
    are added post-commit.
    """
    c = Coach.objects.aggregate(Max("id"))
    return c['id__max']+1

def update_conference_membership(year):
    # check prev year conference and update current year with it, then mark conf games.
    previous_year = year-1
    teams = CollegeYear.objects.filter(season=previous_year, conference__isnull=False)
    for team in teams:
        cy = CollegeYear.objects.get(season=year, college=team.college)
        cy.conference = team.conference
        cy.save()
    

def update_conf_games(year):
    """
    Marks a game as being a conference game if teams are both in the same conference.
    """
    games = Game.objects.filter(season=year, team1__college__updated=True, team2__college__updated=True)
    for game in games:
        try:
            if game.team1.conference == game.team2.conference:
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
    teams = CollegeYear.objects.select_related().filter(season=year, college__updated=True).order_by('college_college.id')
    for team in teams:
        games = Game.objects.filter(team1=team.college, season=year, t1_result__isnull=False).values("t1_result").annotate(count=Count("id")).order_by('t1_result')
        d = {}
        for i in range(games.count()):
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
                for i in range(conf_games.count()):
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
    teams = College.objects.all().order_by('id')
    for team in teams:
        cy, created = CollegeYear.objects.get_or_create(season=year, college=team)

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
        new_week, created = Week.objects.get_or_create(season=min.year, week_num = week, end_date = end_date)
        date += datetime.timedelta(days=7)
        week += 1      

def game_weeks(year):
    """
    Populates week foreign key for games.
    """
    weeks = Week.objects.filter(season=year).order_by('week_num')
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
