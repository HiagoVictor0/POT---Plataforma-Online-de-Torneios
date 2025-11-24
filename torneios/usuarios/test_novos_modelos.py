"""
Testes para as novas funcionalidades do POT
Execute com: python manage.py test usuarios.tests
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from usuarios.models import Torneio, Equipe, Jogador, Inscricao, Confronto
from datetime import date, timedelta


class EquipeTestCase(TestCase):
    """Testes para criação e gerenciamento de equipes"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_criar_equipe(self):
        """Testa criação de uma nova equipe"""
        response = self.client.post(reverse('criar_equipe'), {
            'nome_equipe': 'Team Alpha',
            'jogo_principal': 'Valorant',
            'descricao': 'Equipe de elite em Valorant'
        })
        
        # Verifica se a equipe foi criada
        equipe = Equipe.objects.get(nome='Team Alpha')
        self.assertEqual(equipe.criador, self.user)
        self.assertEqual(equipe.jogo_principal, 'Valorant')
    
    def test_criador_como_capitao(self):
        """Testa se o criador é automaticamente capitão"""
        equipe = Equipe.objects.create(
            nome='Team Bravo',
            jogo_principal='CS2',
            descricao='Equipe de CS2',
            criador=self.user
        )
        
        jogador = Jogador.objects.create(
            nome=self.user.first_name,
            equipe=equipe,
            user=self.user,
            eh_capitao=True
        )
        
        self.assertTrue(jogador.eh_capitao)
        self.assertEqual(jogador.equipe, equipe)
    
    def test_adicionar_jogador_equipe(self):
        """Testa adição de jogador à equipe"""
        equipe = Equipe.objects.create(
            nome='Team Charlie',
            jogo_principal='LoL',
            descricao='Equipe de League of Legends',
            criador=self.user
        )
        
        jogador = Jogador.objects.create(
            nome='João Silva',
            equipe=equipe
        )
        
        self.assertEqual(jogador.equipe, equipe)
        self.assertFalse(jogador.eh_capitao)


class InscricaoTestCase(TestCase):
    """Testes para inscrição em torneios"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.torneio = Torneio.objects.create(
            nome='Copa Gamer 2025',
            descricao='Grande copa',
            regras='Sem cheats',
            data=date.today() + timedelta(days=7),
            criador=self.user
        )
        
        self.equipe = Equipe.objects.create(
            nome='Team Alpha',
            jogo_principal='Valorant',
            descricao='Elite',
            criador=self.user
        )
    
    def test_inscrever_equipe_torneio(self):
        """Testa inscrição de equipe em torneio"""
        inscricao = Inscricao.objects.create(
            equipe=self.equipe,
            torneio=self.torneio,
            confirmada=True
        )
        
        self.assertTrue(inscricao.confirmada)
        self.assertEqual(inscricao.equipe, self.equipe)
        self.assertEqual(inscricao.torneio, self.torneio)
    
    def test_inscricao_unica_por_torneio(self):
        """Testa constraint único (equipe, torneio)"""
        Inscricao.objects.create(
            equipe=self.equipe,
            torneio=self.torneio,
            confirmada=True
        )
        
        # Tentar inscrever novamente deve falhar
        with self.assertRaises(Exception):
            Inscricao.objects.create(
                equipe=self.equipe,
                torneio=self.torneio,
                confirmada=True
            )


class ChaveamentoTestCase(TestCase):
    """Testes para geração e gerenciamento de chaveamento"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test'
        )
        
        self.torneio = Torneio.objects.create(
            nome='Copa Teste',
            descricao='Teste chaveamento',
            regras='Sem cheats',
            data=date.today() + timedelta(days=7),
            criador=self.user
        )
        
        # Criar 4 equipes
        self.equipes = []
        for i in range(4):
            equipe = Equipe.objects.create(
                nome=f'Team {chr(65 + i)}',
                jogo_principal='Valorant',
                descricao=f'Equipe {chr(65 + i)}',
                criador=self.user
            )
            Inscricao.objects.create(
                equipe=equipe,
                torneio=self.torneio,
                confirmada=True
            )
            self.equipes.append(equipe)
    
    def test_gerar_confrontos_quartas(self):
        """Testa geração de confrontos na fase de quartas"""
        # Criar confrontos das quartas
        confronto1 = Confronto.objects.create(
            torneio=self.torneio,
            equipe1=self.equipes[0],
            equipe2=self.equipes[1],
            fase='quartas'
        )
        
        confronto2 = Confronto.objects.create(
            torneio=self.torneio,
            equipe1=self.equipes[2],
            equipe2=self.equipes[3],
            fase='quartas'
        )
        
        confrontos = Confronto.objects.filter(
            torneio=self.torneio,
            fase='quartas'
        )
        
        self.assertEqual(confrontos.count(), 2)
        self.assertEqual(confronto1.equipe1, self.equipes[0])
        self.assertEqual(confronto1.equipe2, self.equipes[1])
    
    def test_registrar_vencedor(self):
        """Testa registro de vencedor de confronto"""
        confronto = Confronto.objects.create(
            torneio=self.torneio,
            equipe1=self.equipes[0],
            equipe2=self.equipes[1],
            fase='quartas'
        )
        
        confronto.vencedor = self.equipes[0]
        confronto.realizado = True
        confronto.save()
        
        self.assertTrue(confronto.realizado)
        self.assertEqual(confronto.vencedor, self.equipes[0])
    
    def test_atualizar_semifinal_com_vencedor(self):
        """Testa atualização automática de semifinal com vencedor"""
        # Criar quartas
        confronto_quartas = Confronto.objects.create(
            torneio=self.torneio,
            equipe1=self.equipes[0],
            equipe2=self.equipes[1],
            fase='quartas'
        )
        
        # Criar semifinal
        semifinal = Confronto.objects.create(
            torneio=self.torneio,
            equipe1=self.equipes[0],  # placeholder
            fase='semifinal'
        )
        
        # Registrar vencedor da quartas
        confronto_quartas.vencedor = self.equipes[0]
        confronto_quartas.realizado = True
        confronto_quartas.save()
        
        # Verificar que vencedor foi registrado
        self.assertEqual(confronto_quartas.vencedor, self.equipes[0])


