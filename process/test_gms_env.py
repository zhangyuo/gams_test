#!/usr/bin/env python
# coding:utf-8
"""
# @Time     : 2019-08-16 15:35
# @Author   : Zhangyu
# @Email    : zhangycqupt@163.com
# @File     : gams_connect.py
# @Software : PyCharm
# @Desc     : test gams environment
"""

'''
PYTHONPATH是Python搜索路径，默认我们import的模块都会从PYTHONPATH里面寻找。

打印PYTHONPATH：
import sys
print sys.path

设置PYTHONPATH：
方法一：命令窗口添加路径,此方法只在当前命令窗口生效
export PYTHONPATH=$PYTHONPATH:/home/ershisui

方法二：在python中添加：
import sys
sys.path.append('/home/ershisui/')
'''

import sys
# sys.path.append('/Applications/GAMS27.3/sysdir/apifiles/Python/api/')
# sys.path.append('/Applications/GAMS27.3')
print(sys.path)

from gams import *


