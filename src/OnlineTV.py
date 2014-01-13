import re

class AlreadyDownloaded(Exception):
	pass

class Episode:
	def __init__(self, show, name='unnamed', season=-1,episode=-1,airdate='mm/dd/yyyy', watched=False, dictionary=None):
		if dictionary != None:
			try:
				self.name 		= dictionary['name']
				self._safeName 	= dictionary['_safeName']
				self.season 	= dictionary['season']
				self.episode 	= dictionary['episode']
				self.airdate 	= dictionary['airdate']
				self.watched 	= dictionary['watched']
				self.href 		= dictionary['href']
				
				self.show 		= show
			except KeyError:
				raise ValueError('Invalid dictionary configuration!')
			
		else:
			self.name = name				# Episode Name
			self.setSafeName(name) 			# Episode name that can be stored in a filesystem
			self.season=season;	 			# The season number that this episode is in
			self.episode=episode;   		# the numerical index of this episode
			self.airdate = airdate  		# original airdate on TV
			self.watched = watched  		# Whether it has been watched or not
			self.show = show				# The parent show object of this episode
			self.href = None				# The primewire page listing the stream sites for this episode
			
			self.download_links = list()	# A list where we will store potential download links for this episode
	
	def setSafeName(self, name):
		self._safeName = name.replace('/', '-').replace(':', '')
		
	def getSafeName(self, ):
		if self._safeName == 'unnamed':
			self.setSafeName(self.name)
		return self._safeName 
	
class TV_Show:
	def __init__(self, title='unnamed', episodes=list(), primewire='unnamed', href=None, 
				dictionary=None):
		if dictionary != None:						# Construct from stored JSON
			try:
				self.title 			= dictionary['title']
				self._safeTitle 	= dictionary['_safeTitle']
				self.primewire 		= dictionary['primewire']
				self.href 			= dictionary['href']
				self.base_url 		= dictionary['base_url']
				self.rel_link 		= dictionary['rel_link']
				self.primeId 		= dictionary['primeId']
				self.key 			= dictionary['key']
				self.unwatched 		= dictionary['unwatched']
				self.to_download 	= dictionary['to_download']
				
				episodeList = list()
				for episode in dictionary['episodes']:
					episodeList.append(Episode(self, dictionary=episode))
					
				self.episodes = episodeList
			except KeyError:
				raise ValueError('Invalid dictionary configuration!')
				
		else:	
			self.title = title						# The title of the show as on tv-links
			self.key = title.lower()				# A key that this show will be referenced by for a dict
			self.setSafeTitle(title)				# The title of the show as it can be used for a file/folder name
			self.primewire = primewire  			# The title of the show as on primewire
			self.episodes = episodes				# The list of episodes that we've collected so far
			self.href = href						# the link in primewire to download the show
			self.primeId = -1		   				# the ID that primewire uses to index the show
			
			self.unwatched = list()					# A list where we will store the indexes of episodes that have not been watched
			self.to_download = list()				# A list where we will store indexes of episodes that can be downloaded
		
	def setSafeTitle(self, title):
		self._safeTitle = title.replace('/','-').replace(':','')

	def getSafeTitle(self):
		return self._safeTitle
	
	def relative_link(self):
		"""
		Return a copy of the href for this show, but with the domain
		name (http://www.xxxx.yyy) removed.
		"""
		self.base_url = re.search('http://[^/]+', self.href).group()		# get the base url from the link
		self.rel_link = self.href[len(self.base_url):]						# Save the rest of the string
		return self.rel_link												# return a copy
	
