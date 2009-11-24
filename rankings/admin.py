from django.contrib import admin
from fumblerooski.rankings.models import *

class RankingTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class RankingAdmin(admin.ModelAdmin):
    list_filter = ('year',)

class RushingSummaryAdmin(admin.ModelAdmin):
    list_display = ('player', 'year', 'rank', 'carries', 'net', 'yards_per_game')
    list_filter = ('year', 'rank')
    ordering = ('-year', 'rank')


admin.site.register(RankingType, RankingTypeAdmin)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(RushingSummary, RushingSummaryAdmin)
