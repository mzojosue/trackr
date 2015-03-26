from objects import *
from db import *
from parsing import *
from core.frontend import *
from settings import *

global ENV_ROOT

"""
try:
	_config  = 'config.yaml'
	SETTINGS = yaml.load(open(_config))
	ENV_ROOT = SETTINGS['data_root']
	print "Loaded settings from '%s'" % (_config)
except IOError:
	ENV_ROOT = '//SERVER/Documents/Esposito'
	print "Unable to load settings. Using default root directory location"
"""

# ENV_ROOT = '/home/ubuntu/server'

#JOB_SUB_DIR = os.path.join(ENV_ROOT, 'Jobs')
#AwardedJob.default_sub_dir = JOB_SUB_DIR

init_db()
