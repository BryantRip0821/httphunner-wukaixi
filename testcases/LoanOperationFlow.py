#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : get_sms_to_login.py
# @Author: Wu
# @Date  : 2022/3/24
# @Desc  :
import pytest
from httprunner import HttpRunner, RunTestCase, Config, Step, Parameters, RunRequest, testcase
from api.QuarkLoanMember import (AppMemberController, AppMemberBasisInfoController, AppMemberCertificateInfoController, AppMemberContactInfoController, AppMemberBankInfoController, AppMemberCompanyInfoController)
from api.QuarkLoanExamine import (AppExamineProduct, AppExamineApplication)


# 发送登陆验证码，通过验证码登陆后获取token
class GetUserToken(HttpRunner):
    """
    登陆手机号与发送验证码手机号一致，登陆成功
    """
    config = (
        Config("登陆手机号与发送验证码手机号一致，登陆成功")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "latitude": "12.67364",
            "longitude": "15.4792",
            "telephoneNo": "${telephoneNo}",
            "sceneEnum": "LOGIN",
            "type": 1,
            "zoneCode": "62"
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
            RunTestCase("验证码登陆成功")
            .with_variables(**{
                "smsCode": "${smsCode}",
            })
            .call(testcase=AppMemberController.AppLoginBySms)
            .export("accessToken")
        ),
    ]


# 密码注册接口测试案例组
class SetUserForPassword(HttpRunner):
    """
    新用户使用密码注册
    """
    config = (
        Config("新用户使用密码注册成功")
        .base_url("${ENV(BASE_URL)}")
        .variables(**{
            "latitude": "12.67364",
            "longitude": "15.4792",
            "telephoneNo": "199308213",
            "password": "222222",
            "zoneCode": "84",
            "type": "1",
            "status": True,
            "fcmKey": "",
        })
        .verify(False)
        .export(*["accessToken"])
    )

    teststeps = [
        Step(
            RunTestCase("获取注册验证码")
            .with_variables(**{
                "sceneCode": "REGISTER",
            })
            .call(testcase=AppMemberController.AppSendSmsCode)
            .export("smsCode")
        ),
        Step(
            RunRequest("新用户使用密码注册成功")
            .post("/app/member/register-with-password")
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
            .extract()
            .with_jmespath("body.data.accessToken", "accessToken")
            .validate()
            .assert_equal("status_code", 200)
            .assert_equal('headers."Content-Type"', "application/json")
            .assert_equal("body.success", True)
        )

    ]


# 创建用户并填写资料完成
class CreateUser(HttpRunner):
    config = (
        Config("创建用户")
        .verify(False)
    )

    teststeps = [
        Step(
            RunTestCase("保存个人信息")
            .call(AppMemberBasisInfoController.AppBasisInfoSave)
        ),
        Step(
            RunTestCase("上传证件照")
            .with_variables(**{
                "filename": "data/file.jpg",
                "type": 1
            })
            .call(testcase=AppMemberCertificateInfoController.AppCertificateInfoUpload)
            .export(*["attachmentInfos"])
        ),
        Step(
            RunTestCase("上传证件照")
            .with_variables(**{
                "filename": "data/file.jpg",
                "type": 2
            })
            .call(testcase=AppMemberCertificateInfoController.AppCertificateInfoUpload)
        ),
        Step(
            RunTestCase("保存证件信息")
            .with_variables(**{
                "attachmentInfos": "${attachmentInfos}",
                "firstName": "",
                "middleName": "",
                "lastName": "",
                "fatherName": "",
                "motherName": "motherName",
                "birthday": "2022-06-28",
                "certificateNo": "FakeId108360582053900",
                "name": "testName",
                "sex": "F"
                 }
                    )
            .call(testcase=AppMemberCertificateInfoController.AppCertificateInfoSave)
        ),
        Step(
            RunTestCase("保存工作信息")
            .call(AppMemberCompanyInfoController.AppCompanyInfoSave)
        ),
        Step(
            RunTestCase("保存联系人信息")
            .call(AppMemberContactInfoController.AppContactInfoSave)
        ),
        Step(
            RunTestCase("银行卡")
            .with_variables(**{
                "bankCode": "BCA",
                "bankName": "Bank BCA                                           ",
                "bankNumber": "123456789",
            })
            .call(AppMemberBankInfoController.AppBankInfoSave)
        ),
    ]


# 提交申请
class CreateApplication(HttpRunner):
    config = (
        Config("创建申请单")
        .variables(**{
            "list": 0
        })
        .verify(False)
    )
    teststeps = [
        Step(
            RunTestCase("获取步骤信息")
            .call(AppMemberController.AppLoadSubmitInfoSteps)
        ),
        Step(
            RunTestCase("获取授信额度")
            .call(AppExamineProduct.AppProductCreditLine)
        ),
        Step(
            RunTestCase("获取可借贷产品")
            .call(AppExamineProduct.AppProductLoanableProduct)
            .export(*["loanProductId", "stage", "period", "maxAmount"])
        ),
        Step(
            RunTestCase("费用试算")
            .with_variables(
                **{
                    "bankCode": "BCA"
                }
            )
            .call(AppExamineProduct.AppProductTrialCalculation)
        ),
        Step(
            RunTestCase("检查是否可以申请")
            .call(AppExamineApplication.AppExamineApplicationCheck)
        ),
        Step(
            RunTestCase("上传活体照片")
            .with_variables(**{
                "base_photo": "${setup_hook_get_base64()}"
            })
            .call(testcase=AppMemberController.AppUploadLivingBase64Photo)
        ),
        Step(
            RunTestCase("提交申请单")
            .call(AppExamineApplication.AppExamineApplicationSave)
        ),
    ]


class Test(HttpRunner):
    # @pytest.mark.parametrize(
    #     "param", Parameters(
    #         {
    #             "telephoneNo":
    #                 [
    #                     "841993082203",
    #                     "841993082204",
    #                     "841993082205",
    #                     "841993082206",
    #                     "841993082207",
    #                     "841993082208",
    #                     "841993082209"
    #                 ]
    #         }
    #     )
    # )
    # def test_start(self, param):
    #     super().test_start(param)

    config = (
        Config("注册用户并申请贷款")
        .verify(False)
        .variables(
            **{
               "telephoneNo": "199308288"
            }
        )
    )
    teststeps = [
        Step(
            RunTestCase("token")
            .call(testcase=SetUserForPassword)
            .export("accessToken")
        ),
        Step(
            RunTestCase("token")
            .call(testcase=CreateUser)
        ),
        # Step(
        #     RunTestCase("token")
        #     .call(testcase=CreateApplication)
        # )
    ]


if __name__ == '__main__':
    Test().test_start()
