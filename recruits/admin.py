from django.contrib import admin
from fumblerooski.recruits.models import SchoolType, City, School, Recruit, Outcome, Signing, Year

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    ordering = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('city',) 

class RecruitAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'height', 'weight', 'home_state')
    search_fields = ('last_name',)
    ordering = ('last_name', 'first_name')
    prepopulated_fields = {'slug': ('id','full_name')}
    raw_id_files = ('school',)

class SigningAdmin(admin.ModelAdmin):
    list_display = ('player', 'player_position', 'school', 'year')
    search_fields = ('player__last_name',)
    raw_id_files = ('school', 'player')

class OutcomeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class SchoolTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(City, CityAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Recruit, RecruitAdmin)
admin.site.register(Signing, SigningAdmin)
admin.site.register(Outcome, OutcomeAdmin)
admin.site.register(SchoolType, SchoolTypeAdmin)