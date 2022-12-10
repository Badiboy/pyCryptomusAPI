import json
from abc import ABC


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
    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(BalanceItem, cls).de_json(data, process_mode=2)
        instance.balance = float(instance.balance)
        instance.balance_usd = float(instance.balance_usd)
        return instance


# noinspection PyMethodOverriding
class Balance(JsonDeserializable):
    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Balance, cls).de_json(data, process_mode=1)
        data = data.get("balance")
        if not data:
            raise ValueError("Not a balance")
        instance.merchant = []
        if "merchant" in data:
            for item in data["merchant"]:
                instance.merchant.append(BalanceItem.de_json(item))
        instance.user = []
        if "user" in data:
            for item in data["user"]:
                instance.user.append(BalanceItem.de_json(item))
        return instance


# noinspection PyMethodOverriding
class ServiceLimit(JsonDeserializable):
    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(ServiceLimit, cls).de_json(data, process_mode=2)
        instance.min_amount = float(instance.min_amount)
        instance.max_amount = float(instance.max_amount)
        return instance


# noinspection PyMethodOverriding
class ServiceCommission(JsonDeserializable):
    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(ServiceCommission, cls).de_json(data, process_mode=2)
        instance.fee_amount = float(instance.fee_amount)
        instance.percent = float(instance.percent)
        return instance


# noinspection PyMethodOverriding
class Service(JsonDeserializable):
    @classmethod
    def de_json(cls, json_dict):
        data = cls.check_json(json_dict)
        instance = super(Service, cls).de_json(data, process_mode=2)
        instance.limit = ServiceLimit.de_json(instance.limit)
        instance.commission = ServiceCommission.de_json(instance.commission)
        return instance
