from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
     url(r"^admin/(.*)", admin.site.root),
     url(r"^blog/", include("blog.urls")),
     url(r"^college/", include("college.urls")),
     url(r"^$", "college.views.homepage"),
)
