from django.conf.urls import patterns, include, url
from django.views.generic import DetailView, ListView, TemplateView
from django.http import HttpResponseServerError, HttpResponseRedirect
from models import *
from views import *

from datetime import date

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', ListView.as_view(
		template_name='purpleposter-list.html',
		queryset=PurplePoster.objects.filter(startTime__gte=date.today()).order_by('-startTime')[:15],
		context_object_name='poster_list',
	)),



	url(r'^poster/(?P<pk>\d+)/$', DetailView.as_view(
		template_name='poster-detail.html',
		model=PurplePoster,
		context_object_name='poster'
	)),
		
	url(r'^submitpurpleposter/$', submitpurpleposter),

	url(r'^searchposters/$', SearchPosters.as_view(
		template_name='purpleposter-list.html',
		context_object_name='poster_list'
	)),
	
#	url(r'^user/(?P<pk>\d+)/$', DetailView.as_view(
	
#	url(r'^userpreference/$', ListView.as_view(
#		template_name='user-preference.html',
#		queryset = Movie.objects.all(),
#		context_object_name='movies'
#	)),

	url(r'^user/$', UserPreferenceView.as_view(
		template_name='userpreference.html'
	)),

	url(r'^error/$', ErrorView.as_view(
		template_name='errorpage.html'
	)),
	
	url(r'login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	
	url(r'signup/$', signup),


	(r'logout/$', 'django.contrib.auth.views.logout',{'next_page': '../'}),
	url(r'^accounts/profile/$', profile),
	
	url(r'trackmovie/$', trackmovie),
	url(r'trackactor/$', trackactor),
	url(r'trackposter/$', trackposter),
	url(r'updateProfile/$', updateProfile),
	url(r'addComment/$', addComment),
	url(r'tracklocation/$', trackposter),
)
