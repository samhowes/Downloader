# StdLib imports
import html.parser as HTMLParser							
import os
import queue
import re
import sys
import threading
import datetime
import time
import locale
import urllib.request
from urllib import request

from collections import OrderedDict as odict

#Third party imports
from bs4 import BeautifulSoup

# Imports from this project								 
from CustomUtilities import create_infra
from OnlineTV import AlreadyDownloaded, Episode, TV_Show 	
import MyThreads					
import GUI
import GUITools

RUN_DIR = "../run/"
LOG_DIR = "../run/log/"
DOWNLOAD_DIR = "../run/Downloads/"


class DownloadMaster(threading.Thread):
	def __init__(self, parent, callbackQ, name=None):
		threading.Thread.__init__(self, name=name)
		self.callbackQ = callbackQ
		self.setDaemon(True)
		self.parent = parent
	
	def run(self):
		DownloadUtilities(self.parent, self.callbackQ).main()
			

########## 		Exceptions 					##########
class InvalidStatusCode(Exception):
	"""Exception raised by DownloadUtilities.grabUrl()
	when it recieves an unexpected status code"""
	def __init__(self, unexpectedCode):
		self.statusCode = unexpectedCode

class UrlRedirected(Exception):
	pass

class BadLink(Exception):
	def __init__(self, message):
		self.msg = message

class MyRequest(urllib.request.Request):
	stdRequest = urllib.request.Request
	def __init__(self, *args, **kwargs):
		self.stdRequest.__init__(self, *args, **kwargs)
		self.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:25.0) Gecko/20100101 Firefox/25.0')

