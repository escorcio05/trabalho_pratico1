from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Filme, Realizador, Ator, Genero, Favorito, Guardado, Avaliacao
from .forms import PesquisaFilmeForm, RegistoForm, FilmeForm, EditarPerfilForm


# 1. Listagem Principal
def lista_filmes(request):
    form = PesquisaFilmeForm(request.GET or None)
    filmes = Filme.objects.all()

    # Listas para controlar as cores dos ícones
    ids_favoritos = []
    ids_guardados = []

    # Pesquisa
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            filmes = filmes.filter(titulo__icontains=query)

    # Ordenação
    ordem = request.GET.get('ordenar')
    if ordem == 'recentes':
        filmes = filmes.order_by('-data_lancamento')
    elif ordem == 'antigos':
        filmes = filmes.order_by('data_lancamento')
    elif ordem == 'titulo':
        filmes = filmes.order_by('titulo')

    # Se logado, buscar o que o user já marcou
    if request.user.is_authenticated and not request.user.is_superuser:
        ids_favoritos = list(Favorito.objects.filter(utilizador=request.user).values_list('filme_id', flat=True))
        ids_guardados = list(Guardado.objects.filter(utilizador=request.user).values_list('filme_id', flat=True))

    return render(request, 'lista_filmes.html', {
        'filmes': filmes,
        'form': form,
        'ordem_atual': ordem,
        'ids_favoritos': ids_favoritos,
        'ids_guardados': ids_guardados
    })


# 2. Detalhes
def detalhe_filme(request, filme_id):
    filme = get_object_or_404(Filme, id=filme_id)
    avaliacoes = filme.avaliacoes.all().order_by('-data_postagem')
    nota_user = 0
    comentario_user = ""

    if request.user.is_authenticated:
        if request.method == "POST":
            nova_nota = request.POST.get('nota')
            novo_comentario = request.POST.get('comentario')
            if nova_nota:
                Avaliacao.objects.update_or_create(
                    filme=filme, utilizador=request.user,
                    defaults={'nota': int(nova_nota), 'comentario': novo_comentario}
                )
                return redirect('detalhe_filme', filme_id=filme.id)

        av = Avaliacao.objects.filter(filme=filme, utilizador=request.user).first()
        if av:
            nota_user = av.nota
            comentario_user = av.comentario

    return render(request, 'detalhe_filme.html', {
        'filme': filme, 'avaliacoes': avaliacoes,
        'nota_user': nota_user, 'comentario_user': comentario_user
    })


# 3. Registo e Perfil
def registo(request):
    if request.method == 'POST':
        form = RegistoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistoForm()
    return render(request, 'registration/registo.html', {'form': form})


@login_required
def editar_perfil(request):
    if request.user.is_superuser: return redirect('admin:index')
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Perfil atualizado!')
            return redirect('lista_filmes')
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request, 'editar_perfil.html', {'form': form})


# 4. Gestão de Filmes (Admin)
@user_passes_test(lambda u: u.is_superuser)
def adicionar_filme(request):
    if request.method == 'POST':
        dados = request.POST.copy()

        # Lógica para Realizador
        r_val = dados.get('realizador')
        if r_val and not r_val.isdigit():
            obj, _ = Realizador.objects.get_or_create(nome=r_val)
            dados['realizador'] = str(obj.id)

        # Lógica para Atores/Géneros (Tags Select2)
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
        dados = request.POST.copy()
        # Repetir a mesma lógica de tratamento de tags do adicionar_filme aqui...
        form = FilmeForm(dados, request.FILES, instance=filme)
        if form.is_valid():
            form.save()
            return redirect('lista_filmes')
    else:
        form = FilmeForm(instance=filme)
    return render(request, 'adicionar_filme.html', {'form': form, 'editando': True})


# 5. Favoritos e Guardados
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