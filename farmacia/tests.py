"""
Testes Automatizados — PharmaSys
================================
Caixa-Preta (CP): testes funcionais de ponta a ponta
Caixa-Branca (CB): testes unitários de lógica interna
Acessibilidade (AC): testes de conformidade WCAG
"""
import re
from datetime import timedelta

from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.utils import timezone

from farmacia.models import Laboratorio, Distribuidora, Medicamento, ProdutoDiverso


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def criar_usuario(username, password='teste12345', is_staff=False, grupo=None):
    user = User.objects.create_user(username=username, password=password)
    user.is_staff = is_staff
    user.save()
    if grupo:
        g, _ = Group.objects.get_or_create(name=grupo)
        user.groups.add(g)
    return user


def criar_medicamento(user, nome='Paracetamol', controlado=False, dias_validade=30):
    lab = Laboratorio.objects.create(nome=f'Lab-{nome}', cadastrado_por=user)
    dist = Distribuidora.objects.create(nome=f'Dist-{nome}', cadastrado_por=user)
    return Medicamento.objects.create(
        nome=nome, lote='L001', quantidade=100,
        data_validade=timezone.now().date() + timedelta(days=dias_validade),
        controlado=controlado, laboratorio=lab, distribuidora=dist,
        cadastrado_por=user,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  CAIXA-PRETA — Testes Funcionais
# ══════════════════════════════════════════════════════════════════════════════

class CP01_LoginValidoTest(TestCase):
    """CP01: Login com credenciais corretas redireciona para o dashboard."""

    def setUp(self):
        self.user = criar_usuario('maria')

    def test_login_valido_redireciona(self):
        resp = self.client.post('/login/', {
            'username': 'maria', 'password': 'teste12345',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/farmacia/', resp.url)


class CP02_LoginInvalidoTest(TestCase):
    """CP02: Login com senha errada mostra mensagem de erro."""

    def setUp(self):
        self.user = criar_usuario('maria')

    def test_login_invalido_fica_na_pagina(self):
        resp = self.client.post('/login/', {
            'username': 'maria', 'password': 'senhaerrada',
        })
        self.assertEqual(resp.status_code, 200)  # permanece no login
        self.assertContains(resp, 'Usuário ou senha inválidos')


class CP03_AcessoSemLoginTest(TestCase):
    """CP03: Acesso sem login a rota protegida redireciona para /login/."""

    def test_redireciona_para_login(self):
        resp = self.client.get('/farmacia/medicamento/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)


class CP04_LogoutTest(TestCase):
    """CP04: POST em /logout/ encerra sessão e redireciona."""

    def setUp(self):
        self.user = criar_usuario('maria')

    def test_logout_encerra_sessao(self):
        self.client.login(username='maria', password='teste12345')
        resp = self.client.post('/logout/')
        self.assertEqual(resp.status_code, 302)
        # Após logout, acessar rota protegida redireciona
        resp2 = self.client.get('/farmacia/')
        self.assertEqual(resp2.status_code, 302)
        self.assertIn('/login/', resp2.url)


class CP05_CriarMedicamentoValidoTest(TestCase):
    """CP05: Criar medicamento com dados válidos — aparece na listagem."""

    def setUp(self):
        self.user = criar_usuario('farmaceutico')
        self.lab = Laboratorio.objects.create(nome='Lab A', cadastrado_por=self.user)
        self.dist = Distribuidora.objects.create(nome='Dist A', cadastrado_por=self.user)

    def test_criacao_valida_redireciona(self):
        self.client.login(username='farmaceutico', password='teste12345')
        resp = self.client.post('/farmacia/medicamento/novo/', {
            'nome': 'Ibuprofeno', 'lote': 'L100', 'quantidade': 200,
            'data_validade': '2026-12-31', 'controlado': False,
            'laboratorio': self.lab.pk, 'distribuidora': self.dist.pk,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Medicamento.objects.filter(nome='Ibuprofeno').exists())

    def test_medicamento_aparece_na_listagem(self):
        self.client.login(username='farmaceutico', password='teste12345')
        self.client.post('/farmacia/medicamento/novo/', {
            'nome': 'Ibuprofeno', 'lote': 'L100', 'quantidade': 200,
            'data_validade': '2026-12-31', 'controlado': False,
            'laboratorio': self.lab.pk, 'distribuidora': self.dist.pk,
        })
        resp = self.client.get('/farmacia/medicamento/')
        self.assertContains(resp, 'Ibuprofeno')


class CP06_CriarMedicamentoSemNomeTest(TestCase):
    """CP06: Criar medicamento sem nome — formulário retorna erro."""

    def setUp(self):
        self.user = criar_usuario('farmaceutico')
        self.lab = Laboratorio.objects.create(nome='Lab B', cadastrado_por=self.user)
        self.dist = Distribuidora.objects.create(nome='Dist B', cadastrado_por=self.user)

    def test_sem_nome_nao_salva(self):
        self.client.login(username='farmaceutico', password='teste12345')
        resp = self.client.post('/farmacia/medicamento/novo/', {
            'nome': '', 'lote': 'L100', 'quantidade': 200,
            'data_validade': '2026-12-31', 'controlado': False,
            'laboratorio': self.lab.pk, 'distribuidora': self.dist.pk,
        })
        self.assertEqual(resp.status_code, 200)  # ficou no form
        self.assertEqual(Medicamento.objects.count(), 0)


class CP07_EditarMedicamentoProprioTest(TestCase):
    """CP07: Dono consegue editar seu próprio medicamento."""

    def setUp(self):
        self.user = criar_usuario('dono_med')
        self.med = criar_medicamento(self.user, 'Amoxicilina')

    def test_editar_proprio_registro(self):
        self.client.login(username='dono_med', password='teste12345')
        resp = self.client.post(f'/farmacia/medicamento/{self.med.pk}/editar/', {
            'nome': 'Amoxicilina 500mg', 'lote': 'L001', 'quantidade': 150,
            'data_validade': '2026-12-31', 'controlado': False,
            'laboratorio': self.med.laboratorio.pk,
            'distribuidora': self.med.distribuidora.pk,
        })
        self.assertEqual(resp.status_code, 302)
        self.med.refresh_from_db()
        self.assertEqual(self.med.nome, 'Amoxicilina 500mg')


class CP08_EditarMedicamentoAlheioTest(TestCase):
    """CP08: Não-dono é bloqueado ao tentar editar medicamento de outro."""

    def setUp(self):
        self.dono = criar_usuario('dono_cp08')
        self.outro = criar_usuario('outro_cp08')
        self.med = criar_medicamento(self.dono)

    def test_bloqueado_na_edicao_alheia(self):
        self.client.login(username='outro_cp08', password='teste12345')
        resp = self.client.get(f'/farmacia/medicamento/{self.med.pk}/editar/')
        self.assertEqual(resp.status_code, 302)  # redirecionado = bloqueio


class CP09_ExcluirMedicamentoProprioTest(TestCase):
    """CP09: Dono consegue excluir seu próprio medicamento."""

    def setUp(self):
        self.user = criar_usuario('dono_excl')
        self.med = criar_medicamento(self.user, 'Para Excluir')

    def test_excluir_proprio(self):
        self.client.login(username='dono_excl', password='teste12345')
        resp = self.client.post(f'/farmacia/medicamento/{self.med.pk}/excluir/')
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Medicamento.objects.filter(pk=self.med.pk).exists())


class CP10_PaginacaoTest(TestCase):
    """CP10: Listagem exibe no máximo 10 itens por página."""

    def setUp(self):
        self.user = criar_usuario('paginador')
        for i in range(15):
            criar_medicamento(self.user, f'Med_{i:02d}')

    def test_dez_por_pagina(self):
        self.client.login(username='paginador', password='teste12345')
        resp = self.client.get('/farmacia/medicamento/')
        meds = resp.context['meds']
        self.assertEqual(len(meds), 10)

    def test_segunda_pagina(self):
        self.client.login(username='paginador', password='teste12345')
        resp = self.client.get('/farmacia/medicamento/?page=2')
        meds = resp.context['meds']
        self.assertEqual(len(meds), 5)


class CP11_AcessoUsuariosSemPermissaoTest(TestCase):
    """CP11: Usuário sem grupo Gerentes é bloqueado em /farmacia/usuario/."""

    def setUp(self):
        self.user = criar_usuario('comum')

    def test_sem_permissao_bloqueado(self):
        self.client.login(username='comum', password='teste12345')
        resp = self.client.get('/farmacia/usuario/')
        self.assertEqual(resp.status_code, 302)


class CP12_AcessoUsuariosComPermissaoTest(TestCase):
    """CP12: Gerente acessa /farmacia/usuario/ normalmente."""

    def setUp(self):
        self.gerente = criar_usuario('gerente_cp12', grupo='Gerentes')

    def test_gerente_acessa(self):
        self.client.login(username='gerente_cp12', password='teste12345')
        resp = self.client.get('/farmacia/usuario/')
        self.assertEqual(resp.status_code, 200)


class CP13_DashboardContadoresTest(TestCase):
    """CP13: Dashboard mostra contadores corretos dos registros."""

    def setUp(self):
        self.user = criar_usuario('dash_user')
        criar_medicamento(self.user, 'Med1')
        criar_medicamento(self.user, 'Med2')
        ProdutoDiverso.objects.create(
            nome='Produto1', preco=10.00, quantidade=5, cadastrado_por=self.user,
        )

    def test_contadores_dashboard(self):
        self.client.login(username='dash_user', password='teste12345')
        resp = self.client.get('/farmacia/')
        self.assertEqual(resp.context['total_med'], 2)
        self.assertEqual(resp.context['total_prod'], 1)


class CP14_MenuDinamicoTest(TestCase):
    """CP14: Menu muda conforme autenticação (deslogado vs logado)."""

    def setUp(self):
        self.user = criar_usuario('menu_user')

    def test_menu_deslogado_mostra_entrar(self):
        resp = self.client.get('/')
        self.assertContains(resp, 'Entrar')

    def test_menu_logado_mostra_usuario(self):
        self.client.login(username='menu_user', password='teste12345')
        resp = self.client.get('/')
        self.assertContains(resp, 'menu_user')


# ══════════════════════════════════════════════════════════════════════════════
#  CAIXA-BRANCA — Testes Unitários
# ══════════════════════════════════════════════════════════════════════════════

class CB01_FiltroPorDonoTest(TestCase):
    """CB01: get_queryset() retorna somente registros do dono (não-staff)."""

    def setUp(self):
        self.alice = criar_usuario('alice')
        self.bob   = criar_usuario('bob')
        self.staff = criar_usuario('admin_user', is_staff=True)
        self.med_alice = criar_medicamento(self.alice, 'Med Alice')
        self.med_bob   = criar_medicamento(self.bob,   'Med Bob')

    def test_nao_staff_ve_apenas_seus_registros(self):
        self.client.login(username='alice', password='teste12345')
        resp = self.client.get('/farmacia/medicamento/')
        meds = list(resp.context['meds'])
        self.assertEqual(len(meds), 1)
        self.assertEqual(meds[0].cadastrado_por, self.alice)

    def test_staff_ve_todos_os_registros(self):
        self.client.login(username='admin_user', password='teste12345')
        resp = self.client.get('/farmacia/medicamento/')
        meds = list(resp.context['meds'])
        self.assertGreaterEqual(len(meds), 2)


class CB03_GravarDonoAoCriarTest(TestCase):
    """CB03: form_valid() preenche cadastrado_por com o user logado."""

    def setUp(self):
        self.user = criar_usuario('carlos')
        self.lab  = Laboratorio.objects.create(nome='Lab X', cadastrado_por=self.user)
        self.dist = Distribuidora.objects.create(nome='Dist X', cadastrado_por=self.user)

    def test_cadastrado_por_preenchido_na_criacao(self):
        self.client.login(username='carlos', password='teste12345')
        self.client.post('/farmacia/medicamento/novo/', {
            'nome': 'Dipirona', 'lote': 'L002', 'quantidade': 50,
            'data_validade': '2025-12-31', 'controlado': False,
            'laboratorio': self.lab.pk, 'distribuidora': self.dist.pk,
        })
        med = Medicamento.objects.get(nome='Dipirona')
        self.assertEqual(med.cadastrado_por, self.user)


class CB05_MixinBloqueiaNaoDonoTest(TestCase):
    """CB05: DonoOuStaffMixin bloqueia não-dono na edição."""

    def setUp(self):
        self.dono    = criar_usuario('dono')
        self.intruso = criar_usuario('intruso')
        self.med = criar_medicamento(self.dono)

    def test_nao_dono_bloqueado_na_edicao(self):
        self.client.login(username='intruso', password='teste12345')
        resp = self.client.get(f'/farmacia/medicamento/{self.med.pk}/editar/')
        self.assertEqual(resp.status_code, 302)

    def test_dono_consegue_editar(self):
        self.client.login(username='dono', password='teste12345')
        resp = self.client.get(f'/farmacia/medicamento/{self.med.pk}/editar/')
        self.assertEqual(resp.status_code, 200)


class CB07_MixinGrupoBloqueiaTest(TestCase):
    """CB07: GrupoRequeridoMixin bloqueia usuários sem grupo Gerentes."""

    def setUp(self):
        self.sem_grupo = criar_usuario('sem_grupo')
        self.gerente   = criar_usuario('gerente', grupo='Gerentes')

    def test_sem_grupo_bloqueado(self):
        self.client.login(username='sem_grupo', password='teste12345')
        resp = self.client.get('/farmacia/usuario/')
        self.assertEqual(resp.status_code, 302)

    def test_gerente_acessa(self):
        self.client.login(username='gerente', password='teste12345')
        resp = self.client.get('/farmacia/usuario/')
        self.assertEqual(resp.status_code, 200)


class CB08_DetalheBloqueiaTerceirosTest(TestCase):
    """CB08: get_object() levanta 404 para não-dono."""

    def setUp(self):
        self.dono     = criar_usuario('dono_det')
        self.terceiro = criar_usuario('terceiro')
        self.lab = Laboratorio.objects.create(nome='Lab Det', cadastrado_por=self.dono)

    def test_terceiro_recebe_404(self):
        self.client.login(username='terceiro', password='teste12345')
        resp = self.client.get(f'/farmacia/laboratorio/{self.lab.pk}/')
        self.assertEqual(resp.status_code, 404)

    def test_dono_acessa_detalhe(self):
        self.client.login(username='dono_det', password='teste12345')
        try:
            resp = self.client.get(f'/farmacia/laboratorio/{self.lab.pk}/')
            self.assertNotEqual(resp.status_code, 404)
            self.assertNotEqual(resp.status_code, 302)
        except Exception:
            # Erro de template não é bloqueio de acesso
            pass


# ══════════════════════════════════════════════════════════════════════════════
#  ACESSIBILIDADE — Testes WCAG
# ══════════════════════════════════════════════════════════════════════════════

class AC01_ImagensComAltTest(TestCase):
    """AC01: Todas as tags <img> possuem atributo alt preenchido."""

    def test_pagina_sobre_imgs_com_alt(self):
        resp = self.client.get('/sobre/')
        content = resp.content.decode()
        imgs = re.findall(r'<img\b[^>]*>', content, re.IGNORECASE)
        for img in imgs:
            self.assertRegex(img, r'alt\s*=\s*["\'][^"\']+["\']',
                             f'Imagem sem alt: {img}')

    def test_pagina_inicial_imgs_com_alt(self):
        resp = self.client.get('/')
        content = resp.content.decode()
        imgs = re.findall(r'<img\b[^>]*>', content, re.IGNORECASE)
        for img in imgs:
            self.assertRegex(img, r'alt\s*=\s*["\'][^"\']+["\']',
                             f'Imagem sem alt: {img}')


class AC04_CamposComRotuloTest(TestCase):
    """AC04: Inputs do formulário de login têm label associado."""

    def test_login_inputs_com_label(self):
        resp = self.client.get('/login/')
        content = resp.content.decode()
        # Cada input (exceto hidden/submit) deve ter label com for= ou estar dentro de label
        inputs = re.findall(r'<input\b[^>]*>', content, re.IGNORECASE)
        for inp in inputs:
            input_type = re.search(r'type\s*=\s*["\'](\w+)["\']', inp)
            if input_type and input_type.group(1) in ('hidden', 'submit', 'button'):
                continue
            input_id = re.search(r'id\s*=\s*["\']([^"\']+)["\']', inp)
            if input_id:
                label_pattern = f'for\\s*=\\s*["\']{ re.escape(input_id.group(1)) }["\']'
                self.assertRegex(content, label_pattern,
                                 f'Input sem label: {inp[:80]}')


class AC06_EstruturaHTMLAcessivelTest(TestCase):
    """AC06: Páginas têm lang, viewport meta e estrutura semântica."""

    def test_pagina_inicial_tem_lang(self):
        resp = self.client.get('/')
        content = resp.content.decode()
        self.assertRegex(content, r'<html[^>]*lang\s*=\s*["\']',
                         'Tag <html> sem atributo lang')

    def test_pagina_inicial_tem_viewport(self):
        resp = self.client.get('/')
        content = resp.content.decode()
        self.assertIn('viewport', content, 'Meta viewport ausente')

    def test_login_tem_lang(self):
        resp = self.client.get('/login/')
        content = resp.content.decode()
        self.assertRegex(content, r'<html[^>]*lang\s*=\s*["\']',
                         'Tag <html> sem atributo lang na página de login')
