# 🎮 POT - Plataforma Online de Torneios ✅

---

## 🚀 Como Usar

### 1. Iniciar Servidor
```bash
cd torneios
python manage.py runserver
```

### 2. Acessar
- **Login:** `http://localhost:8000/`
- **Criar Equipe:** `http://localhost:8000/criar_equipe/`
- **Dashboard:** `http://localhost:8000/dashboard_equipe/`
- **Chaveamento:** `http://localhost:8000/chaveamento/1/` (ID do torneio)
- **Admin:** `http://localhost:8000/admin/`

### 3. Fluxo Completo
```
1. Crie conta (cadastro)
2. Faça login
3. Crie equipe (/criar_equipe/)
4. Inscreva em torneio (/inscricoes/)
5. Veja chaveamento (/chaveamento/<id>/)
6. Defina vencedores
```

---

## ✨ Recursos Implementados

- ✅ Banco de dados refletindo tudo
- ✅ Validações (não duplicar, permissões)
- ✅ Mensagens de feedback (sucesso/erro)
- ✅ Redirecionamentos apropriados
- ✅ Segurança (@login_required)
- ✅ Admin Django completo
- ✅ Responsividade (mobile/desktop)


## 📊 Funcionalidades

- [ ] Criar equipe
- [ ] Adicionar jogador
- [ ] Remover jogador  
- [ ] Inscrever em torneio
- [ ] Gerar chaveamento
- [ ] Registrar vencedor
- [ ] Ver campeão







