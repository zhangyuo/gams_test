'''
@file
This is the 8th model in a series of tutorial examples. Here we show:
  - How to use a queue to solve multiple GamsModelInstances in parallel
  - Note that the CPython implementation will not run threads in parallel
    due to its Global Interpreter Lock. See the transport8a example that
    uses the multiprocessing module for parallel computation.
'''

from __future__ import print_function
from gams import *
import threading
import sys

def get_model_text():
    return '''
  Sets
       i   canning plants   / seattle, san-diego /
       j   markets          / new-york, chicago, topeka / ;

  Parameters

       a(i)  capacity of plant i in cases
         /    seattle     350
              san-diego   600  /

       b(j)  demand at market j in cases
         /    new-york    325
              chicago     300
              topeka      275  / ;

  Table d(i,j)  distance in thousands of miles
                    new-york       chicago      topeka
      seattle          2.5           1.7          1.8
      san-diego        2.5           1.8          1.4  ;

  Scalar f      freight in dollars per case per thousand miles  /90/ ;
  Scalar bmult  demand multiplier /1/;

  Parameter c(i,j)  transport cost in thousands of dollars per case ;

            c(i,j) = f * d(i,j) / 1000 ;

  Variables
       x(i,j)  shipment quantities in cases
       z       total transportation costs in thousands of dollars ;

  Positive Variable x ;

  Equations
       cost        define objective function
       supply(i)   observe supply limit at plant i
       demand(j)   satisfy demand at market j ;

  cost ..        z  =e=  sum((i,j), c(i,j)*x(i,j)) ;

  supply(i) ..   sum(j, x(i,j))  =l=  a(i) ;

  demand(j) ..   sum(i, x(i,j))  =g=  bmult*b(j) ;

  Model transport /all/ ;
'''


def scen_solve(workspace, checkpoint, bmult_list, list_lock, io_lock):
    list_lock.acquire()
    mi = checkpoint.add_modelinstance()
    list_lock.release()
    bmult = mi.sync_db.add_parameter("bmult", 0, "demand multiplier")
    opt = ws.add_options()
    opt.all_model_types = "cplexd"

    # instantiate the GAMSModelInstance and pass a model definition and GAMSModifier to declare bmult mutable
    mi.instantiate("transport use lp min z", GamsModifier(bmult), opt)
    bmult.add_record().value = 1.0

    while True:
        # dynamically get a bmult value from the queue instead of passing it to the different threads at creation time
        list_lock.acquire()
        if 0 == len(bmult_list):
            list_lock.release()
            return
        b = bmult_list.pop()
        list_lock.release()
        bmult.first_record().value = b
        mi.solve()

        # we need to make the ouput a critical section to avoid messed up report informations
        io_lock.acquire()
        print("Scenario bmult=" + str(b) + ":")
        print("  Modelstatus: " + str(mi.model_status))
        print("  Solvestatus: " + str(mi.solver_status))
        print("  Obj: " + str(mi.sync_db.get_variable("z").find_record().level))
        io_lock.release()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ws = GamsWorkspace(system_directory = sys.argv[1])
    else:
        ws = GamsWorkspace()

    cp = ws.add_checkpoint()

    # initialize a GAMSCheckpoint by running a GAMSJob
    t8 = ws.add_job_from_string(get_model_text())
    t8.run(checkpoint=cp)

    bmult_list = [ 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6 ]

    # solve multiple model instances in parallel
    list_lock = threading.Lock()
    io_lock = threading.Lock()

    # start 2 threads
    nr_workers = 2
    threads = {}
    for i in range(nr_workers):
        threads[i] = threading.Thread(target=scen_solve, args=(ws, cp, bmult_list, list_lock, io_lock))
        threads[i].start()
    for i in range(nr_workers):
        threads[i].join()



