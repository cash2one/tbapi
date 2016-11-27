#coding:utf-8
"""
@file:      default_run
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-11-24 20:45
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
    run(big_loop=True,thread_cot=64)
