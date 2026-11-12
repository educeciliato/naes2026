"""Testes dos requisitos: django-filter + paginação que preserva a busca,
registros por dono, mensagens, plugins jQuery e consultas sem N+1."""
from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.contrib.messages import get_messages
from django.db import connection
from django.template import Context, Template
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from .forms import MedicamentoForm
from .models import Distribuidora, Laboratorio, Medicamento, ProdutoDiverso

SENHA = 'teste12345'


def usuario(username, **extra):
    return User.objects.create_user(username=username, password=SENHA, **extra)


def medicamento(dono, nome='Dipirona', dias=90, controlado=False, lab=None, dist=None):
    lab = lab or Laboratorio.objects.create(nome=f'Lab {nome}', cadastrado_por=dono)
    dist = dist or Distribuidora.objects.create(nome=f'Dist {nome}', cadastrado_por=dono)
    return Medicamento.objects.create(
        nome=nome, lote='L1', quantidade=10, controlado=controlado,
        data_validade=timezone.localdate() + timedelta(days=dias),
        laboratorio=lab, distribuidora=dist, cadastrado_por=dono)


def mensagens(response):
    """Só a última mensagem (sem follow=True, as anteriores ainda não foram exibidas)."""
    return [str(m) for m in get_messages(response.wsgi_request)][-1:]


class FiltrosEPaginacaoTest(TestCase):
    def setUp(self):
        self.ana = usuario('ana')
        self.client.force_login(self.ana)
        self.lab = Laboratorio.objects.create(nome='EMS', cadastrado_por=self.ana)
        self.dist = Distribuidora.objects.create(nome='Distrib', cadastrado_por=self.ana)

    def test_filtra_medicamentos_por_nome_controlado_e_validade(self):
        medicamento(self.ana, 'Dipirona', lab=self.lab, dist=self.dist)
        medicamento(self.ana, 'Rivotril', controlado=True, lab=self.lab, dist=self.dist)
        medicamento(self.ana, 'Vencido', dias=-1, lab=self.lab, dist=self.dist)
        medicamento(self.ana, 'Quase', dias=10, lab=self.lab, dist=self.dist)
        url = reverse('medicamento_listar')
        nomes = lambda r: sorted(m.nome for m in r.context['meds'])  # noqa: E731
        self.assertEqual(nomes(self.client.get(url, {'nome': 'dipi'})), ['Dipirona'])
        self.assertEqual(nomes(self.client.get(url, {'controlado': 'true'})), ['Rivotril'])
        self.assertEqual(nomes(self.client.get(url, {'situacao': 'vencido'})), ['Vencido'])
        self.assertEqual(nomes(self.client.get(url, {'situacao': 'a_vencer'})), ['Quase'])

    def test_filtra_produtos_por_preco_e_status(self):
        ProdutoDiverso.objects.create(nome='Shampoo', preco=10, cadastrado_por=self.ana)
        ProdutoDiverso.objects.create(nome='Perfume', preco=200, cadastrado_por=self.ana)
        ProdutoDiverso.objects.create(nome='Velho', preco=50, ativo=False, cadastrado_por=self.ana)
        r = self.client.get(reverse('produto_listar'), {'preco_min': '20', 'ativo': 'true'})
        self.assertEqual([p.nome for p in r.context['prods']], ['Perfume'])

    def test_paginacao_preserva_os_filtros(self):
        for i in range(15):
            medicamento(self.ana, f'Dipirona {i:02d}', lab=self.lab, dist=self.dist)
        medicamento(self.ana, 'Outro', lab=self.lab, dist=self.dist)
        r = self.client.get(reverse('medicamento_listar'), {'nome': 'dipirona'})
        self.assertEqual(r.context['page_obj'].paginator.count, 15)
        self.assertEqual(len(r.context['meds']), 10)
        self.assertContains(r, 'href="?nome=dipirona&amp;page=2" rel="next"')
        r2 = self.client.get(reverse('medicamento_listar'), {'nome': 'dipirona', 'page': 2})
        self.assertEqual(len(r2.context['meds']), 5)
        self.assertContains(r2, 'href="?nome=dipirona&amp;page=1" rel="prev"')

    def test_todas_as_listas_do_dono_tem_filtro(self):
        for nome in ('medicamento_listar', 'produto_listar', 'laboratorio_listar',
                     'distribuidora_listar', 'farmacia_listar'):
            with self.subTest(nome):
                r = self.client.get(reverse(nome))
                self.assertIn('filter', r.context)
                self.assertContains(r, 'form-filtro')

    def test_opcoes_do_filtro_so_tem_laboratorios_do_usuario(self):
        Laboratorio.objects.create(nome='Lab do Bruno', cadastrado_por=usuario('bruno'))
        r = self.client.get(reverse('medicamento_listar'))
        opcoes = list(r.context['filter'].form.fields['laboratorio'].queryset)
        self.assertEqual(opcoes, [self.lab])
        self.assertNotContains(r, 'Lab do Bruno')


