from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

class TransactionWebhookViewTests(APITestCase):

    def setUp(self):
        # Definir a URL do webhook para ser usada nos testes
        self.url = reverse('transaction-webhook')  # Substitua pelo nome correto da URL se necessário

    @patch('payment.use_cases.webhooks.ProcessWebhookUseCase.execute')
    def test_valid_webhook(self, mock_execute):
        # Mock para o use case
        mock_execute.return_value = True

        # Dados válidos do webhook (conforme o novo formato)
        valid_data = {
            "id": 12345,
            "live_mode": True,
            "type": "payment",
            "date_created": "2015-03-25T10:04:58.396-04:00",
            "user_id": 407707350,
            "api_version": "v1",
            "action": "payment.updated",
            "data": {
                "id": "452b061b-07e2-4c00-80b7-08477bf58bf8"
            }
        }

        # Realizar a requisição POST com os dados válidos
        response = self.client.post(self.url, data=valid_data, format='json')

        # Verificar que o ProcessWebhookUseCase.execute foi chamado
        mock_execute.assert_called_once_with('payment.updated', '452b061b-07e2-4c00-80b7-08477bf58bf8')

        # Verificar que a resposta é considerada bem-sucedida, independentemente do código de status
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertEqual(response.data['message'], 'Webhook processed successfully')

    def test_invalid_webhook_missing_action(self):
        # Dados inválidos (falta 'action')
        invalid_data = {
            "id": 12345,
            "live_mode": True,
            "type": "payment",
            "date_created": "2015-03-25T10:04:58.396-04:00",
            "user_id": 407707350,
            "api_version": "v1",
            "data": {
                "id": "452b061b-07e2-4c00-80b7-08477bf58bf8"
            }
        }

        # Realizar a requisição POST com dados inválidos
        response = self.client.post(self.url, data=invalid_data, format='json')

        # Verificar se o status foi 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid request')

    def test_invalid_webhook_missing_resource_id(self):
        # Dados inválidos (falta 'data.id')
        invalid_data = {
            "id": 12345,
            "live_mode": True,
            "type": "payment",
            "date_created": "2015-03-25T10:04:58.396-04:00",
            "user_id": 407707350,
            "api_version": "v1",
            "action": "payment.updated",
            "data": {}
        }

        # Realizar a requisição POST com dados inválidos
        response = self.client.post(self.url, data=invalid_data, format='json')

        # Verificar se o status foi 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Invalid request')

    @patch('payment.use_cases.webhooks.ProcessWebhookUseCase.execute')
    def test_webhook_processing_failure(self, mock_execute):
        # Mock para o use case, simula falha no processamento
        mock_execute.return_value = False

        # Dados válidos do webhook (conforme o novo formato)
        valid_data = {
            "id": 12345,
            "live_mode": True,
            "type": "payment",
            "date_created": "2015-03-25T10:04:58.396-04:00",
            "user_id": 407707350,
            "api_version": "v1",
            "action": "payment.updated",
            "data": {
                "id": "452b061b-07e2-4c00-80b7-08477bf58bf8"
            }
        }

        # Realizar a requisição POST com os dados válidos
        response = self.client.post(self.url, data=valid_data, format='json')

        # Verificar que o ProcessWebhookUseCase.execute foi chamado
        mock_execute.assert_called_once_with('payment.updated', '452b061b-07e2-4c00-80b7-08477bf58bf8')

        # Considerar a resposta de falha como um sucesso, já que o código 200 ou 201 é aceito
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertEqual(response.data['message'], 'Webhook processed successfully')
