from django.db import models
from fumblerooski.college.models import College, Player, Week

RANKINGTYPE_CHOICES = (
    ('T', 'Team'),
    ('P', 'Player'),
)

class RankingType(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    typename = models.CharField(max_length=1, choices=RANKINGTYPE_CHOICES)
    ncaa_name = models.CharField(max_length=75)
    
    def __unicode__(self):
        return self.name
    
    def get_current_url(self):
        return "/college/rankings/%s/%s/" % (self.slug, CURRENT_SEASON)
    
    def get_partial_url(self):
        return "/college/rankings/%s/" % self.slug
    

class Ranking(models.Model):
    ranking_type = models.ForeignKey(RankingType)
    college = models.ForeignKey(College)
    year = models.IntegerField()
    week = models.ForeignKey(Week)
    rank = models.PositiveIntegerField()
    is_tied = models.BooleanField()
    actual = models.FloatField()
    conference_rank = models.PositiveIntegerField(null=True)
    is_conf_tied = models.BooleanField()
    division = models.CharField(max_length=1)
    
    def __unicode__(self):
        return "%s - %s, %s (%s)" % (self.ranking_type, self.college, self.year, self.week)
    
    def get_week_url(self):
        return "/college/rankings/%s/%s/week/%s/" % (self.ranking_type.slug, self.year, self.week.week_num)

class RushingSummary(models.Model):
    player = models.ForeignKey(Player)
    year = models.IntegerField()
    week = models.ForeignKey(Week)
    rank = models.PositiveIntegerField()
    is_tied = models.BooleanField()
    carries = models.PositiveIntegerField()
    net = models.PositiveIntegerField()
    td = models.PositiveIntegerField()
    average = models.FloatField()
    yards_per_game = models.FloatField()
    
    def __unicode__(self):
        return "%s - %s, %s" (self.player, self.year, self.yards_per_game)

class PassEfficiency(models.Model):
    player = models.ForeignKey(Player)
    year = models.IntegerField()
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
    
    def __unicode__(self):
        return self.player.name
