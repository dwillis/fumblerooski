from django.conf.urls.defaults import *
from piston.resource import Resource
from fumblerooski.api.handlers import CollegeHandler

college_handler = Resource(CollegeHandler)

urlpatterns = patterns('',
   url(r'^college/(?P<slug>[^/]+)/', college_handler),
)
