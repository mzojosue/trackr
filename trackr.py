import core
from mongodict import MongoDict
import shelve
import pickle

"""
trackr_db = shelve.open('trackr.db', writeback=True)


# create database keys if not already present
_dicts = ['workers', 'jobs', 'materials', 'deliveries', 'todos', 'completed']
_ints = ['job_num']
for i in _dicts:
	if i not in trackr_db:
		trackr_db[i] = dict()
for i in _ints:
	if i not in trackr_db:
		trackr_db[i] = 0


# set database object
core.Worker.db = trackr_db
core.Job.db = trackr_db
core.MaterialList.db = trackr_db
core.Delivery.db = trackr_db
core.Todo.db = trackr_db"""

# TODO:implement job number storage
core.Worker.db = MongoDict(database='trackr_db', collection='workers')
core.Job.db = MongoDict(database='trackr_db', collection='jobs')
core.MaterialList.db = MongoDict(database='trackr_db', collection='materials')
core.Delivery.db = MongoDict(database='trackr_db', collection='deliveries')
core.Todo.db = MongoDict(database='trackr_db', collection='todos')
core.Todo.completed_db = MongoDict(database='trackr_db', collection='completed_todos')

if __name__ == "__main__":
	core.page.app.run(debug=True)
	"""trackr_db.close()

	print " ** Database saved ** """