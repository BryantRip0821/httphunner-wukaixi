import os.path
import time
import logging
import pymysql
import base64
import json
import requests
import sys

from httprunner import __version__
from httprunner.exceptions import ValidationFailure
from httprunner.testcase import StepRequestValidation
from jmespath import search
from httprunner.builtin import comparators as comp


# 初始化案例执行返回列表
resplist = []


# 获取httprunner版本号
def get_httprunner_version():
    """
    :return: httprunner-version
    """
    return __version__


# 获取毫秒时间戳
def get_time_key():
    """
    :return: 毫秒级时间戳
    """
    t = time.time()
    return int(round(t * 1000))


# 保存response对象
def save_resp(response):
    """
    用法：${saveResp($response)}
    :param resp: 返回的内容
    :return:
    """
    if resplist is None:
        raise ValueError
    else:
        resplist.append(response)


# 根据jmespath表达式获取值
def get_resp_list_value(jmse_search_value,resp_key):
    """
    从response对象列表中，根据jmespath表达式提取对应值
    :param resp_key:指定从那一个response对象取值
    :param jmse_search_value:jmespath表达式
    :return: 对应值
    """
    resp_obj = resplist[resp_key]
    resp_data = {
            "status_code": resp_obj.status_code,
            "headers": resp_obj.headers,
            "cookies": resp_obj.cookies,
            "body": resp_obj.body,
        }
    jmse_data = search(jmse_search_value, resp_data)
    return search(jmse_search_value, resp_data)


# 清空resplit
def remove_resp_list():
    resplist[:] = []


# 获取活体图片
def setup_hook_get_base64():
    """
    图片转base64
    return: 活体图片base64文件
    """
    filepath = os.path.abspath(os.path.dirname(__file__))
    image_path = filepath + "/data/file.jpg"
    with open(image_path, "rb") as image_file:
        data = base64.b64encode(image_file.read())
        base_data = str(data).split("'")[1]
        return base_data


# 更新活体上传参数
def setup_hook_update_request(req):
    req["req_json"]["attachmentInfos"][0].pop("previewUrl")


def get_methods(self):
    return (list(filter(lambda m: not m.startswith("_") and callable(getattr(self, m)),dir(self))))


def call_assert(assert_enum):
    """
    提取assert变量列表
    :param assert_enum:
    :return:
    """
    print(assert_enum)

    for k,v in assert_enum.items():
        assert_func_method = k
        print("断言方法：" + k)
        check_value = v[0]
        expect_value = v[1]
        resp_assert(assert_func_method, check_value, expect_value)


# 自定义系统断言["success","errorMsg']
def resp_assert(assertType, check_value, expect_value):
    """
    teardown_hook:自定义断言
    :param assertType: 断言类型
    :param check_value: 返回值
    :param expect_value: 比较值
    :return:
    """
    if isinstance(check_value,str):
        pass
    elif isinstance(check_value,dict):
        check_value = get_resp_list_value(check_value["jmes"],check_value["respkey"])
        print(check_value)
    else:
        raise TypeError["assert type error"]

    if isinstance(expect_value,list):
        expect_value = get_resp_list_value(expect_value["jmes"],expect_value["respkey"])
    else:
        pass

    if isinstance(assertType,str) == True:
        if assertType in get_methods(comp):
            getattr(comp, assertType)(check_value, expect_value)
        else:
            raise IndexError["no such assertion method"]
    else:
        raise TypeError["assertion type must be a string"]


def getValue(data, key):
    """
    读取传入的字典、列表的对应key的值
    :param data: 数据（字典、列表）
    :param key: 如果是字典则是字符串，列表则传常数
    :return: 对应key的值
    """
    if type(data) == dict:
        return data[key]
    elif type(data) == list:
        return data[int(key)]
    else:
        pass


# 初始化数据库连接
def mysql_conn():
    conn = pymysql.connect(
        user="wukaixi",
        password="wukaixi123_",
        port=33306,
        host="47.108.1.74",
        db="quark_loan_member_dev",
        charset="utf8"
    )
    return conn


def removeRespList():
    resplist[:] = []