class UrlComParametrosTest(TestCase):
    def render(self, query, codigo):
        request = RequestFactory().get('/lista/', query)
        return Template('{% load url_params %}' + codigo).render(Context({'request': request}))

    def test_troca_so_a_pagina(self):
        html = self.render({'nome': 'a b', 'page': '3', 'ativo': 'true'}, '{% url_com_parametros page=4 %}')
        self.assertEqual(html, '?nome=a+b&amp;page=4&amp;ativo=true')

    def test_remove_parametro_vazio(self):
        self.assertEqual(self.render({'nome': 'x', 'page': '2'}, '{% url_com_parametros page=None %}'), '?nome=x')


class DonoTest(TestCase):
    def setUp(self):
        self.ana, self.bruno = usuario('ana'), usuario('bruno', is_staff=True)
        self.med = medicamento(self.ana)

    def test_outro_usuario_nao_lista_nem_acessa(self):
        self.client.force_login(self.bruno)  # mesmo sendo staff
        self.assertNotContains(self.client.get(reverse('medicamento_listar')), 'Dipirona')
        for nome in ('medicamento_detalhe', 'medicamento_editar', 'medicamento_excluir'):
            with self.subTest(nome):
                self.assertEqual(self.client.get(reverse(nome, args=[self.med.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('medicamento_excluir', args=[self.med.pk])).status_code, 404)
        self.assertTrue(Medicamento.objects.filter(pk=self.med.pk).exists())
        lab = self.med.laboratorio
        self.assertEqual(self.client.post(reverse('laboratorio_editar', args=[lab.pk]),
                                          {'nome': 'Hack', 'ativo': 'on'}).status_code, 404)

    def test_form_so_oferece_laboratorios_do_usuario(self):
        lab_bruno = Laboratorio.objects.create(nome='Lab Bruno', cadastrado_por=self.bruno)
        form = MedicamentoForm(usuario=self.ana)
        self.assertEqual(list(form.fields['laboratorio'].queryset), [self.med.laboratorio])
        self.client.force_login(self.ana)
        r = self.client.post(reverse('medicamento_novo'), {
            'nome': 'X', 'lote': '1', 'quantidade': 1, 'data_validade': '2030-01-01',
            'laboratorio': lab_bruno.pk, 'distribuidora': self.med.distribuidora.pk})
        self.assertEqual(r.status_code, 200)
        self.assertIn('laboratorio', r.context['form'].errors)

    def test_dono_ve_detalhe_com_campos(self):
        self.client.force_login(self.ana)
        r = self.client.get(reverse('medicamento_detalhe', args=[self.med.pk]))
        self.assertContains(r, 'Data de validade')
        self.assertContains(r, 'Lab Dipirona')
        self.assertContains(r, reverse('medicamento_editar', args=[self.med.pk]))


class MensagensTest(TestCase):
    def setUp(self):
        self.ana = usuario('ana')
        self.client.force_login(self.ana)

    def test_cadastro_alteracao_e_exclusao_mostram_mensagem(self):
        r = self.client.post(reverse('distribuidora_novo'), {'nome': 'Profarma', 'cnpj': '12.345.678/0001-90',
                                                            'ativo': 'on'}, follow=True)
        self.assertContains(r, 'Distribuidora &quot;Profarma&quot; cadastrada com sucesso.')
        dist = Distribuidora.objects.get()
        self.assertEqual(dist.cadastrado_por, self.ana)

        r = self.client.post(reverse('distribuidora_editar', args=[dist.pk]), {'nome': 'Profarma SA'})
        self.assertEqual(mensagens(r), ['Distribuidora "Profarma SA" atualizada com sucesso.'])

        r = self.client.post(reverse('distribuidora_excluir', args=[dist.pk]))
        self.assertEqual(mensagens(r), ['Distribuidora "Profarma SA" excluída com sucesso.'])
        self.assertFalse(Distribuidora.objects.exists())

    def test_exclusao_protegida_vira_mensagem_de_erro(self):
        med = medicamento(self.ana)
        r = self.client.post(reverse('laboratorio_excluir', args=[med.laboratorio.pk]), follow=True)
        self.assertContains(r, 'Não foi possível excluir')
        self.assertContains(r, 'alert-danger')
        self.assertTrue(Laboratorio.objects.filter(pk=med.laboratorio.pk).exists())

    def test_gerente_recebe_mensagens_em_usuarios_e_grupos(self):
        self.ana.is_staff = True
        self.ana.save()
        r = self.client.post(reverse('grupo_novo'), {'name': 'Balconistas'})
        self.assertEqual(mensagens(r), ['Grupo "Balconistas" cadastrado com sucesso.'])
        bruno = usuario('bruno')
        r = self.client.post(reverse('usuario_editar', args=[bruno.pk]),
                             {'username': 'bruno', 'is_active': 'on', 'groups': [Group.objects.get().pk]})
        self.assertEqual(mensagens(r), ['Usuário "bruno" atualizado com sucesso.'])
        self.assertTrue(User.objects.get(pk=bruno.pk).has_usable_password())  # senha preservada


class PluginsJQueryTest(TestCase):
    def test_modelo_carrega_jquery_e_plugins(self):
        ana = usuario('ana')
        self.client.force_login(ana)
        r = self.client.get(reverse('distribuidora_novo'))
        for trecho in ('jquery.min.js', 'jquery.mask.min.js', 'bootbox.min.js', 'dataTables.min.js',
                       'js/site.js', 'mascara-cnpj'):
            self.assertContains(r, trecho)
        medicamento(ana)
        self.assertContains(self.client.get(reverse('medicamento_listar')), 'data-confirmar=')

    def test_css_do_site_existe(self):
        # O modelo apontava para css/pharma.css, que não existe.
        self.assertContains(self.client.get('/'), 'css/farma.css')


class ConsultasTest(TestCase):
    """Debug Toolbar mostrou queries repetidas; estes testes travam a correção."""

    def medir(self, url):
        with CaptureQueriesContext(connection) as ctx:
            self.assertEqual(self.client.get(url).status_code, 200)
        return len(ctx)

    def test_lista_de_medicamentos_nao_cresce_com_os_registros(self):
        ana = usuario('ana')
        self.client.force_login(ana)
        for i in range(2):
            medicamento(ana, f'M{i}')
        poucas = self.medir(reverse('medicamento_listar'))
        for i in range(2, 10):
            medicamento(ana, f'M{i}')  # cada um com laboratório próprio
        self.assertEqual(self.medir(reverse('medicamento_listar')), poucas)

    def test_lista_de_grupos_usa_annotate(self):
        gerente = usuario('gerente', is_staff=True)
        self.client.force_login(gerente)
        Group.objects.create(name='G0').user_set.add(gerente)
        poucas = self.medir(reverse('grupo_listar'))
        for i in range(1, 8):
            Group.objects.create(name=f'G{i}').user_set.add(gerente)
        self.assertEqual(self.medir(reverse('grupo_listar')), poucas)
        self.assertEqual(self.client.get(reverse('grupo_listar')).context['grupos'][0].num_membros, 1)

    def test_lista_de_usuarios_usa_prefetch_dos_grupos(self):
        gerente = usuario('gerente', is_staff=True)
        self.client.force_login(gerente)
        g = Group.objects.create(name='Balcão')
        usuario('u0').groups.add(g)
        poucas = self.medir(reverse('usuario_listar'))
        for i in range(1, 8):
            usuario(f'u{i}').groups.add(g)
        self.assertEqual(self.medir(reverse('usuario_listar')), poucas)
