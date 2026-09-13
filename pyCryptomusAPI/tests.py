import base64
import datetime
from hashlib import md5
import json
import unittest
from unittest.mock import patch

from . import api as api_module
from .api import pyCryptomusAPI
from .webhooks import WebhookVerificationError


class MockResponse:
    def __init__(self, data, status_code = 200):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data


class TestPyCryptomusAPI(unittest.TestCase):
    """Mockup tests for all public client methods. No API keys or network are used."""

    def setUp(self):
        self.client = pyCryptomusAPI("merchant-id", "payment-key", "payout-key")

    @staticmethod
    def invoice_response():
        return MockResponse({
            "state": 0,
            "result": {"uuid": "invoice-id", "amount": "1", "currency": "USDT"},
        })

    @staticmethod
    def payout_response():
        return MockResponse({
            "state": 0,
            "result": {"uuid": "payout-id", "amount": "1", "currency": "USDT"},
        })

    @staticmethod
    def history_response():
        return MockResponse({
            "state": 0,
            "result": {"items": [], "paginate": {"count": 0, "perPage": 15}},
        })

    @staticmethod
    def webhook_sign(data, api_key):
        signed_data = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("/", "\\/")
        return md5(base64.b64encode(signed_data.encode("utf-8")) + api_key.encode("utf-8")).hexdigest()

    @patch.object(api_module.requests, "post")
    def test_create_invoice(self, post):
        post.return_value = self.invoice_response()

        invoice = self.client.create_invoice(
            "1.25", "USDT", "invoice-order", network="tron", additional_data="test",
            accuracy_payment_percent=1.25)

        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payment")
        self.assertEqual(json.loads(post.call_args.kwargs["data"])["amount"], "1.25")
        self.assertEqual(json.loads(post.call_args.kwargs["data"])["accuracy_payment_percent"], "1.25")
        self.assertEqual(json.loads(post.call_args.kwargs["data"])["network"], "tron")
        self.assertEqual(invoice.uuid, "invoice-id")

        post.return_value = self.invoice_response()
        self.client.create_invoice(1.25, "USDT", "float-invoice-order", accuracy_payment_percent=1)
        self.assertEqual(json.loads(post.call_args.kwargs["data"])["amount"], "1.25")
        self.assertEqual(json.loads(post.call_args.kwargs["data"])["accuracy_payment_percent"], "1")

    @patch.object(api_module.requests, "post")
    def test_create_wallet_and_qr_codes(self, post):
        post.return_value = MockResponse({
            "state": 0,
            "result": {
                "uuid": "wallet-id", "wallet_uuid": "merchant-wallet-id",
                "network": "tron", "currency": "TRX", "url": "https://pay.example",
            },
        })

        wallet = self.client.create_wallet("tron", "TRX", "wallet-order")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/wallet")
        self.assertEqual(wallet.url, "https://pay.example")

        post.return_value = MockResponse({"state": 0, "result": {"image": "data:image/png;base64,qr"}})
        self.assertEqual(self.client.payment_qr_code("invoice-id"), "data:image/png;base64,qr")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payment/qr")
        self.assertEqual(self.client.wallet_qr_code("wallet-id"), "data:image/png;base64,qr")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/wallet/qr")

    @patch.object(api_module.requests, "post")
    def test_wallet_block_and_refund(self, post):
        post.return_value = MockResponse({"state": 0, "result": {"success": True}})

        self.assertTrue(self.client.block_wallet(wallet_uuid="wallet-id")["success"])
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/wallet/block-address")

        post.return_value = MockResponse({"state": 0, "result": {"amount": "1"}})
        self.assertEqual(
            self.client.block_wallet_refund("refund-address", wallet_uuid="wallet-id")["amount"], "1")
        self.assertEqual(
            post.call_args.args[0],
            "https://api.cryptomus.com/v1/wallet/blocked-address-refund")

    @patch.object(api_module.requests, "post")
    def test_payment_information_and_refund(self, post):
        post.return_value = self.invoice_response()

        invoice = self.client.payment_information(invoice_uuid="invoice-id")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payment/info")
        self.assertEqual(invoice.uuid, "invoice-id")

        post.return_value = MockResponse({"state": 0, "result": []})
        self.assertEqual(self.client.refund("refund-address", True, invoice_uuid="invoice-id"), [])
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payment/refund")

    @patch.object(api_module.requests, "post")
    def test_payment_history_services_and_balance(self, post):
        post.return_value = self.history_response()

        history = self.client.payment_history(
            "2026-09-01 00:00:00", "2026-09-02 23:59:59", cursor="next-page")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payment/list")
        self.assertEqual(post.call_args.kwargs["params"], {"cursor": "next-page"})
        self.assertEqual(json.loads(post.call_args.kwargs["data"]), {
            "date_from": "2026-09-01 00:00:00",
            "date_to": "2026-09-02 23:59:59",
        })
        self.assertEqual(history.items, [])
        self.assertEqual(self.client.payment_history_filtered(max_pages=1).items, [])

        post.return_value = MockResponse({
            "state": 0,
            "result": [{
                "network": "tron", "currency": "USDT", "is_available": True,
                "limit": {"min_amount": "1", "max_amount": "10"},
                "commission": {"fee_amount": "0", "percent": "0"},
            }],
        })
        self.assertEqual(self.client.payment_services()[0].currency, "USDT")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payment/services")

        post.return_value = MockResponse({"state": 0, "result": [{"balance": {"merchant": [], "user": []}}]})
        self.assertEqual(self.client.balance().merchant, [])
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/balance")

    @patch.object(api_module.requests, "post")
    def test_payment_webhook_requests_and_mark_as_paid(self, post):
        post.return_value = MockResponse({"state": 0, "result": {"success": True}})

        self.assertTrue(self.client.resend_payment_webhook(order_id="invoice-order")["success"])
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v2/payment/resend")

        post.return_value = MockResponse({"state": 0, "result": []})
        self.assertEqual(
            self.client.test_payment_webhook("https://example.com/callback", "USDT", "tron"), [])
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/test-webhook/payment")

        post.return_value = MockResponse({"state": 0, "result": {"success": True}})
        self.assertTrue(self.client.mark_payment_as_paid(order_id="invoice-order")["success"])
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payment/mark-as-paid")

    @patch.object(api_module.requests, "post")
    def test_payout_methods(self, post):
        post.return_value = self.payout_response()

        payout = self.client.create_payout(
            1, "USDT", "payout-order", "payout-address", True, network="tron")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payout")
        self.assertEqual(payout.uuid, "payout-id")

        payout = self.client.payout_information(payout_uuid="payout-id")
        expected_body = json.dumps({"uuid": "payout-id"})
        expected_sign = md5(base64.b64encode(expected_body.encode("utf-8")) +
                            b"payout-key").hexdigest()
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payout/info")
        self.assertEqual(post.call_args.kwargs["headers"]["sign"], expected_sign)
        self.assertEqual(payout.uuid, "payout-id")

        post.return_value = self.history_response()
        history = self.client.payout_history(
            datetime.datetime(2026, 9, 1), datetime.date(2026, 9, 2), cursor="next-page")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payout/list")
        self.assertEqual(post.call_args.kwargs["params"], {"cursor": "next-page"})
        self.assertEqual(json.loads(post.call_args.kwargs["data"]), {
            "date_from": "2026-09-01 00:00:00",
            "date_to": "2026-09-02 00:00:00",
        })
        self.assertEqual(history.items, [])

        post.return_value = MockResponse({
            "state": 0,
            "result": [{
                "network": "tron", "currency": "USDT", "is_available": True,
                "limit": {"min_amount": "1", "max_amount": "10"},
                "commission": {"fee_amount": "0", "percent": "0"},
            }],
        })
        self.assertEqual(self.client.payout_services()[0].currency, "USDT")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/payout/services")

    @patch.object(api_module.requests, "post")
    def test_payout_webhook_and_wallet_transfers(self, post):
        post.return_value = MockResponse({"state": 0, "result": []})

        self.assertEqual(
            self.client.test_payout_webhook("https://example.com/callback", "USDT", "tron"), [])
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/test-webhook/payout")

        post.return_value = MockResponse({"state": 0, "result": {"merchant_balance": "1"}})
        self.assertEqual(self.client.transfer_to_personal(1, "USDT")["merchant_balance"], "1")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/transfer/to-personal")
        self.assertEqual(self.client.transfer_to_business(1, "USDT")["merchant_balance"], "1")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/transfer/to-business")

    @patch.object(api_module.requests, "post")
    def test_recurrence_methods(self, post):
        recurrence_data = {
            "uuid": "recurrence-id", "amount": "1", "currency": "USDT",
            "name": "Test recurrence", "period": "monthly",
        }
        post.return_value = MockResponse({"state": 0, "result": recurrence_data})

        recurrence = self.client.create_recurrence(1, "USDT", "Test recurrence", "monthly")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/recurrence/create")
        self.assertEqual(recurrence.uuid, "recurrence-id")

        recurrence = self.client.recurrence_information(recurrence_uuid="recurrence-id")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/recurrence/info")
        self.assertEqual(recurrence.period, "monthly")

        post.return_value = self.history_response()
        history = self.client.recurrence_history(cursor="next-page")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/recurrence/list")
        self.assertEqual(post.call_args.kwargs["params"], {"cursor": "next-page"})
        self.assertEqual(history.items, [])

        post.return_value = MockResponse({"state": 0, "result": recurrence_data})
        recurrence = self.client.cancel_recurrence(recurrence_uuid="recurrence-id")
        self.assertEqual(post.call_args.args[0], "https://api.cryptomus.com/v1/recurrence/cancel")
        self.assertEqual(recurrence.uuid, "recurrence-id")

    def test_process_payment_webhook(self):
        webhook_data = {
            "type": "payment", "uuid": "payment-id", "order_id": "payment-order",
            "amount": "3.00000000", "payment_amount": "3.00000000",
            "payment_amount_usd": "0.23", "merchant_amount": "2.94000000",
            "commission": "0.06000000", "is_final": True, "status": "paid",
            "from": "payer-wallet", "network": "tron", "currency": "TRX",
            "payer_currency": "TRX", "payer_amount": "0.00234567",
            "payer_amount_exchange_rate": "42650.00000000", "additional_data": "Тест",
            "convert": {"to_currency": "USDT", "commission": "0", "rate": "0.07700000",
                        "amount": "0.22638000"},
            "txid": "transaction/with/slash",
        }
        webhook_data["sign"] = self.webhook_sign(webhook_data, "payment-key")

        webhook = self.client.process_payment_webhook(webhook_data)
        self.assertEqual(webhook.uuid, "payment-id")
        self.assertEqual(webhook.from_, "payer-wallet")
        self.assertEqual(webhook.amount, 3.0)
        self.assertEqual(webhook.convert.rate, 0.077)
        self.assertIn("sign", webhook_data)

        webhook = self.client.process_payment_webhook(json.dumps(webhook_data, ensure_ascii=False))
        self.assertEqual(webhook.status, "paid")
        webhook = self.client.process_payment_webhook(json.dumps(webhook_data).encode("utf-8"))
        self.assertEqual(webhook.txid, "transaction/with/slash")

        wallet_data = webhook_data.copy()
        wallet_data["type"] = "wallet"
        wallet_data.pop("sign")
        wallet_data["sign"] = self.webhook_sign(wallet_data, "payment-key")
        webhook = self.client.process_payment_webhook(wallet_data)
        self.assertEqual(webhook.type, "wallet")

    def test_process_payout_webhook(self):
        webhook_data = {
            "type": "payout", "uuid": "payout-id", "order_id": "payout-order",
            "amount": "207.00000000", "merchant_amount": "207.30000000",
            "commission": "0.30000000", "is_final": True, "status": "fail",
            "fail_reason": "aml", "txid": None, "currency": "USDT", "network": "bsc",
            "payer_currency": "USDT", "payer_amount": "207.00000000",
        }
        webhook_data["sign"] = self.webhook_sign(webhook_data, "payout-key")

        webhook = self.client.process_payout_webhook(webhook_data)
        self.assertEqual(webhook.uuid, "payout-id")
        self.assertEqual(webhook.merchant_amount, 207.3)
        self.assertEqual(webhook.fail_reason, "aml")

    def test_process_webhook_rejects_invalid_payload(self):
        webhook_data = {"type": "payment", "uuid": "payment-id"}
        webhook_data["sign"] = self.webhook_sign(webhook_data, "payment-key")
        webhook_data["sign"] = "invalid"

        with self.assertRaises(WebhookVerificationError):
            self.client.process_payment_webhook(webhook_data)
        with self.assertRaises(WebhookVerificationError):
            self.client.process_payout_webhook(webhook_data)
        with self.assertRaises(WebhookVerificationError):
            self.client.process_payment_webhook({"type": "payment"})
        with self.assertRaises(WebhookVerificationError):
            self.client.process_payment_webhook("not json")


if __name__ == "__main__":
    unittest.main()
