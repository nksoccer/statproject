class Movie:
	'Movie storage class for IMDB movies'
	
	def __init__(self, name, date):
		self.name = name
		self.date = date
		self.critic = 0
		self.user = 0
		self.url = ""
		
	def getName(self):
		return self.name
		
	def setUrl(self, url):
		self.url = url
		
	def getUrl(self):
		return self.url
		
	def getDate(self):
		return self.date
		
	def setCriticScore(self, score):
		self.critic = score
		
	def getCriticScore(self):
		return self.critic
	
	def setUserScore(self, score):
		self.user = score
		
	def getUserScore(self):
		return self.user
		
	