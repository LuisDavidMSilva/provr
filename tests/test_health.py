import unittest
from app import create_app, db

class TestHealthCheck(unittest.TestCase):
    def setUp(self):
        # Inicializar a aplicação com configuração de testes
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def test_liveness_endpoint(self):
        response = self.client.get('/health/live')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data, {'alive': True})

    def test_readiness_endpoint(self):
        response = self.client.get('/health/ready')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data, {'ready': True})

    def test_health_check_endpoint(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')
        self.assertIn('timestamp', data)
        self.assertEqual(data['version'], '1.3.0')
        self.assertIn('uptime', data)

    def test_health_check_token_unauthorized(self):
        # Forçar token de segurança para testar validação
        self.app.config['HEALTH_CHECK_TOKEN'] = 'custom-test-token'
        
        # Testar acesso sem enviar token
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data['status'], 'unhealthy')
        self.assertEqual(data['reason'], 'Unauthorized')

    def test_health_check_token_authorized(self):
        # Forçar token de segurança para testar validação
        self.app.config['HEALTH_CHECK_TOKEN'] = 'custom-test-token'
        
        # Testar acesso correto via cabeçalho HTTP
        headers = {'X-Health-Token': 'custom-test-token'}
        response = self.client.get('/health/', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')

        # Testar acesso correto via parâmetro de query
        response = self.client.get('/health/?token=custom-test-token')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
