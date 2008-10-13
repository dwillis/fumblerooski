from django.contrib.gis.db import models
from django import forms
import datetime

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

SIDE_CHOICES = (
    ('O', 'Own'),
    ('P', 'Opponents'),
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

RANKINGTYPE_CHOICES = (
    ('T', 'Team'),
    ('P', 'Player'),
)

DIVISION_CHOICES = (
    ('B', 'Bowl Subdivision'),
    ('C', 'Championship Subdivision'),
    ('D', 'Division II'),
    ('T', 'Division III'),
)

class State(models.Model):
    id = models.CharField(max_length=2, editable=False, primary_key=True)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/states/%s/" % self.id.lower()
    
class StateForm(forms.Form):
    name = forms.CharField(max_length=50, widget=forms.Select())

class City(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    state = models.ForeignKey(State)
    point = models.PointField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return "%s, %s" % (self.name, self.state.id)
    
    def get_absolute_url(self):
        return "/college/states/%s/%s" % (self.state.id.lower(), self.slug)

class Week(models.Model):
    year = models.IntegerField()
    week_num = models.IntegerField()
    end_date = models.DateField()
    
    def __unicode__(self):
        return "Week %s, %s" % (self.week_num, self.year)
    
    def week_games_url(self):
        return "/college/seasons/%s/week/%s/" % (self.year, self.week_num)

class Conference(models.Model):
    abbrev = models.CharField(max_length=10)
    name = models.CharField(max_length=90)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/college/conferences/%s/' % self.abbrev.lower()

class College(models.Model):
    name = models.CharField(max_length=90)
    slug = models.SlugField(max_length=90)
    drive_slug = models.CharField(max_length=90)
    state = models.ForeignKey(State, blank=True)
    official_url = models.CharField(max_length=120, blank=True)
    official_rss = models.CharField(max_length=120, blank=True)
    conference = models.ForeignKey(Conference, null=True, blank=True)
    updated = models.BooleanField()
    division = models.CharField(max_length=1, choices=DIVISION_CHOICES)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '/college/teams/%s/' % self.slug

class CollegeYear(models.Model):
    college = models.ForeignKey(College)
    year = models.IntegerField()
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    ties = models.IntegerField(default=0)
    conference_wins = models.IntegerField(default=0)
    conference_losses = models.IntegerField(default=0)
    conference_ties = models.IntegerField(default=0)
    freshmen = models.IntegerField(default=0)
    sophomores = models.IntegerField(default=0)
    juniors = models.IntegerField(default=0)
    seniors = models.IntegerField(default=0)
    
    def __unicode__(self):
        return "%s - %s" % (self.college, str(self.year))
    
    def game_count(self):
        return self.wins+self.losses+self.ties

class CollegeTotal(models.Model):
    college = models.ForeignKey(College)
    year = models.IntegerField()
    third_down_attempts = models.IntegerField(default=0)
    third_down_conversions = models.IntegerField(default=0)
    fourth_down_attempts = models.IntegerField(default=0)
    fourth_down_conversions = models.IntegerField(default=0)
    first_downs_rushing = models.IntegerField(default=0)
    first_downs_passing = models.IntegerField(default=0)
    first_downs_penalty = models.IntegerField(default=0)
    first_downs_total = models.IntegerField(default=0)
    penalties = models.IntegerField(default=0)
    penalty_yards = models.IntegerField(default=0)
    fumbles = models.IntegerField(default=0)
    fumbles_lost = models.IntegerField(default=0)
    rushes = models.IntegerField(default=0)
    rush_gain = models.IntegerField(default=0)
    rush_loss = models.IntegerField(default=0)
    rush_net = models.IntegerField(default=0)
    rush_touchdowns = models.IntegerField(default=0)
    total_plays = models.IntegerField(default=0)
    total_yards = models.IntegerField(default=0)
    pass_attempts = models.IntegerField(default=0)
    pass_completions = models.IntegerField(default=0)
    pass_interceptions = models.IntegerField(default=0)
    pass_yards = models.IntegerField(default=0)
    pass_touchdowns = models.IntegerField(default=0)
    receptions = models.IntegerField(default=0)
    receiving_yards = models.IntegerField(default=0)
    receiving_touchdowns = models.IntegerField(default=0)
    punts = models.IntegerField(default=0)
    punt_yards = models.IntegerField(default=0)
    punt_returns = models.IntegerField(default=0)
    punt_return_yards = models.IntegerField(default=0)
    punt_return_touchdowns = models.IntegerField(default=0)
    kickoff_returns = models.IntegerField(default=0)
    kickoff_return_yards = models.IntegerField(default=0)
    kickoff_return_touchdowns = models.IntegerField(default=0)
    touchdowns = models.IntegerField(default=0)
    pat_attempts = models.IntegerField(default=0)
    pat_made = models.IntegerField(default=0)
    two_point_conversion_attempts = models.IntegerField(default=0)
    two_point_conversions = models.IntegerField(default=0)
    field_goal_attempts = models.IntegerField(default=0)
    field_goals_made = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

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
    college = models.ForeignKey(College)
    job = models.ForeignKey(CoachingJob)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.coach, self.college)

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

class Game(models.Model):
    season = models.IntegerField()
    team1 = models.ForeignKey(College, related_name='first_team')
    team2 = models.ForeignKey(College, related_name='second_team')
    date = models.DateField()
    week = models.ForeignKey(Week)
    t1_game_type = models.CharField(max_length=1, choices=GAME_TYPE_CHOICES)
    t1_result = models.CharField(max_length=1, choices=RESULT_CHOICES, blank=True)
    team1_score = models.IntegerField(null=True)
    team2_score = models.IntegerField(null=True)
    site = models.CharField(max_length=90, blank=True)
    attendance = models.IntegerField(null=True)
    ncaa_xml = models.CharField(max_length=120)
    duration = models.TimeField(null=True)
    
    def __unicode__(self):
        return '%s vs. %s, %s' % (self.team1, self.team2, self.date)
    
    def get_absolute_url(self):
        return '/college/teams/%s/vs/%s/%s/%s/%s/' % (self.team1.slug, self.team2.slug, self.date.year, self.date.month, self.date.day)

    def get_matchup_url(self):
        return '/college/teams/%s/vs/%s/' % (self.team1.slug, self.team2.slug)
    
    def get_reverse_url(self):
        return '/college/teams/%s/vs/%s/%s/%s/%s/' % (self.team2.slug, self.team1.slug, self.date.year, self.date.month, self.date.day)
    
    def get_ncaa_drive_url(self):
        return "http://web1.ncaa.org/mfb/driveSummary.jsp?acadyr=%s&h=%s&v=%s&date=%s&game=%s" % (self.season, self.team1.id, self.team2.id, self.date.strftime("%d-%b-%y").upper(), self.ncaa_xml.strip())
    
    def margin(self):
        return self.team1_score-self.team2_score
    
    def display(self):
        if self.margin() > 0:
            return "%s %s, %s %s" % (self.team1, self.team1_score, self.team2, self.team2_score)
        else:
            return "%s %s, %s %s" % (self.team2, self.team2_score, self.team1, self.team1_score)
    
class DriveOutcome(models.Model):
    abbrev = models.CharField(max_length=5)
    name = models.CharField(max_length=50, null=True)
    slug = models.SlugField(max_length=50, null=True)
    
    def __unicode__(self):
        return self.name

class GameDrive(models.Model):
    game = models.ForeignKey(Game)
    team = models.ForeignKey(College)
    drive = models.IntegerField()
    quarter = models.PositiveSmallIntegerField()
    start_how = models.CharField(max_length=25)
    start_time = models.TimeField()
    start_position = models.IntegerField()
    start_side = models.CharField(max_length=1, choices=SIDE_CHOICES)
    end_result = models.ForeignKey(DriveOutcome)
    end_time = models.TimeField()
    end_position = models.IntegerField(null=True)
    end_side = models.CharField(max_length=1, choices=SIDE_CHOICES)
    plays = models.IntegerField()
    yards = models.IntegerField()
    time_of_possession = models.TimeField()
    
    def __unicode__(self):
        return "%s: %s drive %s" % (self.game, self.team, self.drive)

class GameOffense(models.Model):
    game = models.ForeignKey(Game)
    team = models.ForeignKey(College)
    year = models.IntegerField()
    third_down_attempts = models.IntegerField(default=0)
    third_down_conversions = models.IntegerField(default=0)
    fourth_down_attempts = models.IntegerField(default=0)
    fourth_down_conversions = models.IntegerField(default=0)
    time_of_possession = models.TimeField(null=True)
    first_downs_rushing = models.IntegerField(default=0)
    first_downs_passing = models.IntegerField(default=0)
    first_downs_penalty = models.IntegerField(default=0)
    first_downs_total = models.IntegerField(default=0)
    penalties = models.IntegerField(default=0)
    penalty_yards = models.IntegerField(default=0)
    fumbles = models.IntegerField(default=0)
    fumbles_lost = models.IntegerField(default=0)
    rushes = models.IntegerField(default=0)
    rush_gain = models.IntegerField(default=0)
    rush_loss = models.IntegerField(default=0)
    rush_net = models.IntegerField(default=0)
    rush_touchdowns = models.IntegerField(default=0)
    total_plays = models.IntegerField(default=0)
    total_yards = models.IntegerField(default=0)
    pass_attempts = models.IntegerField(default=0)
    pass_completions = models.IntegerField(default=0)
    pass_interceptions = models.IntegerField(default=0)
    pass_yards = models.IntegerField(default=0)
    pass_touchdowns = models.IntegerField(default=0)
    receptions = models.IntegerField(default=0)
    receiving_yards = models.IntegerField(default=0)
    receiving_touchdowns = models.IntegerField(default=0)
    punts = models.IntegerField(default=0)
    punt_yards = models.IntegerField(default=0)
    punt_returns = models.IntegerField(default=0)
    punt_return_yards = models.IntegerField(default=0)
    punt_return_touchdowns = models.IntegerField(default=0)
    kickoff_returns = models.IntegerField(default=0)
    kickoff_return_yards = models.IntegerField(default=0)
    kickoff_return_touchdowns = models.IntegerField(default=0)
    touchdowns = models.IntegerField(default=0)
    pat_attempts = models.IntegerField(default=0)
    pat_made = models.IntegerField(default=0)
    two_point_conversion_attempts = models.IntegerField(default=0)
    two_point_conversions = models.IntegerField(default=0)
    field_goal_attempts = models.IntegerField(default=0)
    field_goals_made = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def __unicode__(self):
        return '%s - %s' % (self.game, self.team)
    
    def third_down_rate(self):
        return float(self.third_down_conversions/self.third_down_attempts)
    
    def field_goal_rate(self):
        return float(self.field_goals_made/self.field_goal_attempts)
    
    def penalty_yard_ratio(self):
        return float(self.penalty_yards/self.total_yards)
    
    def yards_per_reception(self):
        return float(self.receiving_yards/self.receptions)
    
    def yards_per_pass_attempt(self):
        return float(self.receiving_yards/self.pass_attempts)
    
    def rushing_first_downs_pct(self):
        return float(self.first_downs_rushing/self.first_downs_total)

    """
    Returns a floating-point number representing the number
    of touchdowns per rushing attempt for a single game.
    """
    def touchdowns_per_rushes(self):
        return float(self.rush_touchdowns/self.rushes)*100
    
    """
    Returns the opponent for a team's given Game Offense record.
    """
    def opponent(self):
        if self.team == self.game.team2:
            return self.game.team1
        else:
            return self.game.team2

class GameDefense(models.Model):
    game = models.ForeignKey(Game)
    team = models.ForeignKey(College)
    safeties = models.IntegerField(default=0)
    unassisted_tackles = models.IntegerField(default=0)
    assisted_tackles = models.IntegerField(default=0)
    unassisted_tackles_for_loss = models.IntegerField(default=0)
    assisted_tackles_for_loss = models.IntegerField(default=0)
    tackles_for_loss_yards = models.IntegerField(default=0)
    unassisted_sacks = models.IntegerField(default=0)
    assisted_sacks = models.IntegerField(default=0)
    sack_yards = models.IntegerField(default=0)
    defensive_interceptions = models.IntegerField(default=0)
    defensive_interception_yards = models.IntegerField(default=0)
    defensive_interception_touchdowns = models.IntegerField(default=0)
    pass_breakups = models.IntegerField(default=0)
    fumbles_forced = models.IntegerField(default=0)
    fumbles_number = models.IntegerField(default=0)
    fumbles_yards = models.IntegerField(default=0)
    fumbles_touchdowns = models.IntegerField(default=0)
    
    def __unicode__(self):
        return '%s - %s' % (self.game, self.team)

class Player(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120)
    team = models.ForeignKey(College)
    year = models.IntegerField()
    position = models.ForeignKey(Position)
    number = models.CharField(max_length=4)
    games_played = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)

    def __unicode__(self):
        return "%s - %s" % (self.name, self.year)
    
    def get_absolute_url(self):
        return '/college/teams/%s/%s/players/%s/' % (self.team.slug, self.year, self.slug)

