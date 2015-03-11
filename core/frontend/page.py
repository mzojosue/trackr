from config import *


@app.route('/upload/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/')
def root():
	return redirect(url_for('home'))


################
## Home pages ##


## _Todo functions ##
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


@app.route('/inventory')
def inventory():
	if hasattr(InventoryItem, 'db'):
		_inventory = InventoryItem.db.itervalues()
		return render_template('inventory.html', inventory=_inventory)

@app.route('/inventory/item', methods=['POST'])
def new_inventory_item():
	_item_id = request.form['itemID']
	_item_label = request.form['itemLabel']
	InventoryItem(_item_id, _item_label)
	return redirect(request.referrer)

@app.route('/inventory/order', methods=['POST'])
def inventory_item_order():
	_item = InventoryItem.find(request.form['itemOrderID'])
	_vend_name = request.form['vendorName']
	_order_price = request.form['orderPrice']
	_order_amount = request.form['orderAmount']
	InventoryOrder(_item, _order_price, _vend_name, _order_amount)
	return redirect(request.referrer)

@app.route('/inventory/<int:item_hash>/del')
def del_inventory_item(item_hash):
	_item = InventoryItem.find(item_hash)
	if _item.orders and hasattr(InventoryOrder, 'db'):
		for i in _item.orders:
			del InventoryOrder.db[i]
	if hasattr(InventoryItem, 'db'):
		del InventoryItem.db[item_hash]
	return redirect(request.referrer)


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


@app.route('/task/<int:t_hash>/complete')
def todo_complete(t_hash):
	# TODO:implement job_completion for job-linked tasks

	_todo = Todo.find(t_hash)
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
