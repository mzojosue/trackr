import os
import yaml

import core

try:
	_config  = 'config.yaml'
	SETTINGS = yaml.load(open(_config))
	core.ENV_ROOT = SETTINGS['data_root']
	print "Loaded settings from '%s'" % (_config)
except IOError:
	core.ENV_ROOT = '//SERVER/Documents/Esposito'
	print "Unable to load settings. Using default root directory location"

JOB_SUB_DIR = os.path.join(core.ENV_ROOT, 'Jobs')
core.AwardedJob.default_sub_dir = JOB_SUB_DIR

core.init_db()

if __name__ == "__main__":
	core.app.run(host='0.0.0.0', port=8080, debug=True)