'''
@file
This is the 13th model in a series of tutorial examples. Here we show:
  - How to run a GamsJob using a wrapper class to package a particulat GAMS model
'''

from __future__ import print_function
import sys
from gams import *
from transport_class import Transport

plants = ["Seattle", "San-Diego"]
markets = ["New-York", "Chicago", "Topeka"]
capacity = {"Seattle": 350.0, "San-Diego": 600.0}
demand = {"New-York": 325.0, "Chicago": 300.0, "Topeka": 275.0}
distance = {("Seattle",   "New-York"): 2.5, \
            ("Seattle",   "Chicago"):  1.7, \
            ("Seattle",   "Topeka"):   1.8, \
            ("San-Diego", "New-York"): 2.5, \
            ("San-Diego", "Chicago"):  1.8, \
            ("San-Diego", "Topeka"):   1.4 \
           }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ws = GamsWorkspace(system_directory = sys.argv[1])
    else:
        ws = GamsWorkspace()
    
    t = Transport(ws)

    for p in plants:
        t.i.add_record(p)
    for m in markets:
        t.j.add_record(m)
    for p in plants:
        t.a.add_record(p).value = capacity[p]
    for m in markets:
        t.b.add_record(m).value = demand[m]
    for k, v in iter(distance.items()):
        t.d.add_record(k).value = v

    t.f.add_record().value = 90
    t.opt.all_model_types = "cplex"
    t.run(output=sys.stdout)

    print("Objective: " + str(t.z.first_record().level))

    for rec in t.x:
        print(rec)