from payment.models.transaction import Transaction
from django.db import transaction
from payment.client import MercadoPagoService
import logging

# Configurar o logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    
class CheckoutOrderUseCase:
    def execute(self, order, transaction_amount):

        transaction_amount

        try:
            # Integrate Mercado Pago QR Code generation
            mercado_pago_service = MercadoPagoService()
            print(transaction_amount)
            print(order)
            response_data = mercado_pago_service.create_qr_code(order, transaction_amount)
            qr_code = response_data.get("qr_data")
            in_store_order_id = response_data.get("in_store_order_id")
            
            logger.info(f'Successfully created QR code and in_store_order_id for order ID {order}: QR code={qr_code}, in_store_order_id={in_store_order_id}')

            # Save the QR code and in_store_order_id in the Payment model
            payment = Transaction.objects.create(
                order_id=order, 
                qrcode=qr_code, 
                external_id=in_store_order_id,  # Save the in_store_order_id in the external_id field
                amount=transaction_amount,
                status='generated'
            )
            logger.info(f'Payment record created with QR code and in_store_order_id for order ID {order}.')
            
            return payment  # Return the created payment
        except Exception as e:
            logger.error(f'Error during QR code generation or payment record creation for order ID {order}: {str(e)}')
            raise

        