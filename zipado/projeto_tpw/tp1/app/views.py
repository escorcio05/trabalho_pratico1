from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Filme, Ator, Realizador, Genero, Avaliacao, Favorito, Guardado
from .forms import PesquisaFilmeForm, RegistoForm, FilmeForm
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission

# --- 1. LISTAGEM E DETALHES ---

def lista_filmes(request):
    form = PesquisaFilmeForm(request.GET or None)
    filmes = Filme.objects.all()
    ids_favoritos = []
    ids_guardados = []

    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            filmes = filmes.filter(titulo__icontains=query)

    ordem = request.GET.get('ordenar')
    if ordem == 'recentes':
        filmes = filmes.order_by('-data_lancamento')
    elif ordem == 'antigos':
        filmes = filmes.order_by('data_lancamento')
    elif ordem == 'titulo':
        filmes = filmes.order_by('titulo')

    if request.user.is_authenticated and not request.user.is_superuser:
        ids_favoritos = list(Favorito.objects.filter(utilizador=request.user).values_list('filme_id', flat=True))
        ids_guardados = list(Guardado.objects.filter(utilizador=request.user).values_list('filme_id', flat=True))

    return render(request, 'lista_filmes.html', {
        'filmes': filmes, 'form': form, 'ordem_atual': ordem,
        'ids_favoritos': ids_favoritos, 'ids_guardados': ids_guardados
    })


def detalhe_filme(request, filme_id):
    filme = get_object_or_404(Filme, id=filme_id)
    avaliacoes = filme.avaliacoes.all().order_by('-data_postagem')

    # Captura o parâmetro 'origem' do URL (se não existir, fica None)
    origem = request.GET.get('origem')

    nota_user = 0
    comentario_user = ""

    if request.user.is_authenticated:
        if request.method == "POST":
            nova_nota = request.POST.get('nota')
            novo_comentario = request.POST.get('comentario')

            # Se houver um redirecionamento após o POST, mantemos a origem no URL
            if nova_nota:
                Avaliacao.objects.update_or_create(
                    filme=filme, utilizador=request.user,
                    defaults={'nota': int(nova_nota), 'comentario': novo_comentario}
                )
                url_redirecionamento = f"{reverse('detalhe_filme', args=[filme.id])}"
                if origem:
                    url_redirecionamento += f"?origem={origem}"
                return redirect(url_redirecionamento)

        av = Avaliacao.objects.filter(filme=filme, utilizador=request.user).first()
        if av:
            nota_user = av.nota
            comentario_user = av.comentario

    return render(request, 'detalhe_filme.html', {
        'filme': filme,
        'avaliacoes': avaliacoes,
        'nota_user': nota_user,
        'comentario_user': comentario_user,
        'origem': origem  # Enviamos a origem para o template
    })


# --- 2. AUTENTICAÇÃO E PERFIL ---

def registo(request):
    if request.method == 'POST':
        form = RegistoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistoForm()
    return render(request, 'registration/registo.html', {'form': form})


def redirecionar_apos_login(request):
    if request.user.is_superuser:
        return redirect('dashboard_admin')
    return redirect('lista_filmes')


def ver_perfil(request, user_id=None):
    target_user = get_object_or_404(User, id=user_id) if user_id else request.user
    origem = request.GET.get('origem')
    grupo_id = request.GET.get('grupo_id')

    return render(request, 'perfil.html', {
        'perfil_user': target_user,
        'origem': origem,
        'grupo_id': grupo_id
    })


@login_required
def editar_perfil(request, user_id):
    # Puxa o utilizador pelo ID para garantir que editamos o correto
    u = get_object_or_404(User, id=user_id)

    # Segurança: Apenas o próprio ou Superuser podem editar
    if request.user != u and not request.user.is_superuser:
        return redirect('lista_filmes')

    if request.method == "POST":
        u.username = request.POST.get('username')
        u.first_name = request.POST.get('first_name')
        u.last_name = request.POST.get('last_name')
        u.email = request.POST.get('email')

        # PASSWORD: Só processa se NÃO for o Admin a editar a conta de outro
        # E se o campo não estiver vazio
        nova_pw = request.POST.get('password')
        if nova_pw and not request.user.is_superuser:
            u.set_password(nova_pw)
            u.save()
            update_session_auth_hash(request, u)
        else:
            u.save()

        # Redireciona para o perfil detalhado do user que acabou de ser editado
        return redirect('perfil_detalhado', user_id=u.id)

    return render(request, 'editar_perfil.html', {'perfil_user': u})


