from django.db import models

POSITION_TYPE_CHOICES = (
    ('O', 'Offense'),
    ('D', 'Defense'),
    ('S', 'Special Teams'),
)

RESULT_CHOICES = (
    ('W', 'Win'),
    ('L', 'Loss'),
)

GAME_TYPE_CHOICES = (
    ('H', 'Home'),
    ('A', 'Away'),
    ('N', 'Neutral Site'),
)

class State(models.Model):
    id = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/states/%s/" % self.id.lower()

    class Admin:
        pass

class Conference(models.Model):
    abbrev = models.CharField(max_length=10)
    name = models.CharField(max_length=90)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/college/conferences/%s/' % self.abbrev.lower()

    class Admin:
        pass

class College(models.Model):
    name = models.CharField(max_length=90)
    slug = models.SlugField(prepopulate_from=("name",))
    state = models.ForeignKey(State, blank=True)
    conference = models.ForeignKey(Conference, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/college/teams/%s/' % self.slug

    class Admin:
        list_display = ['name', 'state']
        ordering = ('name',)
        search_fields = ('name',)

class Coach(models.Model):
    ncaa_name = models.CharField(max_length=90)
    name = models.CharField(max_length=75)
    slug = models.SlugField(prepopulate_from=('name',))
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

    class Admin:
        pass

    class Meta:
        verbose_name_plural = 'Coaches'

class CoachingJob(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(prepopulate_from=('name',))
    
    def __unicode__(self):
        return self.name
    
    class Admin:
        pass

class CollegeCoach(models.Model):
    coach = models.ForeignKey(Coach)
    college = models.ForeignKey(College)
    job = models.ForeignKey(CoachingJob)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.coach, self.college)

    class Admin:
        list_display = ['coach', 'college', 'job', 'start_date', 'end_date']

    class Meta:
        verbose_name_plural = 'College coaches'

class Position(models.Model):
    abbrev = models.CharField(max_length=5)
    name = models.CharField(max_length=25)
    plural_name = models.CharField(max_length=25)
    position_type = models.CharField(max_length=1, choices=POSITION_TYPE_CHOICES)

    def __unicode__(self):
        return self.abbrev

    def get_absolute_url(self):
        return '/recruits/positions/%s/' % self.abbrev.lower()

    class Admin:
        pass

class Game(models.Model):
    season = models.IntegerField()
    team1 = models.ForeignKey(College, related_name='first_team')
    team2 = models.ForeignKey(College, related_name='second_team')
    date = models.DateField()
    t1_game_type = models.CharField(max_length=1, choices=GAME_TYPE_CHOICES)
    t1_result = models.CharField(max_length=1, choices=RESULT_CHOICES, blank=True)
    team1_score = models.IntegerField(null=True)
    team2_score = models.IntegerField(null=True)
    
    class Admin:
        list_display = ('team1', 'team2', 'date', 't1_result', 'team1_score', 'team2_score')
        list_filter = ['t1_result', 'team1_score', 'team2_score']
    
    def __unicode__(self):
        return '%s vs. %s, %s' % (self.team1, self.team2, self.date)
    
    def get_absolute_url(self):
        return '/college/teams/%s/vs/%s/%s/' % (self.team1.slug, self.team2.slug, str(self.season))

    def get_matchup_url(self):
        return '/college/teams/%s/vs/%s/' % (self.team1.slug, self.team2.slug)
