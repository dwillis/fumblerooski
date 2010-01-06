from django.conf.urls.defaults import *
from piston.resource import Resource
from fumblerooski.api.handlers import CollegeHandler, CoachHandler, CollegeYearHandler

college_handler = Resource(CollegeHandler)
coach_handler = Resource(CoachHandler)
college_year_handler = Resource(CollegeYearHandler)

urlpatterns = patterns('',
   url(r'^college/teams/(?P<slug>[^/]+)/$', college_handler),
   url(r'^college/teams/(?P<slug>[^/]+)/(?P<year>\d\d\d\d)/$', college_year_handler),
   url(r'^coach/(?P<slug>[^/]+)/$', coach_handler),
)
