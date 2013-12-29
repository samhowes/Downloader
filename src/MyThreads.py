from DownloadUtilities import DownloadUtilities, UrlRedirected
from CustomUtilities import create_infra, Log
from base64 import b64decode
import curses
import html.parser as HTMLParser
import locale	
import os
import queue
import urllib
import re
import sys
import threading
import time

from bs4 import BeautifulSoup		# Third party imports
import Interface					# Imports from this project

import pydevd

FAIL_DIR = "../run/failed/"

class BadQMessage(Exception):
	"""An exception for InterfaceThread to say that it got an invalid task request in its queue."""
	pass

class ExitLoop(Exception):
	"""An exception to break out of the main event loop from a function"""
	@staticmethod
	def raiseme(dummyVariable=None):
		"""A simple function to raise this exception"""
		raise ExitLoop
	
def myRaise(exception, interfaceThread=None):
	if interfaceThread != None:
		if interfaceThread.exited == False:
			interfaceThread.interface.unexpected_error()
			interfaceThread.childQ.put('Exit')
			interfaceThread.childQ.join()				# Wait for the InputThread to tell us we can exit
			interfaceThread.exitCurses()
				
	raise exception

class Output:
	"""A Convenience class to send messages to the thread managing the UI"""
	def __init__(self, messageQ, noLog=None):
		if noLog == None:
			self.log = Log()
		self.messageQ = messageQ
	
	def updateStatus(self, newStatus):
		self.messageQ.put(('SetFooter', (newStatus,)))
		try:
			self.log.debug(newStatus)
		except NameError:
			pass
		
	def updateTitle(self, newTitle):
		self.messageQ.put(('SetTitle', (newTitle,)))
	
	def addBody(self, newBody):
		screen = None; log = None
		output = newBody.split('$!', 1)
		
		if len(output) == 2:
			screen = output[0]
			log = output[1]
		else:
			screen = output[0]
			
		self.messageQ.put(('AddBody', (screen,)))
		try:
			self.log.debug(screen + str(log))
		except NameError:
			pass
		
	def setBody(self, body):
		self.messageQ.put(('SetBody', (body,)))
		try:
			self.log.debug(body)
		except NameError:
			pass
		
class UserInputThread(threading.Thread):
	"""A class to run a curses interface and handle user input"""
	def __init__(self, mainQ, interfaceQ, inputWindow, name=None):
		threading.Thread.__init__(self, name=name)
		self.mainQ = mainQ
		self.interfaceQ = interfaceQ
		self.inputWindow = inputWindow
			
	def run(self):
		while self.mainQ.empty():
			inputChar = self.inputWindow.getkey()
			message = ('KeyPress', (inputChar,) )	# Get a character from the user and pack it for the queue
			self.interfaceQ.put(message)	# send the character on to the content handling thread
		
		self.mainQ.get()								# Empty the queue so we can exit nicely
		self.mainQ.task_done()							# tell the queue we're done
		
