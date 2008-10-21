from django.contrib import admin
from fumblerooski.college.models import State, College, Game, Coach, Position, Player, PlayerGame, PlayerRush, PlayerPass,PlayerReceiving, PlayerFumble, PlayerScoring, PlayerTackle, PlayerTacklesLoss, PlayerPassDefense, PlayerReturn, PlayerSummary, CollegeYear, Conference, GameOffense, GameDefense, Week, GameDrive, DriveOutcome, Ranking, RankingType

class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    ordering = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CoachAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CoachingJobAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CollegeCoachAdmin(admin.ModelAdmin):
    list_display = ('coach', 'college', 'job', 'start_date', 'end_date')

class GameAdmin(admin.ModelAdmin):
    list_display = ('team1', 'team2', 'date', 't1_result', 'team1_score', 'team2_score')
    ordering = ('-date',)
    list_filter = ('season','week')

class PlayerAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class RankingTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class RankingAdmin(admin.ModelAdmin):
    list_filter = ('year', 'ranking_type')

class WeekAdmin(admin.ModelAdmin):
    list_filter = ('year',)

class DriveOutcomeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('abbrev', 'name')

class GameDriveAdmin(admin.ModelAdmin):
    list_filter = ('start_how', 'plays')
    list_display = ('game', 'team', 'drive', 'end_result')

class PlayTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(PlayerPass)
admin.site.register(PlayerRush)
admin.site.register(PlayerGame)
admin.site.register(PlayerReceiving)
admin.site.register(Position)
admin.site.register(College, CollegeAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Coach, CoachAdmin)
admin.site.register(CoachingJob, CoachingJobAdmin)
admin.site.register(CollegeCoach, CollegeCoachAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(RankingType, RankingTypeAdmin)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(DriveOutcome, DriveOutcomeAdmin)
admin.site.register(GameDrive, GameDriveAdmin)
admin.site.register(PlayType, PlayTypeAdmin)