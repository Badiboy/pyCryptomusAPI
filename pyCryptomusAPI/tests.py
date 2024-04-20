import inspect
import uuid
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
        print("API call failed. Code: {}, Message: {}".format(pe.code, pe.message))
    except Exception as e:
        raise e
    return None

def test_api_functions():
    client = pyCryptomusAPI(
        test_merchant_uuid,
        payment_api_key=test_api_token_payment,
        payout_api_key=test_api_token_payout,
    print_errors=True)
    invoice = run_and_print(lambda: client.create_invoice(1, "USDT", str(uuid.uuid4())))
    invoice_uuid = invoice.uuid if invoice else "123"
    wallet = run_and_print(lambda: client.create_wallet("TRON", "TRX", str(uuid.uuid4())))
    wallet_uuid = wallet.uuid if wallet else "123"
    wallet_adress = wallet.address if wallet else "123"
    run_and_print(lambda: client.block_wallet(wallet_uuid = wallet_uuid))                        # Server error (reason unknown)
    run_and_print(lambda: client.block_wallet_refund(wallet_adress, wallet_uuid = wallet_uuid))  # Server error (it's ok)
    run_and_print(lambda: client.payment_information(invoice_uuid = invoice_uuid))
    run_and_print(lambda: client.refund(wallet_adress, True, invoice_uuid = invoice_uuid))       # Server error (looks ok)
    run_and_print(lambda: client.payment_services())
    run_and_print(lambda: client.payment_history())
    run_and_print(lambda: client.payment_history_filtered(is_final=True))
    run_and_print(lambda: client.payout_services())
    run_and_print(lambda: client.payout_history())
    run_and_print(lambda: client.balance())

test_api_functions()
