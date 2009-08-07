from django.contrib import admin
from fumblerooski.coaches.models import Coach, CoachingJob

class CoachAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('first_name','last_name')}
    search_fields = ('last_name',)
    list_display = ('last_name', 'first_name', 'years')
    list_filter = ('years',)

class CoachingJobAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Coach, CoachAdmin)
admin.site.register(CoachingJob, CoachingJobAdmin)
