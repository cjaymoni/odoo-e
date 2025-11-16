import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class ExpressPayController(http.Controller):

    @http.route('/payment/expresspay/return', type='http', auth='public', csrf=False)
    def expresspay_return(self, **post):
        """ Handle customer return from ExpressPay """
        _logger.info("ExpressPay return data: %s", post)
        
        try:
            # Let Odoo handle the notification
            env = request.env['payment.transaction'].sudo()
        # Find tx by order-id (your _get_tx_from_notification_data already matches on order-id)
            order_id = post.get('order-id')
            token = post.get('token')

            if not order_id or not token:
                _logger.error("Return missing required data: order-id=%s, token=%s", order_id, token)
                return request.redirect('/payment/status')

            tx = env._get_tx_from_notification_data('expresspay', {'order-id': order_id})
            if not tx:
                _logger.error("Return with unknown order-id: %s", order_id)
                return request.redirect('/payment/status')

            _logger.info("Processing return for transaction %s with token %s", order_id, token)

        # Synchronously query status from ExpressPay
            provider = tx.provider_id
            status_payload = provider._expresspay_query_status(token=token, order_id=order_id)
            _logger.info("ExpressPay query response: %s", status_payload)

        # Reuse your validator (expects response-code mapping)
            tx._expresspay_validate_transaction(status_payload)
            
            # If webhooks are disabled and fallback polling is enabled, schedule polling for pending payments
            if not provider._expresspay_should_use_webhooks() and provider._expresspay_should_use_fallback_polling():
                if status_payload.get('result') == 4:  # Pending status
                    tx._expresspay_schedule_polling()
                    _logger.info("ExpressPay fallback polling scheduled for pending payment: %s", order_id)

        except Exception as e:
            _logger.error("Error processing ExpressPay return: %s", e)
            # Redirect to payment status on error
            return request.redirect('/payment/status')

        return request.redirect('/payment/status')


    @http.route('/payment/expresspay/webhook', type='http', auth='public', csrf=False)
    def expresspay_webhook(self, **post):
        """Handle ExpressPay webhook notifications"""
        _logger.info("ExpressPay webhook data: %s", post)
        
        try:
            # Check if webhooks are enabled
            tx_reference = post.get('order-id') or post.get('transaction-id')
            if not tx_reference:
                _logger.error("Webhook missing transaction reference: %s", post)
                return request.make_response("Missing transaction reference", status=400)

            # Find the transaction
            transaction = request.env['payment.transaction'].sudo().search([
                ('reference', '=', tx_reference)
            ])
            
            if not transaction:
                _logger.error("Transaction not found for reference: %s", tx_reference)
                return request.make_response("Transaction not found", status=404)

            # Check if webhooks are enabled for this provider
            if not transaction.provider_id._expresspay_should_use_webhooks():
                _logger.warning("Webhook received but webhooks are disabled for provider %s", transaction.provider_id.name)
                return request.make_response("Webhooks disabled", status=200)  # Return 200 to acknowledge receipt

            _logger.info("Processing webhook for transaction %s with provider %s", tx_reference, transaction.provider_id.name)

            # Validate the transaction
            transaction._expresspay_validate_transaction(post)
            _logger.info("Webhook processed successfully for TX %s", tx_reference)
            return request.make_response("OK", status=200)

        except Exception as e:
            _logger.error("Error processing webhook: %s", e)
            return request.make_response("Server Error", status=500)