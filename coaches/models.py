from django.db import models
from fumblerooski.college.models import CollegeYear

class Coach(models.Model):
    ncaa_name = models.CharField(max_length=90)
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    alma_mater = models.CharField(max_length=75)
    birth_date = models.DateField(null=True, blank=True)
    years = models.IntegerField(default=0, blank=True)
    wins = models.IntegerField(default=0, blank=True)
    losses = models.IntegerField(default=0, blank=True)
    ties = models.IntegerField(default=0, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/college/coaches/%s/' % self.slug

    class Meta:
        verbose_name_plural = 'Coaches'

class CoachingJob(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    
    def __unicode__(self):
        return self.name


class CollegeCoach(models.Model):
    coach = models.ForeignKey(Coach)
    collegeyear = models.ForeignKey(CollegeYear)
    job = models.ForeignKey(CoachingJob)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.coach, self.collegeyear)
    
    def is_current_job(self):
        if self.collegeyear.year == CURRENT_SEASON and self.end_date == None:
            return True
        else:
            return False

    class Meta:
        verbose_name_plural = 'College coaches'