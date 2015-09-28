from config import *
from core.sorting import *

@app.route('/j/')
def all_jobs():
	"""
	Displays links to all current and past jobs
	:return:
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	return render_template('jobs/all_jobs.html', usr=auth)


@app.route('/j/<int:job_num>')
def job_overview(job_num):
	"""
	Renders overview template which displays active objects and general information such as jobs address
	:param job_num: specifies jobs number
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	try:
		_job = AwardedJob.find(job_num)
		_todos = _job.tasks.itervalues()
		return render_template('jobs/job_overview.html', job=_job, todos=_todos, usr=auth)
	except KeyError:
		return "Error: AwardedJob does not exist"

@app.route('/j/<int:job_num>/info')
def job_info(job_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth
	try:
		_job = AwardedJob.find(job_num)
		return render_template('jobs/job_info.html', job=_job, usr=auth)
	except KeyError:
		return "Error: AwardedJob does not exist"

@app.route('/j/<int:job_num>/analytics')
def job_analytics(job_num):
	"""
	Displays statistics such as estimated jobs cost and labor averages.
	:param job_num: specifies jobs number
	"""
	return abort(404)


@app.route('/j/<int:job_num>/materials/<doc_hash>')
def job_material_doc(job_num, doc_hash):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_job = AwardedJob.find(job_num)
	_doc = _job.materials[int(doc_hash)]

	if type(_doc.doc) is tuple:
		return send_from_directory(*_doc.doc)


@app.route('/j/<int:job_num>/materials/<int:doc_hash>/del')
def delete_material_doc(doc_hash, job_num=None):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	# TODO:delete document in filesystem
	AwardedJob.db[job_num].del_mat_list(doc_hash)
	del MaterialList.db[doc_hash]
	return redirect(request.referrer)



@app.route('/j/<int:job_num>/quotes/<int:doc_hash>/update', methods=['POST'])
def update_job_quote(job_num, doc_hash):
	""" Updates specified document object based on given POST variables. Meant for changing price of object or adding a document file once quote object has been created.
	:param job_num:
	:param doc_hash:
	:return:
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	return abort(404)



@app.route('/j/<int:job_num>/quotes/<int:doc_hash>/del')
def delete_job_quote(job_num, doc_hash):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	# TODO:implement quote deletion functions
	AwardedJob.db[job_num].del_quote(doc_hash)
	return redirect(request.referrer)


@app.route('/j/<int:job_num>/quotes/<int:doc_hash>/award')
def job_quote_award_po(doc_hash, job_num=None):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_job = AwardedJob.find(job_num)
	_doc = _job.quotes[doc_hash]
	_doc.mat_list.issue_po(_doc, auth)
	return redirect(request.referrer)


@app.route('/j/<int:job_num>/deliveries')
def job_deliveries(job_num=None):
	"""
	Displays history of all future and past deliveries listed in a table-like format for the specified jobs.
	:param job_num: specifies job_num
	:return:
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	return abort(404)


@app.route('/j/<int:job_num>/purchases')
@app.route('/j/<int:job_num>/purchases/sort/<sort_by>')
def job_pos(job_num, sort_by=None):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	try:
		_job = AwardedJob.find(int(job_num))
		_pos = _job.POs.values()
		if sort_by:
			_pos = sort_pos(_pos, sort_by)
		return render_template('jobs/job_purchases.html', job=_job, pos=_pos, usr=auth			)
	except KeyError:
		return "Error: AwardedJob does not exist"


@app.route('/j/<int:job_num>/rentals')
def job_rentals(job_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	return abort(404)


@app.route('/j/create', methods=['GET', 'POST'])
def create_job():
	"""
	First renders jobs creation page, then processes POST request and creates AwardedJob object.
	:return:
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if request.method == 'POST':

		# TODO:create form field for PO-prefix, foreman, wage rate,

		_name = str(request.form['newJobName'])
		_job_num = int(request.form['jobNumber'])
		_job_type = str(request.form['jobType'])
		_job_address = str(request.form['jobAddress'])
		_contract_amt = float(request.form['contractAmt'])
		if 'taxExempt' in request.form:
			_tax_exempt = True
		else:
			_tax_exempt = False
		if 'certifiedPayroll' in request.form:
			_certified_pay = True
		else:
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
		return render_template('jobs/job_create.html', usr=auth)


@app.route('/j/<int:job_num>/update', methods=['POST'])
def update_job_info(job_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_job = AwardedJob.db[job_num]
	_job.address = str(request.form['jobAddress'])
	_job.desc = str(request.form['jobDesc'])
	_job.po_pre = str(request.form['poPre'])
	return redirect(request.referrer)


## END JOB FUNCTIONS ##
#######################