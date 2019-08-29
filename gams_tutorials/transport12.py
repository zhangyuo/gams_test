'''
@file
This is the 12th model in a series of tutorial examples. Here we show:
  - How to implement a GUSS approach using the GAMS API
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

  Model transport /all/ ;
'''


# Needs to be called with an uninstantiated GAMSModelInstance
def guss_call(dict, mi, solve_statement, opt = None, mi_opt = None, output=None):
    modifier_list = []

    if dict.dimension != 3:
        raise GamsException("Dict needs to be 3-dimensional")

    scen_name = dict.first_record((" ", "scenario", " ")).key(0)
    scen_symbol = dict.database[scen_name]

    for rec in dict:
        if rec.key(1).lower() == "scenario":
            continue
        if rec.key(1).lower() == "param":
            modifier_dim = dict.database[rec.key(2)].dimension - scen_symbol.dimension
            if modifier_dim < 0:
                raise GamsException("Dimension of " + rec.key(2) + " too small")
            modifier_list.append((GamsModifier(mi.sync_db.add_parameter(rec.key(0), modifier_dim, "")), dict.database[rec.key(2)]))
        elif (rec.key(1).lower() == "lower") or (rec.key(1).lower() == "upper") or (rec.key(1).lower() == "fixed"):
            modifier_dim = dict.database[rec.key(2)].dimension - scen_symbol.dimension
            if modifier_dim < 0:
                raise GamsException("Dimension of " + rec.key(2) + " too small")
            modifier_var = None
            try:
                modifier_var = dict.database[rec.key(0)]
            except:
                modifier_var = mi.sync_db.add_variable(rec.key(0), modifier_dim, VarType.Free, "")
            if (rec.key(1).lower() == "lower"):
                modifier_list.append((GamsModifier(modifier_var, UpdateAction.Lower, mi.sync_db.add_parameter(rec.key(2), modifier_dim, "")), dict.database[rec.key(2)]))
            elif rec.key(1).lower() == "upper":
                modifier_list.append((GamsModifier(modifier_var, UpdateAction.Upper, mi.sync_db.add_parameter(rec.key(2), modifier_dim, "")), dict.database[rec.key(2)]))
            else:  #fixed
                modifier_list.append((GamsModifier(modifier_var, UpdateAction.Fixed, mi.sync_db.add_parameter(rec.key(2), modifier_dim, "")), dict.database[rec.key(2)]))
        elif (rec.key(1).lower() == "level") or (rec.key(1).lower() == "marginal"):
            # Check that parameter exists in GAMSDatabase, will throw an exception if not
            x = dict.database[rec.key(2)]
        else:
            raise GamsException("Cannot handle UpdateAction " + rec.key(1))

    ml = []
    for tup in modifier_list:
        ml.append(tup[0])
    mi.instantiate(solve_statement, ml, opt)

    out_list = []

    for s in scen_symbol:
        for tup in modifier_list:
            p = None
            pscen = tup[1]

            if tup[0].data_symbol == None:
                p = tup[0].gams_symbol
            else:
                p = tup[0].data_symbol

            # Implemented SymbolUpdateType=BaseCase
            p.clear()

            rec = None
            filter = [""]*pscen.dimension
            for i in range(scen_symbol.dimension):
                filter[i] = s.key(i)
            for i in range (scen_symbol.dimension, pscen.dimension):
                filter[i] = " "
            try:
                rec = pscen.first_record(filter)
            except:
                continue

            while True:
                my_keys = []
                for i in range(p.dimension):
                    my_keys.append(rec.key(scen_symbol.dimension+i))
                p.add_record(my_keys).value = rec.value
                if not rec.move_next():
                    break

        mi.solve(SymbolUpdateType.BaseCase, output, mi_opt)
        if len(out_list) == 0:
            for rec in dict:
                if (rec.key(1).lower() == "level") or (rec.key(1).lower() == "marginal"):
                    out_list.append((mi.sync_db[rec.key(0)], dict.database[rec.key(2)], rec.key(1).lower()))

        for tup in out_list:
            my_keys = [""]*(scen_symbol.dimension + len(tup[0].first_record().keys))
            for i in range(scen_symbol.dimension):
                my_keys[i] = s.key(i)

            if (tup[2] == "level") and (isinstance(tup[0],GamsVariable)):
                for rec in tup[0]:
                    for i in range(len(rec.keys)):
                        my_keys[scen_symbol.dimension + i] = s.key(i)
                    tup[1].add_record(my_keys).value = rec.level
            elif (tup[2] == "level") and (isinstance(tup[0], GamsEquation)):
                for rec in tup[0]:
                    for i in range(len(rec.keys)):
                        my_keys[scen_symbol.dimension + i] = s.key(i)
                    tup[1].add_record(my_keys).value = rec.level
            elif (tup[2] == "marginal") and (isinstance(tup[0], GamsVariable)):
                for rec in tup[0]:
                    for i in range(len(rec.keys)):
                        my_keys[scen_symbol.dimension + i] = s.key(i)
                    tup[1].add_record(my_keys).value = rec.marginal
            elif (tup[2] == "marginal") and (isinstance(tup[0], GamsEquation)):
                for rec in tup[0]:
                    for i in range(len(rec.keys)):
                        my_keys[scen_symbol.dimension + i] = s.key(i)
                    tup[1].add_record(my_keys).value = rec.marginal


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ws = GamsWorkspace(system_directory = sys.argv[1])
    else:
        ws = GamsWorkspace()

    cp = ws.add_checkpoint()

    # initialize a GAMSCheckpoint by running a GAMSJob
    t12 = ws.add_job_from_string(get_model_text())
    t12.run(checkpoint=cp)

    # create a GAMSModelInstance and solve it multiple times with different scalar bmult
    mi = cp.add_modelinstance()

    bmultlist = [ 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3 ]

    db = ws.add_database()

    scen = db.add_set("scen", 1, "")
    bmult = db.add_parameter_dc("bmultlist", [scen])
    zscen = db.add_parameter_dc("zscen", [scen])

    i = 0
    for b in bmultlist:
        bmult.add_record("s" + str(i)).value = b
        scen.add_record("s" + str(i))
        i += 1


    dict = db.add_set("dict",3,"")
    dict.add_record((scen.name, "scenario", ""))
    dict.add_record(("bmult", "param", bmult.name))
    dict.add_record(("z", "level", zscen.name))

    guss_call(dict, mi, "transport use lp min z");

    for rec in db[zscen.name]:
        print(rec.key(0) + " obj: " + str(rec.value))

    #*******************

    mi2 = cp.add_modelinstance()
    db2 = ws.add_database()

    scen2 = db2.add_set("scen", 1, "")
    zscen2 = db2.add_parameter_dc("zscen", [scen2])
    xup = db2.add_parameter("xup", 3, "")

    for j in range(4):
        for irec in t12.out_db["i"]:
            for jrec in t12.out_db["j"]:
                xup.add_record(("s" + str(j), irec.key(0), jrec.key(0))).value = j+1
        scen2.add_record("s" + str(j))

    dict2 = db2.add_set("dict", 3, "")
    dict2.add_record((scen2.name, "scenario", ""))
    dict2.add_record(("x", "lower", xup.name))
    dict2.add_record(("z", "level", zscen2.name))

    guss_call(dict2, mi2, "transport use lp min z", output=sys.stdout)

    for rec in db2[zscen2.name]:
        print(rec.key(0) + " obj: " + str(rec.value))


