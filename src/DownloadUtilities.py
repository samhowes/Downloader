import html.parser as HTMLParser							# StdLib imports
import os
import queue
import re
import sys
import time
import locale
import urllib.request
import pydevd


from bs4 import BeautifulSoup 								#Third party imports #TODO make this an included file, not a dependent library
from OnlineTV import AlreadyDownloaded, Episode, TV_Show 	# Imports from this project
import MyThreads					

RUN_DIR = "../run/"
LOG_DIR = "../run/log/"
DOWNLOAD_DIR = "../run/Downloads/"

########## 		Exceptions 					##########
class InvalidStatusCode(Exception):
	"""Exception raised by DownloadUtilities.grabUrl()
	when it recieves an unexpected status code"""
	def __init__(self, unexpectedCode):
		self.statusCode = unexpectedCode

class UrlRedirected(Exception):
	pass

##########		Main Class					##########
class DownloadUtilities:
	def __init__(self, out):
		self.out = out
		self.log = out.log
		self.encoding = locale.getpreferredencoding()
		
	def get_watchlist(self):
		"""Retrieve the watchlist from TVLinks"""
		home_url = 'http://www.tvmuse.eu'		# The base URL that we will be making requests from
		watchlist_url = '/myaccount.html?zone=subscriptions' # the HREF to get to my watchlist
		phpsess_re = '(PHPSESSID=[^;]+);'		# RegEx to extract a PHP Session Id from a cookie header
		tvlsess_re = '(tvl_keepon=[^;]+);'		# RegEx to extract a tv-links session id from a cookie header
	
		self.out.addBody('\rLoading TVMuse Homepage...')
		with urllib.request.urlopen(home_url) as response:					### First request: get TVMuse Homepage for a PHP Session
			set_cookie = response.getheader('Set-Cookie')					# If we don't set our PHP Session, then it won't like our session
			if set_cookie is not None:
				phpsess = re.search(phpsess_re, set_cookie, re.IGNORECASE)	# Extract the session id from the Cookie the server gave us
				if phpsess:
					phpsess = phpsess.group(1)
		
		headers = {'Cookie': phpsess,										# Set up headers for a POST to the server for logging in				   
			   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
		
		data = {'action': '7', 'username': 'showes06@gmail.com',			# Prepare the POST body for the server
				'passw': 'wed629'}  										# 'action=7&username=showes06@gmail.com&passw=wed629'
		data = urllib.parse.urlencode(data).encode(self.encoding)				# first URLEncode the string, then encode to bytes with our encoding
		
		self.out.addBody('\rLogging in to TVMuse...')
		req = urllib.request.Request(home_url + '/ajax.php', data, headers, method='POST') ### Second request: log in to the server
		with urllib.request.urlopen(req) as response:
			xml = response.read().decode(self.encoding)							# the server should respond with xml this time
			set_cookie = response.getheader('Set-Cookie')
		
		tvlsess = re.search(tvlsess_re, set_cookie).group(1)				# Record our site session id
		soup = BeautifulSoup(xml)											
		try:																# Make sure the login process succeeded
			assert soup.results.refresh.string == '1'						# Check the contents of the two tags 
			assert soup.results.renable.button.string == 'fsend_b'
		except (AssertionError, TypeError):									# TypeError is here in case the tags that we referenced didn't exist
			if AssertionError:
				sys.stderr.write('Error: Login to: "' + home_url + '"failed!\n')
			elif TypeError:
				sys.stderr.write('Error: Unexpected server response to login!\n')
			exit(1)
		
		
		headers = {'Cookie': phpsess+ '; ' + tvlsess}						# Set our session information
		self.out.addBody('\rRetrieving the watchlist from TVMuse...')
		req = urllib.request.Request(home_url + watchlist_url, headers=headers, method='GET') ### Third request: get the watchlist page
		with urllib.request.urlopen(req) as response:
			html = response.read().decode(self.encoding, 'ignore')
		
		with open(LOG_DIR + 'TVWatchlist.html', 'w') as debugOut:
			debugOut.write(html)
		
		### Now process our results and get show names ###
		self.out.addBody('\rExtracting show names and information...')
		titles = list()	 			# a collection of titles that we'll build
		self.shows = dict()	  		# the collection of shows that we find
		soup = BeautifulSoup(html)
		parent = soup.find('ul', class_='table_subscriptions')					# shows are contained <li> in a <ul>
		
		### Get show names
		for item in parent.find_all('li', class_='cfix brd_b'):					# iterate thorugh each show
			showdiv = item.find('div', class_='c1 brd_r_dot')					# the information we want is in a <div>
			title_a = showdiv.find('a', class_='bold big f_left mr_1')			# The show title is in an <a>
			title = title_a.get_text()
			titles.append(title)												# record the title that we found
			
			episode_div = item.find('div', id=re.compile('subs_[0-9]+'))		# The watched and unwatched episodes are in a div titled by its subscription number
			episode_list = episode_div.find_all('li', class_='cfix brd_b_dot')  # an episode is contained in an <li>
			
			newShow = TV_Show(title = title, primewire = title.lower())
			episodes = list()
			### Get the unwatched episodes
			for episode in episode_list:										
				anchor = episode.find('span', class_='c2').a					# get the <a> that contains "season x, episode y" text
				try:
					anchor['class'].index('gray')								# test if the <a> has a class atribute of 'gray'
					continue													# if it does, this episode has not yet aired and can't be downloaded yet
				except ValueError:
					pass														# this means that the class list doesn't contain gray, and we can download the video
				
				label = episode.find('span', class_='c2').a.get_text()		  	# get the "Season x, episode y" text
				(season, index) = label.split(', ')
				season = season.split(' ')[-1]								  	# now get just the number of each
				index = index.split(' ')[-1]
				
				airdate = episode.find('span', class_='c3').span.get_text().strip() # get the "mm/dd/yyyy" for the airdate
				if airdate == None or airdate == '':							# if there is no airdate listed, then it is likely a false entry
					continue
				
				try:															
					episode.find('span', class_='c4').input["checked"]		  	# this input appears if the the show has been watched
					watched = True
				except KeyError:
					watched = False											 	# otherwise you can click a box and javascript submits
					newShow.unwatched.append(len(episodes))						# Record the episode's index in the Show's download queue
					
				episodes.append(Episode(show=newShow, name='unnamed', season=season,
										episode=index, airdate=airdate, watched=watched))
			
			newShow.episodes = episodes	
			self.shows[newShow.key] = newShow
		return self.shows
	
	def get_download_links(self):
		"""Log in to Primewire and get the homepage for each show"""
		link_re = re.compile(r'(?P<href>/tv-(?P<id>[0-9]+)-(?P<name>[^"]+)?)') 	# RegEx to extract the show name and id from the Href in primewire
		phpsess_re = '(PHPSESSID=[^;]+);'										# RegEx for extracting a PHP session id from a Cookie
		home_url = 'http://www.primewire.ag'									# The base URL that we will be making requests from									   
		login_url = '/login.php'												# The URL for the login page that we post to
		username = 'showes06'; password = 'wed629'								# Login information for the POST body
		
		########## First retrieve user information from Primewire		##########
		self.out.addBody('\rLogging in to Primewire...')
		login = {'username': username, 'password': password, 'login_submit': 'Login'} 
		data = urllib.parse.urlencode(login).encode(self.encoding)							# URL encode the string, then encode to bytes with our encoding
		
		req = urllib.request.Request(home_url + login_url, data, method='POST')				### First Request: log in to primewire
		with urllib.request.urlopen(req) as response:
			assert response.status == 200
			set_cookie = response.getheader('Set-Cookie')									# get the cookie for the session ID
			assert set_cookie is not None
		
		self.out.addBody('\rRetrieving the watchlist from primewire')
		headers = {'Cookie': re.search(phpsess_re, set_cookie, re.IGNORECASE).group(1)} 	# Keep our session id in the headers for future requests
		req = urllib.request.Request(home_url + '/towatch' + '/' + username, headers=headers, method='GET') ### Second Request: get the primewire watchlist
		with urllib.request.urlopen(req) as response:
			html = response.read().decode(self.encoding, 'ignore')
			assert response.status == 200
		
		########## Now process the data and match tv-links shows to Primewire 	##########
		self.out.addBody('\rLinking TVMuse to Primewire...')
		soup = BeautifulSoup(html)
		profile_div = soup.find('div', class_='regular_page profile_page')					# Get the main content holder <div> of the page
		show_divs = profile_div.find_all('div', class_='index_item')						# It contains one show in each <div>
		
		tv_titles_list = list(self.shows.keys())		# Get a list of TV Titles for iterating...
		tv_titles = set(tv_titles_list)					# 	and a set for membership
		prime_titles = list()							# Primewire show titles
		unmatched_titles = list()						# Titles that we find on TV-links, but not Primewire
		
		for div in show_divs:																# For each div from Primewire
			link = link_re.search(div.a['href'])											# extract the link for each show's home page
			prime_titles.append(															# pack the name, href, and id into a tuple
				(link.group("name").replace('-', ' '), 
				 link.group("href"), 
				 link.group('id')
				)) 
		
		for ii in range(len(prime_titles)):													# Now match each title found with an existing show
			title = prime_titles[ii][0].lower()
			if title not in tv_titles:									  					# If the two sites don't name the shows the exact same thing...
				words = title.split(' ')
				maxindex = -1																# The index of the item with the most matches
				maxwords = 0																# the actual number of matches for the words
				for jj in range(len(tv_titles_list)):					   					# For each title...
					wordsincommon = len(set(tv_titles_list[jj].split(' ')) & set(words))	# check the number of words that they have in common
					
					if wordsincommon > maxwords:											# Ignoring the possiblity of two identical matches for now TODO
						maxindex = jj
						maxwords = wordsincommon
		
				if maxwords == 0 or maxindex == -1:						 
					self.log.error('Title %s found in Primewire watchlist but not in TVLinks Watchlist.' % (prime_titles[ii])[0])
					unmatched_titles.append(title)											# record the missed title
					continue																# don't continue processing this title
				else:													 					# We should have found the title for primewire
					title = tv_titles_list[maxindex]
			
			tv_titles.remove(title)															# update the set for later comparisons
				
			self.shows[title].primewire = prime_titles[ii][0]								# record the primewire name
			self.shows[title].href = home_url + prime_titles[ii][1]							# record the link for the show home page
			self.shows[title].primeId = prime_titles[ii][2]					 				# record the index that primwire uses
		return self.shows
	
	def grabUrl(self, url, statuscode, post=None):
		""" Convenience function to download a URL
		@param statuscode: The expected Server Response code 
		@raise InvalidStatusCode: When received status code is not as expected
		@return: html decoded from UTF-8"""
		if post != None:													# If we should do a post
			if type(post) != type(dict()):
				raise TypeError('Post values must be of type "dict" not "%s"' % (type(post)))
			method = 'POST'
			data = urllib.parse.urlencode(post).encode(self.encoding)		# Encode into URL for POST body, then encode into bytes using our locale 
		else:
			method = 'GET'													# Do a GET by default
			data = None
		
		req = urllib.request.Request(url, data, method=method)
		with urllib.request.urlopen(req) as response: 						# Get the url
			if response.status != statuscode:								# Check to see if the status code is what we expect
				raise InvalidStatusCode(response.status)
			elif response.url != url:										# Check if we were redirected
				raise UrlRedirected()
			else:
				return response.read().decode(self.encoding, 'ignore')		# Otherwise, return the body of the response
	
	def generateDownloadQueue(self): #TODO Test this funciton
		"""Generate a queue of episode links to download 
		@return: unordered set of shows whose episodes have valid 
		download links"""
		
		########## 	Process our data to find unwatched episodes 	##########
		MAX_THREADS = 6
		download_queue = set()				# The final output set of shows that we can stream from
		threadPool = list()					# Collection of threads to do work 
		jobQ = queue.Queue()				# Job queue that the threads will get from, and join to when we are done
		messageQ = queue.Queue()			# Queue for messages from the threads to output to the user
		resultsQ = queue.Queue()			# Queue that the threads will place the results on 
		
		self.out.addBody('\rPopulating the Queue with download links...')
		for key in self.shows:														# Check each show for unwatched episodes
			show = self.shows[key]
			if show.href == None or len(show.unwatched) == 0:						# Check if we can download for this show
				continue
			jobQ.put(show)
		
		for ii in range(MAX_THREADS):
			threadPool.append(MyThreads.InfoThread(jobQ, messageQ, resultsQ, self.grabUrl, name="InfoThread%d" % (ii)))
			threadPool[-1].setDaemon(True)
			threadPool[-1].start()		
			
		show = None
		while jobQ.unfinished_tasks > 0:											# While the threads are still working...
			show = resultsQ.get()													# Retrieve a result from the threads
			if show != None:
				self.shows[show.key] = show											# store the results
				download_queue.add(self.shows[show.key])
			
			while not messageQ.empty():												# While there are messages to print from the threads
				message = messageQ.get()
				if len(message) != 2:
					raise ValueError('Tuple from messageQ must be of length 2!')
				
				if message[0] == 'Error':											# Print the message in its appropriate form
					self.log.error(message[1])
				elif message[0] == 'Body':
					self.out.addBody(message[1])
				else:
					raise ValueError('String "%s" is not a valid message for the messageQ!' % (message[0]))
		
		jobQ.join()																	# Block until all threads have exited
		return download_queue														# Return the set
	
	def download_episodes(self, download_queue):
		""" Attempt to download all episodes in the queue 
		MULTITHREAD"""
		
		self.out.addBody('\rDownloading the queue...')
		video_format = DOWNLOAD_DIR + '{0}/S{1:>02}_E{2:>02}--{3}'							# Format string for the file name we will store
		
		for show in download_queue:														
			for ind in show.to_download:											# For each episode that has download links...
				episode = show.episodes[ind]
				video_filename = video_format.format(episode.show.getSafeTitle(),
									episode.season, episode.episode, episode.getSafeName()) + '.flv'
				
				for stream_link in episode.download_links:								# For each streaming link we found earlier...
					try:
						if self.do_download(stream_link, video_filename) == True:		# Attempt to download the link
							break														# terminate if the download was successful
					except AlreadyDownloaded:
						self.out.addBody('File "%s" already exists! Skipping download.' % (video_filename))
						self.log.error('File "%s" already exists! Skipping download.' % (video_filename))
						break
				
		self.log.success('Downloaded entire queue!')
		self.out.addBody('Downloaded entire queue! Exiting! :D')
	
	def do_download(self, stream_link, video_filename):
		"""Given a link to a video on Putlocker or Sockshare, download the video.
		Return True on success, False otherwise."""
		if not os.path.exists(video_filename[:video_filename.rfind('/')]):			# Make sure the target directory exists
			sys.stderr.write('Error: path not found: "%s"' % (video_filename[:video_filename.rfind('/')]))
			return False
		
		if os.path.exists(video_filename):											# Make sure the the file hasn't already been downloaded
			raise AlreadyDownloaded()	
		########## 	Navigate to the actual link for the download stream		##########
		
		self.out.addBody('Downloading video from: "' + stream_link + '"')
		url_re = 'url=["\'](?P<href>[^"\']*)["\']'									# RegEx to extract an url from "url=''"
		stream_re = "playlist:\s*['\"](?P<href>[^'\"]+)['\"]"						# RegEx to extract the "playlist: ''" entry that indicates the location of the stream
		
		home_url = re.search('http://[^/]+', stream_link).group()					# Get the base url from the link for future requests
		
		try:	
			html = self.grabUrl(stream_link, 200)									###First Request: Grab the landing page for the video
		except UrlRedirected:
			self.out.addBody('\rBad link found, trying the next one')
			self.log.error('Bad Sockshare link found: %s' % (stream_link))
			return False
		
		try:
			soup = BeautifulSoup(html)
			input_tag = soup.find('input',											# The server wants us to post back the hash found in the confirm form
							  attrs={'name':'hash', 'type':'hidden'})
		
			values = {'hash': input_tag['value'],									# Set up the POST body content for the next request
						'confirm': 'Continue as Free User'}
		except: 
			pydevd.settrace()
	
		html = self.grabUrl(stream_link,200,values)									### Second request: Get the page with the video player
		
		try:
			stream_href = re.search(stream_re, html).group('href')					# Extract the href for the /getfile.php? query that leads us to the MRSS feed
		except:
			pydevd.settrace()
	
		xml = self.grabUrl(home_url + stream_href, 200)								#### Third request: get the mrss feed and the URL of the .flv file
		
		real_stream_link = re.search(url_re, xml).group('href')						# extract the final URL for the .flv download
		real_stream_link = HTMLParser.HTMLParser().unescape(real_stream_link)		# escape the HTML entities in the link
		
		########## 		Start the actual Download 			##########
		req = urllib.request.Request(real_stream_link, method='GET')				### Fourth request: get the source video file
		with urllib.request.urlopen(req) as response:								
			assert response.status == 200											#TODO
			self.out.addBody('\rVideo Size: %.1f MB.' % (int(response.getheader('Content-Length'))/1048576.))	# '\r' tells the addBody function to not ouput a blank line before this one
			bytecount = 0															# Bytes downloaded
			block_size = 4*1024														# Block transfer size
			startTime = time.perf_counter()											# Time the download time
			lastUpdate = None														# Last time the screen was updated
			try:
				out_stream = open(video_filename, 'wb')								# open our output file stream for writing raw binary
				assert out_stream is not None
			except (OSError, IOError) as err:
				sys.stderr.write('Unable to open for writing: %s' % str(err))
				return False
			########## 	Download the file! 				##########
			while True:																# Download data and write to a local file
				data_block = response.read(block_size)								# Get 'block_size' of data at a time
				assert response.getheader('Content-Type') != 'text/html'			# TODO make sure we get xml, not html ??
	
				if len(data_block) == 0:											# make sure we are still downloading
					break
				
				bytecount += len(data_block)										# keep track of our total size
				out_stream.write(data_block)										# write the output data to our local file
				
				if lastUpdate == None or time.perf_counter() - lastUpdate > 1.: 	# update the screen once every second
					diff = time.perf_counter() - startTime
					self.out.updateStatus("Bytes Downloaded: %.1f MB. Elapsed time: %dm %ds. Speed: %d kB/s %s"
										% (bytecount/1048576, int(diff)/60, int(diff) % 60, bytecount/(1024*diff), ' '*10))
					lastUpdate = time.perf_counter()
					
		self.out.addBody('Download completed! Total time = %dm %ds.\n' % (diff/60, diff % 60))
		
		message = 'Successfully downloaded file: %s from %s; total time = %d; total size = %.2f MB' % \
					(video_filename, stream_link, time.time()-startTime, bytecount/1048576)
		self.out.addBody(message)
		self.log.success(message)
		
		with open(RUN_DIR + 'completed.txt','a') as stream:
			stream.write(video_filename + '\n')
		
		return True
