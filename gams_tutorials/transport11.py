'''
@file
This is the 11th model in a series of tutorial examples. Here we show:
  - How to create and use a save/restart file
'''

from __future__ import print_function
from gams import *
import os
import sys

def get_base_model_text():
    return '''
$onempty
  Sets
       i(*)   canning plants / /
       j(*)   markets        / /

  Parameters
       a(i)   capacity of plant i in cases / /
       b(j)   demand at market j in cases  / /
       d(i,j) distance in thousands of miles / /
  Scalar f  freight in dollars per case per thousand miles /0/;

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

  Solve transport using lp minimizing z ; '''
    
def get_model_text():
    return '''
$if not set gdxincname $abort 'no include file name for data file provided'
$gdxin %gdxincname%
$onMulti
$load i j a b d f
$gdxin

  Display x.l, x.m ; '''

def create_save_restart(cp_file_name):
    if len(sys.argv) > 1:
        ws = GamsWorkspace(os.path.dirname(cp_file_name), sys.argv[1])
    else:
        ws = GamsWorkspace(os.path.dirname(cp_file_name))

    j1 = ws.add_job_from_string(get_base_model_text())
    opt = ws.add_options()
    
    opt.action = Action.CompileOnly
    cp = ws.add_checkpoint(os.path.basename(cp_file_name))
    j1.run(opt, cp)
    del opt


if __name__ == "__main__":
    # Create a save/restart file usually supplied by an application provider
    # We create it for demonstration purpose
    w_dir = os.path.join(".", "tmp")
    create_save_restart(os.path.join(w_dir, "tbase"));

    plants   = [ "Seattle", "San-Diego" ]
    markets  = [ "New-York", "Chicago", "Topeka" ]
    capacity = { "Seattle": 350.0, "San-Diego": 600.0 } 
    demand   = { "New-York": 325.0, "Chicago": 300.0, "Topeka": 275.0 }

    distance = { ("Seattle",   "New-York") : 2.5,
                 ("Seattle",   "Chicago")  : 1.7,
                 ("Seattle",   "Topeka")   : 1.8,
                 ("San-Diego", "New-York") : 2.5,
                 ("San-Diego", "Chicago")  : 1.8,
                 ("San-Diego", "Topeka")   : 1.4
               }
               
    if len(sys.argv) > 1:
        ws = GamsWorkspace(w_dir, sys.argv[1])
    else:
        ws = GamsWorkspace(w_dir)

    db = ws.add_database()
    
    # prepare a GAMSDatabase with data from the Python data structures
    i = db.add_set("i", 1, "canning plants")
    for p in plants:
        i.add_record(p)
    
    j = db.add_set("j", 1, "markets")
    for m in markets:
        j.add_record(m)
        
    a = db.add_parameter_dc("a", [i], "capacity of plant i in cases")
    for p in plants:
        a.add_record(p).value = capacity[p]
    
    b = db.add_parameter_dc("b", [j], "demand at market j in cases")
    for m in markets:
        b.add_record(m).value = demand[m]
    
    d = db.add_parameter_dc("d", [i,j], "distance in thousands of miles")
    for k, v in iter(distance.items()):
        d.add_record(k).value = v
    
    f = db.add_parameter("f", 0, "freight in dollars per case per thousand miles")
    f.add_record().value = 90
    
    # run a job using data from the created GAMSDatabase
    cp_base = ws.add_checkpoint("tbase")
    t4 = ws.add_job_from_string(get_model_text(), cp_base)
    opt = ws.add_options()
    opt.defines["gdxincname"] = db.name
    opt.all_model_types = "xpress"
    t4.run(opt, databases=db)
    
    for rec in t4.out_db["x"]:
        print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))

