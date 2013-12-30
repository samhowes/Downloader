# Imports from this project
from MyThreads import InterfaceThread, DownloaderThread, InfoThread
from DownloadUtilities import DownloadUtilities 
from MyThreads import Output
from CustomUtilities import create_infra
import signal
import time
import queue
import pydevd
####pydevd.settrace(host=None, stdoutToServer=False, stderrToServer=True, port=5678, suspend=False, trace_only_current_thread=False); import threading; threading.settrace(pydevd.GetGlobalDebugger().trace_dispatch)

def main():
	### First set up the working environment ###
	create_infra([])
	
	################## First create all of our queues for communication ############
	mainQ = queue.Queue()									# The queue that will start and join all threads							
	interfaceQ = queue.Queue()								# The queue to push jobs to the User Interface Thread
	recvQ = queue.Queue()									# Queue to receive information from threads
	mainQ.put('Start')										# The interfaceThread will not start until we tell it to. For now, We want it to start imediately
	
	interfaceThread = InterfaceThread(mainQ, interfaceQ, recvQ, name='InterfaceThread')
	interfaceThread.setDaemon(True)
	
	def signal_handler(signal, frame):						# Register a signal handler for Ctrl+C before we start the interface thread
		"""Handler to recieve a Ctrl+C and safely
		Exit by joining all threads that are active
		and preserve the function of the terminal"""
		
		print('You pressed Ctrl+C!')						# otherwise we could exit abruptly and ruin the output console
		if interfaceThread.is_alive():
			interfaceThread.jobQ.put(('Exit', ()))
			interfaceThread.join()
		exit(1)												# Now simply exit now that everything is cleaned up.
	signal.signal(signal.SIGINT, signal_handler)
	
	interfaceThread.start()									# Start the user interface now that we're set up
	
	########## Now gather all the data to prepare for downloading 	##########
	out = Output(interfaceQ)

	out.setBody('Initializing internal data structures...')
	out.updateStatus('Finding files to download...')
		
	utils = DownloadUtilities(out)								# Get our convenience object for running download tasks
	shows = utils.get_watchlist()								# First get all the shows into a data structure for processing
	shows = utils.get_download_links()							# Now match the shows from tv-links to primewire #MULTITHREAD
	download_queue = utils.generateDownloadQueue()				# Create a set of all the episodes we can download
	
	out.addBody('Checking Folders...')
	folders = list()											# Make sure we have our folder heirarchy for each show
	for show in shows.values():
		folders.append(show.getSafeTitle())
	
	create_infra(folders)
	
	#export_watchlist(shows)									# TODO: export the watchlist and data structures for later use/resuming downloads
	
	########## 		Have the user select the download order 		##########
	
	download_order = list(download_queue)						# Convert the set to a list for ordering
	choices = ['']*len(download_queue)
	for ii in range(len(download_order)):						# Get the title of each show to display to the user
		choices[ii] = download_order[ii].title 
	
	out.setBody('Starting Downloads')
	out.updateStatus('Preparing to start downloading...')

	interfaceQ.put(('DisplayChooser', ('Select which show you would like to download first:', choices)))
	choice = recvQ.get()										# Wait for the user to select their choice
	
	if choice != 0:
		temp = download_order[0]   
		download_order[0] = download_order[choice]
		download_order[choice] = temp
	
	
	utils.download_episodes(download_order)						# Do the actual downloading
	
	mainQ.join()
	interfaceThread.join()
		
if __name__ == '__main__':
	main()
	
	
