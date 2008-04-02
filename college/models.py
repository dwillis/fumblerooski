from django.db import models
from django import newforms as forms
#from fumblerooski.recruits.models import Year

STATUS_CHOICES = (
    ('FR', 'Freshman'),
    ('SO', 'Sophomore'),
    ('JR', 'Junior'),
    ('SR', 'Senior'),
)

POSITION_TYPE_CHOICES = (
    ('O', 'Offense'),
    ('D', 'Defense'),
    ('S', 'Special Teams'),
)

RESULT_CHOICES = (
    ('W', 'Win'),
    ('L', 'Loss'),
    ('T', 'Tie'),
)

GAME_TYPE_CHOICES = (
    ('H', 'Home'),
    ('A', 'Away'),
    ('N', 'Neutral Site'),
)

class State(models.Model):
    id = models.CharField(max_length=2, primary_key=True, editable=False)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/states/%s/" % self.id.lower()

    class Admin:
        pass
    
class StateForm(forms.Form):
    name = forms.CharField(max_length=50, widget=forms.Select())

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
    official_url = models.CharField(max_length=120, blank=True)
    official_rss = models.CharField(max_length=120, blank=True)
    conference = models.ForeignKey(Conference, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/college/teams/%s/' % self.slug

    class Admin:
        list_display = ['name', 'state']
        ordering = ('name',)
        search_fields = ('name',)

class CollegeYear(models.Model):
    college = models.ForeignKey(College)
    year = models.IntegerField()
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    ties = models.IntegerField(default=0)
    conference_wins = models.IntegerField(default=0)
    conference_losses = models.IntegerField(default=0)
    conference_ties = models.IntegerField(default=0)
    
    def __unicode__(self):
        return "%s - %s" % (self.college, str(self.year))
    
    class Admin:
        pass

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
    site = models.CharField(max_length=90, blank=True)
    
    class Admin:
        list_display = ('team1', 'team2', 'date', 't1_result', 'team1_score', 'team2_score')
        list_filter = ['t1_result', 'team1_score', 'team2_score']
    
    def __unicode__(self):
        return '%s vs. %s, %s' % (self.team1, self.team2, self.date)
    
    def get_absolute_url(self):
        return '/college/teams/%s/vs/%s/%s/' % (self.team1.slug, self.team2.slug, str(self.season))

    def get_matchup_url(self):
        return '/college/teams/%s/vs/%s/' % (self.team1.slug, self.team2.slug)

class Player(models.Model):
    ncaa_id = models.IntegerField(primary_key=True)
    last_name = models.CharField(max_length=90)
    first_name = models.CharField(max_length=75, blank=True)
    first_name_fixed = models.CharField(max_length=75, blank=True)
    
    class Admin:
        pass
        
    def __unicode__(self):
        return "%s %s" % (self.first_name_fixed, self.last_name)

class PlayerYear(models.Model):
    player = models.ForeignKey(Player)
    team = models.ForeignKey(College)
    year = models.IntegerField()
    position = models.ForeignKey(Position)
    number = models.CharField(max_length=4)
    ncaa_number = models.CharField(max_length=3)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    
    class Admin:
        pass
        
    def __unicode__(self):
        return "%s - %s" % (self.player, self.year)

class PlayerScore(models.Model):
    playeryear = models.ForeignKey(PlayerYear)
    game = models.ForeignKey(Game)
    total_td = models.IntegerField()
    total_points = models.IntegerField()

    class Admin:
        list_display = ('playeryear', 'game', 'total_td', 'total_points')
    
    def __unicode__(self):
        return self.playeryear.player.full_name()

class PlayerOffense(models.Model):
    playeryear = models.ForeignKey(PlayerYear)
    game = models.ForeignKey(Game)
    rushes = models.IntegerField()
    rush_gain = models.IntegerField()
    rush_loss = models.IntegerField()
    rush_net = models.IntegerField()
    rush_td = models.IntegerField()
    pass_attempts = models.IntegerField()
    pass_complete = models.IntegerField()
    pass_intercept = models.IntegerField()
    pass_yards = models.IntegerField()
    pass_td = models.IntegerField()
    conversions = models.IntegerField()
    offense_plays = models.IntegerField()
    offense_yards = models.IntegerField()
    receptions = models.IntegerField()
    reception_yards = models.IntegerField()
    reception_td = models.IntegerField()

    def yards_per_rush(self):
        return self.rush_net/self.rushes

    def yards_per_attempt(self):
        return self.pass_yards/self.pass_attempts

    def yards_per_catch(self):
        return self.reception_yards/self.receptions

    class Admin:
        pass
        
    def __unicode__(self):
        return "%s - %s" % (self.playeryear.player, self.game)

class PlayerDefense(models.Model):
    playeryear = models.ForeignKey(PlayerYear)
    game = models.ForeignKey(Game)
    interceptions = models.IntegerField()
    interception_yards = models.IntegerField()
    interception_td = models.IntegerField()
    fumble_returns = models.IntegerField()
    fumble_return_yards = models.IntegerField()
    fumble_return_td = models.IntegerField()
    safeties = models.IntegerField()

    class Admin:
        pass
        
    def __unicode__(self):
        return "%s - %s" % (self.playeryear.player, self.game)

class PlayerSpecial(models.Model):
    playeryear = models.ForeignKey(PlayerYear)
    game = models.ForeignKey(Game)
    punts = models.IntegerField()
    punt_yards = models.IntegerField()
    punt_returns = models.IntegerField()
    punt_return_yards = models.IntegerField()
    punt_return_td = models.IntegerField()
    kickoff_returns = models.IntegerField()
    kickoff_return_yards = models.IntegerField()
    kickoff_return_td = models.IntegerField()
    pat_attempts = models.IntegerField()
    pat_made = models.IntegerField()
    two_point_attempts = models.IntegerField()
    two_point_made = models.IntegerField()
    defense_pat_attempts = models.IntegerField()
    defense_pat_made = models.IntegerField()
    defense_return_attempts = models.IntegerField()
    defense_return_made = models.IntegerField()
    field_goal_attempts = models.IntegerField()
    field_goal_made = models.IntegerField()
    
    class Admin:
        pass
        
    def __unicode__(self):
        return "%s - %s" % (self.playeryear.player, self.game)

class PlayerSummary(models.Model):
    playeryear = models.ForeignKey(PlayerYear)
    rushes = models.IntegerField(null=True)
    rush_gain = models.IntegerField(null=True)
    rush_loss = models.IntegerField(null=True)
    rush_net = models.IntegerField(null=True)
    rush_td = models.IntegerField(null=True)
    pass_attempts = models.IntegerField(null=True)
    pass_complete = models.IntegerField(null=True)
    pass_intercept = models.IntegerField(null=True)
    pass_yards = models.IntegerField(null=True)
    pass_td = models.IntegerField(null=True)
    conversions = models.IntegerField(null=True)
    offense_plays = models.IntegerField(null=True)
    offense_yards = models.IntegerField(null=True)
    receptions = models.IntegerField(null=True)
    reception_yards = models.IntegerField(null=True)
    reception_td = models.IntegerField(null=True)

    class Admin:
        list_display = ('playeryear', 'rush_net', 'pass_yards', 'offense_yards')
    
    def __unicode__(self):
        return "%s - %s" % (self.playeryear.player, self.playeryear.year)