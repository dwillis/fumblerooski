from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic import list_detail, date_based, create_update
from fumblerooski.college import views as college_views

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^football/', include('football.foo.urls')),

    # Uncomment this for admin:
     (r'^admin/(.*)', admin.site.root),
     (r'^$', college_views.homepage),
     (r'^college/seasons/(?P<season>\d+)/week/(?P<week>\d+)/$', college_views.season_week),
     (r'^college/conferences/$', college_views.conference_index),
     (r'^college/conferences/(?P<conf>[-a-z0-9]+)/$', college_views.conference_detail),
     (r'^college/games/$', college_views.game_index),
     (r'^college/coaches/(?P<coach>[-a-z]+)/$', college_views.coach_detail),
     (r'^college/teams/$', college_views.team_index),
     (r'^college/teams/undefeated/(?P<season>\d+)/$', college_views.undefeated_teams),
     (r'^college/teams/(?P<team>[-a-z]+)/$', college_views.team_detail),
     (r'^college/teams/(?P<team>[-a-z]+)/offense/$', college_views.team_offense),
     (r'^college/teams/(?P<team>[-a-z]+)/offense/rushing/$', college_views.team_offense_rushing),
     (r'^college/teams/(?P<team>[-a-z]+)/defense/$', college_views.team_defense),
     (r'^college/teams/(?P<team>[-a-z]+)/penalties/$', college_views.team_penalties),
     (r'^college/teams/(?P<team>[-a-z]+)/first-downs/$', college_views.team_first_downs),     
     (r'^college/teams/(?P<team>[-a-z]+)/first-downs/(?P<category>rushing|passing|penalty)/$', college_views.team_first_downs_category),     
     (r'^college/teams/(?P<team>[-a-z]+)/(?P<season>\d+)/$', college_views.team_detail_season),
     (r'^college/teams/(?P<team>[-a-z]+)/(?P<season>\d+)/classes/(?P<cl>[fr|so|jr|sr])/$', college_views.team_by_cls),
#     (r'^college/teams/(?P<team>[-a-z]+)/(?P<season>\d+)/positions/(?<pos>[a-z][a-z][a-z]?)/$', college_views.team_positions),
     (r'^college/teams/(?P<team>[-a-z]+)/opponents/$', college_views.team_opponents),
     (r'^college/teams/(?P<team>[-a-z]+)/(?P<season>\d+)/players/$', college_views.team_players),
     (r'^college/teams/(?P<team>[-a-z]+)/(?P<season>\d+)/players/(?P<player>[-a-z]+)/$', college_views.player_detail),
#     (r'^college/teams/(?P<team>[-a-z]+)/recruits/$', recruit_views.team_detail),
     (r'^college/teams/(?P<team1>[-a-z]+)/vs/(?P<team2>[-a-z]+)/$', college_views.team_vs),
     (r'^college/teams/(?P<team1>[-a-z]+)/vs/(?P<team2>[-a-z]+)/(?P<outcome>wins|losses|ties)/$', college_views.team_vs),
     (r'^college/teams/(?P<team1>[-a-z]+)/vs/(?P<team2>[-a-z]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', college_views.game),
     (r'^college/teams/(?P<team1>[-a-z]+)/vs/(?P<team2>[-a-z]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/drives/$', college_views.game_drive),     
#    (r'^college/teams/(?P<team>[-a-z]+)/recruits/(?P<year>2\d\d\d)/$', recruit_views.team_detail_year),
#    (r'^college/teams/(?P<team>[-a-z]+)/recruits/(?P<pos>[a-z][a-z]?[a-z]?)/$', recruit_views.team_detail_position),
     (r'^states/$', college_views.state_index),
     (r'^states/(?P<state>[a-z][a-z])/$', college_views.state_detail),
)
