import os

import pymongo
from mongodict import *

import core


def init_db(db='trackr_db'):
	try:
		core.Worker.db = MongoDict(database=db, collection='workers')
		core.Job.db = MongoDict(database=db, collection='jobs')
		core.MaterialList.db = MongoDict(database=db, collection='materials')
		core.Delivery.db = MongoDict(database=db, collection='deliveries')
		core.Todo.db = MongoDict(database=db, collection='todos')
		core.Todo.completed_db = MongoDict(database=db, collection='completed_todos')
		core.InventoryItem.db = MongoDict(database=db, collection='inventory_items')
		core.InventoryOrder.db = MongoDict(database=db, collection='inventory_orders')
	except:
		print "Cannot connect to MongoDB Database... Job storage will not be implemented"
		core.Worker.db = {}
		core.Job.db = {}
		core.MaterialList.db = {}
		core.Delivery.db = {}
		core.Todo.db = {}
		core.Todo.completed_db = {}
		core.InventoryItem.db = {}
		core.InventoryOrder.db = {}
	return True


def clear_db(db='trackr_db'):
	client = pymongo.MongoClient("localhost", 27017)
	client.drop_database(str(db))
	return True


def reset_db(db='trackr_db', log='betterPOlog.xlsx'):
	_cwd = os.getcwd()
	os.chdir('//SERVER/Documents/Esposito')

	clear_db()
	init_db()
	core.parse_PO_log(log, create=True)

	os.chdir(_cwd)


init_db()

if __name__ == "__main__":
	core.frontend.page.app.run(debug=True)