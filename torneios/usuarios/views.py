from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Torneio, Inscricao, Equipe, Jogador, Confronto
from django.contrib import messages
from django.http import JsonResponse
from itertools import combinations

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
        return redirect('inscricoes')

    return render(request, 'criar_torneio.html')


@login_required(login_url='login')
def criar_equipe_view(request):
    """View para criar uma nova equipe"""
    if request.method == 'POST':
        nome = request.POST.get('nome_equipe')
        jogo_principal = request.POST.get('jogo_principal')
        descricao = request.POST.get('descricao')

        if not nome or not jogo_principal or not descricao:
            messages.error(request, "Por favor, preencha todos os campos.")
            return redirect('criar_equipe')

        equipe = Equipe.objects.create(
            nome=nome,
            jogo_principal=jogo_principal,
            descricao=descricao,
            criador=request.user
        )

        # Adiciona o criador como capitão
        Jogador.objects.create(
            nome=request.user.first_name or request.user.username,
            equipe=equipe,
            user=request.user,
            eh_capitao=True
        )

        messages.success(request, f"✅ Equipe '{nome}' criada com sucesso!")
        return redirect('dashboard_equipe_detail', equipe_id=equipe.id)

    return render(request, 'criar_equipe.html')


@login_required(login_url='login')
def dashboard_equipe_view(request, equipe_id=None):
    """View para exibir o dashboard da equipe"""
    if equipe_id:
        equipe = get_object_or_404(Equipe, id=equipe_id)
    else:
        # Tenta obter a primeira equipe do usuário
        equipe = Equipe.objects.filter(criador=request.user).first()
        if not equipe:
            messages.info(request, "Você ainda não criou nenhuma equipe.")
            return redirect('criar_equipe')

    # Verifica se o usuário é criador da equipe ou membro
    jogador = Jogador.objects.filter(equipe=equipe, user=request.user).first()
    eh_criador = equipe.criador == request.user
    eh_membro = jogador is not None

    if not eh_criador and not eh_membro:
        messages.error(request, "Acesso negado a esta equipe.")
        return redirect('painel')

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'adicionar_jogador':
            nome_jogador = request.POST.get('nome_jogador')
            if nome_jogador:
                if not Jogador.objects.filter(equipe=equipe, nome=nome_jogador).exists():
                    Jogador.objects.create(nome=nome_jogador, equipe=equipe)
                    messages.success(request, f"Jogador '{nome_jogador}' adicionado à equipe!")
                else:
                    messages.error(request, "Este jogador já está na equipe.")
            return redirect('dashboard_equipe_detail', equipe_id=equipe.id)

        elif acao == 'remover_jogador':
            jogador_id = request.POST.get('jogador_id')
            jogador_remover = get_object_or_404(Jogador, id=jogador_id, equipe=equipe)
            if not jogador_remover.eh_capitao or eh_criador:
                nome = jogador_remover.nome
                jogador_remover.delete()
                messages.success(request, f"Jogador '{nome}' removido da equipe.")
            else:
                messages.error(request, "Apenas o criador pode remover o capitão.")
            return redirect('dashboard_equipe_detail', equipe_id=equipe.id)

    jogadores = equipe.jogadores.all()
    inscricoes = Inscricao.objects.filter(equipe=equipe)

    context = {
        'equipe': equipe,
        'jogadores': jogadores,
        'inscricoes': inscricoes,
        'eh_criador': eh_criador,
        'eh_membro': eh_membro,
    }

    return render(request, 'dashboard_equipe.html', context)


