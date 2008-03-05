from django.db import models
from fumblerooski.college.models import Coach, College, CollegeCoach, Position, State

class SchoolType(models.Model):
    name = models.CharField(max_length=15)
    slug = models.SlugField(prepopulate_from=("name",))

    def __unicode__(self):
        return self.name

    class Admin:
        pass

class City(models.Model):
    name = models.CharField(max_length=90)
    slug = models.SlugField(prepopulate_from=("name",))
    state = models.ForeignKey(State, null=True, blank=True)

    def __unicode__(self):
        return "%s, %s" % (self.name, self.state.id)

    def get_city_url(self):
        return "/recruits/states/%s/%s/" % (self.state.id.lower(), self.slug)

    class Admin:
        list_display = ['name', 'state']
        ordering = ('name',)
        search_fields = ('name',)

    class Meta:
        verbose_name_plural = 'Cities'

class School(models.Model):
    name = models.CharField(max_length=90)
    slug = models.SlugField(prepopulate_from=("name",))
    city = models.ForeignKey(City, raw_id_admin=True)
    school_type = models.ForeignKey(SchoolType)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/states/%s/%s/%s/recruits/" % (self.city.state.id.lower(), self.city.slug, self.slug)

    class Admin:
        list_display = ['name', 'city']
        search_fields = ['name']

class Player(models.Model):
    first_name = models.CharField(max_length=75)
    last_name = models.CharField(max_length=90)
    slug = models.SlugField(prepopulate_from=('id','full_name'), blank=True)
    height = models.CharField(max_length=4, blank=True)
    weight = models.PositiveIntegerField(null=True)
    position = models.ForeignKey(Position)
    home_state = models.ForeignKey(State)
    school = models.ManyToManyField(School, raw_id_admin=True)
    ncaa_id = models.IntegerField(null=True, blank=True)

    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_absolute_url(self):
        return "/players/%s/" % (self.slug)

    def __unicode__(self):
        return self.full_name()

    class Admin:
        list_display = ['full_name', 'position', 'height', 'weight', 'home_state']
        search_fields = ('last_name',)
        ordering = ('last_name', 'first_name')
    
    def save(self):
        super(Player, self).save()
        self.slug = str(self.id)+'_'+self.full_name().lower().replace(' ','_').replace(',','').replace('.','').replace("'","")
        super(Player, self).save()

class Outcome(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(prepopulate_from=("name",))
    
    def __unicode__(self):
        return self.name

    class Admin:
       pass

class Year(models.Model):
    id = models.PositiveIntegerField(primary_key=True)

    def __unicode__(self):
        return str(self.id)

    class Admin:
        pass

class Signing(models.Model):
    school = models.ForeignKey(College, raw_id_admin=True)
    player = models.ForeignKey(Player, raw_id_admin=True)
    year = models.ForeignKey(Year)
    outcome = models.ForeignKey(Outcome, blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.school, self.player)

    def player_position(self):
        return self.player.position

    class Admin:
        list_display = ['player', 'player_position', 'school', 'year']
        search_fields = ['player__last_name']