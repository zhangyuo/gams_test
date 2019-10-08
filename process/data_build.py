#!/usr/bin/env python
# coding:utf-8
"""
# @Time     : 2019-09-19 09:47
# @Author   : Zhangyu
# @Email    : zhangycqupt@163.com
# @File     : data_build.py
# @Software : PyCharm
# @Desc     :
"""

from __future__ import print_function

import json
import pickle

import numpy
from gams import *

if __name__ == "__main__":
    # gams workspace config
    # mac os
    ws = GamsWorkspace(system_directory='/Applications/GAMS27.3/sysdir', working_directory='../gams_model')
    # windows
    # ws = GamsWorkspace(working_directory='../gams_model')

    # load parameters demand
    # para_list = []
    with open("../data/test_para.json", "r", encoding="utf-8") as fr:
        para_list = json.load(fr)

    # load gams file
    model_string = ""
    with open("../gams_model/stdcge_modified1.gms", "r", encoding="utf-8") as fr:
        model_string_0 = fr.read()

    ############# gams loop ##############
    # define data list
    data_list = []
    shock_para = "tauz"
    shock_scope = "TOTAL"
    for i, shock_value in enumerate(numpy.arange(0, 0.0101, 0.001)):
        # shock_value = round(shock_value, 3)
        shock_value = "%.3f" % shock_value
        print("#%d:\t%s" % (i, str(shock_value)))
        shock_scope_gms = shock_scope
        if shock_scope == "TOTAL":
            shock_scope_gms = "i"
        model_string = model_string_0 % "%s(%s) = %s" % (shock_para, shock_scope_gms, str(shock_value))
        t1 = ws.add_job_from_string(model_string)
        t1.run()
        # data build
        _data = []
        result_list = {
            "shockPara": shock_para,
            "shockScope": shock_scope,
            "shockValue": shock_value,
            "data": _data
        }
        for para in para_list:
            for rec in t1.out_db[para.get("name")]:
                # print(rec.keys)
                # print(str(rec.level))
                _data.append({
                    "parameter": para.get("name"),
                    "dim": str(rec.keys).replace("\'", "").replace("[", "").replace("]", "").replace(" ", "") if len(
                        rec.keys) else "",
                    "value": str("%.4f" % rec.value)
                })
        data_list.append(result_list)

    # output file
    # with open("../data/singleCountry_01.json", "w", encoding="utf-8") as fp:
    #     json.dump(data_list, fp, ensure_ascii=False, indent=4)
    pickle.dump(data_list, open('../data/singleCountry_01.pkl', 'wb'), protocol=2)
    data = pickle.load(open("../data/singleCountry_01.pkl", "rb"))
    for _ in data:
        print(_)