class InterfaceThread(threading.Thread):
	"""A class to embody a curses interface in a thread"""
	def __init__(self, mainQ, jobQ, downloaderQ, name=None):
		threading.Thread.__init__(self, name=name)
		self.mainQ = mainQ							# the Queue from the main function
		self.jobQ = jobQ							# The queue that will hold commands from the worker thread
		self.downloaderQ = downloaderQ				# The queue to send user selections to
		self.childQ = queue.Queue()					# A queue that for the child thread that we will launch to receive user input
		self.inputThread = None
		self.exited = False
		self.user_is_selecting = False				# A state variable to indicate if we are waiting for the user to make a selection from a dialog
		self.timeout = -1							# A state variable to indicate a timeout for a jobQ.get(). -1 means no timeout
	
	def run(self):
		message = self.mainQ.get()
		if message != 'Start':
			sys.stderr.write('Error in InterfaceThread: unexpected string from mainQ: "%s"' % (message))
		
		try:											# Make sure to catch any exceptions that get raised...
			self.stdscr = curses.initscr()					# Get the main screen	
			curses.noecho()									# Allow curses to intercept user input without it displaying on the screen
			curses.cbreak()									# Instantly react to any character input by the user
			self.stdscr.keypad(True)						# enable multibyte characters 
			curses.curs_set(False)							# Turn off the cursor
			
			if curses.has_colors():							# start colors 								
				curses.start_color()												
	
			self.interface = Interface.Interface(self.stdscr)			# Create a new User Interface
			
			self.inputThread = UserInputThread(self.childQ, 		# Launch a child thread to handle input from the user
 										self.jobQ, self.interface.input_win, name='InputThread')
			self.inputThread.setDaemon(True)
			self.inputThread.start()
			
			self.interfaceMain()						#### Execute the main function for the interface
						
			self.exitCurses()								# Properly shut down the interface and extract ourselves from the terminal
			
		except:												# Catch all exceptions to maintain the usability of the terminal
			self.exitCurses()								# Properly shut down the interface and extract ourselves from the terminal
			raise 											# Pass the exception up the chain
		
		self.mainQ.task_done()
	
	def exitCurses(self):
		if self.inputThread != None and self.inputThread.is_alive():
			self.interface.set_body('We are now exiting, please press any key to exit...')
			self.inputThread.mainQ.put('Exit')	# Tell the child thread we are exiting
			self.inputThread.mainQ.join()		# interfaceMain should have left the thread waiting for a keypress
			self.inputThread.join()				# wait for the child thread to exit so it's window can be removed
		curses.curs_set(True)			# Turn on the Cursor
		curses.nocbreak()				# Don't break on every character
		self.stdscr.keypad(False)			# Don't allow multibyte characters
		curses.echo()					# Enable instant echoing of characters
		curses.endwin()					# shut down the window
		self.exited = True
		
	def interfaceMain(self):
		"""The main interface function for Curses. Written in a wrapper(stdscr) style."""
		self.interface.set_title('Downloader by Sam Howes', refresh=False)		# Initialize the content, only refresh at the end for efficiency
		self.interface.set_body('Please wait while the program initializes. :)', refresh=False)
		self.interface.set_footer('Initializing Downloader...', refresh=False)
		self.interface.refresh()													# Update the user screen
		
		jobs = {
			'SetTitle': 		self.interface.set_title,
			'SetFooter': 		self.interface.set_footer,
			'SetBody':			self.interface.set_body,
			'AddBody':			self.interface.add_body,
			'KeyPress':			self.keyPress,
			'Exit':				ExitLoop.raiseme,
			'DisplayChooser':	self.displayChooser
			}
		
		while True:								### Enter the main event loop
			task = self.jobQ.get()				# wait for a task from the other threads		
			
			if type(task) != type(tuple()):
				myRaise(TypeError("Message sent into the InterfaceQ must be of type 'tuple', not type '%s'" % (type(task))), self)
			elif type(task[0]) != type('') or type(task[1]) != type(tuple()):
				myRaise(TypeError("Message sent into the InterfaceQ must be a tuple of the format: (string, tuple) not: (%s,%s)" % (type(task[0]),type(task[1]))), self)
								
			try:
				func = jobs[task[0]]			# The task is a tuple: (instruction, (Args))
				func(*task[1])					# Execute the function to update content, and update the interface
					
				self.jobQ.task_done()
			
			except KeyError:					# make sure to properly handle an incorrect instruction
				myRaise(BadQMessage('String: "%s" is not a valid command.' % (task[0])))							
			
			except ExitLoop:					# Our exit function raises this exception to tell us to break the event loop
				self.interface.set_body('We are now exiting, please press any key to exit...')
				self.jobQ.task_done()
				break
	
	def displayChooser(self, title=None, choices=None, timeout=120):
		"""Have the user select an item from choices
		@return: index into choices of the item that the user chose
		@param title: the title of the dialog that the user sees
		@param choices: @type list of strings: the choices to display to the user
		@param timeout: @type integer: the time to display the dialog before automatically returning 
		If the user takes longer than <timeout>, automatically return 0.
		"""
		if type(title) != str:
			raise TypeError('Parameter "title" must be of type string not %s' % (type(title)))
		if type(choices) != type(list()):
			raise TypeError('Parameter "choices" must be of type list(), not %s' % (type(choices)))
		
		self.interface.displayChooser(title, choices)
		
		self.user_is_selecting = True
		self.timeout = timeout
		
	############ Begin Input Response Functions #############

	def select_keyPress(self, inputKey):
		"""Interpret a keypress when the user is selecting a choice from a dialog box."""
		
		#BOOKMARK 

	def newBody(self):
		"""Simple Trial refresh of the body"""
		self.interface.set_body('This is a new sexyyyyy body! :D')
			
	def userExit(self):
		"""The user wants to exit"""
		raise ExitLoop
		
	def keyPress(self, inputKey):
		"""Function to handle a keypress that was sent by the user"""
		switch = {											# My solution for the lack of a Python switch-case statement
				ord('r'): self.newBody,
				ord('q'): self.userExit
				}
		if self.user_is_selecting:							# If we a dialog is being displayed to the user
			choice = self.interface.chooser_input(inputKey)	# send the keyPress onward for interpretation
			if choice != None:
				self.downloaderQ.put(choice)				# If the user made a selection, send it on to the downloaderQ
				
		else:	
			try:											# Otherwise map the keyPress to our normal functionality
				switch[inputKey]()
			except KeyError:
				pass
		
