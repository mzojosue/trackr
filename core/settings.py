import yaml

def load_config(config='config.yaml'):
	config = 'config.yaml'
	return yaml.load(open(config))

def get_env_root():
	settings = load_config()
	return str( settings['data_root'] )

def get_po_log():
	# TODO: use yaml configuration file to return PO log path
	return '/home/ubuntu/server/betterPOlog.xlsx'