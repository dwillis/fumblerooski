from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic import list_detail, date_based, create_update
#from fumblerooski.recruits import views as recruit_views
from fumblerooski2.college import views as college_views

#admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^football/', include('football.foo.urls')),

    # Uncomment this for admin:
     (r'^admin/(.*)', admin.site.root),
     (r'^$', college_views.homepage),
#     (r'^recruits/positions/$', recruit_views.position_index),
#     (r'^recruits/positions/(?P<pos>[a-z][a-z]?[a-z]?)/$', recruit_views.position_detail),
#     (r'^recruits/positions/(?P<pos>[a-z][a-z]?[a-z]?)/(?P<year>all)/$', recruit_views.position_detail),
#     (r'^recruits/positions/(?P<pos>[a-z][a-z][a-z]?)/(?P<year>2\d\d\d)/$', recruit_views.position_detail),
#     (r'^recruits/positions/(?P<pos>\w{2,3})/height/(?P<height>\d-\d\d?)/$', recruit_views.position_height),
#     (r'^recruits/positions/(?P<pos>\w{2,3})/height/under-six-foot/$', recruit_views.position_height_under_six),
#     (r'^players/(?P<slug>[_a-z0-9]+)/$', recruit_views.player_detail),
     (r'^college/conferences/$', college_views.conference_index),
     (r'^college/conferences/(?P<conf>[-a-z0-9]+)/$', college_views.conference_detail),
     (r'^college/games/$', college_views.game_index),
     (r'^college/coaches/(?P<coach>[-a-z]+)/$', college_views.coach_detail),
     (r'^college/teams/$', college_views.team_index),
     (r'^college/teams/(?P<team>[-a-z]+)/$', college_views.team_detail),
     (r'^college/teams/(?P<team>[-a-z]+)/(?P<season>\d+)/$', college_views.team_detail_season),
     (r'^college/teams/(?P<team>[-a-z]+)/(?P<season>\d+)/classes/(?P<cl>[fr|so|jr|sr])/$', college_views.team_by_cls),
#     (r'^college/teams/(?P<team>[-a-z]+)/(?P<season>\d+)/positions/(?<pos>[a-z][a-z][a-z]?)/$', college_views.team_positions),
     (r'^college/teams/(?P<team>[-a-z]+)/opponents/$', college_views.team_opponents),
     (r'^college/teams/(?P<team>[-a-z]+)/(?P<season>\d+)/players/$', college_views.team_players),
     (r'^college/teams/(?P<team>[-a-z]+)/(?P<season>\d+)/players/(?P<player>[-a-z]+)/$', college_views.player_detail),
#     (r'^college/teams/(?P<team>[-a-z]+)/recruits/$', recruit_views.team_detail),
     (r'^college/teams/(?P<team1>[-a-z]+)/vs/(?P<team2>[-a-z]+)/$', college_views.team_vs),
     (r'^college/teams/(?P<team1>[-a-z]+)/vs/(?P<team2>[-a-z]+)/(?P<outcome>wins|losses|ties)/$', college_views.team_vs),
     (r'^college/teams/(?P<team1>[-a-z]+)/vs/(?P<team2>[-a-z]+)/(?P<year>[1|2]\d\d\d)/$', college_views.game),
#    (r'^college/teams/(?P<team>[-a-z]+)/recruits/(?P<year>2\d\d\d)/$', recruit_views.team_detail_year),
#    (r'^college/teams/(?P<team>[-a-z]+)/recruits/(?P<pos>[a-z][a-z]?[a-z]?)/$', recruit_views.team_detail_position),
     (r'^states/$', college_views.state_index),
     (r'^states/(?P<state>[a-z][a-z])/$', college_views.state_detail),
#    (r'^states/(?P<state>[a-z][a-z])/recruits/$', recruit_views.state_detail),
#     (r'^states/(?P<state>[a-z][a-z])/(?P<pos>[a-z][a-z]?[a-z]?)/recruits/$', recruit_views.state_position_index),
#     (r'^states/(?P<state>[a-z][a-z])/(?P<city>[-a-z]+)/recruits/$', recruit_views.city_index),
#     (r'^states/(?P<state>[a-z][a-z])/(?P<city>[-a-z]+)/(?P<school>[-a-z]+)/recruits/$', recruit_views.school_detail),
#     (r'^states/(?P<state>[a-z][a-z])/(?P<city>[-a-z]+)/(?P<school>[-a-z]+)/(?P<pos>[a-z][a-z]?[a-z]?)/recruits/$', recruit_views.school_detail),
)