@login_required(login_url='login')
def chaveamento_view(request, torneio_id):
    """View para exibir e gerar o chaveamento de um torneio"""
    torneio = get_object_or_404(Torneio, id=torneio_id)

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'gerar_chaveamento':
            # Obtém todas as equipes inscritas
            inscricoes = Inscricao.objects.filter(torneio=torneio)
            equipes = [insc.equipe for insc in inscricoes]

            if len(equipes) < 2:
                messages.error(request, "É necessário pelo menos 2 equipes para gerar o chaveamento.")
                return redirect('chaveamento', torneio_id=torneio_id)

            # Limpa confrontos anteriores
            Confronto.objects.filter(torneio=torneio).delete()

            # Gera chaveamento para fase de quartas
            num_equipes = len(equipes)
            
            # Determina o número de confrontos na primeira fase
            if num_equipes == 2:
                confrontos_quartas = 1
            elif num_equipes <= 4:
                confrontos_quartas = 2
            elif num_equipes <= 8:
                confrontos_quartas = 4
            else:
                confrontos_quartas = 8

            # Cria os confrontos das quartas
            for i in range(0, confrontos_quartas * 2, 2):
                if i < len(equipes) and i + 1 < len(equipes):
                    Confronto.objects.create(
                        torneio=torneio,
                        equipe1=equipes[i],
                        equipe2=equipes[i + 1],
                        fase='quartas'
                    )
                elif i < len(equipes):
                    Confronto.objects.create(
                        torneio=torneio,
                        equipe1=equipes[i],
                        fase='quartas'
                    )

            # Cria confrontos das semifinais (aguardando vencedores)
            num_semifinais = (confrontos_quartas + 1) // 2
            for i in range(num_semifinais):
                Confronto.objects.create(
                    torneio=torneio,
                    equipe1=equipes[0],  # Placeholder
                    fase='semifinal'
                )

            # Cria confronto da final
            Confronto.objects.create(
                torneio=torneio,
                equipe1=equipes[0],  # Placeholder
                fase='final'
            )

            torneio.status = 'chaveamento'
            torneio.save()

            messages.success(request, "✅ Chaveamento gerado com sucesso!")
            return redirect('chaveamento', torneio_id=torneio_id)

        elif acao == 'atualizar_vencedor':
            confronto_id = request.POST.get('confronto_id')
            vencedor_id = request.POST.get('vencedor_id')
            
            confronto = get_object_or_404(Confronto, id=confronto_id, torneio=torneio)
            vencedor = get_object_or_404(Equipe, id=vencedor_id)
            
            confronto.vencedor = vencedor
            confronto.realizado = True
            confronto.save()

            # Atualiza confrontos das próximas fases
            atualizar_proximas_fases(confronto, torneio)

            messages.success(request, f"✅ Vencedor '{vencedor.nome}' registrado!")
            return redirect('chaveamento', torneio_id=torneio_id)

    confrontos_por_fase = {
        'quartas': Confronto.objects.filter(torneio=torneio, fase='quartas'),
        'semifinal': Confronto.objects.filter(torneio=torneio, fase='semifinal'),
        'final': Confronto.objects.filter(torneio=torneio, fase='final'),
    }

    context = {
        'torneio': torneio,
        'confrontos_por_fase': confrontos_por_fase,
    }

    return render(request, 'chaveamento.html', context)


def atualizar_proximas_fases(confronto, torneio):
    """Atualiza os confrontos das próximas fases com os vencedores"""
    if confronto.fase == 'quartas':
        # Encontra o confronto correspondente da semifinal
        semifinais = Confronto.objects.filter(torneio=torneio, fase='semifinal')
        num_confronto = list(Confronto.objects.filter(
            torneio=torneio, 
            fase='quartas'
        ).values_list('id', flat=True)).index(confronto.id)
        
        semifinal_index = num_confronto // 2
        if semifinal_index < semifinais.count():
            semifinal = list(semifinais)[semifinal_index]
            if num_confronto % 2 == 0:
                semifinal.equipe1 = confronto.vencedor
            else:
                semifinal.equipe2 = confronto.vencedor
            semifinal.save()

    elif confronto.fase == 'semifinal':
        # Atualiza a final com o vencedor
        final = Confronto.objects.filter(torneio=torneio, fase='final').first()
        if final:
            semifinais = list(Confronto.objects.filter(torneio=torneio, fase='semifinal'))
            num_confronto = semifinais.index(confronto)
            if num_confronto == 0:
                final.equipe1 = confronto.vencedor
            else:
                final.equipe2 = confronto.vencedor
            final.save()

    elif confronto.fase == 'final':
        # Atualiza o campeão do torneio
        torneio.campeao = confronto.vencedor.nome
        torneio.status = 'finalizado'
        torneio.save()


@login_required(login_url='login')
def inscricoes_view(request):
    torneios = Torneio.objects.all().order_by('-data')
    equipes_usuario = Equipe.objects.filter(criador=request.user)

    if request.method == 'POST':
        equipe_id = request.POST.get('equipe')
        torneio_id = request.POST.get('torneio')

        if not equipe_id or not torneio_id:
            messages.error(request, "Por favor, preencha todos os campos obrigatórios.")
        else:
            equipe = get_object_or_404(Equipe, id=equipe_id)
            torneio = get_object_or_404(Torneio, id=torneio_id)

            if Inscricao.objects.filter(equipe=equipe, torneio=torneio).exists():
                messages.error(request, "Esta equipe já está inscrita neste torneio.")
            else:
                Inscricao.objects.create(equipe=equipe, torneio=torneio, confirmada=True)
                messages.success(request, f"✅ {equipe.nome} foi inscrita no torneio {torneio.nome}!")
                return redirect('inscricoes')

    context = {
        'torneios': torneios,
        'equipes': equipes_usuario,
    }

    return render(request, 'inscricoes.html', context)


