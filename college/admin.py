from django.contrib import admin
from fumblerooski.college.models import State, City, College, Coach, CoachingJob, CollegeYear, CollegeCoach, Game, Position, Player, PlayerGame, PlayerRush, PlayerPass,PlayerReceiving, PlayerFumble, PlayerScoring, PlayerTackle, PlayerTacklesLoss, PlayerPassDefense, PlayerReturn, Conference, GameOffense, GameDefense, Week, GameDrive, DriveOutcome, BowlGame, QuarterScore

class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated')
    list_filter = ('updated',)
    ordering = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class CollegeYearAdmin(admin.ModelAdmin):
    list_filter = ('year',)
    list_display = ('college', 'year', 'wins','losses')
    search_fields = ('college__name',)
    ordering = ('-id',)

class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbrev')
    search_fields = ('name','abbrev')
    ordering = ('name',)

class CoachAdmin(admin.ModelAdmin):
    search_fields = ('last_name',)
    list_display = ('last_name', 'first_name', 'years')
    list_filter = ('years','college', 'grad_year')

class CoachingJobAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CollegeCoachAdmin(admin.ModelAdmin):
    list_display = ('coach', 'collegeyear', 'jobs_display', 'start_date', 'end_date')
    search_fields = ('coach__last_name','collegeyear__college__name')
    ordering = ('-id',)

class BowlGameAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class GameAdmin(admin.ModelAdmin):
    list_display = ('team1', 'team2', 'date', 't1_result', 'team1_score', 'team2_score')
    ordering = ('-date',)
    list_filter = ('season','week')
    search_fields = ('team1__name',)

class PlayerAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'team', 'year','position', 'status')
    list_filter = ('year','position', 'status')
    search_fields = ('name',)

class WeekAdmin(admin.ModelAdmin):
    list_display = ('year', 'week_num', 'end_date')
    list_filter = ('year',)

class DriveOutcomeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('abbrev', 'name')

class GameDriveAdmin(admin.ModelAdmin):
    list_filter = ('start_how', 'plays')
    list_display = ('game', 'team', 'drive', 'end_result')

class PlayerRushAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'rushes', 'net', 'td')
    list_filter = ('td', 'net')
    search_fields = ('player__name',)

class PlayerPassAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'completions', 'attempts', 'yards', 'td', 'interceptions', 'pass_efficiency')
    list_filter = ('td', 'interceptions')

class PlayerReceivingAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'receptions', 'yards', 'td', 'average')
    list_filter = ('td', 'receptions')

class RushingSummaryAdmin(admin.ModelAdmin):
    list_display = ('player', 'year', 'rank', 'carries', 'net', 'yards_per_game')
    list_filter = ('year', 'rank')
    ordering = ('-year', 'rank')

class QuarterScoreAdmin(admin.ModelAdmin):
    list_display = ('game', 'team', 'season','quarter','points')
    list_filter = ('quarter', 'season')

admin.site.register(College, CollegeAdmin)
admin.site.register(CollegeYear, CollegeYearAdmin)
admin.site.register(Coach, CoachAdmin)
admin.site.register(CoachingJob, CoachingJobAdmin)
admin.site.register(CollegeCoach, CollegeCoachAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(PlayerPass, PlayerPassAdmin)
admin.site.register(PlayerRush, PlayerRushAdmin)
admin.site.register(PlayerGame)
admin.site.register(PlayerReceiving, PlayerReceivingAdmin)
admin.site.register(PlayerTackle)
admin.site.register(PlayerTacklesLoss)
admin.site.register(PlayerPassDefense)
admin.site.register(Position)
admin.site.register(City, CityAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(DriveOutcome, DriveOutcomeAdmin)
admin.site.register(GameDrive, GameDriveAdmin)
admin.site.register(BowlGame, BowlGameAdmin)
