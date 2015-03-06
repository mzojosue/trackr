from config import *

@app.route('/j/')
def all_jobs():
	"""
	Displays links to all current and past jobs
	:return:
	"""
	return render_template('all_jobs.html')


@app.route('/j/<int:job_num>')
def job_overview(job_num=None):
	"""
	Renders overview template which displays active objects and general information such as job address
	:param job_num: specifies job number
	"""
	try:
		_job = Job.find(job_num)
		_todos = _job.tasks.itervalues()
		return render_template('job_overview.html', job=_job, todos=_todos)
	except KeyError:
		return "Error: Job does not exist"


@app.route('/j/<int:job_num>/analytics')
def job_analytics(job_num=None):
	"""
	Displays statistics such as estimated job cost and labor averages.
	:param job_num: specifies job number
	"""
	return NotImplemented

@app.route('/materials/<doc_hash>')
@app.route('/j/<int:job_num>/materials/<doc_hash>')
def job_material_doc(doc_hash, job_num=None):
	if not job_num:
		_doc = MaterialList.db[int(doc_hash)]
		_job = _doc.job
	else:
		_job = Job.find(job_num)
		_doc = _job.materials[int(doc_hash)]
		if type(_doc.doc) is tuple:
			return send_from_directory(*_doc.doc)
		else:
			print "not using _doc.doc"
			return send_from_directory(os.path.join(_job.sub_path, 'Materials'), _doc.doc)


@app.route('/j/<int:job_num>/materials/<int:doc_hash>/del')
def delete_material_doc(doc_hash, job_num=None):
	# TODO:delete document in filesystem
	Job.db[job_num].del_material_list(doc_hash)
	del MaterialList.db[doc_hash]
	return redirect(request.referrer)


@app.route('/quote/<doc_hash>')
@app.route('/j/<int:job_num>/qoutes/<doc_hash>')
def job_quote_doc(doc_hash, job_num=None):
	if not job_num:
		_doc = MaterialList.db[int(doc_hash)]
		_job = _doc.job
	else:
		_job = Job.find(job_num)
		_doc = _job.quotes[int(doc_hash)]
		if type(_doc.doc) is tuple:
			return send_from_directory(*_doc.doc)
		else:
			return send_from_directory(os.path.join(_job.sub_path, 'quotes'), _doc.doc)


@app.route('/j/<int:job_num>/quotes/<int:doc_hash>/del')
def delete_job_quote(job_num, doc_hash):
	# TODO:implement quote deletion functions
	Job.db[job_num].del_quote(doc_hash)
	return redirect(request.referrer)


@app.route('/j/<int:job_num>/quotes/<int:doc_hash>/award')
def job_quote_award_po(doc_hash, job_num=None):
	_job = Job.find(job_num)
	_doc = _job.quotes[doc_hash]
	_doc.mat_list.issue_po(_doc)
	return redirect(request.referrer)



@app.route('/j/<int:job_num>/deliveries')
def job_deliveries(job_num=None):
	"""
	Displays history of all future and past deliveries listed in a table-like format for the specified job.
	:param job_num: specifies job_num
	:return:
	"""
	return NotImplemented


@app.route('/j/<int:job_num>/purchases')
def job_pos(job_num=None):
	try:
		_job = Job.find(int(job_num))
		return render_template('job_purchases.html', job=_job)
	except KeyError:
		return "Error: Job does not exist"


@app.route('/j/<int:job_num>/rentals')
def job_rentals(job_num=None):
	return NotImplemented


@app.route('/j/create', methods=['GET', 'POST'])
def create_job():
	"""
	First renders job creation page, then processes POST request and creates Job object.
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

		_job = Job(job_num=_job_num, name=_name, gc=_gc, gc_contact=_gc_contact, address=_job_address,
					start_date=_start, end_date=_end, desc=_desc,
					contract_amount=_contract_amt, scope=_scope,
					tax_exempt=_tax_exempt, certified_pay=_certified_pay)

		return redirect(url_for('job_overview', job_num=_job.number))
	else:
		return render_template('job_create.html')


## END JOB FUNCTIONS ##
#######################