# --- 3. DASHBOARD E BACKOFFICE ---

@user_passes_test(lambda u: u.is_superuser)
def dashboard_admin(request):
    context = {
        'total_users': User.objects.count(),
        'total_grupos': Group.objects.count(),
        'total_filmes': Filme.objects.count(),
        'total_atores': Ator.objects.count(),
        'total_realizadores': Realizador.objects.count(),
        'total_generos': Genero.objects.count(),
        'total_avaliacoes': Avaliacao.objects.count(),
    }
    return render(request, 'dashboard_admin.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_utilizadores(request):
    usuarios = User.objects.all().order_by('-date_joined')
    return render(request, 'relAdmin/admin_utilizadores.html', {'itens': usuarios})


@user_passes_test(lambda u: u.is_superuser)
def admin_atores(request):
    atores = Ator.objects.all().order_by('nome')
    return render(request, 'relAdmin/admin_atores.html', {'itens': atores})


@user_passes_test(lambda u: u.is_superuser)
def admin_realizadores(request):
    realizadores = Realizador.objects.all().order_by('nome')
    return render(request, 'relAdmin/admin_realizadores.html', {'itens': realizadores})


@user_passes_test(lambda u: u.is_superuser)
def admin_generos(request):
    generos = Genero.objects.all().order_by('nome')
    return render(request, 'relAdmin/admin_generos.html', {'itens': generos})


@user_passes_test(lambda u: u.is_superuser)
def admin_filmes(request):
    filmes = Filme.objects.all().order_by('-id')
    return render(request, 'relAdmin/admin_filmes.html', {'itens': filmes})


@user_passes_test(lambda u: u.is_superuser)
def admin_avaliacoes(request):
    avaliacoes = Avaliacao.objects.all().order_by('-data_postagem')
    return render(request, 'relAdmin/admin_avaliacoes.html', {'itens': avaliacoes})




# --- 5. FAVORITOS / GUARDADOS / ADICIONAR FILME (Código Original Mantido) ---

@user_passes_test(lambda u: u.is_superuser)
def adicionar_filme(request):
    if request.method == 'POST':
        dados = request.POST.copy()
        r_val = dados.get('realizador')
        if r_val and not r_val.isdigit():
            obj, _ = Realizador.objects.get_or_create(nome=r_val)
            dados['realizador'] = str(obj.id)
        for field in ['atores', 'generos']:
            vals = dados.getlist(field)
            new_ids = []
            for v in vals:
                if v.isdigit():
                    new_ids.append(v)
                else:
                    model = Ator if field == 'atores' else Genero
                    obj, _ = model.objects.get_or_create(nome=v.strip())
                    new_ids.append(str(obj.id))
            dados.setlist(field, new_ids)
        form = FilmeForm(dados, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_filmes')
    else:
        form = FilmeForm()
    return render(request, 'adicionar_filme.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_staff)
def editar_filme(request, id):
    filme = get_object_or_404(Filme, id=id)
    if request.method == 'POST':
        form = FilmeForm(request.POST, request.FILES, instance=filme)
        if form.is_valid():
            form.save()
            return redirect('lista_filmes')
    else:
        form = FilmeForm(instance=filme)
    return render(request, 'adicionar_filme.html', {'form': form, 'editando': True})


@login_required
def meus_favoritos(request):
    favs = Favorito.objects.filter(utilizador=request.user)
    return render(request, 'meus_favoritos.html', {'favoritos': favs})


@login_required
def meus_guardados(request):
    gs = Guardado.objects.filter(utilizador=request.user)
    return render(request, 'meus_guardados.html', {'guardados': gs})


@login_required
def toggle_favorito(request, filme_id):
    filme = get_object_or_404(Filme, id=filme_id)
    fav, created = Favorito.objects.get_or_create(utilizador=request.user, filme=filme)
    if not created: fav.delete()
    return redirect(request.META.get('HTTP_REFERER', 'lista_filmes'))


@login_required
def toggle_guardado(request, filme_id):
    filme = get_object_or_404(Filme, id=filme_id)
    g, created = Guardado.objects.get_or_create(utilizador=request.user, filme=filme)
    if not created: g.delete()
    return redirect(request.META.get('HTTP_REFERER', 'lista_filmes'))


@user_passes_test(lambda u: u.is_superuser)
def editar_item(request, modelo, item_id):
    # Determina o modelo com base na string enviada pelo URL
    modelos = {'ator': Ator, 'genero': Genero, 'realizador': Realizador}
    model_class = modelos.get(modelo)

    item = get_object_or_404(model_class, id=item_id)

    if request.method == "POST":
        novo_nome = request.POST.get('nome')
        if novo_nome:
            item.nome = novo_nome
            item.save()
            messages.success(request, f"{modelo.capitalize()} atualizado com sucesso!")
        return redirect(f'admin_{modelo}es' if modelo != 'ator' else 'admin_atores')

    return render(request, 'relAdmin/editar_item_admin.html', {'item': item, 'tipo': modelo})


@user_passes_test(lambda u: u.is_superuser)
def apagar_item(request, modelo, item_id):
    modelos = {'ator': Ator, 'genero': Genero, 'realizador': Realizador}
    model_class = modelos.get(modelo)

    item = get_object_or_404(model_class, id=item_id)
    item.delete()
    messages.success(request, f"{modelo.capitalize()} removido da base de dados.")

    # Redireciona de volta para a lista correta
    url_redirect = f'admin_{modelo}es' if modelo != 'ator' else 'admin_atores'
    return redirect(url_redirect)

@user_passes_test(lambda u: u.is_superuser)
def apagar_filme(request, filme_id):
    filme = get_object_or_404(Filme, id=filme_id)
    nome_filme = filme.titulo
    filme.delete()
    messages.success(request, f"O filme '{nome_filme}' foi apagado com sucesso.")
    return redirect('admin_filmes')


@user_passes_test(lambda u: u.is_superuser)
def lista_grupos(request):
    grupos = Group.objects.all().order_by('name')
    return render(request, 'relAdmin/admin_permissoes.html', {'grupos': grupos})

@user_passes_test(lambda u: u.is_superuser)
def criar_grupo(request):
    todas_permissoes = Permission.objects.all()
    if request.method == "POST":
        nome = request.POST.get('nome')
        perms_selecionadas = request.POST.getlist('permissoes')
        if nome:
            novo_grupo = Group.objects.create(name=nome)
            novo_grupo.permissions.set(perms_selecionadas)
            messages.success(request, f"Grupo '{nome}' criado!")
            return redirect('lista_grupos')
    return render(request, 'relAdmin/editar_grupo.html', {'todas_permissoes': todas_permissoes, 'modo': 'Criar'})

@user_passes_test(lambda u: u.is_superuser)
def editar_grupo(request, grupo_id):
    grupo = get_object_or_404(Group, id=grupo_id)
    todas_permissoes = Permission.objects.all()
    if request.method == "POST":
        grupo.name = request.POST.get('nome')
        perms_selecionadas = request.POST.getlist('permissoes')
        grupo.permissions.set(perms_selecionadas)
        grupo.save()
        messages.success(request, f"Grupo '{grupo.name}' atualizado!")
        return redirect('lista_grupos')
    return render(request, 'relAdmin/editar_grupo.html', {'grupo': grupo, 'todas_permissoes': todas_permissoes, 'modo': 'Editar'})

@user_passes_test(lambda u: u.is_superuser)
def detalhe_grupo(request, grupo_id):
    grupo = get_object_or_404(Group, id=grupo_id)
    utilizadores = grupo.user_set.all()
    permissoes = grupo.permissions.all().select_related('content_type')
    return render(request, 'relAdmin/detalhe_grupo.html', {'grupo': grupo, 'utilizadores': utilizadores, 'permissoes': permissoes})

@user_passes_test(lambda u: u.is_superuser)
def apagar_grupo(request, grupo_id):
    grupo = get_object_or_404(Group, id=grupo_id)
    grupo.delete()
    messages.success(request, "Grupo removido com sucesso.")
    return redirect('lista_grupos')

@user_passes_test(lambda u: u.is_superuser)
def remover_utilizador_grupo(request, grupo_id, user_id):
    grupo = get_object_or_404(Group, id=grupo_id)
    u = get_object_or_404(User, id=user_id)
    grupo.user_set.remove(u)
    messages.success(request, f"Utilizador {u.username} removido do grupo.")
    return redirect('detalhe_grupo', grupo_id=grupo_id)

@user_passes_test(lambda u: u.is_superuser)
def apagar_avaliacao(request, av_id):
    avaliacao = get_object_or_404(Avaliacao, id=av_id)
    avaliacao.delete()
    messages.success(request, "Avaliação removida com sucesso.")
    return redirect('admin_avaliacoes')