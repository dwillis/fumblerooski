import datetime
from django.db import models
from fumblerooski.college.models import College, Player, Week, CollegeYear
from django.conf import settings

if datetime.date.today().month < 8:
    CURRENT_SEASON = datetime.date.today().year-1
else:
    CURRENT_SEASON = datetime.date.today().year-1

RANKINGTYPE_CHOICES = (
    ('T', 'Team'),
    ('P', 'Player'),
)

class RankingType(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    typename = models.CharField(max_length=1, choices=RANKINGTYPE_CHOICES)
    ncaa_name = models.CharField(max_length=75)
    
    def __str__(self):
        return self.name
    
    def get_current_url(self):
        return "/rankings/%s/%s/" % (self.slug, CURRENT_SEASON)
    
    def get_partial_url(self):
        return "/rankings/%s/" % self.slug
        
    def year_list(self):
        return list(set([y.season for y in self.ranking_set.all()]))    

class Ranking(models.Model):
    ranking_type = models.ForeignKey(RankingType)
    collegeyear = models.ForeignKey(CollegeYear)
    season = models.IntegerField(db_index=True)
    week = models.ForeignKey(Week)
    rank = models.PositiveIntegerField()
    is_tied = models.BooleanField()
    actual = models.FloatField()
    conference_rank = models.PositiveIntegerField(null=True)
    is_conf_tied = models.BooleanField()
    division = models.CharField(max_length=1)
    
    def __str__(self):
        return "%s - %s (%s)" % (self.ranking_type, self.collegeyear, self.week)
    
    def get_week_url(self):
        return "/rankings/%s/%s/week/%s/" % (self.ranking_type.slug, self.year, self.week.week_num)

class RushingSummary(models.Model):
    player = models.ForeignKey(Player)
    season = models.IntegerField()
    week = models.ForeignKey(Week)
    rank = models.PositiveIntegerField()
    is_tied = models.BooleanField()
    carries = models.PositiveIntegerField()
    net = models.PositiveIntegerField()
    td = models.PositiveIntegerField()
    average = models.FloatField()
    yards_per_game = models.FloatField()
    
    def __str__(self):
        return "%s - %s, %s" % (self.player, self.year, self.yards_per_game)

class PassEfficiency(models.Model):
    player = models.ForeignKey(Player)
    season = models.IntegerField()
    week = models.ForeignKey(Week)
    rank = models.PositiveIntegerField()
    attempts = models.PositiveIntegerField()
    completions = models.PositiveIntegerField()
    completion_pct = models.FloatField()
    interceptions = models.PositiveIntegerField()
    attempts_per_interception = models.FloatField()
    yards = models.PositiveIntegerField()
    yards_per_attempt = models.FloatField()
    touchdowns = models.PositiveIntegerField()
    attempts_per_touchdown = models.FloatField()
    rating = models.FloatField()
    
    def __str__(self):
        return self.player.name
