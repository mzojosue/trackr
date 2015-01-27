from trackr import *

# create 10 dummy todos
for i in xrange(1, 11):
	name = '-'.join([ 'Task', str(i) ])
	core.Todo( name=name )

if __name__ == "__main__":
	core.page.app.run(debug=True)
	trackr_db.close()

	print "\n\n ** Database saved ** \n"