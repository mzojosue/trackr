from datetime import datetime

today = datetime.today

class Worker(object):
    workers = {}
    #pay rate constants
    A_RATE = 100.84
    A_RATE_journeyman = 97.38
    B_RATE = 51.76
    def __init__(self, name, phone=None, email=None, job=None, rate=None):
        self.name = name
        super(Worker, self).__setattr__('job', job)
        self.prev_jobs = []
        self.phone = str( phone )
        self.email = str( email )
        if rate is 'a':
            self.rate = Worker.A_RATE
        elif rate is 'b':
            self.rate = Worker.B_RATE
        return None
    def __setattr__(self, name, value):
        if name is 'job':
            if self.job not in self.prev_jobs:
                self.prev_jobs.append( self.job )
        return super(Worker, self).__setattr__(name, value)

class Job(object):
    number = 0
    jobs = {}
    def __init__(self, name, number=None, gc=None, foreman=None, sub_path=None, rate='a'):
        self.name = '-'.join([ str(number), str(name) ])
        if not number:
            Job.number += 1
            self.number = Job.number
        else:
            self.number = number
        Job.jobs[ self.number ] = self
        self.alt_name = ""
        self.address  = ""
        self.gc = gc
        self.foreman = foreman
        self.workers = []
        self.material_lists = []
        self._PO = 0        #stores most recent PO suffix number
        self.POs = {}       #stores PO strings as keys
        
        #Job.timesheets.key is datetime.datetime object
        #Job.timesheets.value is [ 'pathname/to/timesheet', hours ]
        self.timesheets = {}

        if rate is 'a':
            self.rate = Job.A_RATE
        elif rate is 'b':
            self.rate = Job.B_RATE
        self.start_date = None
        self.sub_path = sub_path
        return None
    @property
    def next_PO(self):
        _po = self._PO
        self._PO += 1
        return _po
    def init_struct(self):
        """ Initializes project directory hierarchy. """
        ##TODO:initialize documents w/ job information
        return NotImplemented
    @property
    def path(self):
        """ Return absolute sub path using global project path and Job.sub_path """
        return NotImplemented
    @property
    def labor(self):
        """ Calculates labor totals """
        hrs = 0.0
        for i in self.timesheets.itervalues():
            hrs += float( i[1] )  #grab second item in list
        return hrs
    @property
    def cost(self):
        """ Calculates job cost totals """
        amt = 0.0
        for i in self.timesheets.itervalues():
            amt += ( float( i[1] ) * float( self.rate ) )
        for i in self.POs.itervalues():
            amt += i.quote.price
        return amt
class MaterialList(object):
    lists = []
    def __init__(self, job, items, foreman=None, date_sent=today(), comments=""):
        job.material_lists.append(self)
        self.job = job
        self.items = items
        self.foreman = foreman
        self.date_sent = date_sent
        self.comments = comments
        self.quotes = []
        self.todo = True
        self.fulfilled = False
        return None
    def issue_PO(self, quote, fulfills=False):
        return PO( self.job, quote=quote, fulfills=fulfills )
        
class Quotes(object):
    def __init__(self, mat_list, price=0.0, vend=None, doc=''):
        self.mat_list = mat_list
        self.mat_list.quotes.append( self )
        self.price = float( price )
        self.vend = str( vend )
        self.doc = str( doc )   #document target path/name
        return None

class PO(object):
    def __init__(self, job, date_issued=today(), fulfills=False, \
                 mat_list=None, quote=None, desc=None, deliveries=None):
        num = job.nextPO()
        self.name = '-'.join([ str( job.name), str( num ) ])
        self.job = job
        self.mat_list = mat_list
        if fulfills:
            self.mat_list.fulfilled = True
        self.quote = quote
        self.job.POs[ self.name ] = self
        self.date_issued = date_issued
        self.deliveries = deliveries  #stores initial delivery date
        self.backorders = None   #stores any backorder delivery dates
        return None

class Vendor(object):
    def __init__(self):
        return NotImplemented

class Delivery(object):
    """ Represents a future delivery.
    :param
        po:     pointer to PO object
    """
    deliveries = []
    def __init__(self, po, items=None, expected=None, destination='shop'):
        Delivery.deliveries.append(self)
        self.delivered = False
        self.po = po
        if items is None:
            self.items = po.items
        else:
            self.items = items
        self.expected = expected
        self.destination = destination
        return None

class Todo(object):
    """ Represents tasks to-do
    :param
        name:   the name of the task
        task:   text description of the task. may include link
        due:    task due date
        notif:  date/time to follow-up
    """
    todos = []
    def __init__(self, name, task="", due=None, notify=None):
        Todo.todos.append(self)
        self.task = task
        self.due = due
        self.notify = notify
        return None