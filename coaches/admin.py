from django.contrib import admin
from fumblerooski.coaches.models import Coach, CoachingJob, CollegeCoach

class CoachAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CoachingJobAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class CollegeCoachAdmin(admin.ModelAdmin):
    list_display = ('coach', 'collegeyear', 'job', 'start_date', 'end_date')

admin.site.register(Coach, CoachAdmin)
admin.site.register(CoachingJob, CoachingJobAdmin)
admin.site.register(CollegeCoach, CollegeCoachAdmin)
