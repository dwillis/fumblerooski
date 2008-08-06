from django.db import models
from fumblerooski.college.models import Coach, College, CollegeCoach, Position, State

class SchoolType(models.Model):
    name = models.CharField(max_length=15)
    slug = models.SlugField(max_length=15)

    def __unicode__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=90)
    slug = models.SlugField(max_length=90)
    state = models.ForeignKey(State, null=True, blank=True)

    def __unicode__(self):
        return "%s, %s" % (self.name, self.state.id)

    def get_city_url(self):
        return "/recruits/states/%s/%s/" % (self.state.id.lower(), self.slug)

    class Meta:
        verbose_name_plural = 'Cities'

class School(models.Model):
    name = models.CharField(max_length=90)
    slug = models.SlugField(max_length=90)
    city = models.ForeignKey(City)
    school_type = models.ForeignKey(SchoolType)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/states/%s/%s/%s/recruits/" % (self.city.state.id.lower(), self.city.slug, self.slug)

class Recruit(models.Model):
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=90)
    slug = models.SlugField(max_length=90, blank=True)
    height = models.CharField(max_length=4, blank=True)
    weight = models.PositiveIntegerField(null=True)
    position = models.ForeignKey(Position)
    home_state = models.ForeignKey(State)
    school = models.ManyToManyField(School)
    ncaa_id = models.IntegerField(null=True, blank=True)

    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_absolute_url(self):
        return "/recruits/%s/" % (self.slug)

    def __unicode__(self):
        return self.full_name()

    def save(self):
        super(Recruit, self).save()
        self.slug = str(self.id)+'_'+self.full_name().lower().replace(' ','_').replace(',','').replace('.','').replace("'","")
        super(Recruit, self).save()

class Outcome(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    
    def __unicode__(self):
        return self.name

class Year(models.Model):
    id = models.PositiveIntegerField(primary_key=True)

    def __unicode__(self):
        return str(self.id)

class Signing(models.Model):
    school = models.ForeignKey(College)
    player = models.ForeignKey(Recruit)
    year = models.ForeignKey(Year)
    outcome = models.ForeignKey(Outcome, blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.school, self.player)

    def player_position(self):
        return self.player.position
