import pymongo
from mongodict import *

from objects import *
from parsing import *

"""
Database initialization functions should go here
"""

def init_db(db='trackr_db'):
	try:
		Worker.db = MongoDict(database=db, collection='workers')
		AwardedJob.db = MongoDict(database=db, collection='jobs')
		MaterialList.db = MongoDict(database=db, collection='materials')
		Delivery.db = MongoDict(database=db, collection='deliveries')
		Todo.db = MongoDict(database=db, collection='todos')
		Todo.completed_db = MongoDict(database=db, collection='completed_todos')
		InventoryItem.db = MongoDict(database=db, collection='inventory_items')
		InventoryOrder.db = MongoDict(database=db, collection='inventory_orders')
		Timesheet.db = MongoDict(database=db, collection='timesheets')
	except:
		print "Cannot connect to MongoDB Database... AwardedJob storage will not be implemented"
		Worker.db = {}
		AwardedJob.db = {}
		MaterialList.db = {}
		Delivery.db = {}
		Todo.db = {}
		Todo.completed_db = {}
		InventoryItem.db = {}
		InventoryOrder.db = {}
		Timesheet.db = {}
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