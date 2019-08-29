'''
@file
This is the 14th model in a series of tutorial examples. Here we show:
  - How to run multiple GamsJobs in parallel each using different scenario data
'''

from __future__ import print_function
from gams import *
import os
import sys
import threading

class Optimizer(object):
    ws = None
    
    def __init__(self):
        if Optimizer.ws == None:
            if len(sys.argv) > 1:
                Optimizer.ws = GamsWorkspace(system_directory = sys.argv[1])
            else:
                Optimizer.ws = GamsWorkspace()
    
    def solve(self, mult):
        db = Optimizer.ws.add_database()
        f = db.add_parameter("f", 0, "freight in dollars per case per thousand miles")
        f.add_record().value = 90 * mult
        job = Optimizer.ws.add_job_from_string(Optimizer.get_model_text())
        opt = Optimizer.ws.add_options()
        opt.defines["gdxincname"] = db.name
        job.run(opt,databases=db)
        
        return job.out_db.get_variable("z").first_record().level

    @staticmethod
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

  Scalar f  freight in dollars per case per thousand miles;

$if not set gdxincname $abort 'no include file name for data file provided'
$gdxin %gdxincname%
$load f
$gdxin

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

  demand(j) ..   sum(i, x(i,j))  =g=  b(j) ;

  Model transport /all/ ;

  Solve transport using lp minimizing z ;

  Display x.l, x.m ; '''
        

if __name__ == "__main__":
    bmultlist = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]      
    optim = Optimizer()
    lock = threading.Lock()
    
    def run_scenario(optim, bmult):
        obj = optim.solve(bmult)
        lock.acquire()
        print("Scenario bmult=" + str(bmult) + ", Obj:" + str(obj))
        lock.release()
    
    for bmult in bmultlist:
        t = threading.Thread(target=run_scenario, args=(optim, bmult))
        t.start()