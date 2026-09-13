import json
from abc import ABC

CryptomusDateFormat = "%Y-%m-%d %H:%M:%S"

class Dictionaryable(ABC):
    """
    (c) Based on pyTelegramBotAPI (https://github.com/eternnoir/pyTelegramBotAPI) Dictionaryable
    Subclasses of this class are guaranteed to be able to be converted to dictionary.
    All subclasses of this class must override to_dict.
    """

    def to_dict(self):
        """
        Returns a DICT with class field values
        This function must be overridden by subclasses.

        :return: a DICT
        """
        raise NotImplementedError


class JsonSerializable(ABC):
    """
    (c) Based on pyTelegramBotAPI (https://github.com/eternnoir/pyTelegramBotAPI) JsonSerializable
    Subclasses of this class are guaranteed to be able to be converted to JSON format.
    All subclasses of this class must override to_json.
    """

    def to_json(self):
        """
        Returns a JSON string representation of this class.
        This function must be overridden by subclasses.

        :return: a JSON formatted string.
        """
        raise NotImplementedError


class JsonDeserializable(ABC):
    """
    (c) Based on pyTelegramBotAPI (https://github.com/eternnoir/pyTelegramBotAPI) JsonDeserializable
    Subclasses of this class are guaranteed to be able to be created from a json-style dict or json formatted string.
    All subclasses of this class must override de_json.
    """

    @classmethod
    def de_json(cls, json_dict, process_mode = 0):
        """
        Returns an instance of this class from the given json dict or string.
        This function must be overridden by subclasses.

        :param json_dict: The json dict from which to create the object.
        :param process_mode: 0 - do nothing, 1 - create class instance, 2 - create class instance and fill fields

        :return: an instance of this class created from the given json dict or string.
        """
        if process_mode == 0:
            return None
        instance = cls()
        if process_mode == 2:
            for key, value in json_dict.items():
                setattr(instance, key, value)
        return instance

    @staticmethod
    def check_json(input_json, dict_copy=False):
        """
        Checks whether input_json is a dict or a string. If it is already a dict, it is returned as-is.
        If it is not, it is converted to a dict by means of json.loads(json_type)

        :param input_json: input json or parsed dict
        :param dict_copy: if dict is passed and it is changed outside
        :return: Dictionary parsed from json or original dict
        """
        if isinstance(input_json, dict):
            return input_json.copy() if dict_copy else input_json
        elif isinstance(input_json, str):
            return json.loads(input_json)
        else:
            raise ValueError("input_json should be a json dict or string.")

    def __str__(self):
        d = {}
        for x, y in self.__dict__.items():
            if isinstance(y, list):
                d[x] = [str(i) for i in y]
            elif isinstance(y, dict):
                d[x] = {k:str(v) for k, v in y.items()}
            elif hasattr(y, '__dict__'):
                d[x] = y.__dict__
            else:
                d[x] = y
        return str(d)


# noinspection PyMethodOverriding
class BalanceItem(JsonDeserializable):
    """Business or personal wallet balance returned by the Balance API.

    :param uuid: Wallet UUID.
    :param balance: Business or personal wallet balance.
    :param currency_code: Wallet currency code.
    """
    def __init__(self):
        self.uuid = None
        self.balance = None
        self.currency_code = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(BalanceItem, cls).de_json(data, process_mode=2)
        instance.balance = float(instance.balance)
        instance.balance_usd = float(instance.balance_usd)
        return instance


# noinspection PyMethodOverriding
class Balance(JsonDeserializable):
    """Balance response from the Balance API.

    :param merchant: List of business wallet balances.
    :param user: List of personal wallet balances.
    """
    def __init__(self):
        self.merchant = []
        self.user = []

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Balance, cls).de_json(data, process_mode=1)
        data = data.get("balance")
        if not data:
            raise ValueError("Not a balance")
        if "merchant" in data:
            for item in data["merchant"]:
                # noinspection PyUnresolvedReferences
                instance.merchant.append(BalanceItem.de_json(item))
        if "user" in data:
            for item in data["user"]:
                # noinspection PyUnresolvedReferences
                instance.user.append(BalanceItem.de_json(item))
        return instance


# noinspection PyMethodOverriding
class ServiceLimit(JsonDeserializable):
    """Payment or payout service limits.

    :param min_amount: Minimum amount available for the operation.
    :param max_amount: Maximum amount available for the operation.
    """
    def __init__(self):
        self.min_amount = None
        self.max_amount = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(ServiceLimit, cls).de_json(data, process_mode=2)
        instance.min_amount = float(instance.min_amount)
        instance.max_amount = float(instance.max_amount)
        return instance


