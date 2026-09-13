import base64
import hmac
import json
from hashlib import md5

from .cryto_types import PaymentWebhook, PayoutWebhook


# Example with a web framework. Receiving an HTTP request is not handled by this library:
#
# data = request.get_json()
# try:
#     payment = client.process_payment_webhook(data)
# except WebhookVerificationError:
#     return "Invalid webhook", 400
#
# if payment.is_final and payment.status in ("paid", "paid_over"):
#     process_order(payment.order_id)
# return "OK", 200


class WebhookVerificationError(ValueError):
    """Webhook payload is invalid or its signature cannot be verified."""


def _parse_webhook(webhook):
    if isinstance(webhook, bytes):
        try:
            webhook = webhook.decode("utf-8")
        except UnicodeDecodeError as error:
            raise WebhookVerificationError("Webhook body is not UTF-8") from error
    if isinstance(webhook, str):
        try:
            webhook = json.loads(webhook)
        except ValueError as error:
            raise WebhookVerificationError("Webhook body is not valid JSON") from error
    if not isinstance(webhook, dict):
        raise WebhookVerificationError("Webhook must be a dict, JSON string or bytes")
    return webhook.copy()


def _json_dumps(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("/", "\\/")


def _process_webhook(webhook, api_key, allowed_types, webhook_class):
    if not api_key:
        raise WebhookVerificationError("API key is empty")

    data = _parse_webhook(webhook)
    sign = data.pop("sign", None)
    if not isinstance(sign, str):
        raise WebhookVerificationError("Webhook signature is empty")
    if data.get("type") not in allowed_types:
        raise WebhookVerificationError("Webhook type is invalid")

    signed_data = _json_dumps(data)
    expected_sign = md5(base64.b64encode(signed_data.encode("utf-8")) +
                        api_key.encode("utf-8")).hexdigest()
    if not hmac.compare_digest(expected_sign, sign):
        raise WebhookVerificationError("Webhook signature is invalid")
    return webhook_class.de_json(data)


def process_payment_webhook(webhook, payment_api_key):
    """
    Verify and deserialize a payment or static wallet webhook.

    :param webhook: (Dict, String or Bytes) Webhook body
    :param payment_api_key: Payment API key
    :return: PaymentWebhook
    """
    return _process_webhook(webhook, payment_api_key, ("payment", "wallet"), PaymentWebhook)


def process_payout_webhook(webhook, payout_api_key):
    """
    Verify and deserialize a payout webhook.

    :param webhook: (Dict, String or Bytes) Webhook body
    :param payout_api_key: Payout API key
    :return: PayoutWebhook
    """
    return _process_webhook(webhook, payout_api_key, ("payout",), PayoutWebhook)
