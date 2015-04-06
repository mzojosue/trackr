import yaml

config_file = 'config.yaml'

def load_config(f):
	try:
		settings = yaml.load(open(config_file))
		print "Successfully loaded '%s'" % config_file
		return f(settings)
	except IOError as e:
		print "Cannot find '%s'" % config_file
		return False
	except KeyError as e:
		print "Cannot find %s for '%s' in '%s'" % (e.args[0], e.args[1], config_file)
		return e.args[2]

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