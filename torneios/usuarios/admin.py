from django.contrib import admin
from .models import Torneio, Equipe, Jogador, Inscricao, Confronto

@admin.register(Torneio)
class TorneioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data', 'criador', 'status', 'campeao')
    list_filter = ('status', 'data', 'criador')
    search_fields = ('nome', 'descricao')
    fields = ('nome', 'descricao', 'regras', 'data', 'criador', 'status', 'campeao')


@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'jogo_principal', 'criador', 'data_criacao')
    list_filter = ('jogo_principal', 'data_criacao', 'criador')
    search_fields = ('nome', 'descricao')
    fields = ('nome', 'jogo_principal', 'descricao', 'criador', 'data_criacao')
    readonly_fields = ('data_criacao',)


@admin.register(Jogador)
class JogadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'equipe', 'eh_capitao', 'data_entrada')
    list_filter = ('equipe', 'eh_capitao', 'data_entrada')
    search_fields = ('nome', 'equipe__nome')
    fields = ('nome', 'equipe', 'user', 'eh_capitao', 'data_entrada')
    readonly_fields = ('data_entrada',)


@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('equipe', 'torneio', 'confirmada', 'data_inscricao')
    list_filter = ('torneio', 'confirmada', 'data_inscricao')
    search_fields = ('equipe__nome', 'torneio__nome')
    fields = ('equipe', 'torneio', 'confirmada', 'data_inscricao')
    readonly_fields = ('data_inscricao',)


@admin.register(Confronto)
class ConfrontoAdmin(admin.ModelAdmin):
    list_display = ('torneio', 'equipe1', 'equipe2', 'fase', 'vencedor', 'realizado')
    list_filter = ('torneio', 'fase', 'realizado')
    search_fields = ('equipe1__nome', 'equipe2__nome', 'torneio__nome')
    fields = ('torneio', 'equipe1', 'equipe2', 'fase', 'vencedor', 'data_confronto', 'realizado')
