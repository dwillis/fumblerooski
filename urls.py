from django.urls import path, include, re_path
from django.contrib import admin
from fumblerooski.feeds import CoachesFeed
from django.contrib.syndication.views import Feed
from fumblerooski.college import views as college_views

feeds = {
    'coaches': CoachesFeed,
}

urlpatterns = [
     re_path(r'^admin/coach_totals/', college_views.admin_coach_totals),
     path('admin/doc/', include('django.contrib.admindocs.urls')),
     path('admin/', admin.site.urls),
     path('blog/', include('fumblerooski.blog.urls')),
     path('college/', include('fumblerooski.college.urls')),
     path('rankings/', include('fumblerooski.rankings.urls')),
     path('api/', include('fumblerooski.api.urls')),
     path('', college_views.homepage),
     re_path(r'^feeds/(?P<url>.*)/$', Feed.as_view(), {'feed_dict': feeds}),

     # Coach URLs
     path('coaches/', college_views.coach_index),
     path('coaches/active/', college_views.active_coaches),
     path('coaches/feeds/recent_hires/', college_views.recent_hires_feed),
     re_path(r'^coaches/detail/(?P<coach>\d+-[-a-z]+)/$', college_views.coach_detail, name='coach_detail'),
     re_path(r'^coaches/detail/(?P<coach>\d+-[-a-z]+)/vs/$', college_views.coach_vs, name='coach_vs'),
     re_path(r'^coaches/detail/(?P<coach>\d+-[-a-z]+)/vs/(?P<coach2>\d+-[-a-z]+)/$', college_views.coach_compare, name='coach_compare'),
     path('coaches/assistants/', college_views.assistant_index),
     re_path(r'^coaches/common/(?P<coach>\d+-[-a-z]+)/(?P<coach2>\d+-[-a-z]+)/$', college_views.coach_common),
     re_path(r'^coaches/departures/(?P<year>\d\d\d\d)/$', college_views.departures),
     re_path(r'^coaches/hires/(?P<year>\d\d\d\d)/$', college_views.coaching_hires),
]
