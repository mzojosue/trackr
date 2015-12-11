from os import path
import time

from flask import *
from werkzeug.utils import secure_filename

from core.objects import *


# Flask environment
TEMPLATE_FOLDER = "../../templates"
STATIC_FOLDER = '../../static'

# Flask upload environment
UPLOAD_FOLDER = 'C:/Users/campano/Documents/GitHub/trackr/uploads/'
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'png', 'jpg'}

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
# generate random private key for encrypting client-side sessions
app.secret_key = str(hash( ''.join(["!campanohvac_2015", str(now()), os.urandom(4)]) ))

# Jinja environment globals
app.jinja_env.globals['Todo'] = Todo
app.jinja_env.globals['MaterialList'] = MaterialList
app.jinja_env.globals['Job'] = AwardedJob
app.jinja_env.globals['Delivery'] = Delivery
app.jinja_env.globals['get_job_num'] = get_job_num
app.jinja_env.globals['today'] = today
app.jinja_env.globals['hasattr'] = hasattr
app.jinja_env.globals['getmtime'] = path.getmtime
app.jinja_env.globals['time'] = time
app.jinja_env.globals['path'] = os.path


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.template_filter()
def friendly_time(dt, past_="ago", future_="from now", default="just now"):
	"""
	Returns string representing "time since"
	or "time until" e.g.
	3 days ago, 5 hours from now etc.
	"""

	now = datetime.utcnow()
	if now > dt:
		diff = now - dt
		dt_is_past = True
	else:
		diff = dt - now
		dt_is_past = False

	periods = (
		(diff.days / 365, "year", "years"),
		(diff.days / 30, "month", "months"),
		(diff.days / 7, "week", "weeks"),
		(diff.days, "day", "days"),
		(diff.seconds / 3600, "hour", "hours"),
		(diff.seconds / 60, "minute", "minutes"),
		(diff.seconds, "second", "seconds"),
	)

	for period, singular, plural in periods:

		if period:
			return "%d %s %s" % (period,
				singular if period == 1 else plural,
				past_ if dt_is_past else future_)

	return default


def check_login():
	""" Checks login and keeps track of user activity. """
	# TODO:implement a debug mode to bypass login check and return True
	try:
		# TODO: merge with user_permissions
		if session['logged_in'] and session['hash_id']:
			usr = User.find(session['hash_id'])
			return usr
		return redirect(url_for('login'))
	except KeyError:
		return redirect(url_for('login'))

@app.before_request
def user_permissions(*args, **kwargs):
	if request.endpoint != 'login' and 'static' not in request.path:  # restrict redirects on neutral paths
		try:
			# TODO: merge with check_login
			if session['logged_in'] and session['hash_id']:  # ensure logged in
				usr = User.find(session['hash_id'])
				_table = {'/estimating': ('admin', 'estimator'),
						  '/j/': ('admin')}  # dict object containing restricted statements and allowed user types
				for restricted, allowed in _table.iteritems():
					if restricted in request.path and usr.role not in allowed:
						# TODO: log user permission error
						print "%s tried illegally accessing %s" % (usr.name, request.url)
						return redirect(url_for('home'))
		except KeyError:
			return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	elif request.method == 'POST':
		uname = request.form['username']
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