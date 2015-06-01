import yaml

config_file = 'config.yaml'

def load_config(f, *args):
	try:
		settings = yaml.load(open(config_file))
		return f(settings, *args)
	except IOError as e:
		print "Cannot find '%s'" % config_file
		return False
	except KeyError as e:
		print "Cannot find %s for '%s' in '%s'" % (e.args[0], e.args[1], config_file)
		return e.args[2]

@load_config
def get_log_file(settings):
	try:
		return str( settings['log_file'] )
	except KeyError:
		raise KeyError('path', 'log file', False)

@load_config
def env_root(settings):
	try:
		return str( settings['data_root'] )
	except KeyError:
		raise KeyError('path', 'root environment', '/no/root')

@load_config
def get_po_log(settings):
	try:
		return str(settings['po_log'])
	except KeyError:
		raise KeyError('path', 'PO log', False)

@load_config
def get_info_log(settings):
	try:
		return str(settings['info_log'])
	except KeyError:
		raise KeyError('path', 'Job Contact Sheet', False)


@load_config
def last_po_log_hash(settings):
	try:
		return str(settings['last_po_log_hash'])
	except KeyError:
		raise KeyError('value', 'the last known PO Log hash', None)


def set_po_log_hash(file_hash, settings=config_file):
	# TODO: test this function!
	with open(settings, 'r') as dump:
		dump = yaml.load(dump)
		dump['last_po_log_hash'] = str(file_hash)
		with open(config_file, 'w') as config:
			yaml.dump(dump, config, default_flow_style=False)