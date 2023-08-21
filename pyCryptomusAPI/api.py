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
            if not(key):
                raise pyCryptomusAPIException(-6, "Key is empty")
            if not(key.isascii()):
                raise pyCryptomusAPIException(-6, "Key contains non-ascii characters")
            if not(self.merchant_uuid):
                raise pyCryptomusAPIException(-6, "Merchant UUID is empty")
            if not(self.merchant_uuid.isascii()):
                raise pyCryptomusAPIException(-6, "Merchant UUID contains non-ascii characters")
            json_dumps = json.dumps(data)
            # json_dumps = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            pre_sign = json_dumps if data else ""
            if pre_sign and not(pre_sign.isascii()):
                raise pyCryptomusAPIException(-6, "Data dump contains non-ascii characters")
            sign = md5(base64.b64encode(pre_sign.encode('ascii')) + key.encode('ascii')).hexdigest()
            headers = {
                "merchant": self.merchant_uuid,
                "sign": sign,
                "Content-Type": "application/json",
            }
            base_resp = requests.post(API_URL + method_url, data=pre_sign, headers=headers, timeout=self.timeout)
            resp = base_resp.json()
        except ValueError as ve:
            code = base_resp.status_code if base_resp else -2
            message = "Response decode failed: {}".format(ve)
            if self.print_errors:
                print(message)
            raise pyCryptomusAPIException(code, message)
        except pyCryptomusAPIException as pe:
            raise pe
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
           amount, currency, order_id, network = None,
           url_return = None, url_success = None, url_callback = None,
           is_payment_multiple = None, lifetime = None, to_currency = None, subtract = None,
           accuracy_payment_percent = None, additional_data = None, currencies = None,
           except_currencies = None, course_source = None, from_referral_code = None,
           discount_percent = None, is_refresh = None):
        """
        Creating an invoice
        https://doc.cryptomus.com/payments/creating-invoice
        Requires PAYMENT API key

        amount: (Float) Amount to be paid. If there are pennies in the amount, then send them with a separator '.' Example: 10.28
        currency: (String) Currency code (https://doc.cryptomus.com/reference)
        order_id: (String[1..128]) Order ID in your system. The parameter should be a string consisting of alphabetic characters, numbers, underscores, and dashes. It should not contain any spaces or special characters.
        network: (String, Optional) Blockchain network code (https://doc.cryptomus.com/reference)
        url_return: (String[6..255], Optional) Before paying, the user can click on the button on the payment form and return to the store page at this URL.
        url_success: (String[6..255], Optional) After successful payment, the user can click on the button on the payment form and return to this URL.
        url_callback: (String[6..255], Optional) Url to which webhooks with payment status will be sent.
        is_payment_multiple: (Bool, Optional) Whether the user is allowed to pay the remaining amount. This is useful when the user has not paid the entire amount of the invoice for one transaction, and you want to allow him to pay up to the full amount. If you disable this feature, the invoice will finalize after receiving the first payment and you will receive funds to your balance.
        lifetime: (Int[300..43200], Optional) The lifespan of the issued invoice (?in seconds?)
        to_currency: (String, Optional) The parameter is used to specify the target currency for converting the invoice amount. When creating an invoice, you provide an amount and currency, and the API will convert that amount to the equivalent value in the to_currency. For example, to create an invoice for 20 USD in bitcoin: amount: 20, currency: USD, to_currency: BTC. The API will convert 20 USD amount to its equivalent in BTC based on the current exchange rate and the user will pay in BTC.
        subtract: (Int[0..100], Optional) Percentage of the payment commission charged to the client. If you have a rate of 1%, then if you create an invoice for 100 USDT with subtract = 100 (the client pays 100% commission), the client will have to pay 101 USDT.
        accuracy_payment_percent: (Float[0..5], Optional) Acceptable inaccuracy in payment. For example, if you pass the value 5, the invoice will be marked as Paid even if the client has paid only 95% of the amount. The actual payment amount will be credited to the balance.
        additional_data: (?String?, Optional) Additional information for you (not shown to the client).
        currencies: (List[Currency][1..255], Optional) List of allowed currencies for payment. This is useful if you want to limit the list of coins that your customers can use to pay invoices.
        except_currencies: (List[Currency], Optional) List of excluded currencies for payment.
        course_source: (String[4..20], Optional) The service from which the exchange rates are taken for conversion in the invoice. If not passed, Cryptomus exchange rates are used. Available values: https://doc.cryptomus.com/payments/creating-invoice
        from_referral_code: (String, Optional) The merchant who makes the request connects to a referrer by code. For example, you are an application that generates invoices via the Cryptomus API and your customers are other stores. They enter their api key and merchant id in your application, and you send requests with their credentials and passing your referral code. Thus, your clients become referrals on your Cryptomus account and you will receive income from their turnover.
        discount_percent: (Int[-99..100], Optional) Positive numbers: allows you to set a discount. To set a 5% discount for the payment, you should pass a value: 5. Negative numbers: allows you to set custom additional commission. To set an additional commission of 10% for the payment, you should pass a value: -10.
        is_refresh: (Bool, Optional) Using this parameter, you can update the lifetime and get a new address for the invoice if the lifetime has expired. To do that, you need to pass all required parameters, and the invoice with passed order_id will be refreshed.

         * The order_id must be unique within the merchant invoices/static wallets/recurrence payments
         * When we find an existing invoice with order_id, we return its details, a new invoice will not be created.
         * The to_currency should always be the cryptocurrency code, not a fiat currency code.
         * The discount percentage when creating an invoice is taken into account only if the invoice has a specific cryptocurrency.
         * Only address, payment_status and expired_at are changed. No other fields are changed, regardless of the parameters passed.
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
        if url_success:
            params["url_success"] = url_success
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
        if course_source:
            params["course_source"] = course_source
        if from_referral_code:
            params["from_referral_code"] = from_referral_code
        if discount_percent is not None:
            params["discount_percent"] = str(discount_percent)
        if is_refresh is not None:
            params["is_refresh"] = is_refresh
        resp = self.__request(method, 1, **params).get("result")
        return Invoice.de_json(resp)

    def create_wallet(self,
           network, currency, order_id, url_callback = None, from_referral_code = None):
        """
        Creating a Static wallet
        https://doc.cryptomus.com/payments/creating-static
        Requires PAYMENT API key

        network: (String) Blockchain network code (https://doc.cryptomus.com/reference)
        currency: (String) Currency code (https://doc.cryptomus.com/reference)
        order_id: (String[1..100]) Order ID in your system. The parameter should be a string consisting of alphabetic characters, numbers, underscores, and dashes. It should not contain any spaces or special characters.
        url_callback: (String[6..255], Optional) URL, to which the webhook will be sent after each top-up of the wallet.
        from_referral_code: (String, Optional) The merchant who makes the request connects to a referrer by code. For example, you are an application that generates invoices via the Cryptomus API and your customers are other stores. They enter their api key and merchant id in your application, and you send requests with their credentials and passing your referral code. Thus, your clients become referrals on your Cryptomus account and you will receive income from their turnover.

        * The order_id must be unique within the merchant invoices/static wallets/recurrence payments
        * When we find an existing invoice with order_id, we return its details, a new invoice will not be created.
        """
        method = "wallet"
        params = {
            "network": network,
            "currency": currency,
            "order_id": str(order_id),
        }
        if url_callback:
            params["url_callback"] = url_callback
        if from_referral_code:
            params["from_referral_code"] = from_referral_code
        resp = self.__request(method, 1, **params).get("result")
        return Wallet.de_json(resp)

    def block_wallet(self,
           wallet_uuid = None, order_id = None, is_force_refund = None):
        """
        Block static wallet
        https://doc.cryptomus.com/payments/block-wallet
        You need to pass one of the required parameters, if you pass both, the account will be identified by order_id
        Requires PAYMENT API key

        wallet_uuid: (String, Optional if order_id set) UUID of a static wallet
        order_id: (String[1..32], Optional if wallet_uuid set) Order ID of a static wallet
        is_force_refund: (Bool, Optional) Refund all incoming payments to sender’s address

        * You need to pass one of the required parameters, if you pass both, the account will be identified by order_id
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

        address: (String[10..128]) Refund all blocked funds to this address
        wallet_uuid: (String, Optional if order_id set) UUID of a static wallet
        order_id: (String[1..32], Optional if wallet_uuid set) Order ID of a static wallet

        * To refund payments you need to pass either uuid or order_id, if you pass both, the static wallet will be identified by uuid
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
        order_id: (String[1..128], Optional if wallet_uuid set) Invoice order ID

        * To get the invoice status you need to pass one of the required parameters, if you pass both, the account will be identified by order_id
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

        address: (String) The address to which the refund should be made
        is_subtract: (Bool) Whether to take a commission from the merchant's balance or from the refund amount. true - take the commission from merchant balance. false - reduce the refundable amount by the commission amount
        invoice_uuid: (String, Optional if order_id set) Invoice UUID
        order_id: (String[1..128], Optional if invoice_uuid set) Invoice order ID

        * Invoice is identified by order_id or uuid, if you pass both, the account will be identified by uuid
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

    def payment_history(self, date_from = None, date_to = None, cursor = None):
        """
        Payment history
        https://doc.cryptomus.com/payments/payment-history
        Requires PAYMENT API key

        date_from: (String, Optional) Filtering by creation date, from
        date_to: (String, Optional) Filtering by creation date, to
        cursor: (String, Optional) Page cursor (hash)
        """
        params = {
        }
        if date_from:
            params["date_from"] = date_from.strftime(CryptomusDateFormat)
        if date_to:
            params["date_to"] = date_to.strftime(CryptomusDateFormat)
        if cursor:
            params["cursor"] = cursor
        method = "payment/list"
        if params:
            resp = self.__request(method, 1, **params).get("result")
        else:
            resp = self.__request(method, 1).get("result")
        return PaymentsHistory.de_json(resp)

    def payment_history_filtered(
            self,
            date_from = None, date_to = None,
            max_results = 15, max_pages = 10,
            currencies = None, networks = None, addresses = None,
            statuses = None, is_final = None, page_delay = 1):
        """
        Payment history (advanced mode)

        Based on: payment_history
        https://doc.cryptomus.com/payments/payment-history
        Requires PAYMENT API key

        Collects only results under filters.
        Process as many pages as needed to collect max_results, but not more than max_pages.

        date_from: (String, Optional) Filtering by creation date, from
        date_to: (String, Optional) Filtering by creation date, to
        max_results: (Int, Optional, default=15) Max number of results to collect
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
            if page_number > 0: sleep(page_delay)
            resp = self.payment_history(date_from = date_from, date_to = date_to, cursor = cursor)

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
