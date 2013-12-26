from curses import wrapper
#from curses.textpad import Textbox, rectangle
import curses
import pydevd

NO_CHOICE_YET = -1

class Chooser():
	"""A convenience class to display a number of choices for the user to select"""
	def __init__(self, parent, parentWindow, title, choices, timeout=120):
		"""Have the user select an item from choices
		@return: index into choices of the item that the user chose
		@param parent: the window that will contain this dialog
		@param title: the title of the dialog that the user sees
		@param choices: @type list of strings: the choices to display to the user
		@param timeout: @type integer: the time to display the dialog before automatically returning 
		If the user takes longer than <timeout>, automatically return 0.
		"""
		if type(title) != type(''):
			raise TypeError('Parameter "title" must be of type string not %s' % (type(title)))
		if type(choices) != type(list()):
			raise TypeError('Parameter "choices" must be of type list(), not %s' % (type(choices)))
		for choice in choices:
			if type(choice) != type(''):
				raise TypeError('Item in list "choices" must be of type "str", not: "%s"' % (type(choice)))
		
		self.choices = choices
		self.parent = parent
		self.parent_win = parentWindow
		self.title = title
		
		self.timeout = timeout
		
		(maxLines,maxChars) = self.parent_win.getmaxyx()
		x0 = 4; y0 = 4											# Starting coordinates of the window
		maxLines -= 2*y0; maxChars -= 2*x0						#	 Subtract 2* to make it a uniform sub-rectangle of the window

		self.chooser_win = self.parent_win.derwin(maxLines, maxChars, y0, x0)
		self.chooser_win.clear()								# make sure to hide the content from the main window
		self.chooser_win.box()
		
		x0 = 2; y0 = 1											# The starting location of the text we will display
		maxChars -= 2*x0; maxLines -= 2*y0						# the max text that we can display
		
		self.text_win = self.chooser_win.derwin(maxLines, maxChars, y0, x0)# now make a sub-window to hold the text
		
		self._display_choices(0)								# Select the first choice in the list by default
		self.selected = 0						
		
		self.parent_win.noutrefresh()
		self.chooser_win.noutrefresh()
		self.text_win.noutrefresh()
		curses.doupdate()
	
	NEXT_CHOICE = -1			# A few class constants in c "macro" style for the selectChoice function 
	PREV_CHOICE = -2
	LOWEST_CONSTANT = -2 		# Provide a way to check an input value against these macros
	
	def selectChoice(self, selection):
		"""Select a choice in the chooser_win"""
		maxVal = len(self.choices)-1
		minVal = self.LOWEST_CONSTANT
		if type(selection) != int:
			raise TypeError('Parameter "selection" must be of type "int", not "%s"' % (type(selection))) 
		elif selection > maxVal or selection < minVal:
			raise ValueError('Parameter "selection" of value: %d is not a valid selection in the range (%d,%d).' % (selection, minVal, maxVal))
		
		if selection == self.NEXT_CHOICE and self.selected < maxVal:
			self.selected = self.selected + 1
		elif selection == self.PREV_CHOICE and self.selected > 0:
			self.selected = self.selected -1
		elif selection > 0 and selection <= maxVal:															# We must be told to select a specific index then
			self.selected = selection
		else:
			pass #do nothing if we are at the boundary points
		
		self._display_choices(self.selected)							# Redraw the output window now that we know this is a safe value
		
	def _display_choices(self, selected=0):
		"""Re-draw the chooser with <selected> choice selected in reverse video 
		@param selected: the index into self.choices of the item to be chosen"""
		maxLines, maxChars = self.text_win.getmaxyx()
		displayChars = maxChars
		x0 = 0; y0 = 0
		self.text_win.addnstr(y0,x0, self.title, displayChars); y0 += 2					# add the title at the top, then skip a line
		
		try:
			startInd = 0
			end = len(self.choices)
			while startInd < end:
				for (ii, line) in zip(range(startInd, end), range(y0, maxLines, 1)):			# Display each choice separated by one blank line, this assumes that all of the lines do not currently have content in them
					if ii == selected: 
						self.text_win.addnstr(line, x0, ' - ' + self.choices[ii],	 			# Display the selected item in reverse video
											displayChars, curses.A_REVERSE) 	
					else:
						self.text_win.addnstr(line, x0, ' - ' + self.choices[ii], displayChars)		# Otherwise, add one item per line like normal
					self.text_win.refresh()														# Update the  screen for the user
				if ii == end -1:
					break
				x0 += int(maxChars/2)												# Display the next collumn
				displayChars -= x0
				if x0 > maxChars:
					raise ValueError('Choices exceed window capacity!')				# <-- Here I am deciding to be lazy and only allow a finite number of choices instead of improving the functionality with a scrolling function
				startInd = ii + 1
			
		except curses.error:
			pass			# ignore the end of screen error
		
	def userInput(self, keyPress):
		"""Process a keyPress from the user"""
		if keyPress == 'KEY_DOWN':
			self.selectChoice(self.NEXT_CHOICE)
			return None
		elif keyPress == 'KEY_UP':
			self.selectChoice(self.PREV_CHOICE)
			return None
		elif keyPress == '\n':											# The user pressed the enter key
			return self.selected										# return the user's choice
		else:
			pass
	
	def __del__(self):
		"""Make sure to delete the windows that we have made"""
		self.text_win.clear()
		del self.text_win			# Try to delete the text window first
		self.chooser_win.clear()
		del self.chooser_win				# Try to delete the window
		
		self.parent_win.redrawwin()		# Make sure this window's content doesn't get left behind
		
