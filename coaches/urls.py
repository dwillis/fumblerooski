from django.conf.urls.defaults import *

urlpatterns = patterns('fumblerooski.coaches.views',
     url(r'^$', 'coach_index'),
     url(r'^(?P<coach>[-a-z]+)/$', 'coach_detail'),
     url(r'^assistants/$', 'assistant_index'),
)