from django.shortcuts import render
from app.models import Filme
from .forms import PesquisaFilmeForm
from django.contrib.auth.decorators import login_required
from .models import Filme, Avaliacao

def lista_filmes(request):
    filmes = Filme.objects.all()
    return render(request, 'lista_filmes.html', {'filmes': filmes})
def detalhe_filme(request, filme_id):
    filme = Filme.objects.get(id=filme_id)
    nota_user = None

    if request.user.is_authenticated:
        if request.method == "POST":
            nova_nota = request.POST.get('nota')
            Avaliacao.objects.update_or_create(
                filme=filme, utilizador=request.user,
                defaults={'nota': nova_nota}
            )
        av = Avaliacao.objects.filter(filme=filme, utilizador=request.user).first()
        nota_user = av.nota if av else None

    return render(request, 'detalhe_filme.html', {
        'filme': filme,
        'nota_user': nota_user
    })


def lista_filmes(request):
    ordem = request.GET.get('ordenar')

    if ordem == 'recentes':
        filmes = Filme.objects.all().order_by('-data_lancamento')
    elif ordem == 'antigos':
        filmes = Filme.objects.all().order_by('data_lancamento')
    elif ordem == 'titulo':
        filmes = Filme.objects.all().order_by('titulo')
    else:
        filmes = Filme.objects.all()

    return render(request, 'lista_filmes.html', {'filmes': filmes, 'ordem_atual': ordem})

def lista_filmes(request):
    form = PesquisaFilmeForm(request.GET or None)
    filmes = Filme.objects.all()

    if form.is_valid():
        query = form.cleaned_data['query']
        filmes = filmes.filter(titulo__icontains=query)

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