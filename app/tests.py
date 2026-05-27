from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Categoria, Transacao, ContaAgendada
import datetime

class BaseTestCase(TestCase): #base de testes para os testes seguintes herdarem
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='nicolas',
            password='senha123'
        )
        self.outro_user = User.objects.create_user(
            username='outro',
            password='senha123'
        )
        response = self.client.post('/api/token/', {
            'username': 'nicolas',
            'password': 'senha123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')





#-----------------------#

# Testes Categorias 

#------------------------#

class CategoriaTestCase(BaseTestCase):  

    def test_criar_categoria(self):
        response = self.client.post('/api/categorias/', {
            'nome': 'Alimentação',
            'tipo': 'despesa'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Categoria.objects.count(), 1)

    def test_listar_categorias(self):
        Categoria.objects.create(usuario=self.user, nome='Alimentação', tipo='despesa')
        Categoria.objects.create(usuario=self.user, nome='Salário', tipo='receita')
        response = self.client.get('/api/categorias/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_isolamento_categoria(self):
        Categoria.objects.create(usuario=self.outro_user, nome='Outro', tipo='despesa')
        response = self.client.get('/api/categorias/')
        self.assertEqual(len(response.data), 0)

    def test_deletar_categoria(self):
        categoria = Categoria.objects.create(usuario=self.user, nome='Alimentação', tipo='despesa')
        response = self.client.delete(f'/api/categorias/{categoria.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Categoria.objects.count(), 0)

    def test_sem_autenticacao_retorna_401(self):
        self.client.credentials()
        response = self.client.get('/api/categorias/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)





#-----------------------#

# Testes Transação 

#------------------------#


class TransacaoTestCase(BaseTestCase):   

    def setUp(self):
        super().setUp()
        self.categoria = Categoria.objects.create(
            usuario=self.user,
            nome='Alimentação',
            tipo='despesa'
        )

    def test_criar_transacao(self):
        response = self.client.post('/api/transacoes/', {
            'descricao': 'Almoço',
            'valor': '25.00',
            'tipo': 'despesa',
            'data': '2026-05-25',
            'categoria': self.categoria.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transacao.objects.count(), 1)

    def test_listar_transacoes(self):
        Transacao.objects.create(
            usuario=self.user,
            descricao='Almoço',
            valor='25.00',
            tipo='despesa',
            data='2026-05-25',
            categoria=self.categoria
        )
        response = self.client.get('/api/transacoes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filtro_por_mes(self):
        Transacao.objects.create(
            usuario=self.user, descricao='Almoço', valor='25.00',
            tipo='despesa', data='2026-05-25', categoria=self.categoria
        )
        Transacao.objects.create(
            usuario=self.user, descricao='Jantar', valor='30.00',
            tipo='despesa', data='2026-04-10', categoria=self.categoria
        )
        response = self.client.get('/api/transacoes/?mes=2026-05')
        self.assertEqual(len(response.data), 1) 





#------------------------#

# Testes Contas agendadas 

#------------------------#


class ContaAgendadaTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.categoria = Categoria.objects.create(
            usuario=self.user,
            nome='Contas',
            tipo='despesa'
        )
        self.conta = ContaAgendada.objects.create(
            usuario=self.user,
            descricao='Aluguel',
            valor='1500.00',
            tipo='despesa',
            vencimento='2026-05-30',
            categoria=self.categoria
        )

    def test_criar_conta_agendada(self):
        response = self.client.post('/api/contas/', {
            'descricao': 'Internet',
            'valor': '100.00',
            'tipo': 'despesa',
            'vencimento': '2026-06-10',
            'categoria': self.categoria.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContaAgendada.objects.count(), 2)

    def test_marcar_como_paga_cria_transacao(self):
        response = self.client.patch(f'/api/contas/{self.conta.id}/', {
            'paga': True
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Transacao.objects.count(), 1)
        transacao = Transacao.objects.first()        





#-------------------------#

# Testes Resumo financeiro 

#-------------------------#


class ResumoFinanceiroTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.categoria = Categoria.objects.create(
            usuario=self.user,
            nome='Alimentação',
            tipo='despesa'
        )
        Transacao.objects.create(
            usuario=self.user, descricao='Salário', valor='3000.00',
            tipo='receita', data='2026-05-01', categoria=self.categoria
        )
        Transacao.objects.create(
            usuario=self.user, descricao='Almoço', valor='500.00',
            tipo='despesa', data='2026-05-10', categoria=self.categoria
        )

    def test_resumo_calcula_saldo(self):
        response = self.client.get('/api/resumo/?mes=2026-05')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['total_receitas']), 3000.00)
        self.assertEqual(float(response.data['total_despesas']), 500.00)
        self.assertEqual(float(response.data['saldo']), 2500.00)

    def test_resumo_sem_mes_usa_mes_atual(self):
        response = self.client.get('/api/resumo/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mes', response.data)

    def test_resumo_por_categoria(self):
        response = self.client.get('/api/resumo/?mes=2026-05')
        self.assertEqual(len(response.data['por_categoria']), 1)
        self.assertEqual(response.data['por_categoria'][0]['categoria'], 'Alimentação')
        self.assertEqual(float(response.data['por_categoria'][0]['total']), 500.00)

    def test_resumo_sem_autenticacao_retorna_401(self):
        self.client.credentials()
        response = self.client.get('/api/resumo/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)        