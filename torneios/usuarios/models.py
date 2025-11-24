from django.db import models
from django.contrib.auth.models import User

class Torneio(models.Model):
    FASES = [
        ('inscricoes', 'Inscrições'),
        ('chaveamento', 'Chaveamento'),
        ('em_progresso', 'Em Progresso'),
        ('finalizado', 'Finalizado'),
    ]
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    regras = models.TextField()
    data = models.DateField()
    criador = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=FASES, default='inscricoes')
    campeao = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nome


class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    jogo_principal = models.CharField(max_length=100)
    descricao = models.TextField()
    criador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='equipes')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Jogador(models.Model):
    nome = models.CharField(max_length=100)
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='jogadores')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    eh_capitao = models.BooleanField(default=False)
    data_entrada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.equipe.nome}"


class Inscricao(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='inscricoes')
    torneio = models.ForeignKey(Torneio, on_delete=models.CASCADE, related_name='inscricoes')
    data_inscricao = models.DateTimeField(auto_now_add=True)
    confirmada = models.BooleanField(default=False)

    class Meta:
        unique_together = ('equipe', 'torneio')

    def __str__(self):
        return f"{self.equipe.nome} - {self.torneio.nome}"


class Confronto(models.Model):
    FASES = [
        ('quartas', 'Quartas'),
        ('semifinal', 'Semifinal'),
        ('final', 'Final'),
    ]
    
    torneio = models.ForeignKey(Torneio, on_delete=models.CASCADE, related_name='confrontos')
    equipe1 = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='confrontos_equipe1')
    equipe2 = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='confrontos_equipe2', null=True, blank=True)
    fase = models.CharField(max_length=20, choices=FASES)
    vencedor = models.ForeignKey(Equipe, on_delete=models.SET_NULL, null=True, blank=True, related_name='confrontos_vencidos')
    data_confronto = models.DateTimeField(null=True, blank=True)
    realizado = models.BooleanField(default=False)

    def __str__(self):
        equipe2_nome = self.equipe2.nome if self.equipe2 else "Aguardando"
        return f"{self.equipe1.nome} vs {equipe2_nome} ({self.fase})"

    class Meta:
        ordering = ['fase', 'id']