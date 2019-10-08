# ecoding = utf8
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

    # 设定文件路径以及代码位置，已经生成中间变量的文件夹位置。
    # mac os
    ws = GamsWorkspace(system_directory='/Applications/GAMS27.3/sysdir', working_directory='../gams_model')
    # windows
    # ws = GamsWorkspace(working_directory='../gams_model')

    # output data
    t1 = ws.add_job_from_file("stdcge.gms")
    t1.run()
    # t1.out_db 其实也是一种database
    t1.out_db.export("data.gdx")

    # print data
    print("Run with t1:")
    for rec in t1.out_db["x"]:
        # print(str(rec.level))
        print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))

    # 重新读取 存储的out_db数据
    # t2 = ws.add_database_from_gdx("data.gdx")
    # print("Run with t2:")
    # for rec in t2["x"]:
    #     print("x(" + rec.key(0) + "," + rec.key(1) + "): level=" + str(rec.level) + " marginal=" + str(rec.marginal))
