#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : get_sms_to_login.py
# @Author: Wu
# @Date  : 2022/3/24
# @Desc  :
from httprunner import HttpRunner, RunTestCase, Parameters, Config, RunRequest, Step
from api.QuarkLoanMember import (AppMemberController, AppMemberBasisInfoController, AppMemberCertificateInfoController, AppMemberContactInfoController, AppMemberBankInfoController, AppMemberCompanyInfoController)
from api.QuarkLoanAsset import (AppAssetRepay, AppAsset)
from api.QuarkLoanPay import QuarkLoanPay
from api.QuarkLoanRisk import QuarkLoanRisk
from testcases import LoanOperationFlow
import pytest


# 获取短信验证码：正案例
class TestSendSmsCode(HttpRunner):
    data = {
        "sceneEnum": ["LOGIN", "REGISTER", "CHANGE_PWD"],
            }

    @pytest.mark.parametrize(
        "param", Parameters(data)
        )
    def test_start(self, param):
        super().test_start(param)

    config = (
        Config("获取短信验证码")
        .variables(**{
            "zoneCode": "62",
            "telephoneNo": "84199308213",
            "type": 1,
            "sceneEnum": "$sceneEnum",
        })
    )

    teststeps = [
        Step(
            RunTestCase("获取短信验证码")
            .with_variables(**{
                "assert_list": {
                    "equal": [{"jmes": "body.success", "respkey": 0}, True],
                    "equal": [{"jmes": 'headers."Content-Type"', "respkey": 0}, "application/json"],
                }
            })
            .call(testcase=AppMemberController.AppSendSmsCode)
            .teardown_hook("${call_assert($assert_list)}")
            .teardown_hook("${removeRespList()}")
        ),
    ]


# 获取短信验证码：反案例
class TestCaseUser010(HttpRunner):

    data = {"sceneEnum-telephoneNo":
                [
                    ("", ""),
                    ("REGISTER", "1234"),
                    ("login", "84199308213"),
                    ("null", "null"),
                    ("1234", "1234"),
                    ("LOGIN", "ROW")
                ]
            }

    @pytest.mark.parametrize(
        "param", Parameters(data)
        )
    def test_start(self, param):
        super().test_start(param)

    config = (
        Config("获取短信验证码")
        .base_url("${ENV(BASE_URL)}")
        .verify(False)
    )
    teststeps = [
        Step(
            RunTestCase("获取短信验证码")
            .with_variables(**{
                "telephoneNo": "$telephoneNo",
                "sceneEnum": "$sceneEnum",
                "type": "1",
                "status": True,
            })
            .call(testcase=AppMemberController.AppSendSmsCode)

        ),
    ]


# 登陆手机号与发送验证码手机号不一致，登陆失败
class TestCaseUser002(HttpRunner):
    """
    陆手机号与发送验证码手机号不一致，登陆失败
    """
    config = (
        Config("陆手机号与发送验证码手机号不一致，登陆失败")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "latitude": "12.67364",
            "longitude": "15.4792",
            "type": 1,
            "zoneCode": "62"
        })
        .verify(False)
    )

    teststeps = [
        Step(
            RunTestCase("发送登陆验证码")
            .with_variables(**{
                "telephoneNo": "841993082110",
                "sceneEnum": "LOGIN"
            })
            .call(testcase=AppMemberController.AppSendSmsCode)
            .export("smsCode")
        ),
        Step(
            RunRequest("使用其他手机号登陆失败")
            .with_variables(**{
                "telephoneNo": "841993082102",
                "smsCode": "${smsCode}",
            })
            .post("/quark-loan-member/app/member/login-by-sms")
            .with_headers(**{
                "Content-Type": "${ENV(ConnectType)}",
                "appInfoId": "${ENV(appInfoId)}",
                "appVersion": "${ENV(appVersion)}",
                "deviceId": "${ENV(deviceId)}",
                "platform": "${ENV(platform)}",
                "langType": "${ENV(LangType)}",
            })
            .with_json(
                {
                    "latitude": "${latitude}",
                    "longitude": "${longitude}",
                    "smsCode": "${smsCode}",
                    "telephoneNo": "${telephoneNo}",
                    "zoneCode": "${zoneCode}"
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal('headers."Content-Type"', "application/json")
            .assert_contains("body", "errMsg")
            .assert_contains("body", "errCode")
            .assert_equal("body.success", False)
            .assert_contains("body.errMsg", "Kode verifikasi telah kedaluwarsa")
        ),
    ]


class TestCaseUser00(HttpRunner):
    """
    陆手机号与发送验证码手机号不一致，登陆失败
    """
    config = (
        Config("登陆手机号与发送验证码手机号不一致，登陆失败")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "latitude": "12.67364",
            "longitude": "15.4792",
            "type": 1,
            "zoneCode": "62",
            "telephoneNo": "08211234568",
            "sceneEnum": "LOGIN",
        })
        .verify(False)
    )

    teststeps = [
        Step(
            RunTestCase("发送验证码")
            .with_variables(**{
                "assert_list": {
                    "equal": [{"jmes": "body.success", "respkey": 0}, "${test_pymysql()}"],
                    "equal": [{"jmes": 'headers."Content-Type"', "respkey": 0}, "application/json"],
                }
            })
            .call(AppMemberController.AppSendSmsCode)
            .teardown_hook("${call_assert($assert_list)}")
        ),
        Step(
            RunTestCase("验证码登录")
            .with_variables(**{
                "smsCode": "${get_resp_list_value(body.data,0)}"
            })
            .call(AppMemberController.AppLoginBySms)
            .teardown_hook("${removeRespList()}")
        )
    ]


