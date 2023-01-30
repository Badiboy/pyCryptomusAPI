import json
from abc import ABC


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
        # d = {
        #     x: y.__dict__ if hasattr(y, '__dict__') else y
        #     for x, y in self.__dict__.items()
        # }
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
                instance.merchant.append(BalanceItem.de_json(item))
        if "user" in data:
            for item in data["user"]:
                instance.user.append(BalanceItem.de_json(item))
        return instance


# noinspection PyMethodOverriding
class ServiceLimit(JsonDeserializable):
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
    def __init__(self):
        self.uuid = None
        self.order_id = None
        self.amount = None
        self.payment_amount = None
        self.payer_amount = None
        self.payer_currency = None
        self.currency = None
        self.comments = None
        self.network = None
        self.address = None
        self.from_ = None
        self.txid = None
        self.url = None
        self.expired_at = None
        self.payment_status = None
        self.is_final = None
        self.additional_data = None
        self.currencies = None

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
        if instance.expired_at is not None:
            instance.expired_at = int(instance.expired_at)
        if instance.currencies:
            instance.currencies = [Currency.de_json(i) for i in instance.currencies]
        return instance

# noinspection PyMethodOverriding
class Wallet(JsonDeserializable):
    def __init__(self):
        self.wallet_uuid = None
        self.uuid = None
        self.address = None
        self.network = None
        self.currency = None

    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Wallet, cls).de_json(data, process_mode=2)
        return instance

# noinspection PyMethodOverriding
class PaymentPaginate(JsonDeserializable):
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
