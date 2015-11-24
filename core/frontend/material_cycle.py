from datetime import datetime
from flask import send_from_directory

from config import *



# Material List Pages #

@app.route('/j/<int:job_num>/materials', methods=['POST', 'GET'])
def job_materials(job_num=None):
	"""
	Displays history of all active and fulfilled material listed in a table-like format for the specified jobs.
	:param job_num: specifies jobs number
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	try:
		_job = AwardedJob.find(int(job_num))
		if request.method == 'POST':
			if 'file' in request.files:
				""" This branch of logic is followed if a file is being uploaded """
				print "file"
				_file = request.files['file']
				if _file and allowed_file(_file.filename):
					filename = secure_filename(_file.filename)
					_path = os.path.join(_job.path, 'Materials', filename)
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
				__obj = MaterialList(_job, items=__items, date_due=_date_due, label=_label, user=auth)
			return redirect(url_for('material_list', job_num=job_num, m_hash=__obj.hash))
		return render_template('jobs/job_materials.html', job=_job, usr=auth)
	except KeyError:
		flash('Error! AwardedJob does not exist.', 'danger')
		return redirect(request.referrer)


@app.route('/j/<int:job_num>/material/<int:m_hash>/')
def material_list(job_num, m_hash):
	"""
	Renders material list page
	:param m_hash: hash attribute of material list object to display
	:return: renders material list page
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	try:
		_job = AwardedJob.find(job_num)
		_list = _job.materials[m_hash]
		return render_template('material_list.html', job=_job, mlist=_list, usr=auth)
	except KeyError:
		return "Material List doesn't exist..."


@app.route('/j/<int:job_num>/material/<int:m_hash>/update', methods=['POST'])
def update_material_list(job_num, m_hash):
	"""
	Updates material list using http post methods
	:param m_hash: Material list hash to update
	:return: Redirects to referring page
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_job = AwardedJob.find(job_num)
	_list = _job.materials[m_hash]
	if 'sentOut' in request.form:
		_list.sent_out = True
		_list.update()
		flash('Material list updated', 'warning')
		return redirect(request.referrer)


# Delivery Pages #

@app.route('/deliveries')
def deliveries():
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	return render_template('deliveries.html', usr=auth)

@app.route('/deliveries/json')
def serialized_deliveries():
	"""
	Displays all future and past deliveries in a table-like format.
	:return:
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login

	# Grab 'from' and 'to' GET requests
	#TODO: implement 'from' and 'to' as search queries
	date_scope = [request.args.get('from'), request.args.get('to')]

	result = ['id', 'title', 'url', 'class', 'start', 'end']
	grab = ['hash', 'label', 'hash', 'countdown', 'timestamp', 'timestamp']
	if hasattr(Delivery, 'db'):
		_deliveries = []
		for delivery in Delivery.db.itervalues():
			_deliv = {}
			for i, z in zip(result, grab):
				_deliv[i] = delivery.__getattribute__(z)
			_deliv['url'] = url_for('material_list', job_num=delivery.job.number, m_hash=delivery.mat_list.hash)
			_deliv['class'] = 'event-info'
			#TODO: format start and end values
			_deliveries.append(_deliv)
		_return = {"success": 1, "result": _deliveries}
		return json.dumps(_return)


@app.route('/delivery/schedule', methods=['POST'])
@app.route('/j/<int:job_num>/deliveries/new', methods=['POST'])
def schedule_delivery(job_num=None):
	""" Schedules deliveries for `job_num`. Should only be called by `objects.delivery_widget`.
	:param job_num: specifies jobs number
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if not job_num:
		job_num = int(request.form['jobs-number'])
	_job = AwardedJob.find(job_num)
	_mlist = int(request.form['materialListHash'])
	_mlist =  _job.materials[_mlist]
	_dest = str(request.form['destination'])
	_deliveryDate = datetime.strptime(request.form['deliveryDate'], '%Y-%m-%d')
	__obj = Delivery(mat_list=_mlist, expected=_deliveryDate, destination=_dest)
	flash('Delivery successfully scheduled.', 'success')
	return redirect(request.referrer)


@app.route('/j/<int:job_num>/deliveries/<int:d_hash>/delivered')
def accept_delivery(job_num, d_hash):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_job = AwardedJob.find(job_num)
	_dlvry = _job.deliveries[d_hash]
	if hasattr(_dlvry, 'delivered'):
		_dlvry.delivered = True
	return redirect(request.referrer)


# Quote Pages #
@app.route('/j/<int:job_num>/material/quote', methods=['GET', 'POST'])
@app.route('/j/<int:job_num>/material/<int:m_hash>/quote', methods=['GET', 'POST'])
def quote(job_num, m_hash=None):
	""" Used for uploading and associating a quote with a material list via HTTP POST methods
	:param:
	:return:
	"""
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	if request.method == 'POST':
		##TODO:correctly implement document upload
		_job = AwardedJob.find(job_num)
		if m_hash:
			_list = _job.materials[m_hash]
		else:
			_list = _job.materials[int(request.form['materialList'])]


		__price = request.form['quotePrice']
		__vend = request.form['vendor']

		_quote = request.files['quote']
		if _quote and allowed_file(_quote.filename):
			filename = secure_filename(_quote.filename)
			_path = os.path.join(_list.job.path, 'Quotes', filename)
			_quote.save(_path)

			_obj = MaterialListQuote(mat_list=_list, doc=filename, price=__price, vend=__vend)
		elif __price and __vend:
			_obj = MaterialListQuote(mat_list=_list, price=__price, vend=__vend)
		flash('Quote successfully uploaded.', 'success')
		return redirect(url_for('material_list', job_num=_job.number, m_hash=_list.hash))

@app.route('/j/<int:job_num>/material/<int:m_hash>/quote/<int:q_hash>/update/doc', methods=['POST'])
def add_quote_doc(job_num, m_hash, q_hash):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_job = AwardedJob.find(job_num)
	_mlist = _job.materials[m_hash]
	_quote = _mlist.quotes[q_hash]
	_file = request.files['fileUpload']
	if _file and allowed_file(_file.filename):
		filename = secure_filename(_file.filename)
		_path = os.path.join(_mlist.job.path, 'Quotes', filename)
		_file.save(_path)
		_quote._doc = filename

		_mlist.del_quote(q_hash)
		_mlist.add_quote(_quote)  # update quote hash
		_job.update()
		print "Saved document %s for %s" % (_quote.doc, _quote.job)
	else:
		print "%s not saved" % _file
	return redirect(url_for('material_list', job_num=_job.number, m_hash=_mlist.hash))

@app.route('/j/<int:job_num>/po/<int:po_num>/update/<attr>', methods=['POST'])
def update_po_attr(job_num, po_num, attr):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_job = AwardedJob.db[job_num]
	_po = _job.POs[po_num]
	_value = request.form['updateValue']

	# TODO: parse/type value!!

	_po.__setattr__(attr, _value)
	_job.add_po(_po)
	log.logger.info("Updated %s for %s to %s" % (attr, _po, _value))
	return redirect(request.referrer)


@app.route('/j/<int:job_num>/materials/<int:m_hash>/qoutes/<int:q_hash>')
def material_quote_doc(job_num, m_hash, q_hash):
	auth = check_login()
	if not hasattr(auth, 'passwd'):
		return auth  # redirects to login
	_job = AwardedJob.find(job_num)
	_m_list = _job.materials[m_hash]
	_doc = _m_list.quotes[q_hash]
	if _doc.doc:
		return send_from_directory(*_doc.doc)