from django.db import models

CURRENT_SEASON = 2009

class Coach(models.Model):
    ncaa_name = models.CharField(max_length=90)
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    alma_mater = models.CharField(max_length=75)
    birth_date = models.DateField(null=True, blank=True)
    years = models.IntegerField(default=0, blank=True)
    wins = models.IntegerField(default=0, blank=True)
    losses = models.IntegerField(default=0, blank=True)
    ties = models.IntegerField(default=0, blank=True)

    def __unicode__(self):
        return self.first_name + " " + self.last_name

    def get_absolute_url(self):
        return '/college/coaches/%s/' % self.slug
    
    def full_name(self):
        return self.first_name + " " + self.last_name
    
    def current_school(self):
        try:
            current_school = self.collegecoach_set.get(collegeyear__year__exact = CURRENT_SEASON, end_date = None).collegeyear.college
        except:
            current_school = None
        return current_school
    
    def current_job(self):
        if self.current_school():
            cy = self.collegecoach_set.filter(collegeyear__college=self.current_school).order_by('start_date')[0]
            return cy
        else:
            return None
    
    class Meta:
        ordering = ['last_name']
        verbose_name_plural = 'Coaches'
        db_table = 'college_coach'

class CoachingJob(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = 'college_coachingjob'