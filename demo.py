import core

# create 10 dummy todos
for i in xrange(1, 11):
    name = '-'.join([ 'Task', str(i) ])
    core.Todo( name=name )

if __name__ == "__main__":
    core.page.app.run(debug=True)