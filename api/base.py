# -*- coding: utf-8 -*-

"""
ApiBase
@author: sam lee
@release: v0.1
@created: 2019-10-15
"""
import json
import sys
import time
from posixpath import normpath

import requests

try:
	import six
	from six.moves import urllib_parse

	_PY2, _PY3 = six.PY2, six.PY3


	def _process_url(prefix, uri):
		full_url = urllib_parse.urljoin(prefix, uri)
		url_parsed = urllib_parse.urlparse(full_url)
		norm_path = normpath(url_parsed[2])
		_ = (url_parsed.scheme, url_parsed.netloc, norm_path, url_parsed.params, url_parsed.query, url_parsed.fragment)
		return urllib_parse.urlunparse(_)
except:
	_PY2 = sys.version_info.major == 2
	_PY3 = sys.version_info.major == 3


	def _process_url(prefix, uri):
		if prefix.endswith("/") and uri.startswith("/"):
			prefix = prefix[:-1]
		return prefix + uri

from config.base import (
	BASE_HOST,
	CONNECT_TIMEOUT,
	SOCKET_TIMEOUT,
	APP_ID,
	APP_KEY,
	APP_SECRET
)

from config.errcode_client import (
	RESP_TIMEOUT,
	OTHER_ERROR,
	ESTABLISH_TIMEOUT
)

# 窗口间隔时间 保证服务端token过期之前 SDK重新请求
_WINDOW_TIME = 60


class ApiBase(object):
	"""
		ApiBase
	"""
	prefix_url = BASE_HOST
	__access_token = _process_url(BASE_HOST, "/auth/token")

	def __init__(self, app_id="", app_key="", app_secret=""):
		self._app_id = app_id.strip() or APP_ID  # 标识应用 此版本预留
		self._app_key = app_key.strip() or APP_KEY
		self.app_secret = app_secret.strip() or APP_SECRET
		self.__client = requests
		self.__version = "0_1_1"
		self.__connect_timeout = CONNECT_TIMEOUT
		self.__socket_timeout = SOCKET_TIMEOUT
		self._proxies = {}
		self._authObj = {}
		self._client_info = {}  # 设备信息

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
			tm = self._authObj.get("time", 0) + int(self._authObj.get("expires_in", 0)) - _WINDOW_TIME
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

	def _request(self, url, data=None, json=None, headers=None, files=None):
		"""
		:param url: 请求URL
		:param data: 请求载荷
		:param headers: 请求头部
		:param files: 文件绝对路径列表
		:return: 响应
		:rtype: json
		"""
		try:
			valid_result = self._validdate(url, data)
			if not valid_result:
				return valid_result

			authObj = self._auth()
			params = self._get_params(authObj)
			jsonobj = self._process_request(url, params, data, json, headers)
			headers = self._get_auth_headers("POST", url, params, headers)
			resp = self.__client.post(
				url, data=data, json=jsonobj, headers=headers, verify=False, timeout=(
					self.__connect_timeout,
					self.__socket_timeout
				),
				proxies=self._proxies,
				files=files
			)

			obj = self._process_result(resp)

			if obj.get("errcode", "") == 7004:
				authObj = self._auth(refresh=True)
				params = self._get_params(authObj)
				jsonobj = self._process_request(url, params, data, json, headers)
				resp = self.__client.post(
					url, data=data, json=jsonobj, headers=headers, verify=False, timeout=(
						self.__connect_timeout,
						self.__socket_timeout
					),
					proxies=self._proxies,
					files=files
				)
				obj = self._process_result(resp)

		except KeyError as why:
			return {
				"errcode": self._authObj.get("errcode") or -1,
				"errmsg": self._authObj.get("errmsg") or why,
				"time": int(time.time())
			}
		except requests.exceptions.ReadTimeout as why:
			return {
				"errcode": RESP_TIMEOUT[0],
				"errmsg": "%s 超过客户端%s秒限制" % (RESP_TIMEOUT[1], SOCKET_TIMEOUT),
				"time": int(time.time())
			}
		except requests.exceptions.Timeout:
			return {
				"errcode": ESTABLISH_TIMEOUT[0],
				"errmsg": "%s 超过%s秒限制" % (ESTABLISH_TIMEOUT[1], CONNECT_TIMEOUT),
				"time": int(time.time())
			}
		except:
			return {
				"errcode": OTHER_ERROR[0],
				"errmsg": OTHER_ERROR[1],
				"time": int(time.time())
			}
		return obj

	def _get_params(self, authobj):
		return {"token": authobj.get("access_token")}

	def _get_auth_headers(self, method, url, params=None, headers=None):
		""" 完善请求头部"""
		return headers or {}

	def _process_request(self, url, params, data, json, headers):
		""" params handle"""
		json = json or {}
		json["api_sdk"] = 'python'
		json['api_version'] = self.__version

		# token 置于data中
		if data and isinstance(data, dict) and data.get("type"):
			prepare_request_type = data["type"]
			if prepare_request_type in ["image"]:
				data["token"] = self._authObj["access_token"]
		else:
			json["token"] = self._authObj["access_token"]
		json["client_info"] = self._get_equipment_info()
		return json

	def _process_result(self, resp):
		"""
		:param content: 返回文本
		统一使用utf-8编码的json字符串
		"""

		def _get_headers():
			return resp.headers

		def _get_status_code():
			return resp.status_code

		self.get_headers = _get_headers
		self.get_status_code = _get_status_code

		if _PY2:
			return json.load(resp.content) or {}
		elif _PY3:
			return json.loads(resp.content.decode()) or {}

	def _get_equipment_info(self):
		try:
			self._client_info["hostname"] = ""
			self._client_info["os"] = ""
		except Exception as why:
			pass
		return self._client_info
