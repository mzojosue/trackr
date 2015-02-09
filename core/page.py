import os
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
app.jinja_env.globals['Job'] = Job
app.jinja_env.globals['Delivery'] = Delivery

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
		_todos = Todo.db['todos'].itervalues()
		_completed = Todo.db['completed'].itervalues()
		_jobs = Job.db['jobs'].itervalues()
		_lists = MaterialList.db['materials'].itervalues()
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
		return render_template('job_overview.html', job=_job)
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
			_file = request.files['file']
			if _file and allowed_file(_file.filename):
				filename = secure_filename(_file.filename)
				_file.save(os.path.join(_job.sub_path), filename)
		return render_template('job_materials.html', job=_job)
	except KeyError:
		return "Error: Job does not exist"


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
	if request.method is 'POST':
		##TODO:correctly implement document upload
		f = request.files['quote']
		upload_file(f)
	else:
		return render_template('delivery.html')


## _Todo functions ##


@app.route('/task/new', methods=['POST'])
def new_todo():
	_title = request.form['title']
	_task = request.form['task']
	if 'job' in request.form:
		_job = request.form['job']
		_job = Job.find(int(_job))

		_title = ' '.join([_title, 'for', _job.name])
		_todo = Todo(_title, task=_task)

		_job.tasks[_todo.hash] = _todo
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
		del Todo.db['todos'][int(t_hash)]
		# TODO:implement task delete function
		return redirect(request.referrer)
	finally:
		# TODO:find exception type to catch error
		# TODO:display error on redirect
		return redirect(request.referrer)
