from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Filme, Avaliacao
from .forms import PesquisaFilmeForm

# 1. Listagem, Pesquisa e Ordenação (Tudo numa só função)
def lista_filmes(request):
    form = PesquisaFilmeForm(request.GET or None)
    filmes = Filme.objects.all()

    # Pesquisa
    if form.is_valid():
        query = form.cleaned_data['query']
        filmes = filmes.filter(titulo__icontains=query)

    # Ordenação
    ordem = request.GET.get('ordenar')
    if ordem == 'recentes':
        filmes = filmes.order_by('-data_lancamento')
    elif ordem == 'antigos':
        filmes = filmes.order_by('data_lancamento')
    elif ordem == 'titulo':
        filmes = filmes.order_by('titulo')

    return render(request, 'lista_filmes.html', {
        'filmes': filmes,
        'form': form,
        'ordem_atual': ordem
    })

# 2. Detalhes e Avaliação
def detalhe_filme(request, filme_id):
    filme = get_object_or_404(Filme, id=filme_id)
    nota_user = None

    if request.user.is_authenticated:
        if request.method == "POST":
            nova_nota = request.POST.get('nota')
            Avaliacao.objects.update_or_create(
                filme=filme, utilizador=request.user,
                defaults={'nota': int(nova_nota)}
            )
        av = Avaliacao.objects.filter(filme=filme, utilizador=request.user).first()
        nota_user = av.nota if av else None

    return render(request, 'detalhe_filme.html', {
        'filme': filme,
        'nota_user': nota_user
    })

# 3. Registo de Utilizador
def registo(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registo.html', {'form': form})