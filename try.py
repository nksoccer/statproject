import urllib2
from movie import Movie 
from lxml import html

NUM_MOVIES = 200
YEAR_MAX = 5

#get list of movies in form from url at imdb site
def getListFromIMDB(URL):
	content = urllib2.urlopen(URL).read()
	tree = html.fromstring(content)	
	names = tree.xpath('//td[@class="title"]/a/text()')
	dates = tree.xpath('//td[@class="title"]/span[@class="year_type"]/text()')
	movielist = []
	for num in range(0, len(names)):
		m = Movie(names[num], int((dates[num])[1:5]))
		movielist.append(m)
	return movielist
	
#get list of movies of size movieListLen from IMDB
def getMovies(movieListLen):
	movies = []
	for num in range(0, movieListLen/50):
		root_url = "http://www.imdb.com/search/title?at=0&genres=drama&sort=num_votes"
		if num == 0:
			movies += getListFromIMDB(root_url)
		else:
			movies += getListFromIMDB(root_url+"&start=%i" % (num*50 + 1))
	return movies

#remove movies that are more than n years old
def alterMovies(n, movies):
	newList = []
	for m in movies:
		if m.getDate() > 2015 - n:
			newList.append(m)
	return newList
		
movies = getMovies(NUM_MOVIES)
movies = alterMovies(YEAR_MAX, movies)
for movie in movies:
	print movie.getName() + " " + str(movie.getDate())