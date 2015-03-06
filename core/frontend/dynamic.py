from config import *

@app.route('/dynamic/j/<int:job_num>/materials')
def get_mat_lists(job_num):
	""" Populates <select> object contents for displaying the material lists for `job_num`
	:param job_num: specifies job number to iterate over
	:return:
	"""
	_job = Job.find(job_num)
	_return = []
	if hasattr(_job, 'materials') and _job.materials:
		_return.append('<option>Please select a Material List/Quote</option>')
		for i in _job.materials.itervalues():
			_opt = '<option value="%s">%s</option>' % (i.hash, i)
			_return.append(_opt)
		return ''.join(_return)