from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Filme, Avaliacao
from .forms import PesquisaFilmeForm
from .forms import RegistoForm
from django.contrib.auth.decorators import user_passes_test
from .forms import FilmeForm
from .models import Filme, Realizador, Ator


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


def is_superuser(user):
    return user.is_superuser


@user_passes_test(is_superuser)
@user_passes_test(is_superuser)
def adicionar_filme(request):
    if request.method == 'POST':
        dados = request.POST.copy() # Criamos uma cópia para poder mexer

        # --- TRATAR REALIZADOR ---
        realizador_val = dados.get('realizador')
        if realizador_val and not realizador_val.isdigit():
            # Se for nome, cria na BD e troca pelo ID
            obj, _ = Realizador.objects.get_or_create(nome=realizador_val)
            dados['realizador'] = str(obj.id)

        # --- TRATAR ATORES ---
        atores_vals = dados.getlist('atores')
        novos_atores_ids = []
        for val in atores_vals:
            if val.isdigit():
                novos_atores_ids.append(val)
            else:
                # Se for um nome novo, cria e guarda o ID
                obj, _ = Ator.objects.get_or_create(nome=val)
                novos_atores_ids.append(str(obj.id))
        dados.setlist('atores', novos_atores_ids)

        # AGORA SIM, passamos os dados com IDs para o Form
        form = FilmeForm(dados, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Filme guardado!')
            return redirect('lista_filmes')
        else:
            # Se der erro, o print ajuda-te a ver no terminal o que falhou
            print(form.errors)
    else:
        form = FilmeForm()

    return render(request, 'adicionar_filme.html', {'form': form})