class Movie:
	'Movie class for IMDB movies'
	
	def __init__(self, name, date):
		self.name = name
		self.date = date
		
	def getName(self):
		return self.name
		
	def getDate(self):
		return self.date
		
	