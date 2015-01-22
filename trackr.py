from core.page import *
import shelve

trackr = shelve.open('trackr')


def start():
    """ Reads values from db and loads into memory
    :return:
    """
    Worker.workers = trackr['workers']
    Job.jobs = trackr['jobs']
    MaterialList.lists = trackr['lists']
    Delivery.deliveries = trackr['deliveries']
    Todo.todos = trackr['todos']
    return True


def update():
    """ Updates the db from variables in memory
    :return:
    """
    trackr['workers'] = Worker.workers
    trackr['jobs'] = Job.jobs
    trackr['lists'] = MaterialList.lists
    trackr['deliveries'] = Delivery.deliveries
    trackr['todos'] = Todo.todos
    return True


def reset():
    return None

if __name__ == "__main__":
    pass