'''
@file
This is the 7th model in a series of tutorial examples. Here we show:
  - How to create a GamsModelInstance from a GamsCheckpoint
  - How to modify a parameter of a GamsModelInstance using GamsModifier
  - How to modify a variable of a GamsModelInstance using GamsModifier
'''

from __future__ import print_function
from gams import *
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

  Model transport /all/ ; '''


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ws = GamsWorkspace(system_directory = sys.argv[1])
    else:
        ws = GamsWorkspace()

    cp = ws.add_checkpoint()

    # initialize a GAMSCheckpoint by running a GAMSJob
    t7 = ws.add_job_from_string(get_model_text())
    t7.run(checkpoint=cp)

    # create a GAMSModelInstance and solve it multiple times with different scalar bmult
    mi = cp.add_modelinstance()
    bmult = mi.sync_db.add_parameter("bmult", 0, "demand multiplier")
    opt = ws.add_options()
    opt.all_model_types = "cplexd"

    # instantiate the GAMSModelInstance and pass a model definition and GAMSModifier to declare bmult mutable
    mi.instantiate("transport use lp min z", GamsModifier(bmult), opt)

    bmult.add_record().value = 1.0
    bmultlist = [ 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3 ]

    for b in bmultlist:
        bmult.first_record().value = b
        mi.solve()
        print("Scenario bmult=" + str(b) + ":")
        print("  Modelstatus: " + str(mi.model_status))
        print("  Solvestatus: " + str(mi.solver_status))
        print("  Obj: " + str(mi.sync_db.get_variable("z").find_record().level))


    # create a GAMSModelInstance and solve it with single links in the network blocked
    mi = cp.add_modelinstance()
    x = mi.sync_db.add_variable("x", 2, VarType.Positive)
    xup = mi.sync_db.add_parameter("xup", 2, "upper bound on x")

    # instantiate the GAMSModelInstance and pass a model definition and GAMSModifier to declare upper bound of X mutable
    mi.instantiate("transport use lp min z", GamsModifier(x, UpdateAction.Upper, xup))
    mi.solve()

    for i in t7.out_db["i"]:
        for j in t7.out_db["j"]:
            xup.clear()
            xup.add_record((i.key(0),j.key(0))).value = 0
            mi.solve()
            print("Scenario link blocked: " + i.key(0)  + " - " + j.key(0))
            print("  Modelstatus: " + str(mi.model_status))
            print("  Solvestatus: " + str(mi.solver_status))
            print("  Obj: " + str(mi.sync_db["z"].find_record().level))


