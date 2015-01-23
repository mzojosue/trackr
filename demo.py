import core

for i in xrange(1, 11):
    core.Todo( '-'.join([ 'Task', str(i) ]) )

if __name__ == "__main__":
    core.page.app.run(debug=True)