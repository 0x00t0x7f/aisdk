# -*- coding: utf-8 -*-

# 客户端错误码 10xxx

# 缺少参数
MISS_PARAM = (10001, "缺少参数")

# 上传文件错误（客户端）
UPLOAD_INTERNAL_ERR = (10004, "上传文件不合法")

ESTABLISH_TIMEOUT = (10005, "客户端连接超时")

OTHER_ERROR = (10006, "客户端未知错误")

RESP_TIMEOUT = (10007, "服务端响应超时")

DISAPPROVED_METHOD = (10011, "该方法不被赞成使用")

REMOTE_SERVER_UNREACHABLE = (10012, "远程服务不可用")
