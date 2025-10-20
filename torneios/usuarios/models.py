from django.db import models
from django.contrib.auth.models import User

class Torneio(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    regras = models.TextField()
    data = models.DateField()
    criador = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome


class Inscricao(models.Model):
    jogador = models.CharField(max_length=100)
    equipe = models.CharField(max_length=100, blank=True, null=True)
    torneio = models.ForeignKey(Torneio, on_delete=models.CASCADE, related_name='inscricoes')
    data_inscricao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.jogador} - {self.torneio.nome}"