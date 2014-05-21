import urllib, json, pprint
API_KEY = "apikey=yx4uxh5f7zvcxtfst6xrxw3u"
BASE_URL = "http://api.rottentomatoes.com/api/public/v1.0/movies.json"
GOOG_URL = "http://maps.googleapis.com/maps/api/geocode/json?address="

def PullExternalData(movie_name):
	movies = SearchMovie(movie_name)
	for movie in movies:
		if movie["title"] == movie_name:
			return movie
	return None

def SearchMovie(movie_name, page_limit=1, page_num=1):
	url = BASE_URL + '?'
	url = url + 'q=' + str(movie_name) + '&'
	url = url + 'page_limit=' + str(page_limit) + '&'
	url = url + 'page=' + str(page_num) + '&'
	url = url + API_KEY

	movies = json.load(urllib.urlopen(url))['movies']
	#pprint.pprint(movies)
	return movies

def GetLocationCoordinates(plain_address):
	plain_address = plain_address.strip().replace(" ", "+")
	URL = GOOG_URL + plain_address + "+nyc&sensor=false"
	response = json.load(urllib.urlopen(URL))
	return response['results'][0]['geometry']['location']

	
