from config import *
from core.sorting import *

@app.route('/j/')
def all_jobs():
	"""
	Displays links to all current and past jobs
	:return:
	"""
	return render_template('jobs/all_jobs.html')


@app.route('/j/<int:job_num>')
def job_overview(job_num=None):
	"""
	Renders overview template which displays active objects and general information such as jobs address
	:param job_num: specifies jobs number
	"""
	try:
		_job = AwardedJob.find(job_num)
		_todos = _job.tasks.itervalues()
		return render_template('jobs/job_overview.html', job=_job, todos=_todos)
	except KeyError:
		return "Error: AwardedJob does not exist"


@app.route('/j/<int:job_num>/analytics')
def job_analytics(job_num=None):
	"""
	Displays statistics such as estimated jobs cost and labor averages.
	:param job_num: specifies jobs number
	"""
	return abort(404)


@app.route('/materials/<doc_hash>')
@app.route('/j/<int:job_num>/materials/<doc_hash>')
def job_material_doc(doc_hash, job_num=None):
	if not job_num:
		_doc = MaterialList.db[int(doc_hash)]
		_job = _doc.job
	else:
		_job = AwardedJob.find(job_num)
		_doc = _job.materials[int(doc_hash)]

	if type(_doc.doc) is tuple:
		return send_from_directory(*_doc.doc)


@app.route('/j/<int:job_num>/materials/<int:doc_hash>/del')
def delete_material_doc(doc_hash, job_num=None):
	# TODO:delete document in filesystem
	AwardedJob.db[job_num].del_material_list(doc_hash)
	del MaterialList.db[doc_hash]
	return redirect(request.referrer)


@app.route('/quote/<doc_hash>')
@app.route('/j/<int:job_num>/qoutes/<doc_hash>')
def job_quote_doc(doc_hash, job_num=None):
	if not job_num:
		_doc = MaterialList.db[int(doc_hash)]
		_job = _doc.job
	else:
		_job = AwardedJob.find(job_num)
		_doc = _job.quotes[int(doc_hash)]
		print _doc._doc
		if type(_doc.doc) is tuple:
			return send_from_directory(*_doc.doc)

@app.route('/j/<int:job_num>/quotes/<int:doc_hash>/update', methods=['POST'])
def update_job_quote(job_num, doc_hash):
	""" Updates specified document object based on given POST variables. Meant for changing price of object or adding a document file once quote object has been created.
	:param job_num:
	:param doc_hash:
	:return:
	"""
	return abort(404)



@app.route('/j/<int:job_num>/quotes/<int:doc_hash>/del')
def delete_job_quote(job_num, doc_hash):
	# TODO:implement quote deletion functions
	AwardedJob.db[job_num].del_quote(doc_hash)
	return redirect(request.referrer)


@app.route('/j/<int:job_num>/quotes/<int:doc_hash>/award')
def job_quote_award_po(doc_hash, job_num=None):
	_job = AwardedJob.find(job_num)
	_doc = _job.quotes[doc_hash]
	_doc.mat_list.issue_po(_doc)
	return redirect(request.referrer)


@app.route('/j/<int:job_num>/deliveries')
def job_deliveries(job_num=None):
	"""
	Displays history of all future and past deliveries listed in a table-like format for the specified jobs.
	:param job_num: specifies job_num
	:return:
	"""
	return abort(404)


@app.route('/j/<int:job_num>/purchases')
@app.route('/j/<int:job_num>/purchases/sort/<sort_by>')
def job_pos(job_num=None, sort_by=None):
	try:
		_job = AwardedJob.find(int(job_num))
		_pos = _job.POs.values()
		if sort_by:
			_pos = sort_pos(_pos, sort_by)
		return render_template('jobs/job_purchases.html', job=_job, pos=_pos)
	except KeyError:
		return "Error: AwardedJob does not exist"


@app.route('/j/<int:job_num>/rentals')
def job_rentals(job_num=None):
	return abort(404)


@app.route('/j/create', methods=['GET', 'POST'])
def create_job():
	"""
	First renders jobs creation page, then processes POST request and creates AwardedJob object.
	:return:
	"""
	if request.method == 'POST':

		# TODO:create form field for PO-prefix, foreman, wage rate,

		_name = str(request.form['newJobName'])
		_job_num = int(request.form['jobNumber'])
		_job_type = str(request.form['jobType'])
		_job_address = str(request.form['jobAddress'])
		_contract_amt = float(request.form['contractAmt'])
		try:
			request.form['taxExempt']
			_tax_exempt = True
		except KeyError:
			_tax_exempt = False
		try:
			request.form['certifiedPayroll']
			_certified_pay = True
		except KeyError:
			_certified_pay = False
		_gc = str(request.form['gc'])
		_gc_contact = str(request.form['gcContact'])
		_scope = str(request.form['scopeOfWork'])
		try:
			_start = datetime(*request.form['contractDate'])
		except TypeError:
			_start = None
		try:
			_end = datetime(*request.form['completionDate'])
		except TypeError:
			_end = None
		_desc = str(request.form['jobDesc'])
		# TODO:figure out how to accept then save uploaded file

		_job = AwardedJob(job_num=_job_num, name=_name, gc=_gc, gc_contact=_gc_contact, address=_job_address,
					start_date=_start, end_date=_end, desc=_desc,
					contract_amount=_contract_amt, scope=_scope,
					tax_exempt=_tax_exempt, certified_pay=_certified_pay)

		return redirect(url_for('job_overview', job_num=_job.number))
	else:
		return render_template('jobs/job_create.html')


@app.route('/j/<int:job_num>/update', methods=['POST'])
def update_job_info(job_num):
	_job = AwardedJob.db[job_num]
	_job.address = str(request.form['jobAddress'])
	_job.desc = str(request.form['jobDesc'])
	_job.po_pre = str(request.form['poPre'])
	return redirect(request.referrer)


## END JOB FUNCTIONS ##
#######################