# 登陆手机号与发送验证码手机号一致，登陆成功
class TestCaseUser003(HttpRunner):
    """
    登陆手机号与发送验证码手机号一致，登陆成功
    """
    config = (
        Config("登陆手机号与发送验证码手机号一致，登陆成功")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "latitude": "12.67364",
            "longitude": "15.4792",
            "telephoneNo": "841993082111",
            "sceneEnum": "LOGIN",
            "type": "1"
        })
        .verify(False)
    )

    teststeps = [
        Step(
            RunTestCase("验证码登陆成功")
            .with_variables(**{
                "status": True
            })
            .call(testcase=QuarkLoanOperationFlow.GetUserToken)
            .export("smsCode")
        ),
    ]


# 未注册用户通过验证码登陆，自动注册并登陆成功
class TestCaseUser004(HttpRunner):
    """
    未注册用户通过验证码登陆，自动注册并登陆成功
    """
    config = (
        Config("未注册用户通过验证码登陆，自动注册并登陆成功")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "latitude": "12.67364",
            "longitude": "15.4792",
            "telephoneNo": "841993082802",
            "sceneEnum": "LOGIN",
            "type": "1",
            "status": True,
        })
        .verify(False)
    )

    teststeps = [
        Step(
            RunTestCase("发送注册验证码")
            .call(testcase=AppMemberController.AppSendSmsCode)
            .export("smsCode")
        ),
        Step(
            RunTestCase("通过验证码登陆，自动注册并登陆成功")
            .with_variables(**{
                "smsCode": "${smsCode}",
            })
            .call(testcase=AppMemberController.AppLoginBySms)
        ),
    ]


# 用户通过密码登陆成功
class TestCaseUser005(HttpRunner):
    """
    用户通过密码登陆测试
    """
    config = (
        Config("用户通过密码登陆成功")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "latitude": "12.1854810",
            "longitude": "27.1811185",
            "status": True
        })
        .verify(False)
    )

    teststeps = [
        Step(
            RunTestCase("用户通过密码登陆测试案例组")
            .with_variables(**{
                "telephoneNo": "841993082893",
                "password": "222222",
                "zoneCode": "62",
            })
            .call(testcase=AppMemberController.AppLoginByPassword)
        ),
    ]


# 用户修改密码成功
class TestCaseUser006(HttpRunner):
    """
    用户设置密码成功
    """
    config = (
        Config("用户设置密码成功")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "latitude": "12.67364",
            "longitude": "15.4792",
            "password": "222222",
            "zoneCode": "62",
            "type": "1",
            "status": True
        })
        .verify(False)
    )

    teststeps = [
        Step(
            RunTestCase("用户登陆获取token")
            .call(testcase=QuarkLoanOperationFlow.GetUserToken)
            .export("accessToken")
        ),
        Step(
            RunTestCase("获取修改密码验证码")
            .with_variables(**{
                "sceneEnum": "CHANGE_PWD",
            })
            .call(testcase=AppMemberController.AppSendSmsCode)
            .export("smsCode")
        ),
        Step(
            RunTestCase("修改密码")
            .call(testcase=AppMemberController.AppChangePassword)
        ),
    ]


