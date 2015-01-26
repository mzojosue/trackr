import core
import shelve

trackr_db = shelve.open('trackr.db' , writeback=True)

_dicts  = ['workers', 'jobs', 'deliveries', 'todos', 'completed']
_ints   = ['job_num']
for i in _dicts:
	if i not in trackr_db:
		trackr_db[i] = {}
for i in _ints:
	if i not in trackr_db:
		trackr_db[i] = 0

core.Worker.workers = trackr_db['workers']
core.Job.jobs = trackr_db['jobs']
core.Job.number = trackr_db['job_num']
core.Delivery.deliveries = trackr_db['deliveries']
core.Todo.todos = trackr_db['todos']
core.Todo.completed = trackr_db['completed']


if __name__ == "__main__":
	core.page.app.run(debug=True)