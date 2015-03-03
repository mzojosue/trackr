from werkzeug import secure_filename
from flask import *
from objects import *

# Flask environment
TEMPLATE_FOLDER = "../templates"
STATIC_FOLDER = '../static'

# Flask upload environment
UPLOAD_FOLDER = 'C:/Users/campano/Documents/GitHub/trackr/uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'png', 'jpg'}

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

# Jinja environment globals
app.jinja_env.globals['Todo'] = Todo
app.jinja_env.globals['MaterialList'] = MaterialList
app.jinja_env.globals['Job'] = Job
app.jinja_env.globals['Delivery'] = Delivery
app.jinja_env.globals['get_job_num'] = get_job_num
app.jinja_env.globals['today'] = today
app.jinja_env.globals['hasattr'] = hasattr

# app upload config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


##################
## Utility urls ##


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	"""
	Accepts a file via POST named 'file' and saves to core.UPLOAD_FOLDER
	:return: redirect to uploaded file if successful. otherwise redirects back to referrer page with error status.
	"""
	if request.method == 'POST':
		# TODO:accept arbitrary http post key name and save destination
		_file = request.files['file']
		if _file and allowed_file(_file.filename):
			filename = secure_filename(_file.filename)
			_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return redirect(url_for('uploaded_file', filename=filename))
		else:
			# TODO:show error status on redirect
			return redirect(request.referrer)


@app.route('/upload/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/')
def root():
	return redirect(url_for('home'))


################
## Home pages ##


@app.route('/home')
def home():
	if hasattr(Todo, 'db') and hasattr(MaterialList, 'db') and hasattr(Job, 'db'):
		_todos = Todo.db.itervalues()
		_completed = Todo.completed_db.itervalues()
		_jobs = Job.db.itervalues()
		_lists = MaterialList.db.itervalues()
		return render_template('dashboard.html', jobs=_jobs, lists=_lists, todos=_todos, completed=_completed)
	else:
		# TODO:display db error on page
		return render_template('dashboard.html')


##############
## Job Pages ##


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
	:param job_num: speicifies job number
	"""
	try:
		_job = Job.find(int(job_num))
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


@app.route('/j/<int:job_num>/materials', methods=['POST', 'GET'])
def job_materials(job_num=None):
	"""
	Displays history of all active and fulfilled material listed in a table-like format for the specified job.
	:param job_num: specifies job number
	"""
	try:
		_job = Job.find(int(job_num))
		if request.method == 'POST':
			if request.files.has_key('file'):
				""" This branch of logic is followed if a file is being uploaded """
				print "file"
				_file = request.files['file']
				if _file and allowed_file(_file.filename):
					filename = secure_filename(_file.filename)
					_path = os.path.join(_job.sub_path, 'materials', filename)
					_file.save(_path)
					_date_sent = datetime.strptime(request.form['dateSubmitted'], '%Y-%m-%d')
					try:
						_date_due  = datetime.strptime(request.form['dateRequired'], '%Y-%m-%d')
					except ValueError:
						print "_date_due value not given. Setting to None."
						_date_due  = None
					_label = request.form['listLabel']
					__obj = MaterialList(_job, doc=filename, date_sent=_date_sent, date_due=_date_due, label=_label)
			elif request.form.has_key('itemCounter'):
				__item_count = int(request.form['itemCounter'])
				__items = []
				_counter = 1
				while _counter <= __item_count:
					_qty = '-'.join([ 'item', str(_counter), 'qty' ])
					_desc = '-'.join([ 'item', str(_counter), 'desc' ])
					_item = [ int(request.form[_qty]), str(request.form[_desc]) ]
					__items.append(_item)
					_counter += 1
				try:
					_date_due  = datetime.strptime(request.form['dateRequired'], '%Y-%m-%d')
				except ValueError:
					print "_date_due value not given. Setting to None."
					_date_due  = None
				_label = request.form['listLabel']
				__obj = MaterialList(_job, items=__items, date_due=_date_due, label=_label)
		return render_template('job_materials.html', job=_job)
	except KeyError:
		return "Error: Job does not exist"

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
		except:
			_tax_exempt = False
		try:
			request.form['certifiedPayroll']
			_certified_pay = True
		except:
			_certified_pay = False
		_gc = str(request.form['gc'])
		_gc_contact = str(request.form['gcContact'])
		_scope = str(request.form['scopeOfWork'])
		try:
			_start = datetime(request.form['contractDate'])
		except TypeError:
			_start = None
		try:
			_end = datetime(request.form['completionDate'])
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


@app.route('/material', methods=['GET', 'POST'])
def material():
	"""
	Displays all active and fulfilled material lists in a table-like format.
	:return:
	"""
	if request.method == 'POST':
		f = request.files['list']
		upload_file(f)
		j = request.form['job']
		j = Job.jobs[j]
		due = request.form['shipping_date']
		##TODO:turn due into datetime obj

		##TODO:pass intended job
		MaterialList(j, doc=f.filename, date_due=due)
		return "successfully uploaded"
	else:
		return render_template('job_materials.html', job=Job.jobs)


@app.route('/material/<int:m_hash>/')
def material_list(m_hash):
	try:
		_list = MaterialList.db[int(m_hash)]
		_job = _list.job
		return render_template('material_list.html', job=_job, mlist=_list)
	except KeyError:
		return "Material List doesn't exist..."


@app.route('/material/<int:m_hash>/update', methods=['POST'])
def update_material_list(m_hash):
	_list = MaterialList.db[int(m_hash)]
	_job = _list.job
	if 'sentOut' in request.form:
		_list.sent_out = True
		return redirect(request.referrer)


@app.route('/deliveries')
def deliveries():
	"""
	Displays all future and past deliveries in a table-like format.
	:return:
	"""
	return NotImplemented


@app.route('/delivery/schedule', methods=['POST'])
@app.route('/j/<int:job_num>/deliveries/new', methods=['POST'])
def schedule_delivery(job_num=None):
	""" Schedules deliveries for `job_num`. Should only be called by `objects.delivery_widget`.
	:param job_num: specifies job number
	"""
	if not job_num:
		job_num = int(request.form['job-number'])
	_job = Job.find(job_num)
	# TODO:show success
	return redirect(request.referrer)


@app.route('/quote', methods=['GET', 'POST'])
def quote():
	""" Used for uploading and associating a quote with a material list
	:param:
	:return:
	"""
	if request.method == 'POST':
		##TODO:correctly implement document upload
		_list = MaterialList.db[int(request.form['materialList'])]
		_quote = request.files['quote']
		if _quote and allowed_file(_quote.filename):
			filename = secure_filename(_quote.filename)
			_path = os.path.join(_list.job.sub_path, 'quotes', filename)
			_quote.save(_path)

			__price = request.form['quotePrice']
			__vend = request.form['vendor']

			_obj = Quotes(mat_list=_list, doc=filename, price=__price, vend=__vend)
		return redirect(request.referrer)


## _Todo functions ##


@app.route('/task/new', methods=['POST'])
def new_todo():
	_title = request.form['title']
	_task = request.form['task']
	if 'job' in request.form:
		_job = request.form['job']
		_job = Job.find(int(_job))

		_title = ' '.join([_title, 'for', _job.name])
		_todo = Todo(_title, task=_task, job=_job)
	else:
		Todo(_title, task=_task)
	return redirect(request.referrer)


@app.route('/task/<t_hash>/complete')
def todo_complete(t_hash):
	# TODO:implement job_completion for job-linked tasks

	_todo = Todo.find(int(t_hash))
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
