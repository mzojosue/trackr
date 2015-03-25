import yaml

def load_config(config='config.yaml'):
	config = 'config.yaml'
	return yaml.load(open(config))

def get_env_root(config='config.yaml'):
	settings = load_config(config)
	return str( settings['data_root'] )