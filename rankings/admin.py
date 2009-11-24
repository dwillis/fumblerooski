from django.contrib import admin
from fumblerooski.rankings.models import *

class RankingTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class RankingAdmin(admin.ModelAdmin):
    list_filter = ('year',)


admin.site.register(RankingType, RankingTypeAdmin)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(RushingSummary, RushingSummaryAdmin)
