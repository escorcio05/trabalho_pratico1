from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Filme, Avaliacao
from .forms import PesquisaFilmeForm
from .forms import RegistoForm

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
    avaliacoes_gerais = filme.avaliacoes.all().order_by('-data_postagem')  # Todas as críticas
    nota_user = 0
    comentario_user = ""

    if request.user.is_authenticated:
        if request.method == "POST":
            # Captura os dados do formulário HTML
            nova_nota = request.POST.get('nota')
            novo_comentario = request.POST.get('comentario')

            if nova_nota:
                Avaliacao.objects.update_or_create(
                    filme=filme,
                    utilizador=request.user,
                    defaults={
                        'nota': int(nova_nota),
                        'comentario': novo_comentario
                    }
                )
                return redirect('detalhe_filme', filme_id=filme.id)

        # Procura se o utilizador já avaliou este filme
        av = Avaliacao.objects.filter(filme=filme, utilizador=request.user).first()
        if av:
            nota_user = av.nota
            comentario_user = av.comentario

    return render(request, 'detalhe_filme.html', {
        'filme': filme,
        'avaliacoes': avaliacoes_gerais,
        'nota_user': nota_user,
        'comentario_user': comentario_user
    })

# 3. Registo de Utilizador
def registo(request):
    if request.method == 'POST':
        form = RegistoForm(request.POST)
        if form.is_valid():
            form.save()
            print("SUCESSO: Utilizador guardado!")  # Vais ver isto no terminal
            return redirect('login')
        else:
            # Isto vai mostrar no terminal do PyCharm o ERRO exato da validação
            print("ERRO NO FORMULÁRIO:", form.errors)
    else:
        form = RegistoForm()

    return render(request, 'registration/registo.html', {'form': form})