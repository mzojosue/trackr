from config import *

@app.route('/dynamic/j/<int:job_num>/materials')
@app.route('/dynamic/j/<int:job_num>/materials/<query>')
def get_mat_lists(job_num, query=None):
	""" Populates <select> object contents for displaying the material lists for `job_num`
	:param job_num: specifies job number to iterate over
	:return:
	"""
	_job = Job.find(job_num)
	_return = []
	if hasattr(_job, 'materials') and _job.materials:
		_return.append('<option>Please select a Material List/Quote</option>')
		for mlist in _job.materials.itervalues():
			_opt = '<option value="%s">%s</option>' % (mlist.hash, mlist)
			if not query:
				_return.append(_opt)
			else:
				_neg = query[0]
				query = query[1:]
				if _neg == '!':
					# negative search query
					_return.append(getattr(mlist, query))
					if hasattr(mlist, query) and not getattr(mlist, query):
						_return.append(_opt)
				else:
					if hasattr(mlist, query) and getattr(mlist, query):
						_return.append(_opt)
		return ''.join(_return)
	elif hasattr(_job, 'materials'):
		_return.append('<option>No material lists available</option>')

@app.route('/dynamic/j/has_open_lists')
def job_with_open_list():
	_return = []
	if hasattr(Job, 'db'):
		_return.append('<option>Please select a job</option>')
		for job in Job.db.itervalues():
			_open = job.has_open_lists
			if _open:
				_opt = '<option value="%s">%s  (%d open lists)</option>' % (job.number, job, _open)
				_return.append(_opt)
		if len(_return) > 1:
			return ''.join(_return)
		else:
			return '<option>No jobs w/ open material lists</option>'