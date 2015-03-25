import pymongo
from mongodict import *

from objects import *
from parsing import *

"""
Database initialization functions should go here
"""

def init_db(db='trackr_db'):

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

	except:
		print "Cannot connect to MongoDB Database... Retaining storage cannot be implemented"

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

	return True


def clear_db(db='trackr_db'):

	client = pymongo.MongoClient("localhost", 27017)
	client.drop_database(str(db))

	return True


def reset_db(db='trackr_db', log='//SERVER/Documents/Esposito/betterPOlog.xlsx'):
	_cwd = os.getcwd()

	clear_db()
	init_db()
	parse_PO_log(log, create=True)

	os.chdir(_cwd)

	return True