# 非修改密码类型验证码LOGIN，用户设置密码失败
class TestCaseUser007(HttpRunner):
    """
    用户设置密码成功
    """

    config = (
        Config("用户设置密码成功")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "latitude": "12.67364",
            "longitude": "15.4792",
            "telephoneNo": "84199308211",
            "password": "654321",
            "type": "1",
            "status": True,
        })
        .verify(False)
    )

    teststeps = [
        Step(
            RunTestCase("用户登陆获取token")
            .call(testcase=QuarkLoanOperationFlow.GetUserToken)
            .export("accessToken")
        ),
        Step(
            RunTestCase("获取错误类型验证码")
            .with_variables(**{
                "sceneEnum": "LOGIN",
            })
            .call(testcase=AppMemberController.AppSendSmsCode)
            .export("smsCode")
        ),
        Step(
            RunRequest("修改登陆密码失败")
            .post("/quark-loan-member/app/member/change-password")
            .with_headers(**{
                "Content-Type": "${ENV(ConnectType)}",
                "appInfoId": "${ENV(appInfoId)}",
                "appVersion": "${ENV(appVersion)}",
                "deviceId": "${ENV(deviceId)}",
                "platform": "${ENV(platform)}",
                "langType": "${ENV(LangType)}",
                "accessToken": "${accessToken}"
            }
                              )
            .with_json(
                {
                    "password": "${password}}",
                    "smsCode": "${smsCode}"
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal('headers."Content-Type"', "application/json")
            .assert_equal("body.success", False)
            .assert_contains("body.errCode", "MB2000000")
            .assert_contains("body.errMsg", "The SMS verification code")

        )
    ]


# 非修改密码类型验证码REGISTER，用户设置密码失败
class TestCaseUser008(HttpRunner):
    """
    非修改密码类型验证码REGISTER，用户设置密码失败
    """

    config = (
        Config("非修改密码类型验证码REGISTER，用户设置密码失败")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "telephoneNo": "84199308211",
            "password": "654321",
            "type": "1",
            "status": True,
        })
        .verify(False)
    )

    teststeps = [
        Step(
            RunTestCase("用户登陆获取token")
            .call(testcase=QuarkLoanOperationFlow.GetUserToken)
            .export("accessToken")
        ),
        Step(
            RunTestCase("获取错误类型验证码")
            .with_variables(**{
                "sceneEnum": "REGISTER",
            })
            .call(testcase=AppMemberController.AppSendSmsCode)
            .export("smsCode")
        ),
        Step(
            RunRequest("修改登陆密码失败")
            .post("/quark-loan-member/app/member/change-password")
            .with_headers(**{
                "Content-Type": "${ENV(ConnectType)}",
                "appInfoId": "${ENV(appInfoId)}",
                "appVersion": "${ENV(appVersion)}",
                "deviceId": "${ENV(deviceId)}",
                "platform": "${ENV(platform)}",
                "langType": "${ENV(LangType)}",
                "accessToken": "${accessToken}"
            }
                              )
            .with_json(
                {
                    "password": "${password}}",
                    "smsCode": "${smsCode}"
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal('headers."Content-Type"', "application/json")
            .assert_equal("body.success", False)
            .assert_contains("body.errCode", "MB2000000")
            .assert_contains("body.errMsg", "The SMS verification code")

        )
    ]


# 密码注册接口测试案例组
class TestCaseUser009(HttpRunner):
    """
    新用户使用密码注册
    """
    config = (
        Config("新用户使用密码注册成功")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "latitude": "12.67364",
            "longitude": "15.4792",
            "telephoneNo": "08211234560",
            "password": "222222",
            "zoneCode": "62",
            "type": "1",
            "status": True,
            "fcmKey": "",
        })
        .verify(False)
    )

    teststeps = [
        Step(
            RunTestCase("获取注册验证码")
            .with_variables(**{
                "sceneEnum": "REGISTER",
            })
            .call(testcase=AppMemberController.AppSendSmsCode)
            .export("smsCode")
        ),
        Step(
            RunRequest("新用户使用密码注册成功")
            .post("/quark-loan-member/app/member/register-with-password")
            .with_headers(**{
                "Content-Type": "${ENV(ConnectType)}",
                "appInfoId": "${ENV(appInfoId)}",
                "appVersion": "${ENV(appVersion)}",
                "deviceId": "${ENV(deviceId)}",
                "platform": "${ENV(platform)}",
                "langType": "${ENV(LangType)}",
            }
                              )
            .with_json(
                {
                    "zoneCode": "${zoneCode}",
                    "fcmKey": "${fcmKey}",
                    "latitude": "${latitude}",
                    "longitude": "${longitude}",
                    "password": "${password}",
                    "telephoneNo": "${telephoneNo}",
                    "smsCode": "${smsCode}"
                }
            )
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal('headers."Content-Type"', "application/json")
            .assert_equal("body.success", True)
        )

    ]


