from page import *

@app.route('/task/new', methods=['POST'])
def new_todo():
	_title = request.form['title']
	_task = request.form['task']
	if 'job' in request.form:
		_job = request.form['job']
		_job = AwardedJob.find(int(_job))

		_title = ' '.join([_title, 'for', _job.name])
		_todo = Todo(_title, task=_task, job=_job)
	else:
		Todo(_title, task=_task)
	return redirect(request.referrer)

@app.route('/task/<int:t_hash>/complete')
def todo_complete(t_hash):
	# TODO:implement job_completion for job-linked tasks

	_todo = Todo.find(t_hash)
	if _todo.complete():
		return redirect(request.referrer)
	# create unknown error exception

@app.route('/task/<t_hash>/del')
def del_todo(t_hash):
	try:
		del Todo.db[int(t_hash)]
		# TODO:implement task delete function
		return redirect(request.referrer)
	finally:
		# TODO:find exception type to catch error
		# TODO:display error on redirect
		return redirect(request.referrer)
