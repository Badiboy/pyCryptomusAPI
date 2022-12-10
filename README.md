[![PyPi Package Version](https://img.shields.io/pypi/v/pyCryptomusAPI.svg)](https://pypi.python.org/pypi/pyCryptomusAPI)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyCryptomusAPI.svg)](https://pypi.python.org/pypi/pyCryptomusAPI)
[![PyPi downloads](https://img.shields.io/pypi/dm/pyCryptomusAPI.svg)](https://pypi.org/project/pyCryptomusAPI/)

# <p align="center">pyCryptomusAPI</p>
Simple Python implementation of [Cryptomus](https://cryptomus.com) public [API](https://doc.cryptomus.com)

# Installation
Installation using pip (a Python package manager):
```
$ pip install pyCryptomusAPI
```

# Usage (todo)
Everything is as simple as the [API](https://help.crypt.bot/crypto-pay-api#available-methods) itself.
1. Create pyCryptomusAPI instance
2. Access API methods in pythonic notation (getInvoices -> get_invoices)
```
from pyCryptomusAPI import pyCryptomusAPI
client = pyCryptomusAPI(api_token="zzz")
print(client.get_balance())
```
You can also check tests.py.

# Exceptions
Exceptions are rised using pyCryptomusAPIException class.
