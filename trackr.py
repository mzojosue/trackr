import core
import shelve

trackr = shelve.open('trackr.db')


def start():
    """ Reads values from db and loads into memory
    :return:
    """
    core.Worker.workers = trackr['workers']
    core.Job.jobs = trackr['jobs']
    core.MaterialList.lists = trackr['lists']
    core.Delivery.deliveries = trackr['deliveries']
    core.Todo.todos = trackr['todos']
    return True


def update():
    """ Updates the db from variables in memory
    :return:
    """
    trackr['workers'] = core.Worker.workers
    trackr['jobs'] = core.Job.jobs
    trackr['lists'] = core.MaterialList.lists
    trackr['deliveries'] = core.Delivery.deliveries
    trackr['todos'] = core.Todo.todos
    return True


def reset():
    return None

if __name__ == "__main__":
    core.page.app.run(debug=True)