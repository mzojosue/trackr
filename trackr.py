import core
from mongodict import MongoDict


# TODO:implement job number storage
core.Worker.db = MongoDict(database='trackr_db', collection='workers')
core.Job.db = MongoDict(database='trackr_db', collection='jobs')
core.MaterialList.db = MongoDict(database='trackr_db', collection='materials')
core.Delivery.db = MongoDict(database='trackr_db', collection='deliveries')
core.Todo.db = MongoDict(database='trackr_db', collection='todos')
core.Todo.completed_db = MongoDict(database='trackr_db', collection='completed_todos')

if __name__ == "__main__":
	core.page.app.run(debug=True)