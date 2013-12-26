import os
import sys
import time
from terminalsize import get_terminal_size
from datetime import datetime

class Log():
	def __init__(self):
		self.log_dir = './log'
		self.error_log =  self.log_dir + '/error.txt'
		self.success_log = self.log_dir + '/success.txt'
		self.debug_log = self.log_dir + '/debug.txt'
		self.term_width = get_terminal_size()[0]
		
		if not os.path.exists(self.log_dir):
			os.mkdir(self.log_dir)
		elif os.path.isfile(self.log_dir):
			sys.stderr.write('Failed to create log directory: file with name %s, exists!\n' % (os.path.abspath(self.log_dir)))
			exit(1)
		elif not os.path.isdir(self.log_dir):
			sys.stderr.write('Unknown error creating log directory with name %s\n' % (os.path.abspath(self.log_dir)))
			exit(1)
	
	def status(self, message):
		"""Helper Function to print a status message that should not permanantly be displayed"""
		sys.stdout.write('\r' + message + ' '*(self.term_width-len(message)))
		self.debug(message)

	def error(self, message):
		with open(self.error_log, 'a') as log:
			timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
			log.write(timestamp + '>> ' + message + '\n')
		self.debug(message)
	
	def success(self, message):
		with open(self.success_log, 'a') as log:
			timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
			log.write(timestamp + '>> ' + message + '\n')
		self.debug(message)
	
	def debug(self, message):
		with open(self.debug_log, 'a') as log:
			timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
			log.write(timestamp + '>> ' + message + '\n')


def create_infra(folders):
	parent_folder = 'Downloads'
	failed_folder = 'failed'
	if not os.path.exists(parent_folder):
		os.mkdir(parent_folder)
	
	if not os.path.exists(failed_folder):
		os.mkdir(failed_folder)
	
	for folder in folders:
		if not os.path.exists(parent_folder + '/' + folder):
			os.mkdir(parent_folder + '/' + folder)

