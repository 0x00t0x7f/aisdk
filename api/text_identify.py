# -*- coding: utf-8 -*-

"""
文本分析
"""
from functools import partial

from .base import ApiBase
from .base import BASE_HOST
from .base import _process_url

_process_url = partial(_process_url, BASE_HOST)


class ApiText(ApiBase):
	"""
	文本SDK接口
	"""

	_emotion_filter_url = _process_url("/api/v1/text_identify/emotion")  # 情感分析

	def basic_emotion(self, json) -> dict:
		"""
		情感分析

		:param json: 请求数据
		:return: 响应结果
		"""
		return self._request(self._emotion_filter_url, json=json)
