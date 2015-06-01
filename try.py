import urllib2
import random
from multiprocessing.pool import ThreadPool
import threading
from movie import Movie 
from lxml import html

NUM_MOVIES = 10000
YEAR_MAX = 5
pool = ThreadPool(processes=1)
		
#get list of movies in form from url at imdb site
def getListFromIMDB(URL, output):
	try:
		content = urllib2.urlopen(URL).read()
	except Exception: return
	else:
		pass
	tree = html.fromstring(content)	
	names = tree.xpath('//td[@class="title"]/a/text()')
	dates = tree.xpath('//td[@class="title"]/span[@class="year_type"]/text()')
	movielist = []
	for num in range(0, len(names)):
		m = Movie(names[num], int((dates[num])[1:5]))
		movielist.append(m)
	print URL[len(URL) - 5:]
	output += movielist
	
#get list of movies of size movieListLen from IMDB
def getMovies(movieListLen, type):
	threads = []
	results = []
	for num in range(0, movieListLen/50):
		root_url = "http://www.imdb.com/search/title?at=0&genres=%s&sort=num_votes" % type
		if num == 0:
			getListFromIMDB(root_url, results)
			#thread = threading.Thread(target = getListFromIMDB, args=(root_url, results))
			#thread.start()
			#threads.append(thread)

		else:
			#thread = threading.Thread(target = getListFromIMDB, args=(root_url+"&start=%i" % (num*50 + 1),results))
			getListFromIMDB(root_url+"&start=%i" % (num*50 + 1),results)
			#thread.start()
			#threads.append(thread)

	#for t in threads:
		#t.join()
		
	return results

#remove movies that are more than n years old
def alterMovies(n, movies):
	newList = []
	for m in movies:
		if m.getDate() > 2015 - n:
			newList.append(m)
	return newList

def setUrl(movie):
	url = "http://www.rottentomatoes.com/search/?search=" + movie.getName().replace(' ', '+')
	#check if non-ascii characters contained - don't bother if its contained
	try:
		url.decode('ascii')
	except Exception:
		return
	else: pass
		
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
	try:
		content = urllib2.urlopen(movie.getUrl()).read()
	except Exception:
		return
	else: pass
	
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
def getMeansDiff(scores):
		means = []
		for set in scores:
			totalLen = len(set)
			totaldiff = 0
			for m in set:
				totaldiff += abs(m.getCriticScore() - m.getUserScore())
				if(m.getCriticScore()  == 0 or m.getUserScore() == 0): totalLen -= 1 #bad entries with no ratings
			avgdiff = totaldiff / totalLen
			means.append(avgdiff)
		return means

def getMeans(scores):
	means = []
	for set in scores:
		total = len(set)
		critic_total = 0
		user_total = 0
		for m in set:
			critic_total += m.getCriticScore()
			user_total += m.getUserScore()
			if(critic_total == 0 or user_total == 0): total -= 1 #bad entries with no ratings
		means.append([critic_total/total, user_total/total])
	return means
		
def printData(scores, means, means2):
	fo = open("data.txt", 'wb')
	for num in range(0, len(scores)):
		if(num == 0): fo.write("Action Movies - n = %i\r\n" % len(scores[num]))
		if(num == 1): fo.write("Drama Movies - n = %i\r\n" % len(scores[num]))
		for m in scores[num]:
			try:
				fo.write(m.toStr()+ "\r\n")
			except Exception:
				continue
			else: pass
	fo.write("Means: " + "Action - %s, Drama - %s\r\n" % (means[0], means[1]))
	fo.write("Action-Critic: %i, Action-User: %i, Drama-Critic: %i, Drama-User: %i" % (means2[0][0], means2[0][1], means2[1][0], means2[1][1]))
	
#get list of movies		
movies_drama = alterMovies(YEAR_MAX,  getMovies(NUM_MOVIES, "drama"))
movies_action = alterMovies(YEAR_MAX,  getMovies(NUM_MOVIES, "action"))
#randomly select 50 from movie list
drama_sample = random.sample(movies_drama, 500)
action_sample = random.sample(movies_action, 500)
#get scores from rottentomatoes
setRottenTomatoes(action_sample)
setRottenTomatoes(drama_sample)
#get means
means = getMeansDiff([action_sample, drama_sample])
means2 = getMeans([action_sample, drama_sample])
printData([action_sample, drama_sample], means, means2)