[![PyPi Package Version](https://img.shields.io/pypi/v/pyCryptomusAPI.svg)](https://pypi.python.org/pypi/pyCryptomusAPI)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyCryptomusAPI.svg)](https://pypi.python.org/pypi/pyCryptomusAPI)
[![PyPi downloads](https://img.shields.io/pypi/dm/pyCryptomusAPI.svg)](https://pypi.org/project/pyCryptomusAPI/)

# <p align="center">pyCryptomusAPI</p>
Python implementation of [Cryptomus](https://cryptomus.com) and [Heleket](https://heleket.com) public [API](https://doc.cryptomus.com)

If you found a bug or have a feature request, just create an issue!

# Installation
Installation using pip (a Python package manager):
```
$ pip install pyCryptomusAPI
```

# Usage
Everything is as simple as the [API](https://doc.cryptomus.com/) itself.
1. Create **pyCryptomusAPI** or **pyHeleketAPI** instance
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
Available methods include:

* Payments: create_invoice(), create_wallet(), payment_qr_code(), wallet_qr_code(),
  block_wallet(), block_wallet_refund(), payment_information(), refund(),
  resend_payment_webhook(), test_payment_webhook(), payment_history(),
  payment_services(), mark_payment_as_paid()
* Payouts: create_payout(), payout_information(), payout_history(), payout_services(),
  transfer_to_personal(), transfer_to_business(), test_payout_webhook()
* Recurring payments: create_recurrence(), recurrence_information(),
  recurrence_history(), cancel_recurrence()
* Webhooks: process_payment_webhook(), process_payout_webhook()
* Other: balance()

# Exceptions
Exceptions are raised using pyCryptomusAPIException class.