##########		Main Class					##########
class DownloadUtilities:
	def __init__(self, parent, callbackQ):
		self.parent = parent
		self.callbackQ = callbackQ
		self.encoding = locale.getpreferredencoding()
		urllib.request.Request = MyRequest
		#install a proxy for debugging
		#proxy = request.build_opener(request.ProxyHandler({'http':'localhost:8080'}))
		#request.install_opener(proxy)
	
	def main(self):
		### First set up the working environment ###
		create_infra([])
		
		########## Now gather all the data to prepare for downloading 	##########
	
		print('Initializing internal data structures...')
			
		shows = self.get_watchlist()								# First get all the shows into a data structure for processing
		shows = self.get_download_links()							# Now match the shows from tv-links to primewire #MULTITHREAD
		self.download_queue = self.generateDownloadQueue()				# Create a set of all the episodes we can download
		
		print('Checking Folders...')
		folders = list()											# Make sure we have our folder heirarchy for each show
		for show in shows.values():
			folders.append(show.getSafeTitle())
		
		create_infra(folders)
		
		#export_watchlist(shows)									# TODO: export the watchlist and data structures for later use/resuming downloads
		
		########## 		Have the user select the download order 		##########
		
		self.download_order = list(self.download_queue)						# Convert the set to a list for ordering
		choices = ['']*len(self.download_queue)
		for ii, show in enumerate(self.download_order):						# Get the title of each show to display to the user
			choices[ii] = show.title
		
		print('Starting Downloads')
		#TODO out.updateStatus('Preparing to start downloading...')
	
		if self.callbackQ != None:									# Have the User choose which shows to download first
			self.callbackQ.put(
				(GUITools.RankPopup, ('Select the order to download...', choices, self.onRank))
				)
			self.event = threading.Event()
			self.event.wait()										# Wait for the shows to be ranked

		# Now actually download everything
		self.download_episodes()# Do the actual downloading

	def onRank(self, rankOrder):									# Executed by the GUIThread
		'''Allow another thread to re-order the download
		queue. This is in response to a user's selection
		of their preference'''
		newOrder = [None]*len(self.download_order)					# Will be the new self.download_order
		unorderedShows = set(list(range(len(self.download_order))))	# Keep track of the shows we haven't ordered yet
		for ii,index in enumerate(rankOrder):						
			if index == None:
				break
			newOrder[ii] = self.download_order[index]				# permute each show in the correct order
			unorderedShows.discard(index)							# Keep track of what we've done: rankOrder isn't a complete array
		
		for ii,index in zip(range(ii,len(newOrder)),unorderedShows):
			newOrder[ii] = self.download_order[index]				# Fill in the rest of the queue with arbitrary values
			
		self.download_order = newOrder
		self.event.set()											# Tell this thread to continue executing
		
	def get_watchlist(self):
		"""Retrieve the watchlist from TVLinks"""
		home_url = 'http://www.tvmuse.com'		# The base URL that we will be making requests from
		watchlist_url = '/myaccount.html?zone=subscriptions' # the HREF to get to my watchlist
		phpsess_re = '(PHPSESSID=[^;]+);'		# RegEx: extract PHP Session Id from cookie header
		tvlsess_re = '(tvl_keepon=[^;]+);'		# RegEx: extract tv-links session id from cookie header
	
		print('Loading TVMuse Homepage...')
		with urllib.request.urlopen(home_url) as response:					### First request: get TVMuse Homepage for a PHP Session
			assert response.code == 200
			if response.url != home_url:									# Check if we were redirected because of a new domain
				home_url = response.url
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
		
		print('Logging in to TVMuse...')
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
		print('Retrieving the watchlist from TVMuse...')
		req = urllib.request.Request(home_url + watchlist_url, headers=headers, method='GET') ### Third request: get the watchlist page
		with urllib.request.urlopen(req) as response:
			html = response.read().decode(self.encoding, 'ignore')
		
		with open(LOG_DIR + 'TVWatchlist.html', 'w') as debugOut:
			debugOut.write(html)
		
		### Now process our results and get show names ###
		print('Extracting show names and information...')
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
		print('Logging in to Primewire...')
		login = {'username': username, 'password': password, 'login_submit': 'Login'} 
		data = urllib.parse.urlencode(login).encode(self.encoding)							# URL encode the string, then encode to bytes with our encoding
		
		req = urllib.request.Request(home_url + login_url, data, method='POST')				### First Request: log in to primewire
		with urllib.request.urlopen(req) as response:
			assert response.status == 200
			set_cookie = response.getheader('Set-Cookie')									# get the cookie for the session ID
			assert set_cookie is not None
		
		print('Retrieving the watchlist from primewire')
		headers = {'Cookie': re.search(phpsess_re, set_cookie, re.IGNORECASE).group(1)} 	# Keep our session id in the headers for future requests
		req = urllib.request.Request(home_url + '/towatch' + '/' + username, headers=headers, method='GET') ### Second Request: get the primewire watchlist
		with urllib.request.urlopen(req) as response:
			html = response.read().decode(self.encoding, 'ignore')
			assert response.status == 200
		
		########## Now process the data and match tv-links shows to Primewire 	##########
		print('Linking TVMuse to Primewire...')
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
					#TODO self.log.error('Title %s found in Primewire watchlist but not in TVLinks Watchlist.' % (prime_titles[ii])[0])
					unmatched_titles.append(title)											# record the missed title
					continue																# don't continue processing this title
				else:													 					# We should have found the title for primewire
					title = tv_titles_list[maxindex]
			
			tv_titles.remove(title)															# update the set for later comparisons
				
			self.shows[title].primewire = prime_titles[ii][0]								# record the primewire name
			self.shows[title].href = home_url + prime_titles[ii][1]							# record the link for the show home page
			self.shows[title].primeId = prime_titles[ii][2]					 				# record the index that primwire uses
		return self.shows
	
	def import_data(self, importFile):
		if not os.path.exists(importFile):
			raise FileNotFoundError(importFile)
		import json
		with open(importFile, 'r') as instream:
			data = json.load(instream)
		try:
			showlist = data['shows']
			if type(showlist) != type(list()):
				raise ValueError('Incorrect input file type!')
			
			newShows = odict()
			
			for show in showlist:
				newShows[show['key']] = TV_Show(dictionary=show)
				
		except KeyError:
			raise ValueError('Incorrect input file type!')
		
	def export_data(self, exportFile):
		import json
		if not os.path.exists(os.path.dirname(exportFile)):
			raise ValueError('Invalid file name!')
		# First convert our data into a dictionary
		data = odict()
		data['Date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		
		showlist = list()
		for show in self.shows:
			episodeList = list()
			for epi in show.episodes:
				episodeList.append(odict([
						('name',			epi.name),
						('_safeName',		epi.getSafeName()),
						('season',			epi.season),
						('episode',			epi.episode),
						('airdate',			epi.airdate),
						('watched',			epi.watched),
						('href',			epi.href),
						('download_links',	epi.download_links),
						]))
			
			showlist.append(odict([
						('title',		show.title),
						('_safeTitle',	show.getSateTitle())
						('primewire',	show.primewire),
						('href',		show.href),
						('base_url',	show.base_url),
						('rel_link',	show.rel_link),
						('prmeId',		show.primeId),
						('key',			show.key),
						('unwatched',	show.unwatched),
						('to_download',	show.to_download)
						('episodes',	episodeList)
						]))

		data['Shows'] = showlist
		with open(exportFile, 'w') as outstream:
			outstream.write(json.dumps(data, indent=4))
			outstream.write('\n')
			
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
		try:
			with urllib.request.urlopen(req) as response: 						# Get the url
				if response.status != statuscode:								# Check to see if the status code is what we expect
					raise InvalidStatusCode(response.status)
				elif response.url != url:										# Check if we were redirected
					raise UrlRedirected()
				else:
					return response.read().decode(self.encoding, 'ignore')		# Otherwise, return the body of the response
		
		except urllib.error.HTTPError as err:								# Catch an HTTP Error and wrap it in our own exception
			raise BadLink('%d: %s' % (err.code, err.reason))
			
		
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
		
		print('Populating the Queue with download links...')
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
					
		jobQ.join()																	# Block until all threads have exited
		return download_queue														# Return the set
	
	def download_episodes(self):
		""" Attempt to download all episodes in the queue 
		MULTITHREAD"""
		
		print('Downloading the queue...')
		video_format = DOWNLOAD_DIR + '{0}/S{1:>02}_E{2:>02}--{3}'							# Format string for the file name we will store
		
		for show in self.download_order:														
			for ind in show.to_download:											# For each episode that has download links...
				episode = show.episodes[ind]
				video_filename = video_format.format(episode.show.getSafeTitle(),
									episode.season, episode.episode, episode.getSafeName()) + '.flv'
				
				for stream_link in episode.download_links:								# For each streaming link we found earlier...
					try:
						if self.do_download(stream_link, video_filename) == True:		# Attempt to download the link
							break														# terminate if the download was successful
					
					except BadLink as err:
						print('Bad link: %s' % (err.msg))
						continue
						
						
					except AlreadyDownloaded:
						print('File "%s" already exists! Skipping download.' % (video_filename))
						#TODO self.log.error('File "%s" already exists! Skipping download.' % (video_filename))
						break
				
		#TODO self.log.success('Downloaded entire queue!')
		print('Downloaded entire queue! Exiting! :D')
	
	def do_download(self, stream_link, video_filename):
		"""Given a link to a video on Putlocker or Sockshare, download the video.
		Return True on success, False otherwise."""
		if not os.path.exists(video_filename[:video_filename.rfind('/')]):			# Make sure the target directory exists
			sys.stderr.write('Error: path not found: "%s"' % (video_filename[:video_filename.rfind('/')]))
			return False
		
		if os.path.exists(video_filename):											# Make sure the the file hasn't already been downloaded
			raise AlreadyDownloaded()	
		########## 	Navigate to the actual link for the download stream		##########
		
		print('Downloading video from: "' + stream_link + '"')
		url_re = 'url=["\'](?P<href>[^"\']*)["\']'								# RegEx to extract an url from "url=''"
		stream_re = {'putlocker': "playlist:\s*['\"](?P<href>[^'\"]+)['\"]",					# RegEx to extract the "playlist: ''" entry that indicates the location of the stream
					'sockshare':  "playlist:\s*['\"](?P<href>[^'\"]+)['\"]",
					'promptfile': "clip:\s*\{\s*url:\s*['\"](?P<href>[^'\"]+)['\"]"}
		
		
		domain = stream_link.split('.')[1]
		if domain not in ('putlocker', 'sockshare', 'promptfile', 'nowvideo'):
			raise ValueError('Domain "%s" can not yet be handled by Downloader!')
		
		home_url = re.search('http://[^/]+', stream_link).group()
		
		try:	
			html = self.grabUrl(stream_link, 200)								###First Request: Grab the landing page for the video
		except UrlRedirected:
			print('Bad link found, trying the next one')
			#TODO self.log.error('Bad link found: %s' % (stream_link))
			return False
	
					
		if domain in ('putlocker', 'sockshare', 'promptfile'):					## These domains use a confirm page
			soup = BeautifulSoup(html)											# The confirm page contains a button, and a 
																				# hash to submit, scrape the page to find it
			if domain == 'promptfile':
				input_tag = soup.find('input',									# Scrape the hidden input tag
								attrs={'name':'chash', 'type':'hidden'})
				values = {'chash': input_tag['value']}							# Pack it for submision
		
			else:
				input_tag = soup.find('input',									# Scrape the hidden input tag	
							attrs={'name':'hash', 'type':'hidden'})
	
				values = {'hash': input_tag['value'],							# Pack it for submision	
						  'confirm': 'Continue as Free User'}
					
			html = self.grabUrl(stream_link,200,values)							### Second request: Submit and get the video page
			stream_href = re.search(stream_re[domain], html).group('href')		# Scrape the video URL
		
			if domain == 'promptfile':								
				real_stream_link = stream_href									# Promptfile will get us to the file with a redirect
			
			else:	
				xml = self.grabUrl(home_url + stream_href, 200)					### Third request: Putlocker and Sockshare use an MRSS feed
				
				real_stream_link = re.search(url_re, xml).group('href')					# extract the final URL for the .flv download
				real_stream_link = HTMLParser.HTMLParser().unescape(real_stream_link)	# escape the HTML entities in the link
		
		elif domain == 'nowvideo':												# Nowvideo brings us to the video page immediately
			index = html.find('flashvars')										# The GET request uses values of the variable "flashvars"
			if index == -1:
				print('Bad link: No flashvars found.')
				return False
			
			sub = html[index:index+1200]										# only use the html we need for faster searching 
			values = odict()
			flashvar_re = r"flashvars\.%s\s*=\s*[\"'](?P<val>[^'\"])[\"']" 		#Regular expression to extract a "flashvars.%s" variable
			
			real_stream_link = re.search(flashvar_re % ('domain'), sub).group('val')	#Get the domain of the video
			
			## The GET for nowvideo retrieves the video immediately, 
			# and takes the following parameters:
			values['file']= re.search(flashvar_re % ('file'), sub).group('val')	# File code
			values['user']= 'undefined'											# User name
			values['numOfErrors'] = 0											# Don't know the purpose of this, but its used normally
			values['cid'] = re.search(flashvar_re % ('cid'),sub).group('val')	# 'cid' is a parameter
			values['key'] =	re.search(r"var\s+fkzd\s*=\s*[\"'](?P<val>[^'\"])[\"']", sub).group('val') # the 'key' comes from the var 'fkzd'
			values['cid3']= re.search(flashvar_re % ('cid3'),sub).group('val')	# 'cid3' is also a parameter, I think the origin domain
			values['pass']= 'undefined'											# Password	
			
			real_stream_link += 'api/player.api.php?'
			real_stream_link += urllib.parse.urlencode(values)					# Add the query string
		elif domain == 'vidxden':
			soup = BeautifulSoup(html)
			input_tag = soup.find('input',										# Grab the captcha form, we'll instruct the user to load the page
								attrs={'name':'chash', 'type':'hidden'})
		
		else: 
			raise ValueError('Domain "%s" can not yet be handled by Downloader!')
		
		
		########## 		Start the actual Download 			##########
		req = urllib.request.Request(real_stream_link, method='GET')			### Final request: get the source video file
		with urllib.request.urlopen(req) as response:								
			if response.status != 200:
				raise BadLink('Invalid status code for video URL: %d' % (response.status))
			
			self.downloadSize = int(response.getheader('Content-Length'))/1048576.0
			
			print('Video Size: %.1f MB.' % (self.downloadSize))
			self.byteCount = 0														# Bytes downloaded
			block_size = 4*1024													# Block transfer size
		
			try:
				out_stream = open(video_filename, 'wb')							# open our output file stream for writing raw binary
				assert out_stream is not None
			except (OSError, IOError) as err:
				sys.stderr.write('Unable to open for writing: %s' % str(err))
				return False
			title = video_filename[video_filename.rfind('/')+1:]
			self.callbackQ.put((self.parent.newProgressBox, (title, self.downloadSize, self.onProgress)))
			
			########## 	Download the file! 				##########
			while True:															# Download data and write to a local file
				data_block = response.read(block_size)							# Get 'block_size' of data at a time
				assert response.getheader('Content-Type') != 'text/html'		# TODO make sure we get xml, not html ??
	
				if len(data_block) == 0:										# make sure we are still downloading
					break
				
				self.byteCount += len(data_block)									# keep track of our total size
				out_stream.write(data_block)									# write the output data to our local file
				
		seconds = self.elapsedTime % 60
		minutes = (self.elapsedTime/60) % 60
		hours 	= (self.elapsedTime/3600)			
		print('%s download completed! Total time: %02d:%02d:%02d.' % (title, hours, minutes, seconds))
		
		
		with open(RUN_DIR + 'completed.txt','a') as stream:
			stream.write(title + '\n')
		
		self.callbackQ.put(tuple(self.parent.deleteProgressBox, tuple())) 		# Get rid of the progress box now that we're done with it
		
		return True

	def onProgress(self, elapsedTime):
		self.elapsedTime = elapsedTime
		return self.byteCount
	
