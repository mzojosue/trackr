import os
from werkzeug import secure_filename
from flask import *
from objects import *

# Flask environment
TEMPLATE_FOLDER = "../templates"
STATIC_FOLDER = '../static'

# Flask upload environment
UPLOAD_FOLDER = 'uploads/folder'
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'png', 'jpg'}

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

# Jinja environment globals
app.jinja_env.globals['Todo'] = Todo

# app upload config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
	return '.' in filename and \
	       filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_file(f):
	try:
		if f and allowed_file(f.filename):
			filename = secure_filename(f.filename)
			f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return True
	finally:
		pass
	return False


@app.route('/')
def root():
	return redirect(url_for('home'))


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


@app.route('/j/')
def all_jobs():
	return render_template('all_jobs.html')


@app.route('/j/<int:job_num>')
def show_job(job_num=None):
	_job = Job.find(job_num)
	return render_template('job.html', job=_job)


@app.route('/j/create', methods=['GET', 'POST'])
def create_job():
	if request.method == 'POST':

		# TODO:create form field for PO-prefix, foreman, wage rate,

		_name = str(request.form['newJobName'])
		_job_num = int(request.form['jobNumber'])
		_job_type = str(request.form['jobType'])
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

		_job = Job(_name, job_num=_job_num, gc=_gc, gc_contact=_gc_contact,
					start_date=_start, end_date=_end,
					contract_amount=_contract_amt, scope=_scope,
					tax_exempt=_tax_exempt, certified_pay=_certified_pay)

		return redirect(url_for('show_job', job_num=_job.number))
	else:
		return render_template('create_job.html')


@app.route('/material', methods=['GET', 'POST'])
def material():
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
		return render_template('material.html', jobs=Job.jobs)


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


@app.route('/task/new', methods=['POST'])
def new_todo():
	_title = request.form['title']
	_task = request.form['task']
	Todo(_title, task=_task)
	return redirect(request.referrer)


@app.route('/task/<t_hash>/complete')
def todo_complete(t_hash):
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