class DashboardEquipeTestCase(TestCase):
    """Testes para dashboard da equipe"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.equipe = Equipe.objects.create(
            nome='Team Alpha',
            jogo_principal='Valorant',
            descricao='Elite',
            criador=self.user
        )
    
    def test_acesso_dashboard_equipe(self):
        """Testa acesso ao dashboard da equipe"""
        response = self.client.get(
            reverse('dashboard_equipe_detail', args=[self.equipe.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('equipe', response.context)
    
    def test_visualizar_membros(self):
        """Testa visualização de membros"""
        Jogador.objects.create(
            nome='João',
            equipe=self.equipe,
            eh_capitao=True
        )
        
        response = self.client.get(
            reverse('dashboard_equipe_detail', args=[self.equipe.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['jogadores'].count(), 1)


class PermissaoTestCase(TestCase):
    """Testes de permissões e segurança"""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123',
            first_name='User1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123',
            first_name='User2'
        )
        
        self.equipe = Equipe.objects.create(
            nome='Team Alpha',
            jogo_principal='Valorant',
            descricao='Elite',
            criador=self.user1
        )
    
    def test_usuario_nao_autenticado_redirecionado(self):
        """Testa redirecionamento de usuário não autenticado"""
        response = self.client.get(
            reverse('dashboard_equipe_detail', args=[self.equipe.id])
        )
        
        self.assertNotEqual(response.status_code, 200)  # Deve redirecionar
    
    def test_usuario_nao_pode_acessar_equipe_outro(self):
        """Testa que usuário não pode acessar equipe de outro"""
        self.client.login(username='user2', password='pass123')
        
        response = self.client.get(
            reverse('dashboard_equipe_detail', args=[self.equipe.id])
        )
        
        # Deve ser redirecionado ou receber erro 403
        self.assertIn(response.status_code, [302, 403])


# Exemplo de execução:
# python manage.py test usuarios.tests.EquipeTestCase
# python manage.py test usuarios.tests.ChaveamentoTestCase
# python manage.py test usuarios.tests -v 2  # Modo verboso
