from hashlib import md5
from time import sleep
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
                 print_errors = False, timeout = None, add_request_params = None):
        """
        Create the pyCryptomusAPI instance.

        :param merchant_uuid: The merchant's uuid, which you can find in the merchant's personal account in the settings section.
        :param payment_api_key: API key for processing payments
        :param payout_api_key: API key for accepting payment and making payouts
        :param print_errors: (Optional) Print dumps on request errors
        :param timeout: (Optional) Request timeout
        :param add_request_params: (List, Optional) Additional request parameters to pass with API calls
        """
        self.merchant_uuid = merchant_uuid
        self.payment_api_key = payment_api_key
        self.payout_api_key = payout_api_key
        self.print_errors = print_errors
        self.timeout = timeout
        self.add_request_params = add_request_params
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

        if self.add_request_params:
            data.update(self.add_request_params)

        base_resp = None
        try:
            key = self.payment_api_key if (mode == 1) else self.payout_api_key
            if key and not(key.isascii()):
                raise pyCryptomusAPIException(-6, "Key contains non-ascii characters")
            json_dumps = json.dumps(data)
            # json_dumps = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            pre_sign = json_dumps if data else ""
            if pre_sign and not(pre_sign.isascii()):
                raise pyCryptomusAPIException(-6, "Data dump contains non-ascii characters")
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
            if resp.get("message"):
                message = resp["message"]
            elif resp.get("errors"):
                message = resp["errors"]
            else:
                message = "No error info provided"
            if self.print_errors:
                print("Response: {}".format(resp))
            raise pyCryptomusAPIException(code, message)
        # code -6 is used above
        else:
            return resp

    def create_invoice(self,
           amount, currency, order_id, network = None, url_return = None, url_callback = None,
           is_payment_multiple = None, lifetime = None, to_currency = None, subtract = None,
           accuracy_payment_percent = None, additional_data = None, currencies = None,
           except_currencies = None):
        """
        Creating an invoice
        https://doc.cryptomus.com/payments/creating-invoice
        Requires PAYMENT API key

        amount: (Float) The amount of the invoice
        currency: (String) Currency code (https://doc.cryptomus.com/reference)
        order_id: (String) Order ID in your system
        network: (String, Optional) Blockchain network code (https://doc.cryptomus.com/reference)
        url_return: (String, Optional) Url to which the user will return after payment
        url_callback: (String, Optional) Url to which webhooks with payment status will be sent
        is_payment_multiple: (Bool, Optional) Whether payment of the remaining amount is possible (true/false)
        lifetime: (?Int?, Optional) The lifespan of the issued invoice (?in seconds?)
        to_currency: (String, Optional) Currency code for accepting payments
        subtract: (?Float?, Optional) Percentage of the payment commission charged to the client. The subtract parameter allows you to specify what percentage of the payment acceptance will be paid by the client. If you have a payment commission 1%, then if you create an invoice for 100 USDT with subtract=100 (the client pays 100% commission), the client will have to pay 101 USDT.
        accuracy_payment_percent: (?Float?, Optional) Acceptable inaccuracy in payment (min 0, max 5.00)
        additional_data: (?String?, Optional) Additional information
        currencies: (List[Currency], Optional) List of allowed currencies for payment Structure
        except_currencies: (List[Currency], Optional) List of excluded currencies for payment Structure
        """
        method = "payment"
        params = {
            "amount": str(amount),
            "currency": currency,
            "order_id": str(order_id),
        }
        if network:
            params["network"] = network
        if url_return:
            params["url_return"] = url_return
        if url_callback:
            params["url_callback"] = url_callback
        if is_payment_multiple is not None:
            params["is_payment_multiple"] = is_payment_multiple
        if lifetime is not None:
            params["lifetime"] = str(lifetime)
        if to_currency:
            params["to_currency"] = to_currency
        if subtract is not None:
            params["subtract"] = str(subtract)
        if accuracy_payment_percent is not None:
            params["accuracy_payment_percent"] = str(accuracy_payment_percent)
        if additional_data:
            params["additional_data"] = additional_data
        if currencies:
            params["currencies"] = [i.to_dict() for i in currencies]
        if except_currencies:
            params["except_currencies"] = [i.to_dict() for i in except_currencies]
        resp = self.__request(method, 1, **params).get("result")
        return Invoice.de_json(resp)

    def create_wallet(self,
           network, currency, order_id, url_callback = None):
        """
        Creating a Static wallet
        https://doc.cryptomus.com/payments/creating-static
        Requires PAYMENT API key

        network: (String) Blockchain network code (https://doc.cryptomus.com/reference)
        currency: (String) Currency code (https://doc.cryptomus.com/reference)
        order_id: (String) Order ID in your system
        url_callback: (String, Optional) Url to which webhooks with payment status will be sent
        """
        method = "wallet"
        params = {
            "network": network,
            "currency": currency,
            "order_id": str(order_id),
        }
        if url_callback:
            params["url_callback"] = url_callback
        resp = self.__request(method, 1, **params).get("result")
        return Wallet.de_json(resp)

    def block_wallet(self,
           wallet_uuid = None, order_id = None, is_force_refund = None):
        """
        Block static wallet
        https://doc.cryptomus.com/payments/block-wallet
        You need to pass one of the required parameters, if you pass both, the account will be identified by order_id
        Requires PAYMENT API key

        wallet_uuid: (String, Optional if order_id set) Wallet UUID
        order_id: (String, Optional if wallet_uuid set) Order ID in your system
        is_force_refund: (Bool, Optional) Refund all incoming payments to sender’s address
        """
        method = "wallet/block-address"
        params = {
        }
        if not(wallet_uuid) and not(order_id):
            raise pyCryptomusAPIException(0, "You need to pass one of the required parameters")
        if wallet_uuid:
            params["uuid"] = wallet_uuid
        if order_id:
            params["order_id"] = order_id
        if is_force_refund is not None:
            params["is_force_refund"] = is_force_refund
        resp = self.__request(method, 1, **params).get("result")
        return resp

    def block_wallet_refund(self,
           address, wallet_uuid = None, order_id = None):
        """
        Refund payments on blocked address
        https://doc.cryptomus.com/payments/refundblocked
        You need to pass one of the required parameters, if you pass both, the account will be identified by order_id
        Requires PAYMENT API key

        address: (String) Address (wallet addres? refund address?)
        wallet_uuid: (String, Optional if order_id set) Wallet UUID
        order_id: (String, Optional if wallet_uuid set) Order ID in your system
        """
        method = "wallet/blocked-address-refund"
        params = {
            "address": address,
        }
        if not(wallet_uuid) and not(order_id):
            raise pyCryptomusAPIException(0, "You need to pass one of the required parameters")
        if wallet_uuid:
            params["uuid"] = wallet_uuid
        if order_id:
            params["order_id"] = order_id
        resp = self.__request(method, 1, **params).get("result")
        return resp

    def payment_information(self,
           invoice_uuid = None, order_id = None):
        """
        Payment information
        https://doc.cryptomus.com/payments/payment-information
        You need to pass one of the required parameters, if you pass both, the account will be identified by order_id
        Requires PAYMENT API key

        invoice_uuid: (String, Optional if order_id set) Invoice UUID
        order_id: (String, Optional if wallet_uuid set) Order ID in your system
        """
        method = "payment/info"
        params = {
        }
        if not(invoice_uuid) and not(order_id):
            raise pyCryptomusAPIException(0, "You need to pass one of the required parameters")
        if invoice_uuid:
            params["uuid"] = invoice_uuid
        if order_id:
            params["order_id"] = order_id
        resp = self.__request(method, 1, **params).get("result")
        return Invoice.de_json(resp)

    def refund(self,
           address, is_subtract, invoice_uuid = None, order_id = None):
        """
        Refund
        https://doc.cryptomus.com/payments/refund
        You need to pass one of the required parameters, if you pass both, the account will be identified by invoice_uuid
        Requires PAYMENT API key

        address: (String) Refund address
        is_subtract: (Bool) Determines whether the commission is to be charged to the merchant or to the client (True - to the merchant, False - to the client)
        invoice_uuid: (String, Optional if order_id set) Invoice UUID
        order_id: (String, Optional if wallet_uuid set) Order ID in your system
        """
        method = "payment/refund"
        params = {
            "address": address,
            "is_subtract": is_subtract,
        }
        if not(invoice_uuid) and not(order_id):
            raise pyCryptomusAPIException(0, "You need to pass one of the required parameters")
        if invoice_uuid:
            params["uuid"] = invoice_uuid
        if order_id:
            params["order_id"] = order_id
        resp = self.__request(method, 1, **params).get("result")
        return Invoice.de_json(resp)

    def payment_history(self, cursor = None):
        """
        Payment history
        https://doc.cryptomus.com/payments/payment-history
        Requires PAYMENT API key

        cursor: (String, Optional) Page cursor (hash)
        """
        params = {
        }
        if cursor:
            params["cursor"] = cursor
        method = "payment/list"
        if params:
            resp = self.__request(method, 1, **params).get("result")
        else:
            resp = self.__request(method, 1).get("result")
        return PaymentsHistory.de_json(resp)

    def payment_history_filtered(
            self, max_results = 15, max_pages = 10,
            currencies = None, networks = None, addresses = None,
            statuses = None, is_final = None, page_delay = 1):
        """
        Payment history (advanced mode)

        Based on: payment_history
        https://doc.cryptomus.com/payments/payment-history
        Requires PAYMENT API key

        Collects only results under filters.
        Process as many pages as needed to collect max_results, but not more than max_pages.

        max_results: (Int) Max number of results to collect
        max_pages: (Int, Optional, default=10) Max number of pages to process
        currencies: (List of Strings, Optional) List of accepted currencies. Codes: https://doc.cryptomus.com/reference
        networks: (List of Strings, Optional) List of accepted networks. Codes: https://doc.cryptomus.com/reference
        addresses: (List of Strings, Optional) List of accepted addresses
        statuses: (List of Strings, Optional) List of accepted statuses. Codes: https://doc.cryptomus.com/payments/payment-statuses
        is_final: (Bool, Optional) If True, only final payments will be collected, if False - only non-final
        page_delay: (Int, Optional, default=1) Delay between pages (in seconds)
        """

        result = PaymentsHistory()

        page_number = 0
        cursor = None
        while page_number < max_pages:
            if page_number > 0: sleep(1)
            resp = self.payment_history(cursor = cursor)

            if not resp.items:
                # No (more) payments
                break

            for payment in resp.items:
                if currencies and not(payment.currency in currencies):
                    continue
                if networks and not(payment.network in networks):
                    continue
                if addresses and not(payment.address in addresses):
                    continue
                if statuses and not(payment.status in statuses):
                    continue
                if (is_final is not None) and payment.is_final != is_final:
                    continue
                result.items.append(payment)

                if len(result.items) >= max_results:
                    # Enough results collected
                    break

            if len(result.items) >= max_results:
                # Enough results collected
                break

            cursor = resp.paginate.nextCursor
            if not cursor:
                # No more pages
                break
            page_number += 1

        return result

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

    def balance(self):
        """
        Get balance of merchant(account) or user(wallet)
        https://doc.cryptomus.com/balance
        Requires PAYMENT API key
        """
        method = "balance"
        resp = self.__request(method, 1).get("result")
        return Balance.de_json(resp[0])
