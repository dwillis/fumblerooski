from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
     url(r'^admin/doc/', include('django.contrib.admindocs.urls')), 
     url(r"^admin/(.*)", admin.site.root),
     url(r"^blog/", include("fumblerooski.blog.urls")),
     url(r"^college/", include("fumblerooski.college.urls")),
     url(r"^api/", include("fumblerooski.api.urls")),
     url(r"^$", "fumblerooski.college.views.homepage"),
)

urlpatterns += patterns('fumblerooski.college.views',
     url(r'^coaches/$', 'coach_index'),
     url(r'^coaches/active/$', 'active_coaches'),
     url(r'^coaches/feeds/recent_hires/$', 'recent_hires_feed'),
     url(r'^coaches/detail/(?P<coach>\d+-[-a-z]+)/$', 'coach_detail', name="coach_detail"),
     url(r'^coaches/assistants/$', 'assistant_index'),
     url(r'^coaches/common/(?P<coach>\d+-[-a-z]+)/(?P<coach2>\d+-[-a-z]+)/$', 'coach_common'),
     url(r'^coaches/departures/(?P<year>\d\d\d\d)/$', 'departures'),
     url(r'^coaches/hires/(?P<year>\d\d\d\d)/$', 'coaching_hires'),
)
