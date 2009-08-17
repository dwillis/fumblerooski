from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
     url(r'^admin/doc/', include('django.contrib.admindocs.urls')), 
     url(r"^admin/(.*)", admin.site.root),
     url(r"^blog/", include("fumblerooski.blog.urls")),
     url(r"^coaches/", include("fumblerooski.college.urls")),
     url(r"^college/", include("fumblerooski.college.urls")),
     url(r"^$", "fumblerooski.college.views.homepage"),
)
