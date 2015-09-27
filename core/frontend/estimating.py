from datetime import datetime

from werkzeug import secure_filename

from job import *


##############################
#** ROUTE/RENDER Functions **#

@app.route('/estimating')
def estimating_home():
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	return render_template('estimating/estimating.html', usr=auth)


@app.route('/estimating/bids/current')
def current_bids():
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		_estimates = EstimatingJob.db.values()
		return render_template('estimating/current_bids.html', estimates=_estimates, usr=auth)


@app.route('/estimating/bids/past')
def past_bids():
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login

	if hasattr(EstimatingJob, 'completed_db'):
		_estimates = reversed(EstimatingJob.completed_db.values())
		return render_template('estimating/past_bids.html', estimates=_estimates, usr=auth)


@app.route('/estimating/bid/<int:bid_num>/overview')
def bid_overview(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating/bid_overview.html', bid=_bid, usr=auth)
		except KeyError:
			return "Error: Bid does not exist."


@app.route('/estimating/analytics')
def estimating_analytics():
	return NotImplemented


@app.route('/estimating/bid/<int:bid_num>/dir/<dir>')
def bid_folder(bid_num, dir):
	""" Renders given directory as page. Renders specific pages for 'Drawings', and 'Takeoffs'.
	:param bid_num: bid number to select
	:param dir: directory to iterate over and render
	:return:
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			if dir == 'Drawings':
				return render_template('estimating/bid_drawings.html', bid=_bid, usr=auth)
			else:
				contents = _bid.dump_folder(dir)
				return render_template('estimating/bid_folder.html', bid=_bid, usr=auth, dir=contents)
		except KeyError:
			return "Error: Bid does not exist."


@app.route('/estimating/bid/<int:bid_num>/drawings')
def bid_drawings(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating/bid_drawings.html', bid=_bid, usr=auth)
		except KeyError:
			return "Error: Bid does not exist."


@app.route('/estimating/bid/<int:bid_num>/takeoffs')
def bid_takeoffs(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if hasattr(EstimatingJob, 'db'):
		try:
			_bid = EstimatingJob.find(bid_num)
			return render_template('estimating/bid_takeoffs.html', bid=_bid, usr=auth)
		except KeyError:
			return "Error: Bid does not exist."


######################
#** API Functions **##


@app.route('/estimating/create', methods=['GET', 'POST'])
def create_bid():
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if request.method == 'POST':
		_name = str(request.form['newBidName'])
		_addr = str(request.form['jobAddress'])
		_desc = str(request.form['jobDesc'])
		_gc   = str(request.form['gc'])
		_gcContact = str(request.form['gcContact'])
		try:
			_bid_date = datetime.strptime(request.form['bid_date'], '%Y-%m-%d')
		except:
			_bid_date = None

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

		bid = EstimatingJob(_name, address=_addr, gc=_gc, gc_contact=_gcContact, scope=_scope,
							date_end=_bid_date, desc=_desc)
		return redirect(url_for('bid_overview', bid_num=bid.number))
	else:
		return render_template('estimating/estimating_create.html', usr=auth)


# Bid Completion Functions #

@app.route('/estimating/bid/<int:bid_num>/award/<int:bid_hash>')
def award_bid(bid_num, bid_hash):
	bid = EstimatingJob.find(bid_num)
	job = bid.award_bid(bid_hash)
	return redirect(url_for('job_overview', job_num=job.number))


@app.route('/estimating/bid/<int:bid_num>/cancel')
def cancel_bid(bid_num):
	""" Moves calls EstiamtingJob.complete_bid to separate submitted bids from unsubmitted ones.
	:param bid_num: Desired bid to complete
	:return:
	"""
	_bid = EstimatingJob.find(bid_num)
	_bid.cancel_bid()
	#TODO: somehow show feedback that bid was successfully moved
	return redirect(request.referrer)


@app.route('/estimating/bid/<int:bid_num>/complete')
def complete_bid(bid_num):
	""" Moves calls EstiamtingJob.complete_bid to separate submitted bids from unsubmitted ones.
	:param bid_num: Desired bid to complete
	:return:
	"""
	_bid = EstimatingJob.find(bid_num)
	_bid.complete_bid()
	#TODO: somehow show feedback that bid was successfully moved
	return redirect(request.referrer)


@app.route('/estimating/bid/<int:bid_num>/delete')
def delete_bid(bid_num):
	""" Removes the existence of bid object via passed `bid_num`
	:param bid_num: Bid object to delete
	:return: Redirects page to `request.referrer`
	"""
	auth = check_login()  # verify that user has admin privileges
	if not hasattr(auth, 'passwd'):
		return auth
	_bid = EstimatingJob.find(bid_num)
	if _bid.delete_bid():
		return redirect(url_for('current_bids'))


# Sub Bid Pages #

@app.route('/estimating/bid/<int:bid_num>/sub/create', methods=['POST'])
def create_sub_bid(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	_gc = request.form['gcName']
	_gc_contact = request.form['gcContact']
	try:
		_bidDate = datetime.strptime(request.form['bidDate'], '%Y-%m-%d')
	except ValueError:
		_bidDate = None


	_scope = []
	__scope = ['materialsScope', 'equipmentScope', 'insulationScope', 'balancingScope']
	for i in __scope:
		try:
			if bool(request.form[i]):    # see if form with same id label returns bool
				__s = str(i[0]).upper()
				_scope.append(__s)       # append first letter to scope
		except:
			continue

	_bid.add_sub(datetime.now(), _gc, _bidDate, _gc_contact, _scope)
	return redirect(url_for('bid_overview', bid_num=_bid.number))


@app.route('/estimating/bid/<int:bid_num>/sub/<sub_hash>/delete')
def delete_sub_bid(bid_num, sub_hash):
	return NotImplemented



@app.route('/estimating/bid/<int:bid_num>/sub/<sub_hash>/cancel')
def cancel_sub_bid(bid_num, sub_hash):
	return NotImplemented


@app.route('/estimating/bid/<int:bid_num>/sub/<sub_hash>/award')
def award_sub_bid(bid_num, sub_hash):
		return NotImplemented


@app.route('/estimating/bid/<int:bid_num>/sub/<int:sub_hash>/update', methods=['POST'])
def update_sub_bid(bid_num, sub_hash):
	""" Updates sub bid attributes based on hardcoded attribute list ('gc', 'gc_contact', 'bid_date').
	Parses bid_date as datetime object.
	:param bid_num: Type int representing bid to update
	:param sub_hash: Sub bid to edit
	:return: Redirects to referring page
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	bid = EstimatingJob.find(bid_num)

	values = ('gc', 'gc_contact', 'bid_date')
	for _val in values:
		val = request.form[_val]  # grab value from POST request
		if _val == 'bid_date':
			val = datetime.strptime(val, '%Y-%m-%d')  # parse value as datetime
		else:
			val = str(val)
		bid.bids[sub_hash][_val] = val  # update value. update is not called
	bid.update()  # update object
	return redirect(request.referrer)


# Bid Quote Pages #

@app.route('/estimating/<int:bid_num>/quote/<scope>/<int:q_hash>')
def bid_quote(bid_num, scope, q_hash):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	_quote = _bid.quotes[scope][q_hash]
	return send_from_directory(*_quote.doc)


@app.route('/estimating/<int:bid_num>/quote/upload', methods=['POST'])
def upload_bid_quote(bid_num):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
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
	if not hasattr(auth, 'passwd'):
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
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	return NotImplemented


@app.route('/estimating/bids/json')
def estimating_serialized_overview():
	""" Aggregates current bids based on due_dates via JSON. Used for Bootstrap Calender.
	:return: JSON containing Bid objects
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login

	# Grab 'from' and 'to' GET requests
	#TODO: implement 'from' and 'to' as search queries
	date_scope = [request.args.get('from'), request.args.get('to')]

	result = ['id', 'title', 'url', 'class', 'start', 'end']
	grab = ['hash', 'name', 'number', 'countdown', 'timestamp', 'timestamp']
	if hasattr(EstimatingJob, 'db'):
		_estimates = []
		for estimate in EstimatingJob.db.itervalues():
			_bid = {}
			for i, z in zip(result, grab):
				_bid[i] = estimate.__getattribute__(z)
			_bid['url'] = url_for('bid_overview', bid_num=_bid['url'])
			# TODO: format class value based on completion/countdown status
			_bid['class'] = 'event-success'
			# TODO: format start and end values
			_estimates.append(_bid)
		_return = {"success": 1, "result": _estimates}
		return json.dumps(_return)

@app.route('/estimating/bid/<int:bid_num>/drawings/<dwg_name>')
def bid_drawing_doc(bid_num, dwg_name):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	doc = _bid.drawings[dwg_name]
	if doc:
		return send_from_directory(*os.path.split(doc[0]))


@app.route('/estimating/bid/<int:bid_num>/get/<path:query>')
def bid_get_document(bid_num, query):

	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_bid = EstimatingJob.find(bid_num)
	doc = os.path.join(_bid.path, query)
	print doc
	if os.path.isfile(doc):
		return send_from_directory(*os.path.split(doc))