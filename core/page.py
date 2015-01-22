import os
from werkzeug import secure_filename
from flask import *
from objects import *

# Flask environment
TEMPLATE_FOLDER = 'template/folder'
STATIC_FOLDER = 'static/folder'

# Flask upload environment
UPLOAD_FOLDER = 'uploads/folder'
ALLOWED_EXTENSIONS = set(['pdf', 'xlsx', 'png', 'jpg'])


app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

# app upload config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
def upload_file(file):
    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save( os.path.join( app.config['UPLOAD_FOLDER'], filename) )
            return True
    except: pass
    return False

@app.route('/')
def root():
    return redirect( url_for('home') )

@app.route('/home')
def home():
    jobs = Job.jobs
    lists = MaterialList.lists
    return render_template('home.html', jobs=jobs, lists=lists)

@app.route('/j/<job_name>')
def show_job(job_name=None):
    return render_template( 'job.html', job=job)

@app.route('/j/create', methods=['GET', 'POST'])
def create_job():
    #not implemented yet
    return None

@app.route('/material', methods=['GET', 'POST'])
def material():
    if request.method is 'POST':
        file = request.files['list']
        upload_file( file )
        j = request.form['job']
        j = Job.jobs[j]
        due = request.form['shipping_date']
        ##TODO:turn due into datetime obj
        MaterialList(j, file=file.filename, due=due)
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
        file = request.files['quote']
        upload_file(file)
    else:
        return render_template('delivery.html')
