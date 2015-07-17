import pymongo
from mongodict import *

from objects import *
from parsing import *
from log import logger
from os import remove

"""
Database initialization functions should go here
"""


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

	if True:  # check_po_log():
		clear_db()
		import_po_log(True, log)
		Worker.load_workers()
	else:
		init_db()

	os.chdir(_cwd)

	print "Database was successfully reset"
	logger.info("Database was successfully reset")

	return True