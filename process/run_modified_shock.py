'''
@file
This is the 1st model in a series of tutorial examples. Here we show:
  - How to run a GAMSJob from file
  - How to specify the solver
  - How to run a job with a solver option file
'''

# from __future__ import print_function
from gams import *
import os
import sys
from config.config import *

# sys.path.append('/Applications/GAMS27.3/sysdir')
# print(sys.path)


if __name__ == "__main__":
    ws = GamsWorkspace(working_directory='../gams_model')
    cp = ws.add_checkpoint()
    # tmp = open("../gams_model/stdcge_modified.gms", "r").read()
    # t1 = ws.add_job_from_string(tmp)
    t1 = ws.add_job_from_file("stdcge_modified.gms")
    t1.run(checkpoint=cp)

    # print("Ran with Default:")
    # for rec in t1.out_db["x"]:
    #     print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))
    #
    # #################### 单次冲击 ####################
    # # 进口关税税率调整
    # mi = cp.add_modelinstance()
    # taum = mi.sync_db.add_parameter("taum", 1, "import tariff rate")
    # mi.instantiate("stdcge maximizing UU using nlp", GamsModifier(taum))
    #
    # for rec in t1.out_db.get_parameter("taum"):
    #     taum.add_record(rec.keys).value = TAUM
    # mi.solve()
    # print("Ran with modified taum:")
    # # print(mi.sync_db.get_variable("x"))
    # for rec in mi.sync_db.get_variable("x"):
    #     print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))
    #
    # # 生产税税率调整
    # mi = cp.add_modelinstance()
    # tauz = mi.sync_db.add_parameter("tauz", 1, "production tax rate")
    # mi.instantiate("stdcge maximizing UU using nlp", GamsModifier(tauz))
    # for rec in t1.out_db.get_parameter("tauz"):
    #     tauz.add_record(rec.keys).value = TAUZ
    # mi.solve()
    # print("Ran with modified tauz:")
    # # print(mi.sync_db.get_variable("x"))
    # for rec in mi.sync_db.get_variable("x"):
    #     print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))
    #
    # # 生产税、进口关税税率同时调整
    # t1 = ws.add_job_from_string(
    #     "tauz(i)=" + str(TAUZ) + "; taum(i)=" + str(TAUM) + ";solve stdcge maximizing UU using nlp;", cp)
    # t1.run()
    # print("Ran with modified tauz and taum:")
    # for rec in t1.out_db["x"]:
    #     print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))

    #################### 循环冲击 ####################
    # 进口关税税率调整
    for index, b in enumerate(TAUZ_X):
        t1 = ws.add_job_from_string("tauz(i)=" + str(b) + "; solve stdcge maximizing UU using nlp;", cp)
        t1.run()
        print("Ran %s with modified tauz:" % (index + 1))
        for rec in t1.out_db["x"]:
            print(
                "x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))
