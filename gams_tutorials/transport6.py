'''
@file
This is the 6th model in a series of tutorial examples. Here we show:
  - How to run multiple GamsJobs in parallel using a GamsCheckpoint
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
  Scalar ms 'model status', ss 'solve status'; '''


def run_scenario(workspace, checkpoint, io_lock, b):
    t6 = workspace.add_job_from_string("bmult=" + str(b) + "; solve transport min z use lp; ms=transport.modelstat; ss=transport.solvestat;", checkpoint)
    t6.run()
    # we need to make the ouput a critical section to avoid messed up report informations
    io_lock.acquire()
    print("Scenario bmult=" + str(b) + ":")
    print("  Modelstatus: " + str(t6.out_db["ms"][()].value))
    print("  Solvestatus: " + str(t6.out_db["ss"][()].value))
    print("  Obj: " + str(t6.out_db["z"][()].level))
    io_lock.release()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ws = GamsWorkspace(system_directory = sys.argv[1])
    else:
        ws = GamsWorkspace()

    cp = ws.add_checkpoint()

    # initialize a GAMSCheckpoint by running a GAMSJob
    t6 = ws.add_job_from_string(get_model_text())
    t6.run(checkpoint=cp)
    bmultlist = [ 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3 ]

    # run multiple parallel jobs using the created GAMSCheckpoint
    io_lock  = threading.Lock()
    threads = {}
    for b in bmultlist:
        threads[b] = threading.Thread(target=run_scenario, args=(ws, cp, io_lock, b))
        threads[b].start()
    for b in bmultlist:
        threads[b].join()