# noinspection PyMethodOverriding
class ServiceCommission(JsonDeserializable):
    """Payment or payout service commission.

    :param fee_amount: Fixed fee amount.
    :param percent: Percentage of the Cryptomus commission.
    """
    def __init__(self):
        self.fee_amount = None
        self.percent = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(ServiceCommission, cls).de_json(data, process_mode=2)
        instance.fee_amount = float(instance.fee_amount)
        instance.percent = float(instance.percent)
        return instance


# noinspection PyMethodOverriding
class Service(JsonDeserializable):
    """Available payment or payout service.

    :param network: Blockchain network code.
    :param currency: Currency code.
    :param is_available: Whether the service is available.
    :param limit: Minimum and maximum amounts for the operation.
    :param commission: Fixed and percentage commission settings.
    """
    def __init__(self):
        self.network = None
        self.currency = None
        self.is_available = None
        self.limit = None
        self.commission = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Service, cls).de_json(data, process_mode=2)
        instance.limit = ServiceLimit.de_json(instance.limit)
        instance.commission = ServiceCommission.de_json(instance.commission)
        return instance


# noinspection PyMethodOverriding
class Currency(Dictionaryable, JsonDeserializable):
    """
    Class representing a currency

    :param currency: Currency code.
    :param network: Blockchain network code.
    """

    def __init__(self, currency, network = None):
        """
        :param currency: (String) currency code
        :param network: (String, Optional) network code
        """
        self.currency = currency
        self.network = network

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Currency, cls).de_json(data, process_mode=2)
        return instance

    def to_dict(self):
        data = {
            "currency": self.currency,
            "network": self.network,
        }
        return data

# noinspection PyMethodOverriding
class Invoice(JsonDeserializable):
    """Payment invoice returned by invoice, information and history APIs.

    :param uuid: Invoice UUID.
    :param order_id: Invoice order ID in the merchant system.
    :param amount: Invoice amount.
    :param payment_amount: Amount actually paid by the client.
    :param payer_amount: Amount the client must pay in payer currency.
    :param discount_percent: Applied discount percentage.
    :param discount: Applied discount amount.
    :param payer_currency: Currency selected by the client for payment.
    :param currency: Invoice currency.
    :param merchant_amount: Amount credited to the merchant after commissions.
    :param network: Blockchain network used for payment.
    :param address: Payment address.
    :param from_: Payer wallet address (API field ``from``).
    :param txid: Blockchain transaction hash.
    :param payment_status: Payment status.
    :param url: Link to the payment form.
    :param expired_at: Invoice expiration timestamp.
    :param is_final: Whether the invoice can no longer be paid.
    :param additional_data: Additional data supplied when creating the invoice.
    :param created_at: Invoice creation time.
    :param updated_at: Invoice last update time.
    """
    def __init__(self):
        self.uuid = None
        self.order_id = None
        self.amount = None
        self.payment_amount = None
        self.payer_amount = None
        self.discount_percent = None
        self.discount = None
        self.payer_currency = None
        self.currency = None
        self.merchant_amount = None
        self.network = None
        self.address = None
        self.from_ = None
        self.txid = None
        self.payment_status = None
        self.url = None
        self.expired_at = None
        self.is_final = None
        self.additional_data = None
        self.created_at = None
        self.updated_at = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Invoice, cls).de_json(data, process_mode=2)
        if instance.amount is not None:
            instance.amount = float(instance.amount)
        if instance.payment_amount is not None:
            instance.payment_amount = float(instance.payment_amount)
        if instance.payer_amount is not None:
            instance.payer_amount = float(instance.payer_amount)
        if instance.discount_percent is not None:
            instance.discount_percent = float(instance.discount_percent)
        if instance.discount is not None:
            instance.discount = float(instance.discount)
        if instance.merchant_amount is not None:
            instance.merchant_amount = float(instance.merchant_amount)
        # if instance.created_at is not None:
        #     instance.created_at = datetime.datetime.strptime(instance.created_at, CryptomusDateFormat)
        # if instance.updated_at is not None:
        #     instance.updated_at = datetime.datetime.strptime(instance.updated_at, CryptomusDateFormat)
        return instance

# noinspection PyMethodOverriding
class Wallet(JsonDeserializable):
    """Static wallet returned by the Creating a Static wallet API.

    :param wallet_uuid: Merchant wallet UUID.
    :param uuid: Wallet UUID in the selected network.
    :param address: Wallet address in the selected network.
    :param network: Wallet network code.
    :param currency: Wallet network currency.
    :param url: Link to the payment form.
    """
    def __init__(self):
        self.wallet_uuid = None
        self.uuid = None
        self.address = None
        self.network = None
        self.currency = None
        self.url = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Wallet, cls).de_json(data, process_mode=2)
        return instance

