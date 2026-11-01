"""
Testes de Carga — PharmaSys
Casos: CG01 (10 users), CG02 (50 users), CG03 (taxa erro), CG04 (pico 100)

Uso:
  pip install locust
  locust -f locustfile.py --host https://pharmasys-497823.rj.r.appspot.com

Depois abra http://localhost:8089 e configure:
  CG01: 10 users, spawn rate 2, duração 5min
  CG02: 50 users, spawn rate 5, duração 5min
  CG03: (verificar taxa de erro durante CG02)
  CG04: 100 users, spawn rate 20, duração 2min
"""
from locust import HttpUser, task, between


class PharmaSysUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Faz login ao iniciar."""
        # Busca o CSRF token da página de login
        resp = self.client.get('/login/')
        csrf = resp.cookies.get('csrftoken', '')
        self.client.post('/login/', {
            'username': 'admin',
            'password': 'admin123',
            'csrfmiddlewaretoken': csrf,
        }, headers={'Referer': self.host + '/login/'})

    @task(3)
    def ver_dashboard(self):
        self.client.get('/farmacia/')

    @task(2)
    def listar_medicamentos(self):
        self.client.get('/farmacia/medicamento/')

    @task(2)
    def listar_produtos(self):
        self.client.get('/farmacia/produto/')

    @task(1)
    def listar_laboratorios(self):
        self.client.get('/farmacia/laboratorio/')

    @task(1)
    def listar_distribuidoras(self):
        self.client.get('/farmacia/distribuidora/')

    @task(1)
    def pagina_inicial(self):
        self.client.get('/')
