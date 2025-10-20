from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Torneio, Inscricao
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        senha = request.POST['senha']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "E-mail não encontrado.")
            return redirect('login')

        user_auth = authenticate(username=user.username, password=senha)
        if user_auth:
            login(request, user_auth)
            return redirect('painel')
        else:
            messages.error(request, "Senha incorreta.")
            return redirect('login')

    return render(request, 'index.html')


def cadastro_view(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        senha = request.POST['senha']

        if User.objects.filter(email=email).exists():
            messages.error(request, "E-mail já cadastrado.")
            return redirect('cadastro')

        username = email.split('@')[0]
        User.objects.create_user(username=username, email=email, password=senha, first_name=nome)
        messages.success(request, "Conta criada com sucesso! Faça login.")
        return redirect('login')

    return render(request, 'cadastro.html')


@login_required(login_url='login')
def painel_view(request):
    torneios = Torneio.objects.filter(criador=request.user)
    user = request.user
    iniciais = (user.first_name[:1] + user.last_name[:1]).upper() if user.first_name and user.last_name else user.first_name[:2].upper()
    return render(request, 'main.html', {'usuario': user, 'iniciais': iniciais, 'torneios': torneios})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def criar_torneio_view(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        descricao = request.POST['descricao']
        regras = request.POST['regras']
        data = request.POST['data']

        Torneio.objects.create(
            nome=nome,
            descricao=descricao,
            regras=regras,
            data=data,
            criador=request.user
        )

        messages.success(request, "Torneio criado com sucesso!")
        return redirect('painel')

    return render(request, 'criar_torneio.html')

@login_required(login_url='login')
def inscricoes_view(request):
    torneios = Torneio.objects.all().order_by('-data')

    if request.method == 'POST':
        jogador = request.POST.get('jogador')
        equipe = request.POST.get('equipe')
        torneio_id = request.POST.get('torneio')

        if not jogador or not torneio_id:
            messages.error(request, "Por favor, preencha todos os campos obrigatórios.")
        else:
            torneio = Torneio.objects.get(id=torneio_id)
            Inscricao.objects.create(jogador=jogador, equipe=equipe, torneio=torneio)
            messages.success(request, f"✅ {jogador} foi inscrito no torneio {torneio.nome}!")
            return redirect('inscricoes')

    return render(request, 'inscricoes.html', {'torneios': torneios})


@login_required(login_url='login')
def resultados_view(request):
    torneios = Torneio.objects.all().order_by('-data')

    if request.method == 'POST':
        torneio_id = request.POST.get('torneio_id')
        campeao = request.POST.get('campeao')

        torneio = get_object_or_404(Torneio, id=torneio_id)
        torneio.campeao = campeao
        torneio.status = 'finalizado'
        torneio.save()

        messages.success(request, f"🏆 Campeão atualizado para o torneio {torneio.nome}!")
        return redirect('resultados')

    return render(request, 'resultados.html', {'torneios': torneios})