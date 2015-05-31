class Movie:
	'Movie storage class for IMDB movies'
	
	def __init__(self, name, date):
		self.name = name
		self.date = date
		
	def __init__(self, critic, user):
		self.critic = critic
		self.user = user
		
	def getName(self):
		return self.name
		
	def getDate(self):
		return self.date
		
	def getCriticScore(self):
		return self.critic
	
	def getUserScore(self):
		return self.user
		
	