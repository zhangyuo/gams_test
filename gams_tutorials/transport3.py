'''
@file
This is the 3rd model in a series of tutorial examples. Here we show:
  - How to read data from string and export to GDX
  - How to run a job using data from GDX
  - How to run a job using implicit database communication
'''
from __future__ import print_function
from gams import *
import os
import sys

def get_data_text():
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

  Scalar f  freight in dollars per case per thousand miles  /90/ ; '''

def get_model_text():
    return '''
  Sets
       i   canning plants
       j   markets

  Parameters
       a(i)   capacity of plant i in cases
       b(j)   demand at market j in cases
       d(i,j) distance in thousands of miles
  Scalar f  freight in dollars per case per thousand miles;

$if not set gdxincname $abort 'no include file name for data file provided'
$gdxin %gdxincname%
$load i j a b d f
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
    if len(sys.argv) > 1:
        ws = GamsWorkspace(system_directory = sys.argv[1])
    else:
        ws = GamsWorkspace()

    t3 = ws.add_job_from_string(get_data_text())
    t3.run()
    t3.out_db.export(os.path.join(ws.working_directory, "tdata.gdx"))
    t3 = ws.add_job_from_string(get_model_text())
    
    opt = ws.add_options()
    opt.defines["gdxincname"] = "tdata"
    opt.all_model_types = "xpress"
    t3.run(opt)
    for rec in t3.out_db["x"]:
        print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))
    
    t3a = ws.add_job_from_string(get_data_text())
    t3b = ws.add_job_from_string(get_model_text())
    t3a.run()
    opt.defines["gdxincname"] = t3a.out_db.name
    t3b.run(opt, databases=t3a.out_db)
    for rec in t3b.out_db["x"]:
        print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))
        