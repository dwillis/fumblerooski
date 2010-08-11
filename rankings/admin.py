from django.contrib import admin
from fumblerooski.rankings.models import *

class RankingTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class RankingAdmin(admin.ModelAdmin):
    list_filter = ('season',)

class RushingSummaryAdmin(admin.ModelAdmin):
    list_display = ('player', 'season', 'rank', 'carries', 'net', 'yards_per_game')
    list_filter = ('season', 'rank')
    ordering = ('-season', 'rank')

class PassEfficiencyAdmin(admin.ModelAdmin):
    list_display = ('player', 'season', 'rank', 'rating')
    list_filter = ('season', 'rank', 'week')
    ordering = ('-season', 'rank')

admin.site.register(RankingType, RankingTypeAdmin)
admin.site.register(Ranking, RankingAdmin)
admin.site.register(RushingSummary, RushingSummaryAdmin)
admin.site.register(PassEfficiency, PassEfficiencyAdmin)