class DownloaderThread(threading.Thread): 	#TODO: change DownloaderThread to be a daemon thread that does _do_download in the background
	def __init__(self, mainQ, messageQ, resultsQ, name=None):
		threading.Thread.__init__(self, name=name)
		self.mainQ = mainQ					# The queue to get jobs from
		self.resultsQ = resultsQ			# The queue to return results when we are done
		
	def run(self): 
		"""Given a link to a video on Putlocker or Sockshare, download the video.
		Return True on success, False otherwise."""
		while True:
			(stream_link, video_filename) = self.mainQ.get()
			if not os.path.exists(video_filename[:video_filename.rfind('/')]):			# Make sure the target directory exists
				sys.stderr.write('Error: path not found: "%s"' % (video_filename[:video_filename.rfind('/')]))
				return False
			
			if os.path.exists(video_filename):											# Make sure the the file hasn't already been downloaded
				self.resultsQ.put((stream_link, 'AlreadyDownloaded'))
				self.mainQ.task_done()
				continue	
			########## 	Navigate to the actual link for the download stream		##########
			
			self.messageQ.add(('Body', 'Downloading video from: "' + stream_link + '"'))
			url_re = 'url=["\'](?P<href>[^"\']*)["\']'									# RegEx to extract an url from "url=''"
			stream_re = "playlist:\s*['\"](?P<href>[^'\"]+)['\"]"						# RegEx to extract the "playlist: ''" entry that indicates the location of the stream
	
			home_url = re.search('http://[^/]+', stream_link).group()					# Get the base url from the link for future requests
			
			try:	
				html = self.grabUrl(stream_link, 200)									###First Request: Grab the landing page for the video
			except UrlRedirected:
				self.messageQ.add(('Body', '\rBad link found, trying the next one'))
				self.messageQ.add(('Error','Bad Sockshare link found: %s' % (stream_link)))
				self.resultsQ.put((stream_link, 'BadLink'))
				self.mainQ.task_done()
				continue
			
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
					self.messageQ.put(('Error', 'Unable to open for writing: %s' % str(err)))
					self.mainQ.task_done()
					continue
				
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
			
			with open('completed.txt','a') as stream:
				stream.write(video_filename + '\n')
			
			return True

