import urllib2
import random
from multiprocessing.pool import ThreadPool
import threading
from movie import Movie 
from lxml import html

NUM_MOVIES = 1000
YEAR_MAX = 5
pool = ThreadPool(processes=1)
		
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
	results = []
	for num in range(0, movieListLen/50):
		root_url = "http://www.imdb.com/search/title?at=0&genres=%s&sort=num_votes" % type
		if num == 0:
			async_result = pool.apply_async(getListFromIMDB, [root_url])
			results.append(async_result)
		else:
			async_result = pool.apply_async(getListFromIMDB, [root_url+"&start=%i" % (num*50 + 1)] )
			results.append(async_result)
		
	movies = []
	for r in results:
		movies += r.get()
		
	return movies

#remove movies that are more than n years old
def alterMovies(n, movies):
	newList = []
	for m in movies:
		if m.getDate() > 2015 - n:
			newList.append(m)
	return newList

def setUrl(movie):
	url = "http://www.rottentomatoes.com/search/?search=" + movie.getName().replace(' ', '+')
	stream = urllib2.urlopen(url)
	print stream.geturl()
	#check for redirect
	if(stream.geturl() != url):
		movie.setUrl(stream.geturl())
		return
	content = stream.read()
	tree = html.fromstring(content)	
	#TODO: check the url if it is the correct year!! quite a few times this fucks up
	searchURL = tree.xpath('//ul[@id="movie_results_ul"]/li[1]/div/div/a/@href')[0]
	movie.setUrl("http://www.rottentomatoes.com" + searchURL)

def setScores(movie):
	content = urllib2.urlopen(movie.getUrl()).read()
	tree = html.fromstring(content)
	critic_score = tree.xpath('//div[@class="critic-score meter"]/a/span/span/text()')
	audience_score = tree.xpath('//div[@class="audience-score meter"]/a/div/div/div/span/text()')
	if(len(critic_score) < 1 or len(audience_score) < 1): #check if bad url or response - reject if it is
		return #do something here!
	movie.setCriticScore(int(critic_score[0]))
	movie.setUserScore(int(audience_score[0]))
	
#set critic scores and user scores in movie type from search query to rottentomatoes -> alters movie list no return
def setRottenTomatoes(movies):
	#search movie in rotten tomatoes and get url
	threads = []
	for m in movies:
		thread = threading.Thread(target = setUrl, args=(m,))
		thread.start()
		threads.append(thread)
	
	for t in threads:
		t.join()
		
	threads = []
	for m in movies:
		thread = threading.Thread(target = setScores, args=(m,))
		thread.start()
		threads.append(thread)
		
	for t in threads:
		t.join()

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

def printData(scores):
	fo = open("data.txt", 'wb')
	for num in range(0, len(scores)):
		if(num == 0): fo.write("Action Movies\r\n")
		if(num == 1): fo.write("Drama Movies\r\n")
		for m in scores[num]:
			fo.write(m.toStr()+ "\r\n")
	
#get list of movies		
movies_drama = alterMovies(YEAR_MAX,  getMovies(NUM_MOVIES, "drama"))
movies_action = alterMovies(YEAR_MAX,  getMovies(NUM_MOVIES, "action"))
#randomly select 50 from movie list
drama_sample = random.sample(movies_drama, 50)
action_sample = random.sample(movies_action, 50)
#get scores from rottentomatoes
setRottenTomatoes(action_sample)
setRottenTomatoes(drama_sample)
#get means
means = getMeans([action_sample, drama_sample])
printData([action_sample, drama_sample])