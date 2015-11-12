import yaml
import os
import subprocess
import hashlib

from core.objects import *
from core.scheduler import scheduler

import pymongo
from mongodict import *
from pymongo.errors import ConnectionFailure

config_file = 'config.yaml'


def load_config(f, *args):
	try:
		settings = yaml.load(open(config_file))
		return f(settings, *args)
	except IOError as e:
		print "Cannot find '%s'" % config_file
		return False
	except KeyError as e:
		print "Cannot find %s for '%s' in '%s'" % (e.args[0], e.args[1], config_file)
		return e.args[2]


@load_config
def env_root(settings):
	try:
		return str(settings['data_root'])
	except KeyError:
		raise KeyError('path', 'root environment', '/no/root')


@load_config
def get_info_log(settings):
	try:
		return str(settings['info_log'])
	except KeyError:
		raise KeyError('path', 'Job Contact Sheet', False)


@load_config
def get_log_file(settings):
	try:
		_str = str( settings['log_file'] )
		return os.path.join(env_root, _str)
	except KeyError:
		raise KeyError('path', 'log file', False)


@load_config
def get_estimating_log(settings):
	try:
		_str = str(settings['estimating_log'])
		return os.path.join(env_root, _str)
	except KeyError:
		raise KeyError('path', 'Estimating Log', False)


@load_config
def get_po_log(settings):
	try:
		_str = str(settings['po_log'])
		return os.path.join(env_root, _str)
	except KeyError:
		raise KeyError('path', 'PO log', False)


class Environment(object):
	""" Environment object that stores instance data and object storage """

	valid_states = ('loading', 'running', 'closing')
	db_label = 'trackr_db'
	def __init__(self):
		self.paths = yaml.load(open(config_file))   # load config paths from 'config.yaml'
		self.objects = {}       # object storage for instance
		self.status = self.valid_states[0]

		self.flask_pid = None   # stores the APC job that starts the Flask server
		self.db_state = None    # stores the status of the MongoDB

		self.users = None
		self.active_users = []

	def start_ui(self):
		""" Starts UI by starting Flask server and saving PID to `self.flask_pid`
		:return:
		"""
		return NotImplemented

	def stop_ui(self):
		""" Stops UI by stopping `self.flask_pid`
		:return:
		"""
		return NotImplemented

	def start_db(self):
		""" Attempts to start MongoDB from hardcoded path based on `self.db_state`. Passes db path, and 'quiet' arguments.
		:return:
		"""
		if not self.db_state:
			try:
				pymongo.MongoClient()
				self.db_state = True
				return self.db_state  # daemon already running
			except ConnectionFailure:
				_paths = ('C:\\Program Files\\MongoDB 2.6 Standard\\bin\\mongod', 'C:\\Program Files\\MongoDB\\Server\\3.0\\bin\\mongod')
				for path in _paths:
					try:
						subprocess.Popen([path, '--dbpath', 'C:\\data\\db', '--quiet'])
						self.db_state = True
						print "Successfully started MongoDB"
						return self.db_state
					except OSError:
						continue  # continue iterating down possible paths

				print "All attempts to start MongoDB failed."
				self.db_state = False
		else:   # verify `self.db_state`
			try:
				pymongo.MongoClient()   # verify status of start_db
				return self.db_state
			except ConnectionFailure:
				self.db_state = False
				self.start_db()

	def check_db(self):
		""" Ensures database is updated by comparing hashes of YAML storage objects with values in database.
		YAML storage is re-imported if database is not up to date.
		:param db: Mongo database to iterate through
		:return: True if operation complete
		"""
		client = pymongo.MongoClient("localhost", 27017)
		_db = client[self.db_label]['environment']
		hashes = _db.yaml_hashes

		stores = [['bid_storage', 'EstimatingJob', 'import_estimating_log'],
				  ['job_storage', 'AwardedJob', 'import_po_log']]       # TODO: implement User Worker db checking
		for _id, obj, update_func in stores:
			_value = hashes.find_one({'_id': _id})

			_path = globals()[obj].storage      # grab YAML storage path for each object type
			m = hashlib.md5()
			m.update(file(_path).read())
		_hash = m.hexdigest()                   # compute md5 digest of _path

			if not _value or not (str(_value['hash']) == _hash):    # execute update_func and schedule database update
				f = globals()[update_func]
				scheduler.add_job(f)
				_value = {'_id': _id, 'hash': _hash, 'date_modified': datetime.now()}
				hashes.update({'_id': _id}, _value, upsert=True)
				print "Updating %s" % _id

