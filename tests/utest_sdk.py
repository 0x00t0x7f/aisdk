# -*- coding: utf-8 -*-

"""
    AI SDK Unit Test.
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2019 by sam lee.
    :version: 0.1

"""
import functools
import os
import pprint
import sys
import time
import unittest

base_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(base_path)

from api import ApiText

# 控制台输出结果
CONSOLE_PRINT = 1


def timeit(cls):
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
        not k.startswith("test_") and callable(v) and setattr(cls, k, decorate(v))
    else:
        return cls


def print_control(func):
    """
    控制台打印输出
    :param func: 被装饰方法
    :return:
    """

    @functools.wraps(func)
    def _decorate(this, *args, **kw):
        resp = func(this, *args, *kw)
        if CONSOLE_PRINT == 1 or (CONSOLE_PRINT is True):
            # print(resp)
            pprint.pprint(resp, indent=4)
        this.assertEqual(resp["errcode"], 200, resp["errmsg"])

    return _decorate


class Mock(object):
    # 短文本测试数据
    short_text = [
        {"contentid": 0, "content": "xxxxxx"},
        {"contentid": 1, "content": "xxxxxx"},
        {"contentid": 2, "content": "xxxxxx"},
    ]

    # 长文本测试数据
    long_text = [
        {"contentid": 0, "content": "xxxxxx"},
        {"contentid": 1, "content": "xxxxxx"},
        {"contentid": 2, "content": "xxxxxx"},
    ]


@timeit
class SdkTextTest(unittest.TestCase):
    """ 文本类分析接口测试用例"""

    def setUp(self):
        self.client = ApiText()
        self.struct_json = {
            "src_id": "xxx",
            "data_id": "xxx",
            "contentlist": Mock.short_text
        }

    def tearDown(self):
        pass

    @print_control
    def test_basic_emotion(self):
        resp = self.client.basic_emotion(json=self.struct_json)
        return resp
