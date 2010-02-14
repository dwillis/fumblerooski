from django.conf.urls.defaults import *

urlpatterns = patterns('fumblerooski.rankings.views',
     url(r'^$', 'rankings_index'),
     url(r'^(?P<rankingtype>[-a-z]+)/(?P<season>\d+)/$', 'rankings_season'),
     url(r'^(?P<rankingtype>[-a-z]+)/(?P<season>\d+)/week/(?P<week>\d+)/$', 'rankings_season'),
)