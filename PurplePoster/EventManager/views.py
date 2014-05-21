# Create your views here.2
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, RequestContext, loader
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, ListView, TemplateView

from EventManager.models import *
from EventManager import rottentomatoes

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

from datetime import datetime

def submitpurpleposter(request):
	# I think the duplicate movie scenario is now handled in models.py
	# it aint pretty tho!!!
	try:
		moviename = request.POST['real-name']
		if moviename == '':
			moviename = (request.POST['project-name'])
		
		if moviename == '':
			raise Exception("Invalid Input!")

		pp = PurplePoster(
			movie = getMovieNamed(moviename),
			alias = request.POST['project-name'],
			startTime = datetime.strptime(request.POST['filming-date'], "%m/%d/%Y"),
		)
		
		if request.POST['filming-location'] != '':
			pp.location = request.POST['filming-location']
			latlng = rottentomatoes.GetLocationCoordinates(pp.location)
			pp.locationLat = float(latlng['lat'])
			pp.locationLon = float(latlng['lng'])
		else:
			pp.locationLat = request.POST['location-lat']
			pp.locationLon = request.POST['location-lon']
			# if this fails, reject and require a filming-location, gracefully

		pp.save()
		return HttpResponseRedirect('/poster/%s/' % pp.pk)
		
	except:
		return HttpResponseRedirect('/error/')

class ErrorView(TemplateView):
	def get_context_data(self):
		return RequestContext(self.request)

class SearchPosters(ListView):
	def get_query(self):
		if(self.request.GET['search-string'] == ''):
			return HttpResponseRedirect('/error/')
		return self.request.GET['search-string']
	
	def get_queryset(self):
		searchstring = self.get_query()

		maxresults = 5

		from django.db.models import Q
		posters = PurplePoster.objects.filter(Q(alias__contains=searchstring)
			| Q(movie__name__contains = searchstring)
			| Q(movie__actor__actorName__contains = searchstring))

		existing_posters = []
		for poster in posters:
			if poster not in existing_posters:
				existing_posters.append(poster)
				
		return existing_posters

class UserPreferenceView(TemplateView):
	def get_context_data(self):
		up = getUserPreference(self.request.user)
		user_movies = up.movie.all
		user_actors = up.actor.all
		user_posters = up.purplePoster.all
		user_locations = up.area.all
		return RequestContext(self.request, {
        	'movies': Movie.objects.all,
       		'actors': Actor.objects.all,
        	'posters': PurplePoster.objects.all,
        	'user': self.request.user,
        	'user_movies': user_movies,
        	'user_actors': user_actors,
			'user_posters': user_posters,
			'user_locations': user_locations,
		})


def profile(request):
	return HttpResponseRedirect('/user/')

@login_required
def updateProfile(request):
	request.user.email = request.POST['email-text']
	request.user.save()
	return HttpResponseRedirect('../')


@login_required
def trackmovie(request):
	up = getUserPreference(request.user)
	up.addUserMovie(request.POST['movie-id'])
	return HttpResponseRedirect('../')

@login_required
def trackactor(request):
	up = getUserPreference(request.user)
	up.addUserActor(request.POST['actor-id'])
	return HttpResponseRedirect('../')

@login_required
def trackposter(request):
	up = getUserPreference(request.user)
	up.addUserPoster(request.POST['poster-id'])
	return HttpResponseRedirect('../')

@login_required
def trackposter(request):
	up = getUserPreference(request.user)
	up.addUserArea(request.POST['location-address'])
	return HttpResponseRedirect('../')


def signup(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)

		if form.is_valid():
			message = None
			form.save()

			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']

			user = authenticate(username=username, password=password)
			request.user = user
			login(request, user)
			return HttpResponseRedirect('../')

	else:
		form = UserCreationForm()
	return render_to_response('signup.html', {'form': form, }, context_instance=RequestContext(request))



def addComment(request):
	if request.user.is_authenticated():
		theSubmitter = request.user.username
	else:
		theSubmitter = "Anonymous User"
	com = Comment(
		commentText = request.POST['comment-text'],
		submitter = theSubmitter,
	)
	com.save()

	pk = request.POST['pp']
	pp = PurplePoster.objects.get(pk = pk)
	pp.addComment(com)
	pp.save()
	return HttpResponseRedirect('../')




