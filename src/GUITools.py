'''
Created on Jan 6, 2014

@author: Samuel Howes
'''

# from tkinter import Tk, Toplevel, Frame, Label, Button
# from tkinter import END, DISABLED, YES, X, BOTH, TOP, BOTTOM, RIGHT, LEFT, N, S, E, W
from tkinter import *
from tkinter.messagebox import askyesno
from tkinter.scrolledtext import ScrolledText
import threading
import time
import sys
from io import StringIO

		
class TSafeRedirect():
	def __init__(self):
		self.mutex = threading.Lock()
		self.buff = ''
		self.sysStreams = (sys.stdin, sys.stdout, sys.stderr)
		self._dirty = False
		
	def write(self, text):
		if not len(text) > 0:
			return 0
		
		with self.mutex:		
			splittext = text.split('$!', 1)
			self.buff += splittext[0]						# Store the text for later retrieval
			
			text = ''.join(splittext)
			self.sysStreams[1].write(text)			# Also print out to the normal Stdout for dev and debugging
			self.sysStreams[1].flush()
			self._dirty = True
		
		return len(text)	
	
	def flush(self):
		pass
			
	def writelines(self, lines):
		map(self.write, lines)
	
	def clear(self):
		with self.mutex:
			tmp = self.buff
			self.buff = ''
			self._dirty = False
		return tmp

	def isEmpty(self):
		return not self._dirty
		
class MainWindow(Tk):
	'''
	The main window of a program
	'''
	def __init__(self, app_name):
		Tk.__init__(self)
		self.protocol('WM_DELETE_WINDOW', self.quit)       # don't close silent
		self.app_name = app_name
		self.title(app_name)
		
	def quit(self):
		if askyesno(self.app_name, 'verify quit program?'):
			self.destroy()
			
class RankItem(Frame):
	def __init__(self, parent, index, item):
		Frame.__init__(self, parent)
		self.pack(side=TOP, fill=X)
		self.rankLabel = Label(self, text='  ', anchor=W, bd=1, relief=SUNKEN)
		self.rankLabel.pack(side=LEFT, fill=X)
		self.rank = None
		self.index = index
		self.item = item
		self.bind('<Double-1>', self.onDouble)				# Assign a rank on Double Clicks
		
		self.itemLabel = Label(self, text=item, anchor=W,bd=1, relief=SUNKEN)
		self.itemLabel.bind('<Double-1>', self.onDouble)
		self.itemLabel.pack(side=RIGHT, anchor=W, expand=YES, fill=X)
		
	def setRank(self, rank):
		self.rank = rank
		self.rankLabel.config(text=str(rank+1))			#Display the rank to the user; Add 1, rank is an index
		self.update()
	
	def clearRank(self):
		self.rank = None
		self.rankLabel.config(text='  ')
		self.update()
	
	def onDouble(self, event):
		if self.rank == None:
			self.master.master.setRank(self)
		else:
			self.master.master.clearRank(self)
		
class RankPopup(Toplevel): #TODO: Make this modal
	def __init__(self, title, items, callback):
		Toplevel.__init__(self)
		self.protocol('WM_DELETE_WINDOW', lambda:0)
		self.title(title)
		self.items = items
		self.order = [None]*len(items)
		self.ranks = list(reversed(range(0,10)))
		self.nextRank = self.ranks.pop()	# The rank of the next item to be ranked; ascending order from 0
		self.callback = callback
		
		self.makeWidgets()					# Make the GUI elements
		
	def makeWidgets(self):
		Label(self, text='Double-click a show to assign an order for downloading').pack(side=TOP,fill=X)
		
		Button(self, text='Submit', command=self.onSubmit).pack(
						side=BOTTOM, anchor=E)
		
		self.container = Frame(self)
		self.container.pack(expand=YES, fill=BOTH, padx=5,pady=5)
		
		self.rankFrames = [None]*len(self.items)
		for ii, item in enumerate(self.items):
			self.rankFrames[ii] = RankItem(self.container, ii, item)
		
		self.update()
		
	def onSubmit(self):
		ii = 0								# There could be gaps in the list, fill them
		jj = 0
		while ii < len(self.order) and jj < len(self.order):
			if self.order[jj] == None:		# Advance the "copyfrom" pointer if there is nothing to copy
				jj += 1
			elif jj == ii:					# Advance both pointers because there isn't a gap
				jj += 1
				ii = jj
			else:							# Copy from the valid slot into the empty/invalid slot
				self.order[ii] = self.order[jj]
				ii += 1; jj += 1
				
		for ii in range(ii, len(self.order)):# Fill the rest of the list with None
			self.order[ii] = None
					
		self.callback(self.order)
		self.destroy()
	
	def setRank(self, rankItem):
		self.order[self.nextRank] = rankItem.index
		rankItem.setRank(self.nextRank)
		self.nextRank = self.ranks.pop()
	
	def clearRank(self, rankItem):
		self.ranks.append(self.nextRank)
		self.nextRank = rankItem.rank
		self.order[self.nextRank] = None
		rankItem.clearRank()
	
class ProgressBox(Frame):
	BYTES_STR = '%.1f / %.1f MB => %.1f %%'
	TIME_STR = 'Elapsed: %02d:%02d:%02d'
	def __init__(self, parent, title, totalBytes, progressFunc):
		Frame.__init__(self, parent, relief=RAISED, bd=2)
		self.title = title
		self.totalBytes = float(totalBytes)
		self.progBytes = 0.0
		self.startTime = int(time.time())
		self.progressFunc = progressFunc
		self.makeWidgets()
		
	def makeWidgets(self):
		args = {'bd':2, 'relief':SUNKEN}

		args['text'] 	= self.title
		self.titleLabel	= Label(self, args)
		
		args['text'] 	= self.BYTES_STR % (0.0, self.totalBytes, 0.0)
		self.bytesUpdate= Label(self, args)
		
		args['text'] 	= self.TIME_STR % (0,0,0)
		self.timeCount	= Label(self, args)
			
	def updateProgress(self):
		eTime = time.time() - self.startTime
		seconds = eTime % 60
		minutes = (eTime/60) % 60
		hours = (eTime/3600)
		self.timeCount.config(text=self.TIME_STR % (hours, minutes, seconds))
		self.timeCount.update()
		
		self.progBytes = self.progressFunc(eTime)/1048576.0				# Convert to Megabytes
		percent = (self.progBytes/self.totalBytes)*100.0
		self.bytesUpdate.config(text=self.BYTES_STR % (self.progBytes, self.totalBytes, percent))
		self.bytesUpdate.update()
			
		self.afterID = self.after(1000, self.updateProgress)
	
	def cancelUpdate(self):
		self.after_cancel(self.afterID)	
	
	def pack(self, **args):
		Frame.pack(self, **args)
		self.titleLabel.pack(side=LEFT, fill=X, expand=YES)
		self.bytesUpdate.pack(side=LEFT, fill=X,expand=YES)
		self.timeCount.pack(side=LEFT, fill=X,expand=YES)
		
		self.after(1000, self.updateProgress)
		
if __name__ == '__main__':
	'''root = MainWindow('TestGui')
	msg = 'Downloader by Sam Howes\nPress Start to begin downloading!'
	Label(root, text=msg).pack(side=TOP, expand=YES, fill=BOTH)	
	Button(root, text='Start!', command=lambda: 0).pack(side=TOP, expand=YES, anchor=S)
	root.mainloop()'''
	root = Tk()
	prog = ProgressBox(root, 'test', 100.0)
	prog.pack(side=BOTTOM, expand=YES,fill=X,anchor=S)
	root.mainloop()
	print('yay')
	
	

