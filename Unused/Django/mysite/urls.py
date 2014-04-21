# --- Default Imports ---
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

# --- My Imports ---
from mysite.views import hello, current_datetime, hours_ahead

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # --- Default Admin URLS ---
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # --- Program Specific URLS ---
    url(r'^$', hello),
    url(r'^time/plus/(\d{1,2})/$', hours_ahead),
    url(r'^time/$', current_datetime),
)
