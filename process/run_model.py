'''
@file
This is the 1st model in a series of tutorial examples. Here we show:
  - How to run a GAMSJob from file
  - How to specify the solver
  - How to run a job with a solver option file
'''

from __future__ import print_function
from gams import *
import os
import sys

# sys.path.append('/Applications/GAMS27.3/sysdir')
# print(sys.path)


if __name__ == "__main__":
    # if len(sys.argv) > 1:
    #     ws = GamsWorkspace(system_directory = sys.argv[1])
    # else:
    #     ws = GamsWorkspace()

    # ws = GamsWorkspace()
    # ws.gamslib("stdcge")

    ws = GamsWorkspace(working_directory='../gams_model')
    t1 = ws.add_job_from_file("stdcge.gms")
    t1.run()

    print("Ran with Default:")
    for rec in t1.out_db["x"]:
        print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))
    #
    # for rec in t1.out_db["UU"]:
    #     print(rec.level)

    # for rec in t1.out_db["Xv"]:
    #     print("Xv(" + rec.key(0) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))

    # for rec in t1.out_db["epsilon"]:
    #     print("level=" + str(rec.level) + " marginal=" + str(rec.marginal))

    # for rec in t1.out_db["dX"]:
    #     print(rec.key(0) + "," + rec.key(1), rec.value)
