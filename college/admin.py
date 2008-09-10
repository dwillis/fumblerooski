from django.contrib import admin
from fumblerooski.college.models import Coach, College, CollegeCoach, Position, State, Game, CoachingJob, PlayerScore

class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    ordering = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class CoachAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CoachingJobAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CollegeCoachAdmin(admin.ModelAdmin):
    list_display = ('coach', 'college', 'job', 'start_date', 'end_date')

class GameAdmin(admin.ModelAdmin):
    list_display = ('team1', 'team2', 'date', 't1_result', 'team1_score', 'team2_score')
    list_filter = ('t1_result', 'team1_score', 'team2_score')

class PlayerScoreAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'total_td', 'total_points')

class PlayerAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(College, CollegeAdmin)
admin.site.register(Coach, CoachAdmin)
admin.site.register(CoachingJob, CoachingJobAdmin)
admin.site.register(CollegeCoach, CollegeCoachAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(PlayerScore, PlayerScoreAdmin)

