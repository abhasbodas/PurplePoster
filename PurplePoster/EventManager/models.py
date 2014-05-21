from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import rottentomatoes, re


# Used by the Movie class
class Actor(models.Model):
	actorRot_ID = models.CharField(max_length=20)
	actorName = models.CharField(max_length=100)
	def __unicode__(self):
		return self.actorName

# Used by the Movie class
class Producer(models.Model):
	producerRot_ID = models.CharField( max_length=20)
	producerName = models.CharField(max_length=100)
	def __unicode__(self):
		return self.producerName

# Used by the Movie class
class Poster(models.Model):
	posterURL = models.URLField();			#Consider changing this to FileField instead
	def __unicode__(self):
		return self.posterURL


# Used by PurplePoster class
class Image(models.Model):
	imageURL = models.URLField();			#Consider changing this to FileField instead
	def __unicode__(self):
		return self.imageURL

# Used by PurplePoster class
class Comment(models.Model):
	commentText = models.CharField(max_length=1000)
	submitter = models.CharField(max_length=50)
	def __unicode__(self):
		return self.commentText
	def addTheComment(self, c, s):
#		self.commentText = c
#		self.submitter = s
#		self.save()
#		return self

class Location(models.Model):
	address = models.CharField(max_length=100)
	lat = models.FloatField(blank=True,null=True)
	lon = models.FloatField(blank=True,null=True)
	def __unicode__(self):
		return self.id

###########################################################################
######					Main Class Models  								###
###########################################################################

class Movie(models.Model):
	movieRot_ID = models.CharField(blank=True, null=True, max_length=20)
	name = models.CharField(max_length=100)
	actor = models.ManyToManyField(Actor)
	producer = models.ManyToManyField(Producer)
	summary = models.CharField(blank=True, null=True, max_length=8000)
	poster = models.ManyToManyField(Poster)
	releaseDate = models.DateField(blank=True, null=True)
	def __unicode__(self):
		return self.name

	def pullExternalData(self):
		try:
			rotMovie = rottentomatoes.PullExternalData(self.name)
			if not rotMovie:
				return None
			
			self.movieRot_ID = rotMovie['id']
			self.name = rotMovie['title']

			#TODO external data node missing
			#self.producer = rotMovie['abridged_directors']
			self.summary = rotMovie['synopsis']
			self.releaseDate = rotMovie['release_dates']['theater']
			
			#FIXME make sure no duplicates get added
			for e in rotMovie['abridged_cast']:
				a = Actor(actorRot_ID = e['id'], actorName = e['name'])
				a.save()
				self.actor.add(a)
				
			for desc in rotMovie['posters']:
				p = Poster(posterURL = rotMovie['posters'][desc])
				p.save()
				self.poster.add(p)
				
			self.save()

		except:
			return None
			
def getMovieNamed(moviename):
	try:
		mv = Movie.objects.get(name=moviename)
	except ObjectDoesNotExist:
		mv = Movie(name = moviename)
		mv.save()
		
	mv.pullExternalData()
	return mv


class PurplePoster(models.Model):
	alias = models.CharField(max_length = 100) 
	movie = models.ForeignKey(Movie)
	submitter = models.CharField(max_length=100, blank=True)    #edit later to point to user intsance
	startTime = models.DateField()
	location = models.CharField(max_length=100)
	locationLat = models.FloatField(blank=True,null=True)
	locationLon = models.FloatField(blank=True,null=True)
	image = models.ManyToManyField(Image)
	comment = models.ManyToManyField(Comment)
	#submitImage()  
	def __unicode__(self):
		moviename = unicode(self.movie)
		if moviename == self.alias:
			return moviename
		else:
			return "%s (%s)" % (self.alias, moviename) 

	def getMovieInfo(self):
		return Movie.objects.get(id=self.movie.id)

	def SetGeoLocation(self, location):
		getLoc = rottentomatoes.GetLocationCoordinates(location)[0]
		self.LocationLat = getLoc['lat']
		self.LocationLat = getLoc['lng']
		self.save()

	def addComment(self, comment):
		self.comment.add(comment)


class UserPreference(models.Model):
	user = models.OneToOneField(User)
	movie = models.ManyToManyField(Movie)
	actor = models.ManyToManyField(Actor)
	#producer = models.ManyToManyField(Producer)
	purplePoster = models.ManyToManyField(PurplePoster)
	area = models.ManyToManyField(Location)
	
	def __unicode__(self):
		return self.user.username

	def addUserMovie(self, movieid):
		try:
			movie = Movie.objects.get(id = movieid)
			self.movie.add(movie)
		except ObjectDoesNotExist:
			print "movie doesnt exist"
		self.save()

	def addUserActor(self, actorid):
		try:
			actor = Actor.objects.get(id = actorid)
			self.actor.add(actor)
		except ObjectDoesNotExist:
			print "actor doesnt exist"
		self.save()

	def addUserPoster(self, purplePosterid):
		try:
			poster = PurplePoster.objects.get(id = purplePosterid)
			self.purplePoster.add(poster)
		except ObjectDoesNotExist:
			print "poster doesnt exist"
		self.save()

	def addUserArea(self, address):
		latlng = rottentomatoes.GetLocationCoordinates(address)
		print latlng
		try:
			location = Location.objects.get(lat = float(latlng['lat']), lon = float(latlng['lng']))
			self.area.add(location)
		except ObjectDoesNotExist:
			location = Location()
			location.address = address
			location.lat = float(latlng['lat'])
			location.lon = float(latlng['lng'])
			location.save()
			self.area.add(location)
		self.save()
				
def getUserPreference(user):
	try:
		return UserPreference.objects.get(user = user)
	except ObjectDoesNotExist:
		up = UserPreference()
		up.user = user
		up.save()
		return up

User.getPreference = getUserPreference
	
