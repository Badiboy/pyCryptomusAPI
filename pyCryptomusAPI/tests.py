import inspect, datetime
from time import sleep
try:
    from pyCryptomusAPI import pyCryptomusAPI, pyCryptomusAPIException
except:
    from api import pyCryptomusAPI, pyCryptomusAPIException

try:
    from private_keys import *
except:
    test_merchant_uuid = "---"
    test_api_token_payment = "---"
    test_api_token_payout = "---"

def run_and_print(f):
    try:
        sleep(1)
        print()
        print(inspect.getsourcelines(f)[0][0].strip())
        res = f()
        if isinstance(res, list):
            for i in res:
                print(i)
        else:
            print(res)
        return res
    except pyCryptomusAPIException as pe:
        if pe.code in [-2]:
            print("API call failed. Code: {}, Message: {}".format(pe.code, pe.message))
        else:
            raise pe
    except Exception as e:
        raise e
    return None

def test_api_functions():
    client = pyCryptomusAPI(
        test_merchant_uuid,
        payment_api_key=test_api_token_payment,
        payout_api_key=test_api_token_payout,
        print_errors=True)
    run_and_print(lambda: client.balance())
    run_and_print(lambda: client.payment_services())
    run_and_print(lambda: client.payout_services())

test_api_functions()
