from config import *
from datetime import datetime
from werkzeug import secure_filename

@app.route('/estimating')
def estimating_home():
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	return render_template('estimating/estimating.html')

@app.route('/estimating/create', methods=['GET', 'POST'])
def estimating_create_bid():
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	if request.method == 'POST':
		_name = str(request.form['newBidName'])
		_addr = str(request.form['jobAddress'])
		_gc   = str(request.form['gc'])
		_gcContact = str(request.form['gcContact'])
		try:
			_bidDate = datetime(*request.form['bidDate'])
		except:
			_bidDate = None

		_scope = []
		__scope = ['materialsScope', 'equipmentScope', 'insulationScope', 'balancingScope']
		for i in __scope:
			try:
				if bool(request.form[i]):
					__s = str(i[0])
					__s = __s.upper()
					_scope.append(__s)
			except:
				continue

		bid = EstimatingJob(_name, address=_addr, gc=_gc, gc_contact=_gcContact, scope=_scope, date_end=_bidDate)
		return redirect(url_for('bid_overview', bid_num=bid.number))
	else:
		return render_template('estimating/estimating_create.html')

@app.route('/estimating/bid/<int:bid_num>/sub/create', methods=['POST'])
def estimating_create_sub_bid(bid_num):
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	_gc = request.form['gcName']
	_gc_contact = request.form['gcContact']
	try:
		_bidDate = datetime(*request.form['bidDate'])
	except:
		_bidDate = None

	_scope = []
	__scope = ['materialsScope', 'equipmentScope', 'insulationScope', 'balancingScope']
	for i in __scope:
		try:
			if bool(request.form[i]):
				__s = str(i[0])
				__s = __s.upper()
				_scope.append(__s)
		except:
			continue

	_bid.add_bid(datetime.now(), _gc, _bidDate, _gc_contact, _scope)
	return redirect(url_for('bid_overview', bid_num=_bid.number))


@app.route('/estimating/<int:bid_num>/quote/<scope>/<int:q_hash>')
def bid_quote(bid_num, scope, q_hash):
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	_quote = _bid.quotes[scope][q_hash]
	return send_from_directory(*_quote.doc)

@app.route('/estimating/<int:bid_num>/quote/upload', methods=['POST'])
def upload_bid_quote(bid_num):
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	_scope = request.form['scope']
	_vend  = request.form['vendor']
	_price = request.form['quotePrice']

	_quote = request.files['quote']

	quote = EstimatingQuote(_bid, _vend, _scope, _price, _quote)

	if _quote and allowed_file(_quote.filename):
		filename = secure_filename(_quote.filename)
		quote._doc = filename
		quote.update()
		_path = os.path.join(*quote.doc)
		_quote.save(_path)
	return redirect(url_for('bid_overview', bid_num=_bid.number))

@app.route('/estimating/<int:bid_num>/quote/<int:q_hash>/update')
def update_bid_quote(bid_num, q_hash):
	""" Updates specified EstimatingQuote object. Meant to change price or add quote after quote has been added to EstimatingJob object.
	:param bid_num: bid number to search for quote in
	:param q_hash: quote to update
	:return: u
	"""
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	return NotImplemented

@app.route('/estimating/<int:bid_num>/quote/<int:q_hash>/del')
def delete_bid_quote(bid_num, q_hash):
	""" Deletes specified EstimatingQuote object from specified EstimatingJob object.
	:param bid_num:
	:param q_hash:
	:return:
	"""
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	return NotImplemented

@app.route('/estimating/analytics')
def estimating_analytics():
	return NotImplemented

@app.route('/estimating/bids/current')
def current_bids():
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		_estimates = EstimatingJob.db.values()
		return render_template('estimating/current_bids.html', estimates=_estimates)

@app.route('/estimating/bids/past')
def past_bids():
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login

	if hasattr(EstimatingJob, 'completed_db'):
		_estimates = EstimatingJob.completed_db.values()
		return render_template('estimating/past_bids.html', estimates=_estimates)

@app.route('/estimating/bid/<int:bid_num>/overview')
def bid_overview(bid_num):
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating/estimating_bid.html', bid=_bid)
		except KeyError:
			return "Error: Bid does not exist."

@app.route('/estimating/bid/<int:bid_num>/documents')
def bid_documents(bid_num):
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('bid_documents.html', bid=_bid)
		except KeyError:
			return "Error: Bid does not exist."

@app.route('/estimating/bid/<int:bid_num>/drawings')
def bid_drawings(bid_num):
	auth = check_login()
	if auth is not True:
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('bid_drawings.html', bid=_bid)
		except KeyError:
			return "Error: Bid does not exist."
