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

@app.errorhandler(404)
def not_implemented(e):
	return "This feature has not been created yet. Go back."