class Interface:
	"""A class to encapsulate a curses interface"""
	def __init__(self, stdscr):	
		curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) 	# Set the color scheme
		
		self.stdscr 		= stdscr
		self.stdscr.bkgd(' ', curses.color_pair(1))
		size = list(self.stdscr.getmaxyx())
		
		self.container_win 	= self.stdscr.derwin(size[0], size[1], 0, 0)			# Create a containing window that takes up the whole screen
		
		self.input_win 		= curses.newwin(1,0,0,0)					# A hidden window to receive input from the user
		self.input_win.keypad(True)
		
		self.header_win 	= self.container_win.derwin(1, size[1], 0,0)			# Create a title bar at the top of the screen
		size[0] = size[0] - 1
		
		self.footer_win 	= self.container_win.derwin(1, size[1], size[0], 0)		# Create a footer window for updating statuses
		size[0] = size[0] - 1
		
		self.content_win 	= self.container_win.derwin(size[0], size[1], 1,0)		# The main content window to contain the body of the text
		self.content_win.box() 														# Draw a border around the main content
		size[0] = size[0] - 2															# The border takes up 1 line on top and bottom...
		size[1] = size[1] - 4															# 	and 1 character on each side
		self.text_win 		= self.content_win.derwin(size[0], size[1], 1, 2)		# The text window that actually draws the text
		
		
		self.refresh_queue = [self.stdscr, self.container_win, self.header_win, 
							self.footer_win, self.content_win, self.text_win]
		self.refresh()
	
		self.bodyLines = []														# the contents of the screen
		
	def set_title(self, title, refresh=True):
		"""Access function to properly set the title in the header of the interface"""
		self.header_win.clear()								# delete previous content
		self._safe_addstr(self.header_win, title)
		
		if refresh == True:									#TODO: only refresh the window that matters
			self.refresh()									# refresh if we are told so 
	
	def set_footer(self, footer, refresh=True):
		"""Convenience function to clear and set new text in the footer"""
		self.footer_win.clear()								# delete previous content
		self._safe_addstr(self.footer_win, footer)			# insert new content
		if refresh == True:
			#self.refresh()									# refresh if we are told so
			self.footer_win.refresh()	
	
	def set_body(self, body, refresh=True):
		"""Convenience function to clear and set new text in the body"""
		self.text_win.clear()								# delete previous content
		self.bodyLines.clear()								# delete our record of previous content
		self.bodyLines.append(body)
		self._safe_addstr(self.text_win, self.bodyLines[-1])# insert new content
		if refresh == True:
			self.refresh()									# refresh if we are told to do so
	
	def _safe_addstr(self, window, content, attr=None):
		"""Safely add the content string to the window without error"""
		if attr == None:
			attr = curses.color_pair(1)
			
		(maxLines, maxChars) = window.getmaxyx()
		for ii,jj in zip(range(0, len(content), maxChars), range(0, maxLines)):
			try:
				window.addnstr(jj,0, content[ii:ii+maxChars], maxChars)
			except curses.error:							# Curses raises an error when we are at the end of the current window, ignore this 
				pass
	
	def add_body(self, newBody, attr=None, refresh=True):
		"""Function to add a new line into the content body, scrolling if necessary"""
		if type(newBody) != type(''):
			raise TypeError('parameter "newBody" must be of type string, not %s' % (type(newBody)))
		elif len(newBody) == 0:
			raise ValueError('parameter "newBody" must contain a string of length greater than 0')
		
		(maxLines, maxChars) = self.text_win.getmaxyx()		# Get the display dimensions
		
		startIndex = 0
		if newBody[0] == '\r':								# Don't print a blank line if we are told not to do so
			startIndex = 1
		elif len(self.bodyLines) > 0:
			self.bodyLines.append(' '*maxChars)				# add an empty line between the new content and the old for readability
		
		for ii in range(startIndex,len(newBody),maxChars):				
			self.bodyLines.append(newBody[ii:ii+maxChars])	# Wrap the body if necessary
			
			if len(self.bodyLines[-1]) < maxChars:
				self.bodyLines[-1] += ' '*(maxChars - len(self.bodyLines[-1])) # Make sure to fill the whole line with characters
			
		if maxLines > len(self.bodyLines):
			maxLines = len(self.bodyLines)
		self.bodyLines = self.bodyLines[-1*maxLines:]		# Only keep the number of lines that we can display on the screen
		
		for ii in range(len(self.bodyLines)):
			try:
				self.text_win.addnstr(ii,0,self.bodyLines[ii],maxChars)
			except curses.error:							# Curses raises an error when we are at the end of the current window, ignore this
				pass
			
		if refresh == True:
			self.refresh()										#Refresh if we are told to do so
	
	def unexpected_error(self):
		"""Convenience function for displaying an error before quitting."""
		self.text_win.clear()
		self._safe_addstr(self.text_win, "An unexpected error has occurred and we must terminate.\n\nPress any key to terminate.")
		self.refresh()
		
	def refresh(self):
		"""Convenience function to update all of the window objects in the refresh queue"""
		for window in self.refresh_queue:	# Make sure to go through in sequential order, as the windows
			window.noutrefresh()			#	in the queue should have been put in bottom-up order
		curses.doupdate()
	
	def displayChooser(self, title, choices, timeout=120):
		"""Create a 'chooser' dialog for the user to select from some choices"""
		self.chooser = Chooser(self, self.text_win, title, choices, timeout)
		self.user_is_selecting = True											# Make sure to set the internal flag that the chooser is displayed

	def chooser_input(self, keyPress):
		"""Send a keypress from the user to the chooser"""
		try:
			choice = self.chooser.userInput(keyPress)
		except NameError:
			raise NameError('There is no chooser currently displayed to the user')
		if choice != None:
			del self.chooser						# The user has made their choice, now we can delete the chooser
			self.refresh()							# redraw the output to the user without the chooser
			self.user_is_selecting = False			# Make sure to set the internal flag properly
			return choice
		else:
			return None	
		
def main(stdscr):
	interface = Interface(stdscr)
	interface.set_title('This is the object title!', refresh=False)
	interface.set_body('This is object body! Its hot!', refresh=False)
	interface.set_footer('Status bar! WOOO!', refresh=False)
	interface.refresh()
		
	while True:
		inChar = interface.content_win.getch()
		
		if inChar in (ord('q'), ord('Q')):
			break
		elif inChar == ord('r'):
			interface.set_body('NewBody!---', refresh=True)
	
if __name__ == '__main__':
	wrapper(main)
	
