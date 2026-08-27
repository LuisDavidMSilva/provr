import unittest
from app import create_app, db

class TestRateLimiter(unittest.TestCase):
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

    def test_login_rate_limiting(self):
        # O limite de login está configurado para 5 requisições por minuto
        # Fazemos 5 requisições normais que devem retornar sucesso (200 ou 302)
        for i in range(5):
            response = self.client.get('/auth/login')
            self.assertIn(response.status_code, [200, 302])
            
            # Validar headers do rate limiter
            self.assertIn('X-RateLimit-Limit', response.headers)
            self.assertIn('X-RateLimit-Remaining', response.headers)
            remaining = int(response.headers['X-RateLimit-Remaining'])
            self.assertEqual(remaining, 5 - (i + 1))

        # A 6ª tentativa (HTML) deve redirecionar (302) para o login com mensagem flash por causa do handle_rate_limit_exceeded
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/auth/login'))
        
        # Se a requisição aceitar apenas JSON, deve retornar 429 (Too Many Requests)
        response = self.client.get('/auth/login', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 429)
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertEqual(data['error'], 'Too many requests')

    def test_health_check_exempt(self):
        # Health check deve estar isento de rate limit (ex: fazer 10 requests seguidos)
        for _ in range(10):
            response = self.client.get('/health/live')
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('X-RateLimit-Limit', response.headers)

if __name__ == '__main__':
    unittest.main()