# noinspection PyMethodOverriding
class PaymentPaginate(JsonDeserializable):
    """Cursor pagination returned by payment, payout and recurrence history APIs.

    :param count: Number of items on the current page.
    :param hasPages: Whether results span multiple pages.
    :param nextCursor: Cursor for the next page.
    :param previousCursor: Cursor for the previous page.
    :param perPage: Maximum number of items per page.
    """
    def __init__(self):
        self.count = None
        self.hasPages = None
        self.nextCursor = None
        self.previousCursor = None
        self.perPage = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(PaymentPaginate, cls).de_json(data, process_mode=2)
        instance.count = int(instance.count)
        instance.perPage = int(instance.perPage)
        return instance

# noinspection PyMethodOverriding
class PaymentsHistory(JsonDeserializable):
    """Payment history response.

    :param items: Array of invoices.
    :param paginate: Cursor pagination for the invoice list.
    """
    def __init__(self):
        self.items = []
        self.paginate = PaymentPaginate()

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(PaymentsHistory, cls).de_json(data, process_mode=2)
        instance.items = [Invoice.de_json(i) for i in instance.items]
        instance.paginate = PaymentPaginate.de_json(instance.paginate)
        return instance

# noinspection PyMethodOverriding
class Payout(JsonDeserializable):
    """Payout returned by payout, information and history APIs.

    :param uuid: Payout UUID.
    :param amount: Payout amount.
    :param currency: Payout currency.
    :param network: Blockchain network used for the payout.
    :param address: Recipient wallet address.
    :param txid: Blockchain transaction hash.
    :param status: Payout status.
    :param is_final: Whether the payout is finalized.
    :param balance: Merchant balance after the payout.
    :param payer_currency: Currency actually sent to the recipient.
    :param payer_amount: Amount sent in payer currency.
    """
    def __init__(self):
        self.uuid = None
        self.amount = None
        self.currency = None
        self.network = None
        self.address = None
        self.txid = None
        self.status = None
        self.is_final = None
        self.balance = None
        self.payer_currency = None
        self.payer_amount = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Payout, cls).de_json(data, process_mode=2)
        if instance.amount is not None:
            instance.amount = float(instance.amount)
        if instance.payer_amount is not None:
            instance.payer_amount = float(instance.payer_amount)
        if instance.balance is not None:
            instance.balance = float(instance.balance)
        return instance

# noinspection PyMethodOverriding
class PayoutHistory(JsonDeserializable):
    """Payout history response.

    :param items: Array of payouts.
    :param paginate: Cursor pagination for the payout list.
    """
    def __init__(self):
        self.items = []
        self.paginate = PaymentPaginate()

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(PayoutHistory, cls).de_json(data, process_mode=2)
        instance.items = [Payout.de_json(i) for i in instance.items]
        instance.paginate = PaymentPaginate.de_json(instance.paginate)
        return instance

# noinspection PyMethodOverriding
class WebhookConvert(JsonDeserializable):
    """Automatic conversion details from a payment webhook.

    :param to_currency: Currency to which payment funds were converted.
    :param commission: Conversion fee.
    :param rate: Conversion exchange rate.
    :param amount: Converted amount credited after commissions.
    """
    def __init__(self):
        self.to_currency = None
        self.commission = None
        self.rate = None
        self.amount = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(WebhookConvert, cls).de_json(data, process_mode=2)
        if instance.commission is not None:
            instance.commission = float(instance.commission)
        if instance.rate is not None:
            instance.rate = float(instance.rate)
        if instance.amount is not None:
            instance.amount = float(instance.amount)
        return instance

# noinspection PyMethodOverriding
class PaymentWebhook(JsonDeserializable):
    """Verified payment or static wallet webhook payload.

    :param type: Invoice type, ``payment`` or ``wallet``.
    :param uuid: Payment UUID.
    :param order_id: Merchant order ID.
    :param amount: Invoice amount.
    :param payment_amount: Amount actually paid by the client.
    :param payment_amount_usd: Amount actually paid in USD.
    :param merchant_amount: Amount credited to the merchant after commissions.
    :param commission: Cryptomus commission amount.
    :param is_final: Whether the invoice is finalized.
    :param status: Payment status.
    :param from_: Payer wallet address (API field ``from``).
    :param wallet_address_uuid: Static wallet UUID.
    :param network: Blockchain network used for payment.
    :param currency: Invoice currency.
    :param payer_currency: Currency actually paid by the client.
    :param payer_amount: Planned payment amount.
    :param payer_amount_exchange_rate: Exchange rate applied to the payment.
    :param transfer_id: Internal P2P transfer identifier.
    :param additional_data: Data supplied when creating the invoice.
    :param convert: Automatic conversion information, if enabled.
    :param txid: Blockchain transaction hash, if available.
    """
    def __init__(self):
        self.type = None
        self.uuid = None
        self.order_id = None
        self.amount = None
        self.payment_amount = None
        self.payment_amount_usd = None
        self.merchant_amount = None
        self.commission = None
        self.is_final = None
        self.status = None
        self.from_ = None
        self.wallet_address_uuid = None
        self.network = None
        self.currency = None
        self.payer_currency = None
        self.payer_amount = None
        self.payer_amount_exchange_rate = None
        self.transfer_id = None
        self.additional_data = None
        self.convert = None
        self.txid = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict, dict_copy=True)
        data["from_"] = data.pop("from", None)
        instance = super(PaymentWebhook, cls).de_json(data, process_mode=2)
        for field in ("amount", "payment_amount", "payment_amount_usd", "merchant_amount",
                      "commission", "payer_amount", "payer_amount_exchange_rate"):
            if getattr(instance, field) is not None:
                setattr(instance, field, float(getattr(instance, field)))
        if instance.convert is not None:
            instance.convert = WebhookConvert.de_json(instance.convert)
        return instance

