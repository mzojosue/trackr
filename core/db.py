import pymongo
from mongodict import *

from core.scheduler import scheduler
from environment import *
from objects import *
from parsing import *
from log import logger


"""
Database initialization functions should go here
"""


def import_po_log(log=environment.get_po_log):
	_file = os.path.join(env_root, AwardedJob.default_sub_dir, 'db_storage.yaml')
	if os.path.isfile(_file):  # check to see if YAML global storage was created
		_stream = file(_file, 'r')
		for _dump in yaml.load_all(_stream):
			for num, obj in _dump.items():
				AwardedJob.db[num] = obj
				obj.init_struct()  # insure directory structure is created
				# TODO: sort between completed and active jobs

	else:  # default to parsing Excel workbook
		_obj_content = parse_po_log(log)  # creates generator from Excel Workbook

		AwardedJob._lock = True  # set lock on object to restrict yaml overwriting
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

		del AwardedJob._lock
		AwardedJob.db.values()[0].dump_all()  # create yaml database


def import_estimating_log(log=environment.get_estimating_log):
	EstimatingJob._lock = True  # set lock on object to restrict yaml overwriting

	_file = os.path.join(env_root, EstimatingJob.default_sub_dir, 'db_storage.yaml')
	if os.path.isfile(_file):  # check to see if YAML global storage was created
		_stream = file(_file, 'r')
		for _dump in yaml.load_all(_stream):
			for num, obj in _dump.items():
				if not obj.completed:
					EstimatingJob.db[num] = obj
				else:
					EstimatingJob.completed_db[num] = obj
				obj.init_struct()  # insure directory structure is created

	else:  # default to parsing Excel workbook
		print "Parsing Estimating Log"
		_row_content = parse_est_log(log)  # creates generator from Excel Workbook

		for _type, obj in _row_content:
			if _type == 'bid':
				# create top-level bid object
				EstimatingJob(**obj)
			elif _type == 'sub_bid':
				_bid_num = obj[1]
				obj = obj[0]
				_bid = EstimatingJob.find(_bid_num)

				_bid.add_sub(add_to_log=False, **obj)

	del EstimatingJob._lock
	return EstimatingJob.db.values()[0].dump_all()


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


def init_db(db='trackr_db'):

	print "Initializing Object DBs"
	logger.debug("Initializing Object DBs...")
	try:
		# Worker/Job DBs
		Worker.db = MongoDict(database=db, collection='workers')
		AwardedJob.db = MongoDict(database=db, collection='jobs')
		AwardedJob.completed_db = MongoDict(database=db, collection='completed_jobs')

		# Material Cycle DBs
		MaterialList.db = MongoDict(database=db, collection='materials')
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


def clear_db(db='trackr_db'):

	print "Clearing Database..."
	try:
		client = pymongo.MongoClient("localhost", 27017)
		client.drop_database(str(db))
		logger.debug('Database was cleared')
	except:
		print "Couldn't connect to database"
		logger.debug('Couldnt connect to database')

	set_po_log_hash('')
	init_db(db)

	return True


def reset_db(db='trackr_db'):
	_cwd = os.getcwd()

	# TODO: reinitialize logger
	#remove(environment.get_log_file)

	clear_db()
	User.load_users()
	if True: #not check_po_log():
		#scheduler.add_job(import_estimating_log)
		#scheduler.add_job(import_po_log)
		#scheduler.start()
		import_estimating_log()
		import_po_log()

	Worker.load_workers()
	os.chdir(_cwd)  # Ensure that directories haven't been changed

	print "Database was successfully reset"
	logger.info("Database was successfully reset")

	return True