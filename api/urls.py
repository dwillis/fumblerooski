from django.conf.urls.defaults import *
from piston.resource import Resource
from fumblerooski.api.handlers import CollegeHandler, CoachHandler

college_handler = Resource(CollegeHandler)
coach_handler = Resource(CoachHandler)

urlpatterns = patterns('',
   url(r'^college/teams/(?P<slug>[^/]+)/$', college_handler),
   url(r'^coach/(?P<slug>[^/]+)/$', coach_handler),
)
