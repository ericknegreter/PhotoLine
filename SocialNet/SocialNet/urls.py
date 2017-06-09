from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'SocialApp.views.index'), # root
    url(r'^login$', 'SocialApp.views.login_view'), # login
    url(r'^logout$', 'SocialApp.views.logout_view'), # logout
    url(r'^signup$', 'SocialApp.views.signup'), # signup
    url(r'^posts$', 'SocialApp.views.public'),
    url(r'^submit$', 'SocialApp.views.submit'), # submit new post
    url(r'^users/$', 'SocialApp.views.users'),
    url(r'^users/(?P<username>\w{0,30})/$', 'SocialApp.views.users'),
    url(r'^follow$', 'SocialApp.views.follow'),
)
