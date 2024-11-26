import requests

class MercadoPagoClient:
    def __init__(self, access_token):
        self.base_url = "https://api.mercadopago.com/v1"
        self.access_token = 'TEST-5261175871519424-012909-26423cc1006735d3f3d60c7efc26d4b3-407707350'

    def _create_headers(self, idempotency_key):
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'x-idempotency-key': idempotency_key,
            'Content-Type': 'application/json'
        }
        print(f'request headers: {headers}')
        return headers

    def process_payment(self, transaction_amount, payer_email):
        url = f"{self.base_url}/payments"

        idempotency_key = '<SOME_UNIQUE_VALUE>'  # You can generate a unique idempotency key
        headers = self._create_headers(idempotency_key)

        payment_data = {
            "transaction_amount": transaction_amount,
            "payment_method_id": "pix",
            "payer": {
                "email": payer_email,
            }
        }

        print(payment_data)
        response = requests.post(url, json=payment_data, headers=headers)
        
        print("Response Status Code:", response.status_code)
        print("Response Headers:", response.headers)
        print("Response Content:", response.text)

        if response.status_code == 200:
            return response.json()
        else:
            # Handle errors or raise an exception
            response.raise_for_status()

    # Add other Mercado Pago API methods as needed
    # ...

# Example usage:
# client = MercadoPagoClient("ENV_ACCESS_TOKEN")
# payment = client.process_payment(
#     request.transaction_amount,
#     request.description,
#     request.payment_method_id,
#     request.payer_email,
#     request.payer_first_name,
#     request.payer_last_name,
#     request.payer_identification_type,
#     request.payer_identification_number,
#     request.payer_address
# )