class PlayerGame(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    played = models.BooleanField()
    
    def __unicode__(self):
        return self.player.name.full_name()

class PlayerOffense(models.Model):
    player = models.ForeignKey(Player)
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

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)

class PlayerDefense(models.Model):
    player = models.ForeignKey(Player)
    game = models.ForeignKey(Game)
    interceptions = models.IntegerField()
    interception_yards = models.IntegerField()
    interception_td = models.IntegerField()
    fumble_returns = models.IntegerField()
    fumble_return_yards = models.IntegerField()
    fumble_return_td = models.IntegerField()
    safeties = models.IntegerField()

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)

class PlayerSpecial(models.Model):
    player = models.ForeignKey(Player)
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

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.game)

class PlayerSummary(models.Model):
    player = models.ForeignKey(Player)
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

    def __unicode__(self):
        return "%s - %s" % (self.player.name, self.player.year)

class RankingType(models.Model):
    name = models.CharField(max_length=75)
    slug = models.SlugField(max_length=75)
    typename = models.CharField(max_length=1, choices=RANKINGTYPE_CHOICES)
    ncaa_name = models.CharField(max_length=75)
    
    def __unicode__(self):
        return self.name

class Ranking(models.Model):
    ranking_type = models.ForeignKey(RankingType)
    college = models.ForeignKey(College)
    year = models.IntegerField()
    week = models.ForeignKey(Week)
    rank = models.PositiveIntegerField()
    actual = models.DecimalField(decimal_places=2, max_digits=5)
    conference_rank = models.PositiveIntegerField(null=True)
    
    def __unicode__(self):
        return "%s - %s, %s (Week %s)" % (self.ranking_type, self.college, self.year, self.week)

class Poll(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    
    def __unicode__(self):
        return self.name
        

class PollResults(models.Model):
    poll = models.ForeignKey(Poll)
    week = models.ForeignKey(Week)
    team = models.ForeignKey(College)
    rank = models.IntegerField()
    
    def __unicode__(self):
        return "%s: %s %s" % (self.poll, self.week, self.team)
