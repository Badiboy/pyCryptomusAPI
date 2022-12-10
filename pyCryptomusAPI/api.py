import json
from hashlib import md5
import base64
import requests

from .cryto_types import *

API_URL = "https://api.cryptomus.com/v1/"


# noinspection PyPep8Naming
class pyCryptomusAPIException(Exception):
    def __init__(self, code, message, full_error = ""):
        self.code = code
        self.message = message
        self.full_error = full_error
        super().__init__(self.message)


# noinspection PyPep8Naming
class pyCryptomusAPI:
    """
    Cryptomus API Client
    """

    def __init__(self,
                 merchant_uuid, payment_api_key = None, payout_api_key = None,
                 print_errors = False, timeout = None):
        """
        Create the pyCryptomusAPI instance.

        :param merchant_uuid: The merchant's uuid, which you can find in the merchant's personal account in the settings section.
        :param payment_api_key: API key for processing payments
        :param payout_api_key: API key for accepting payment and making payouts
        :param print_errors: (Optional) Print dumps on request errors
        :param timeout: (Optional) Request timeout
        """
        self.merchant_uuid = merchant_uuid
        self.payment_api_key = payment_api_key
        self.payout_api_key = payout_api_key
        self.print_errors = print_errors
        self.timeout = timeout
        if not(self.payment_api_key) and not(self.payout_api_key):
            raise Exception("You must specify at least one API key.")

    def __request(self, method_url, mode, **kwargs):
        """
        Send request to API

        :param method_url: (String) API method url (part)
        :param mode: (Int) Method mode (1: payment, 2: payout)
        :param kwargs: request data
        """
        if kwargs:
            data = dict(kwargs)
        else:
            data = {}

        base_resp = None
        try:
            key = self.payment_api_key if (mode == 1) else self.payout_api_key
            json_dumps = json.dumps(data)
            # json_dumps = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            pre_sign = json_dumps if data else ""
            sign = md5(base64.b64encode(pre_sign.encode('ascii')) + key.encode('ascii')).hexdigest()
            # sign = md5(base64.encodebytes(pre_sign.encode('utf-8')) + key.encode('utf-8')).hexdigest()
            headers = {
                "merchant": self.merchant_uuid,
                "sign": sign,
                "Content-Type": "application/json",
            }
            # resp = requests.post(ENDPOINT + url, data=data, headers=headers, timeout=self.timeout).json()
            base_resp = requests.post(API_URL + method_url, data=pre_sign, headers=headers, timeout=self.timeout)
            resp = base_resp.json()
        except ValueError as ve:
            code = base_resp.status_code if base_resp else -2
            message = "Response decode failed: {}".format(ve)
            if self.print_errors:
                print(message)
            raise pyCryptomusAPIException(code, message)
        except Exception as e:
            code = base_resp.status_code if base_resp else -3
            message = "Request unknown exception: {}".format(e)
            if self.print_errors:
                print(message)
            raise pyCryptomusAPIException(code, message)
        if not resp:
            code = base_resp.status_code if base_resp else -4
            message = "None request response"
            if self.print_errors:
                print(message)
            raise pyCryptomusAPIException(code, message)
        elif not resp.get("result"):
            code = base_resp.status_code if base_resp else -5
            message = resp.get("message") if resp.get("message") else "No error info provided"
            if self.print_errors:
                print("Response: {}".format(resp))
            raise pyCryptomusAPIException(code, message)
        else:
            return resp

    def balance(self):
        """
        Get balance of merchant(account) or user(wallet)
        https://doc.cryptomus.com/balance
        Requires PAYMENT API key
        """
        method = "balance"
        resp = self.__request(method, 1).get("result")
        return Balance.de_json(resp[0])

    def payment_services(self):
        """
        Get collection of all available payment services
        https://doc.cryptomus.com/payments/list-of-services
        Requires PAYMENT API key
        """
        method = "payment/services"
        resp = self.__request(method, 1).get("result")
        return [Service.de_json(i) for i in resp]

    def payout_services(self):
        """
        Get collection of all available payout services
        https://doc.cryptomus.com/payouts/list-of-services
        Requires PAYMOUT API key
        """
        method = "payout/services"
        resp = self.__request(method, 2).get("result")
        return [Service.de_json(i) for i in resp]
