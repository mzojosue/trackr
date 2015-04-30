from flask import *
from core.objects import *
from werkzeug import secure_filename

# Flask environment
TEMPLATE_FOLDER = "../../templates"
STATIC_FOLDER = '../../static'

# Flask upload environment
UPLOAD_FOLDER = 'C:/Users/campano/Documents/GitHub/trackr/uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'png', 'jpg'}

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
app.secret_key = "!campanohvac_2015"

# Jinja environment globals
app.jinja_env.globals['Todo'] = Todo
app.jinja_env.globals['MaterialList'] = MaterialList
app.jinja_env.globals['Job'] = AwardedJob
app.jinja_env.globals['Delivery'] = Delivery
app.jinja_env.globals['get_job_num'] = get_job_num
app.jinja_env.globals['today'] = today
app.jinja_env.globals['hasattr'] = hasattr

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


def check_login():
	""" Checks login and keeps track of user activity. """
	# TODO:implement a debug mode to bypass login check and return True
	try:
		if session['logged_in'] and session['hash_id']:
			usr = User.find(hash(session['hash_id']))
			return True
		return redirect(url_for('login'))
	except KeyError:
		return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	elif request.method == 'POST':
		uname = request.form['username']
		uname = hash(uname)
		passwd = request.form['password']

		user = User.find(uname)
		try:
			if pass_auth(user, passwd):
				session['hash_id'] = user.hash
				session['logged_in'] = True     # log the user in
				flash('You were logged in')
				return redirect(url_for('home'))
			else:
				return "Bad password supplied"
		except AttributeError:
			return "User does not exist"


@app.route('/logout')
def logout():
	"""Logs the user out"""
	session.pop('logged_in', None)
	session.pop('hash_id', None)
	flash('You were logged out')
	return redirect(url_for('login'))

@app.errorhandler(404)
def not_implemented(e):
	return "This feature has not been created yet. Go back."