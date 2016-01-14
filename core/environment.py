import subprocess

import time
import pymongo
from mongodict import *
from pymongo.errors import ConnectionFailure

from core.objects import *
from core.parsing import *
from core.scheduler import scheduler

config_file = 'config.yaml'


class Environment(object):
	""" Environment object that stores instance data and object storage """

	valid_states = ('loading', 'running', 'closing')
	db_label = 'trackr_db'
	config_file = 'config.yaml'
	objects = (User, AwardedJob, EstimatingJob, Worker)

	def __init__(self):
		self.init_paths()
		self.status = self.valid_states[0]

		self.flask_pid = None  # stores the APC job that starts the Flask server
		self.db_state = None  # stores the status of the MongoDB

		self.users = None
		self.active_users = []

		self.reset_db()

	def init_paths(self):
		""" Sets environment instance for all objects found in Environment.objects.
		Also initializes `env_root` attribute for all objects.
		:return:
		"""
		for obj in self.objects:
			obj.env = self
			obj.env_root = self.paths['env_root']

	@property
	def paths(self):
		_settings = yaml.load(open(config_file))
		return _settings

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

	def reset_db(self):
		_cwd = os.getcwd()

		# TODO: reinitialize logger
		# remove(environment.get_log_file)

		self.start_db()
		init_db(self.db_label)
		self.check_db()

		User.load_users()
		Worker.load_workers()

		os.chdir(_cwd)  # Ensure that directories haven't been changed

		print "Database was successfully reset\n"
		# TODO: log reset

		return True

	def start_db(self):
		""" Attempts to start MongoDB from hardcoded path based on `self.db_state`. Passes db path, and 'quiet' arguments.
		:return:
		"""
		if not self.db_state:
			try:
				pymongo.MongoClient('127.0.0.1', 27017)
				self.db_state = True
				return self.db_state  # daemon already running
			except ConnectionFailure:
				_paths = ('C:\\Program Files\\MongoDB 2.6 Standard\\bin\\mongod',
						  'C:\\Program Files\\MongoDB\\Server\\3.0\\bin\\mongod',
						  'C:\\Program Files\\MongoDB\\Server\\3.2\\bin\\mongod')
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
		else:  # verify `self.db_state`
			try:
				pymongo.MongoClient('127.0.0.1', 27017)  # verify status of start_db
				print "MongoDB already started"
				return self.db_state
			except ConnectionFailure:
				print "Starting MongoDB"
				self.db_state = False
				self.start_db()

	def check_db(self):
		""" Ensures database is updated by comparing hashes of YAML storage objects with values in database.
		YAML storage is re-imported if database is not up to date
		:return: True if operation complete
		"""
		client = pymongo.MongoClient("localhost", 27017)
		_db = client[self.db_label]['environment']
		hashes = _db.yaml_hashes

		stores = [['bid_storage', 'EstimatingJob', 'import_estimating_log'],
				  ['job_storage', 'AwardedJob', 'import_po_log']]  # TODO: implement User Worker db checking
		for _id, obj, update_func in stores:
			_value = hashes.find_one({'_id': _id})

			_path = globals()[obj].storage()  # grab YAML storage path for each object type
			m = hashlib.md5()
			m.update(file(_path).read())
			_hash = m.hexdigest()  # compute md5 digest of _path

			if not _value or not (str(_value['hash']) == _hash):  # execute update_func and schedule database update
				f = globals()[update_func]
				scheduler.add_job(f)
				_value = {'_id': _id, 'hash': _hash, 'date_modified': datetime.now()}
				hashes.update({'_id': _id}, _value, upsert=True)
				print "Updating %s" % _id


def import_po_log(method='iter', src=None):
	"""
	Imports AwardedJob objects based on `method` and `src`
	:param method: Method to import objects. If 'iter', function iterates through project directories and imports YAML,
	 if 'backup', function imports YAML file from `src`.
	 If not 'iter' or 'backup', function defaults to importing PO log worksheet
	:param src: path to object storage file
	:return:
	"""
	_startTime = time.time()  # used for timing function duration
	AwardedJob._dump_lock = True  # set lock on object to restrict yaml overwriting

	if method == 'iter':
		_method = 'file hierarchy'
		_path = os.path.join(AwardedJob.env_root, AwardedJob.default_sub_dir)
		for _store in iter_project_dir(_path, AwardedJob.yaml_filename):
			_store = open(_store)
			obj = yaml.load(_store)
			AwardedJob.db[obj.number] = obj

	elif method == 'backup':
		if os.path.isdir(src):
			_file = src
			_method = 'yaml backup'
			_stream = file(_file, 'r')
			for _dump in yaml.load_all(_stream):
				for num, obj in _dump.items():
					AwardedJob.db[num] = obj
					obj.init_struct()  # insure directory structure is created

				# TODO: sort between completed and active jobs
		else:
			print "Invalid directory '%s'" % src
			return None

	else:  # default to parsing Excel workbook
		_method = 'PO Log'
		if not src:
			src = AwardedJob.get_po_log
		_obj_content = parse_po_log(src)  # creates generator from Excel Workbook

		for _type, _content in _obj_content:
			if _type == 'job':
				_job = AwardedJob(*_content)
			elif _type == 'po':
				_mat_list = MaterialList(_job, **_content['mat_list'])
				_list_quote = MaterialListQuote(_mat_list, **_content['list_quote'])
				_po = PO(_job, _mat_list, quote=_list_quote, **_content['po'])

				_mat_list.sent_out = True
				if _mat_list.age > 5:
					_mat_list.delivered = True

	del AwardedJob._dump_lock
	# TODO: backup db
	_elapsedTime = time.time() - _startTime
	print "Finished importing Jobs and POs from %s. Operation took %s seconds." % (_method, _elapsedTime)


