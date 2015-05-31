import urllib2
import random
from movie import Movie 
from lxml import html

NUM_MOVIES = 100
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
def getMovies(movieListLen, type):
	movies = []
	for num in range(0, movieListLen/50):
		root_url = "http://www.imdb.com/search/title?at=0&genres=%s&sort=num_votes" % type
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

#set critic scores and user scores in movie type from search query to rottentomatoes -> alters movie list no return
def setRottenTomatoes(movies):
	#search movie in rotten tomatoes and get url
	for m in movies:
		url = "http://www.rottentomatoes.com/search/?search=" + m.getName().replace(' ', '+')
		stream = urllib2.urlopen(url)
		print stream.geturl()
		#check for redirect
		if(stream.geturl() != url):
			m.setUrl(stream.geturl())
			continue
		content = stream.read()
		tree = html.fromstring(content)	
		#TODO: check the url if it is the correct year!! quite a few times this fucks up
		searchURL = tree.xpath('//ul[@id="movie_results_ul"]/li[1]/div/div/a/@href')[0]
		m.setUrl("http://www.rottentomatoes.com" + searchURL)
	
	scoreList = []
	for m in movies:
		content = urllib2.urlopen(m.getUrl()).read()
		tree = html.fromstring(content)
		if m.getUrl().find(".com/m/") == -1: 
			movies.remove(m) #check if bad url - reject if it is
			continue
		critic_score = tree.xpath('//div[@class="critic-score meter"]/a/span/span/text()')
		audience_score = tree.xpath('//div[@class="audience-score meter"]/a/div/div/div/span/text()')
		if(len(critic_score) < 1 or len(audience_score) < 1):
			movies.remove(m) #check if bad url - reject if it is
			continue
		m.setCriticScore(int(critic_score[0]))
		m.setUserScore(int(audience_score[0]))
	

#from paired means turn into set of differences then into mean of difference for each set
def getMeans(scores):
		means = []
		for set in scores:
			totaldiff = 0
			for m in set:
				totaldiff += abs(m.getCriticScore() - m.getUserScore())
			avgdiff = totaldiff / len(set)
			means.append(avgdiff)
		return means

#get list of movies		
movies_drama = alterMovies(YEAR_MAX,  getMovies(NUM_MOVIES, "drama"))
movies_action = alterMovies(YEAR_MAX,  getMovies(NUM_MOVIES, "action"))
#randomly select 50 from movie list
drama_sample = random.sample(movies_drama, 5)
action_sample = random.sample(movies_action, 5)
#get scores from rottentomatoes
setRottenTomatoes(action_sample)
setRottenTomatoes(drama_sample)
#get means
means = getMeans([action_sample, drama_sample])
print means