class InfoThread(threading.Thread):
	"""Thread class that get's the download links for an episode"""
	def __init__(self, mainQ, messageQ, resultsQ, urlGrabFunc, name=None):
		
		if type(urlGrabFunc) != type(self.run):
			raise TypeError('Third positional argument must be a function type, not: %s' % (type(urlGrabFunc)))
		elif type(mainQ) != type(queue.Queue()) or type(resultsQ) != type(mainQ):
			raise TypeError('First and second positional arguments must be of type "queue", not: %s' % (type(queue.Queue())))
		
		threading.Thread.__init__(self, name=name)
		self.mainQ = mainQ
		self.resultsQ = resultsQ
		self.grabUrl = urlGrabFunc
		self.messageQ = messageQ
		self.encoding = locale.getpreferredencoding()
		
	def run(self):
		"""Process episodes and get a streaming link for each one"""
		domain_source_re = r"document\.writeln\('(putlocker\.com|sockshare\.com|promptfile\.com)'\);"		#RegEx to extract the Host website for a stream on Primewire
		while True:
			try:
				show = self.mainQ.get(False)
				show_html = self.grabUrl(show.href, 200)										# First get the show's homepage
			
			except queue.Empty:
				break 	
			except UrlRedirected:
				self.messageQ.put(('Error', 'Show %s homepage broken on Primewire' % (show.title)))
				continue				
				
			show_soup = BeautifulSoup(show_html)							  				# First extract the link for the episode that we want
			episodes_container = show_soup.find('div', class_='actual_tab', id='first') 	# Get the container of all the episodes
			
			for ind in show.unwatched:													# For each index in the show's queue
				episode = show.episodes[ind]
					
				targetHref = show.relative_link() + '/season-' \
								+ episode.season + '-episode-' + episode.episode			# Construct what we know the Href will be HARDCODING
				
				anchor = episodes_container.find('a', href=targetHref) 						# Get the specific episode that we want
				if anchor == None:
					self.messageQ.put(('Error', 'Link "%s" not found on Primewire!' % (targetHref)))
					continue
				
				episode.name = anchor.text.split(' - ')[-1].strip()							# Record the name: the text was 'Episode x	 - <name>\n' so we extract <name> and strip trailing whitespace
				episode.href = show.base_url + anchor['href']								# Record the streaming page found
					
				self.messageQ.put(('Body', '\rFinding links for: "%s": "%s"$!, at "%s"' % 
								(show.title, episode.name, episode.href)))
				
				assert episode.href != show.base_url
				
				########## 	Extract the external streaming link			##########
				html =  self.grabUrl(episode.href, 200)										# Get the episode streams page
				soup = BeautifulSoup(html)
				version_div = soup.find('div', class_='actual_tab', id='first')				# Get the div that contains all the streaming versions
				best_links = version_div.find_all('span', class_='version_host',			# Find all the spans that contain our valid host names
												  text=re.compile(domain_source_re))
				
				for ii in range(len(best_links)):											# Now grab the streaming link from the Host name container
					# The link's span is in the table that is a grandparent of this span.
					link = best_links[ii].parent.parent.find('span', class_='movie_version_link').a['href']
					
					link = re.search('url=(?P<base64>[^&]+)&', link).group('base64')		# The actual link is encoded to base64 for a .php submission
					best_links[ii] = b64decode(link).decode(self.encoding, 'ignore')		# We will save the direct link instead
					
				if len(best_links) == 0:													# If there are no links, record our failure for post processing
					outfilename = FAIL_DIR + show.title + '--' + \
									episode.getSafeName() + '.html'							# TODO: figure out how to write multi-line strings
					self.messageQ.put(('Body','%s: %s does not have any usable links links.' % 
					 					(show.title, episode.name)))
					self.messageQ.put(('Error','%s: %s does not have any usable links.' % 
					 					(show.title, episode.name)))
					with open(outfilename, 'w') as out:										# Write the output to the file
						out.write(html)
				else:
					episode.download_links = best_links											# If we have links, store them for downloading
					show.to_download.append(ind)												# Record that this episode can be downloaded
			
			if len(show.to_download) == 0:
				show = None
			self.resultsQ.put(show)															# Communicate back to the parent thread
			self.mainQ.task_done()
	
	