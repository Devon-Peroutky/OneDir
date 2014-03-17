from django.conf.urls import patterns, include, url
from mysite.views import hello
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^hello/$', hello),
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', hello),
    url(r'^admin/', include(admin.site.urls)),
)