# noinspection PyMethodOverriding
class PayoutWebhook(JsonDeserializable):
    """Verified payout webhook payload.

    :param type: Webhook type, always ``payout``.
    :param uuid: Payout UUID.
    :param order_id: Merchant payout order ID.
    :param amount: Payout amount.
    :param merchant_amount: Amount debited from the merchant balance with commissions.
    :param commission: Cryptomus commission amount.
    :param is_final: Whether the payout is finalized.
    :param status: Payout status.
    :param fail_reason: Failure reason, if the payout failed.
    :param txid: Blockchain transaction hash, if available.
    :param currency: Payout currency.
    :param network: Blockchain network used for the payout.
    :param payer_currency: Currency actually sent to the recipient.
    :param payer_amount: Amount sent in payer currency.
    """
    def __init__(self):
        self.type = None
        self.uuid = None
        self.order_id = None
        self.amount = None
        self.merchant_amount = None
        self.commission = None
        self.is_final = None
        self.status = None
        self.fail_reason = None
        self.txid = None
        self.currency = None
        self.network = None
        self.payer_currency = None
        self.payer_amount = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(PayoutWebhook, cls).de_json(data, process_mode=2)
        for field in ("amount", "merchant_amount", "commission", "payer_amount"):
            if getattr(instance, field) is not None:
                setattr(instance, field, float(getattr(instance, field)))
        return instance

# noinspection PyMethodOverriding
class Recurrence(JsonDeserializable):
    """Recurring payment returned by recurring payment APIs.

    :param uuid: Recurring payment UUID.
    :param name: Recurring payment name.
    :param order_id: Merchant order ID.
    :param amount: Recurring payment amount.
    :param currency: Recurring payment currency.
    :param payer_currency: Currency selected by the payer.
    :param payer_amount_usd: Payment amount in USD.
    :param payer_amount: Payment amount in payer currency.
    :param url_callback: URL for payment status callbacks.
    :param discount_days: Number of discount days.
    :param discount_amount: Discount amount.
    :param end_of_discount: Discount expiration date.
    :param period: Recurring payment period.
    :param status: Recurring payment status.
    :param url: Link to the payment form.
    :param last_pay_off: Time of the last payment.
    :param additional_data: Additional data supplied when creating the payment.
    """
    def __init__(self):
        self.uuid = None
        self.name = None
        self.order_id = None
        self.amount = None
        self.currency = None
        self.payer_currency = None
        self.payer_amount_usd = None
        self.payer_amount = None
        self.url_callback = None
        self.discount_days = None
        self.discount_amount = None
        self.end_of_discount = None
        self.period = None
        self.status = None
        self.url = None
        self.last_pay_off = None
        self.additional_data = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Recurrence, cls).de_json(data, process_mode=2)
        if instance.amount is not None:
            instance.amount = float(instance.amount)
        if instance.payer_amount_usd is not None:
            instance.payer_amount_usd = float(instance.payer_amount_usd)
        if instance.payer_amount is not None:
            instance.payer_amount = float(instance.payer_amount)
        if instance.discount_amount is not None:
            instance.discount_amount = float(instance.discount_amount)
        return instance

# noinspection PyMethodOverriding
class RecurrencesHistory(JsonDeserializable):
    """Recurring payment history response.

    :param items: Array of recurring payments.
    :param paginate: Cursor pagination for the recurring payment list.
    """
    def __init__(self):
        self.items = []
        self.paginate = PaymentPaginate()

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(RecurrencesHistory, cls).de_json(data, process_mode=2)
        instance.items = [Recurrence.de_json(i) for i in instance.items]
        instance.paginate = PaymentPaginate.de_json(instance.paginate)
        return instance
