import pymongo
from mongodict import *

from environment import *
from objects import *
from parsing import *
from log import logger


"""
Database initialization functions should go here
"""


def import_po_log(log=environment.get_po_log):
	_obj_content = parse_po_log(log)  # creates generator from Excel Workbook

	for _row in _obj_content:
		_job = AwardedJob(*_row['job'])
		_mat_list = MaterialList(_job, **_row['mat_list'])
		_list_quote = MaterialListQuote(_mat_list, **_row['list_quote'])
		_po = PO(_job, _mat_list, quote=_list_quote, **_row['po'])

		_mat_list.sent_out = True
		if _mat_list.age > 5:
			_mat_list.delivered = True


def import_estimating_log(log=environment.get_estimating_log):
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


def reset_db(db='trackr_db', log=environment.get_po_log):
	_cwd = os.getcwd()

	print "Beginning to reset database..."

	# TODO: reinitialize logger
	#remove(environment.get_log_file)

	User.load_users()
	if True: #not check_po_log():
		clear_db()
		import_po_log(log)
	else:
		init_db()

	Worker.load_workers()
	os.chdir(_cwd)  # Ensure that directories haven't been changed

	print "Database was successfully reset"
	logger.info("Database was successfully reset")

	return True