def import_estimating_log(method='iter', src=None):
	"""
	Imports EstimatingJob objects based on `method` and `src`
	:param method: Method to import objects. If 'iter', function iterates through project directories and imports YAML,
	 if 'backup', function imports YAML file from `src`.
	 If not 'iter' or 'backup', function defaults to importing Estimating log worksheet
	:param src: path to object storage file
	:return:
	"""
	_startTime = time.time()  # used for timing function duration
	EstimatingJob._dump_lock = True  # set lock on object to restrict yaml overwriting

	if method == 'iter':
		_method = 'file hierarchy'
		_path = os.path.join(EstimatingJob.env_root, EstimatingJob.default_sub_dir)
		for _store in iter_project_dir(_path, EstimatingJob.yaml_filename):
			_store = open(_store)
			obj = yaml.load(_store)
			if not obj.completed:
				EstimatingJob.db[obj.number] = obj
			else:
				EstimatingJob.completed_db[obj.number] = obj
	elif method == 'backup':
		# TODO: implement import from backup
		if os.path.isdir(src):
			_file = src
			_method = 'yaml storage'
			_stream = file(_file, 'r')
			for _dump in yaml.load_all(_stream):
				for num, obj in _dump.items():
					if not obj.completed:
						EstimatingJob.db[num] = obj
					else:
						EstimatingJob.completed_db[num] = obj
					obj.init_struct()  # insure directory structure is created
		else:
			print "Invalid directory '%s'" % src
			return None

	else:  # default to parsing Excel workbook
		_method = 'Estimating Log'
		if not src:
			src = EstimatingJob.get_estimating_log()
		_row_content = parse_est_log(src)  # creates generator from Excel Workbook

		for _type, obj in _row_content:
			if _type == 'bid':
				# create top-level bid object
				EstimatingJob(**obj)
			elif _type == 'sub_bid':
				_bid_num = obj[1]
				obj = obj[0]
				_bid = EstimatingJob.find(_bid_num)

				_bid.add_sub(add_to_log=False, **obj)

	del EstimatingJob._dump_lock
	# TODO: backup db
	_elapsedTime = time.time() - _startTime
	print "Finished EstimatingJob import from %s. Operation took %s seconds." % (_method, _elapsedTime)


def iter_project_dir(path, filename):
	""" A generator function that iterates through the directory `path` and yields paths that contain `filename`
	:param path: folder path to iterate through
	:param filename: search query to look for in directories
	:return: yields folder paths that contain a file `filename`
	"""
	if os.path.isdir(path):
		_dirs = os.listdir(path)  # get all folders in subdirectory
		for _folder in _dirs:
			try:
				_folder = os.path.join(path, _folder)
				_dump = os.listdir(_folder)
				if filename in _dump:
					_path = os.path.join(_folder, filename)
					print "Found '%s'" % _path
					yield _path  # return project path
			except OSError:  # `_folder` is not a directory
				continue


def backup_globals():
	_globals = (AwardedJob, EstimatingJob)  # backup both global db's
	for obj in _globals:
		_backup = obj.storage()
		if os.path.isfile(_backup):
			# TODO: call Environment method to get backup directory
			_name = getattr(obj, 'yaml_filename')  # create descriptive filename
			_name = parse('{}.yaml', _name)[0]
			_name = '_'.join([_name, datetime.now().strftime('%m-%d-%Y_%H%M')]) + '.yaml'
			_path = os.path.join(env.paths['envroot'], 'backups', _name)  # backup path directory
			shutil.copyfile(_backup, _path)
			# log backup
			pass
		else:
			print "%s doesn't exist" % _backup


def init_db(db):
	print "Connecting objects to DB\n"
	# TODO: log connection

	try:
		# Worker/Job DBs
		Worker.db = MongoDict(database=db, collection='workers')
		AwardedJob.db = MongoDict(database=db, collection='jobs')
		AwardedJob.completed_db = MongoDict(database=db, collection='completed_jobs')

		# Material Cycle DB
		Delivery.db = MongoDict(database=db, collection='deliveries')

		# _Todo DBs
		Todo.db = MongoDict(database=db, collection='todos')
		Todo.completed_db = MongoDict(database=db, collection='completed_todos')

		# Inventory DBs
		InventoryItem.db = MongoDict(database=db, collection='inventory_items')
		InventoryOrder.db = MongoDict(database=db, collection='inventory_orders')

		# Timesheet DB
		Timesheet.db = MongoDict(database=db, collection='timesheets')

		# Estimating DBs
		EstimatingJob.db = MongoDict(database=db, collection='estimating_jobs')
		EstimatingJob.completed_db = MongoDict(database=db, collection='completed_bids')
		EstimatingQuote.db = MongoDict(database=db, collection='estimating_quotes')

		# User Database
		User.db = MongoDict(database=db, collection='users')

	except:
		print "Cannot connect to MongoDB Database... Retaining storage cannot be implemented"
		disconnect_db()

	return True


def disconnect_db():
	""" Sets all class databases to blank dictionaries """
	# Worker/Job DBs
	Worker.db = {}
	AwardedJob.db = {}
	AwardedJob.completed_db = {}

	# Material Cycle DBs
	MaterialList.db = {}
	Delivery.db = {}

	# _Todo DBs
	Todo.db = {}
	Todo.completed_db = {}

	# Inventory DBs
	InventoryItem.db = {}
	InventoryOrder.db = {}

	# Timesheet DB
	Timesheet.db = {}

	# Estimating DBs
	EstimatingJob.completed_db = {}
	EstimatingJob.db = {}
	EstimatingQuote.db = {}

	# User Database
	User.db = {}


env = Environment()
Environment.instance = env
