from django.conf.urls.defaults import *

urlpatterns = patterns('fumblerooski.coaches.views',
     url(r'^$', 'coach_index'),
     url(r'^active/$', 'active_coaches'),
     url(r'^feeds/recent_hires/$', 'recent_hires_feed'),
     url(r'^detail/(?P<coach>[-a-z]+)/$', 'coach_detail'),
     url(r'^assistants/$', 'assistant_index'),
)