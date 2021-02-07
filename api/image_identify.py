"""
图像识别
"""
import os
import time
from functools import partial, wraps
from hashlib import md5

from config.base import (PRE_REQUEST_CHECK, ALLOWED_FILE_SUFFIX, MAX_FILE_LENGTH)
from config.errcode_client import *
from .base import ApiBase
from .base import BASE_HOST
from .base import _process_url

_process_url = partial(_process_url, BASE_HOST)


# 请求参数核查
def check_files(func):
    """
    检查上传文件是否符合要求
    :param func: 被装饰函数
    :return:
    """

    @wraps(func)
    def decorated(self, files):
        send_files = []
        for file in files:
            if os.path.exists(file) and os.path.isfile(file):
                with open(file, "rb") as f:
                    bfile = f.read()
                    _md5 = md5()
                    for block in f:
                        _md5.update(block)
                    file_md5 = _md5.hexdigest()
                    file_name = os.path.split(file)
                    _, ext = os.path.splitext(file)
                    file_type = "image/%s" % ext.strip(".")
                    file_size = os.path.getsize(file)
                    send_files.append((
                        "image",
                        (
                            file_name[1],
                            bfile,
                            file_type,
                            {
                                "md5": file_md5,
                                "filesize": file_size
                            }
                        )
                    ))
        else:
            prequest_send_files = []
            if send_files:
                if PRE_REQUEST_CHECK:
                    for index, item in enumerate(send_files):
                        file_body = item[1]
                        file_info = item[1][3]
                        filetype = file_body[2]
                        filesize = file_info["filesize"]
                        fileext = filetype.split("/")[1]
                        if fileext in ALLOWED_FILE_SUFFIX and filesize <= MAX_FILE_LENGTH:
                            prequest_send_files.append(item)
                return func(self, **{
                    "files": prequest_send_files or (not PRE_REQUEST_CHECK and send_files),
                })
        return {
            "errcode": UPLOAD_INTERNAL_ERR[0],
            "errmsg": UPLOAD_INTERNAL_ERR[1],
            "time": int(time.time())
        }

    return decorated


class ApiImage(ApiBase):
    """
    图像识别
    """

    _sign = "image"
    _face_detect_url = _process_url("/api/v1/image_identify/facedet")  # 人脸识别

    def __init__(self, *args, **kwargs):
        super(ApiImage, self).__init__(*args, **kwargs)
        self.default_datas = {"type": self._sign}

    @check_files
    def basic_face(self, files) -> dict:
        """
        人脸识别

        :param files: 待上传图片绝对路径
        :return: 结果
        """
        return self._request(self._face_detect_url, data=self.default_datas, files=files)
