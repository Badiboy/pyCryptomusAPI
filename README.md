[![PyPi Package Version](https://img.shields.io/pypi/v/pyCryptomusAPI.svg)](https://pypi.python.org/pypi/pyCryptomusAPI)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyCryptomusAPI.svg)](https://pypi.python.org/pypi/pyCryptomusAPI)
[![PyPi downloads](https://img.shields.io/pypi/dm/pyCryptomusAPI.svg)](https://pypi.org/project/pyCryptomusAPI/)

# <p align="center">pyCryptomusAPI</p>
Python implementation of [Cryptomus](https://cryptomus.com) public [API](https://doc.cryptomus.com)

**This library is developing for my personal needs, so it may not fully implement API. However I will continue to maintain it, so if you need some not implemented methods - just open an issue.**

# Installation
Installation using pip (a Python package manager):
```
$ pip install pyCryptomusAPI
```

# Usage
Everything is as simple as the [API](https://help.crypt.bot/crypto-pay-api#available-methods) itself.
1. Create pyCryptomusAPI instance
2. Access API methods in pythonic notation (e.g. "Creating an invoice" -> create_invoice())
3. Most methods return result as correspondent class, so you can access data as fields 
```
from pyCryptomusAPI import pyCryptomusAPI
client = pyCryptomusAPI(
    "xxxx-xxxx-xxxx-xxxx-xxxx",  # Merchand UUID
    payment_api_key="xxxxxxx",   # Payment API key (for payment methods)
    payout_api_key="xxxxxxx")    # Payout API key (for payout methods)
balance = client.balance()
for item in balance.merchant:
    print("Merchant balance: {} {}".format(item.balance, item.currency_code))
```
You can also check tests.py.

# Exceptions
Exceptions are rised using pyCryptomusAPIException class.
