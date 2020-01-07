# -*- coding: utf-8 -*-

"""
ApiBase
@author: sam lee
@release: v0.1
@created: 2019-10-15
"""
import six
import time
import json
import requests
from posixpath import normpath
from six.moves import urllib_parse

from config.base import (BASE_HOST, CONNECT_TIMEOUT, SOCKET_TIMEOUT)


def _process_url(prefix, uri):
	full_url = urllib_parse.urljoin(prefix, uri)
	url_parsed = urllib_parse.urlparse(full_url)
	norm_path = normpath(url_parsed[2])
	_ = (url_parsed.scheme, url_parsed.netloc, norm_path, url_parsed.params, url_parsed.query, url_parsed.fragment)
	return urllib_parse.urlunparse(_)


class ApiBase(object):
	"""
		ApiBase
	"""
	prefix_url = BASE_HOST
	__access_token = _process_url(BASE_HOST, "/v1/token")

	def __init__(self, app_id, app_key, app_secret):
		self._app_id = app_id.strip()  # 标识应用 此版本预留
		self._app_key = app_key.strip()
		self.app_secret = app_secret.strip()
		self.__client = requests
		self.__version = "0_1_1"
		self.__connect_timeout = CONNECT_TIMEOUT
		self.__socket_timeout = SOCKET_TIMEOUT
		self._proxies = {}
		self._authObj = {}

	def get_version(self):
		return self.__version

	def set_proxies(self, proxies):
		self._proxies = proxies

	@staticmethod
	def _validdate(url, data):
		return True

	def _auth(self, refresh=False):
		"""
		:param refresh: 是否刷新token
		:return: 请求参数
		:rtype: dict
		"""
		if not refresh:
			tm = self._authObj.get("time", 0) + int(self._authObj.get("expires_in", 0)) - 30
			if tm > int(time.time()):
				return self._authObj

		obj = self.__client.post(self.__access_token, verify=False, data={
			'grant_type': 'client_credentials',
			'client_id': self._app_key,
			'client_secret': self.app_secret,
		}, proxies=self._proxies, timeout=(
			self.__connect_timeout,
			self.__socket_timeout
		)).json()

		obj['time'] = int(time.time())
		self._authObj = obj
		return obj

	def _request(self, url, data=None, json=None, headers=None):
		"""
		:param url: 请求URL
		:param data: 请求载荷
		:param headers: 请求头部
		:return: 响应
		:rtype: json
		"""
		try:
			valid_result = self._validdate(url, data)
			if not valid_result:
				return valid_result

			authObj = self._auth()
			params = self._get_params(authObj)
			jsonobj = self._process_request(url, params, json, headers)
			headers = self._get_auth_headers("POST", url, params, headers)
			resp = self.__client.post(
				url, data=data, json=jsonobj, headers=headers, verify=False, timeout=(
					self.__connect_timeout,
					self.__socket_timeout
				),
				proxies=self._proxies
			)

			obj = self._process_result(resp.content)
			if obj.get("errcode", "") == 7004:
				authObj = self._auth(refresh=True)
				params = self._get_params(authObj)
				resp = self.__client.post(
					url, data=data, json=jsonobj, headers=headers, verify=False, timeout=(
						self.__connect_timeout,
						self.__socket_timeout
					),
					proxies=self._proxies
				)
				obj = self._process_result(resp.content)
		except:
			return {
				"errcode": "SDK Error",
				"errmsg": "connect or read data timeout or client error.",
				"time": int(time.time())
			}
		return obj

	def _get_params(self, authobj):
		return {"token": authobj["access_token"]}

	def _get_auth_headers(self, method, url, params=None, headers=None):
		""" 完善请求头部"""
		return headers or {}

	def _process_request(self, url, params, json, headers):
		""" params handle"""
		json["api_sdk"] = 'python'
		json['api_version'] = self.__version

		# token 置于data中
		json["token"] = self._authObj.get("access_token") or ""
		return json

	def _process_result(self, content):
		"""
		:param content: 返回文本
		统一使用utf-8编码的json字符串
		"""
		if six.PY2:
			return json.load(content) or {}
		elif six.PY3:
			return json.loads(content.decode()) or {}
