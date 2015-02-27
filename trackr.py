import os
import core
import pymongo
from mongodict import MongoDict


def init_db(db='trackr_db'):
	# TODO:implement job number storage
	core.Worker.db = MongoDict(database=db, collection='workers')
	core.Job.db = MongoDict(database=db, collection='jobs')
	core.MaterialList.db = MongoDict(database=db, collection='materials')
	core.Delivery.db = MongoDict(database=db, collection='deliveries')
	core.Todo.db = MongoDict(database=db, collection='todos')
	core.Todo.completed_db = MongoDict(database=db, collection='completed_todos')
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
	core.page.app.run(debug=True)