# 流程
class TestCaseUser(HttpRunner):
    config = (
        Config("基本信息填写流程")
        .verify(False)
    )

    teststeps = [
        # Step(
        #     RunTestCase("验证码登陆成功")
        #     .with_variables(**{
        #         "telephoneNo": "841993082415",
        #         "password": "222222",
        #         "zoneCode": "62",
        #         "latitude": "12.1854810",
        #         "longitude": "27.1811185",
        #         "status": True
        #     })
        #     .call(testcase=QuarkLoanOperationFlow.GetUserToken)
        #     .export("accessToken")
        # ),
        # Step(
        #     RunTestCase("用户需还款信息")
        #     .call(AppAssetRepay.AppRepayToRepayInfo)
        # ),
        # Step(
        #     RunTestCase("用户借款记录")
        #     .call(AppAsset.AppAssetCustomerAssets)
        #     .export("assetNo")
        # ),
        # Step(
        #     RunTestCase("用户借款详情")
        #     .call(AppAsset.AppAssetPaydayLoanQuery)
        # ),
        Step(
            RunTestCase("用户放款回调")
            # .with_variables(**{
            #     "payProxyTransactionId": "aa978074439f4d289ce5f7bb97eb0633",
            #     "transactionId": "284da9f391a9459e93539a892e010520",
            #     "withdrawalTime": "2022-06-18 14:00:00"
            # })
            .call(QuarkLoanPay.instamoneyPayCallback)
        ),
        # Step(
        #     RunTestCase("用户还款")
        #     .with_variables(**{
        #             "amount": 1700,
        #             "bankCode": "BT"
        #         })
        #     .call(AppAssetRepay.AppRepayUserRepay)
        #     .export("repaymentOrderNo")
        # ),
        # Step(
        #     RunTestCase("用户还款回调")
        #     .with_variables(**{
        #         "repaymentOrderNo": "${repaymentOrderNo}",
        #         "withholdAmount": 17-00,
        #         "repaymentSuccessTime": "2022-06-13 14:34:09",
        #         "repayTransactionNo": "123456789",
        #     })
        #     .call(AppAssetRepay.AppRepayRepayMentNotify)
        # ),
        # Step(
        #     RunTestCase("用户需还款信息")
        #     .call(AppAssetRepay.AppRepayToRepayInfo)
        # ),
        # Step(
        #     RunTestCase("风控机审回调")
        #     .with_variables(**{
        #         "reqNo": "risk2022071109592982633000",
        #         "resultType": 3
        #     })
        #     .call(QuarkLoanRisk.riskCallback)
        # ),
        # Step(
        #     RunTestCase("风控机审")
        #     .with_variables(**{
        #         "reqNo": "risk2022071109592982633000",
        #         "resultType": 3
        #     })
        #     .call(QuarkLoanRisk.executeAudit)
        # ),
        # Step(
        #     RunTestCase("用户是否注册")
        #     .with_variables(**{
        #         "telephoneNo": "841993082891",
        #     })
        #     .call(AppMemberController.AppCheckRegisterStatus)
        # )
        # Step(
        #     RunTestCase("修改放款时间")
        #     .with_variables(**{
        #         "type": 1,
        #         "sceneEnum": "CHANGE_PWD",
        #         "telephoneNo": "841993082441",
        #         "password": "222222",
        #         "zoneCode": "62",
        #         "latitude": "12.1854810",
        #         "longitude": "27.1811185",
        #     })
        #     .call(AppMemberController.AppSendSmsCode)
        # ),
        # Step(
        #     RunTestCase("修改放款时间")
        #     .with_variables(**{
        #         "type": 1,
        #         "sceneEnum": "CHANGE_PWD",
        #         "telephoneNo": "841993082441",
        #         "password": "222222",
        #         "zoneCode": "62",
        #         "latitude": "12.1854810",
        #         "longitude": "27.1811185",
        #     })
        #     .call(AppMemberController.AppChangePassword)
        # )

    ]


if __name__ == '__main__':
    pytest.main(["-v", "./LoanMemberTest.py"])

