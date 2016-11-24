#coding:utf-8
"""
@file:      run_loop_kick
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-11-24 20:43
@description:
            --
"""
import os,sys
sys.path.append(
    os.path.dirname(
        sys.path[0]
    )
)

from KickTaskManager import run


if __name__=="__main__":
    run(big_loop=False,leftest=400000000,rightest=900000000)