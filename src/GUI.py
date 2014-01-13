from tkinter import *
#from tkinter import Frame, Label, Button, TOP, YES, BOTH, S, DISABLED, NORMAL, END
from tkinter.scrolledtext import ScrolledText
from queue import Queue
import queue
#imports from this project
import GUITools
if __name__ != '__main__':
	from DownloadUtilities import DownloadMaster

#testing imports
import threading

import sys

class GUI(GUITools.MainWindow):
	ITEMS_PER_WAKE = 10
	WAKE_INTERVAL = 100
	def __init__(self, app_name):
		GUITools.MainWindow.__init__(self, app_name)
		self.displayStart()
		
	def displayStart(self):
		self.container = Frame(self)
		self.container.pack(expand=YES, fill=BOTH)
		msg = 'Downloader by Sam Howes\nPress Start to begin downloading!'
		Label(self.container, text=msg).pack(side=TOP, expand=YES, fill=BOTH)	
		Button(self.container, text='Start!', command=self.onStart).pack(side=TOP, expand=YES, anchor=S)
		
	def onStart(self): 
		self.stdout = GUITools.TSafeRedirect()						# Create a buffer to replace stdout
		self.systemStreams = (sys.stdin, sys.stdout, sys.stderr)	# Save the system streams to replace them later
		sys.stdout = self.stdout									# Redirect writes to stdout and stderr
		sys.stderr = self.stdout
		
		newFrame = Frame(self)										# Create a display for the stdout
		self.textDisplay = ScrolledText(newFrame)
		self.textDisplay.config(state=DISABLED)						# make it read only
	
		self.container.pack_forget()								# remove the old window contents
		del self.container											# explicitly delete to destroy the elements
		
		self.mainContainer = newFrame									# Replace the windows content	
		self.progressContainer = Frame(self)
		self.progressContainer.pack(side=BOTTOM, fill=X)
		self.mainContainer.pack(expand=YES, fill=BOTH)					# Pack now to display the frame
		self.textDisplay.pack(expand=YES, fill=BOTH)
		
		self.callbackQ = Queue()									# Kick off the main worker thread to start downloading
		self.mainWorker = DownloadMaster(self, self.callbackQ, name='DownloadMaster')		
		#self.mainWorker = DryRun(self, self.callbackQ, name='DryRun')		
		self.mainWorker.start()
		
		self.after(self.WAKE_INTERVAL, self.onWake)					# Set the timer to refresh the GUI
		
	def newProgressBox(self, title, totalBytes, progressFunc):
		self.progressBox = GUITools.ProgressBox(self.progressContainer, title, totalBytes, progressFunc)
		self.progressBox.pack(side=BOTTOM, fill=X)	
	
	def deleteProgressBox(self):
		self.progressBox.cancelUpdate()
		self.progressBox.pack_forget()
		del self.progressBox
			
	def onWake(self):
		if not self.stdout.isEmpty():
			self.textDisplay.config(state=NORMAL)
			self.textDisplay.insert(END, self.stdout.clear())
			self.textDisplay.see(END)		
			self.textDisplay.config(state=DISABLED)
			self.textDisplay.update()
		
		for ii in range(self.ITEMS_PER_WAKE):
			try:
				callback, args = self.callbackQ.get(block=False)
			except queue.Empty:
				break
			else:
				callback(*args)
						
		self.after(self.WAKE_INTERVAL, self.onWake)

class DryRun(threading.Thread):
	def __init__(self, parent, callbackQ, name=None):
		threading.Thread.__init__(self,name=name)
		self.parent = parent
		self.setDaemon(True)
		self.callbackQ = callbackQ
		
	def run(self):
		title = 'WhiteCollar'
		self.downloadSize = 254.5
		self.callbackQ.put((self.parent.newProgressBox, (title, self.downloadSize, self.onProgress)))
		
	def onProgress(self, eTime):
		self.eTime = eTime
		return 10.1
	
if __name__ == '__main__':
	GUI('Downloader').mainloop()
	