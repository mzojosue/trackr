import yaml

config_file = 'config.yaml'

def load_config(f):
	try:
		settings = yaml.load(open(config_file))
		print "Successfully loaded '%s'" % config_file
		return f(settings)
	except IOError:
		return False

@load_config
def env_root(settings):
	return str( settings['data_root'] )


def get_po_log():
	# TODO: use yaml configuration file to return PO log path
	return '/home/ubuntu/server/betterPOlog.xls'