'''
@file
This is the 10th model in a series of tutorial examples. Here we show:
  - How to fill a GamsDatabase by reading from MS Excel
'''

from __future__ import print_function
from xlrd import open_workbook
from gams import *
import sys

def get_model_text():
    return '''
  Sets
       i   canning plants
       j   markets

  Parameters
       a(i)   capacity of plant i in cases
       b(j)   demand at market j in cases
       d(i,j) distance in thousands of miles
  Scalar f  freight in dollars per case per thousand miles /90/;

$if not set gdxincname $abort 'no include file name for data file provided'
$gdxin %gdxincname%
$load i j a b d
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
    wb = open_workbook("..\\Data\\transport.xls")

    capacity = wb.sheet_by_name("capacity")
    demand = wb.sheet_by_name("demand")
    distance = wb.sheet_by_name("distance")
    
    # number of markets/plants have to be the same in all spreadsheets
    assert (distance.ncols-1 == demand.ncols) and (distance.nrows-1 == capacity.ncols), \
            "Size of the spreadsheets doesn't match"
    
    if len(sys.argv) > 1:
        ws = GamsWorkspace(system_directory = sys.argv[1])
    else:
        ws = GamsWorkspace()

    db = ws.add_database()
    i = db.add_set("i", 1, "Plants")
    j = db.add_set("j", 1, "Markets")
    capacity_param = db.add_parameter_dc("a", [i], "Capacity")
    demand_param = db.add_parameter_dc("b", [j], "Demand")
    distance_param = db.add_parameter_dc("d", [i,j], "Distance")
    
    for cx in range(capacity.ncols):
        i.add_record(str(capacity.cell_value(0, cx)))
        capacity_param.add_record(str(capacity.cell_value(0, cx))).value = capacity.cell_value(1, cx)
    
    for cx in range(demand.ncols):
        j.add_record(str(demand.cell_value(0, cx)))
        demand_param.add_record(str(demand.cell_value(0, cx))).value = demand.cell_value(1, cx)
    
    for cx in range(1, distance.ncols):
        for rx in range(1, distance.nrows):
            keys = ( str(distance.cell_value(rx, 0)), str(distance.cell_value(0, cx)) )
            distance_param.add_record(keys).value = distance.cell_value(rx, cx)

    # Create and run the GAMSJob
    t10 = ws.add_job_from_string(get_model_text())
    opt = ws.add_options()
    opt.defines["gdxincname"] = db.name
    opt.all_model_types = "xpress"
    t10.run(opt, databases=db)
    for rec in t10.out_db["x"]:
        print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))
