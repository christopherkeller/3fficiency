from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', 'status.views.index'),
  	(r'^status/$', 'status.views.status'),
	(r'^status/(?P<status_id>\d+)/$', 'status.views.status_detail'),
  	(r'^accounts/login/$', 'django.contrib.auth.views.login'),
  	(r'^accounts/logout/$','django.contrib.auth.views.logout_then_login'),
	(r'^playground', 'status.views.playground'),
	(r'^status/latest/(?P<format>\w+)/$', 'status.views.get_latest_status_by_user_tag'),
    # Examples:
    # url(r'^$', 'threefficiency.views.home', name='home'),
    # url(r'^threefficiency/', include('threefficiency.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
