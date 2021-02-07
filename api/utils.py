# -*- coding: utf-8 -*-


import functools
import time


def timeitcls(cls):
    """ 类装饰器-类方法用时统计"""

    def decorate(func):

        @functools.wraps(func)
        def _inner(*args, **kwargs):
            start_t = time.time()
            resp = func(*args, **kwargs)
            cost_t = time.time() - start_t
            print("[%s method: %s] cost: %s" % (cls.__name__, func.__name__, cost_t))
            return resp

        return _inner

    for k, v in cls.__dict__.items():
        not k.startswith("_") and callable(v) and setattr(cls, k, decorate(v))
    else:
        return cls


def timeitfunc(func):
    """ 方法装饰器-类方法用时统计"""

    @functools.wraps(func)
    def decorated(*args, **kw):
        start_t = time.time()
        resp = func(*args, **kw)
        cost_t = time.time() - start_t
        print("[method: %s] cost: %s" % (func, cost_t))
        return resp

    return decorated
