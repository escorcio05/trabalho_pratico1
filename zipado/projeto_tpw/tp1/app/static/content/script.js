document.addEventListener("DOMContentLoaded", function() {
    const estrelas = document.querySelectorAll('.estrela');
    const textoNota = document.getElementById('nota-escolhida');
    const inputNotaEscondido = document.getElementById('input-nota'); // <--- NOVO: Referência ao campo do Django
    let classificacaoAtual = parseInt(inputNotaEscondido.value) || 0;

    preencherEstrelas(classificacaoAtual);
    textoNota.innerText = classificacaoAtual;

    function preencherEstrelas(valor) {
        estrelas.forEach(estrela => {
            const valorEstrela = parseInt(estrela.getAttribute('data-valor'));
            if (valorEstrela <= valor) {
                estrela.classList.add('preenchida');
            } else {
                estrela.classList.remove('preenchida');
            }
        });
    }

    estrelas.forEach(estrela => {
        estrela.addEventListener('mouseover', () => {
            const valorHover = parseInt(estrela.getAttribute('data-valor'));
            preencherEstrelas(valorHover);
        });

        estrela.addEventListener('mouseout', () => {
            preencherEstrelas(classificacaoAtual);
        });

        estrela.addEventListener('click', () => {
            classificacaoAtual = parseInt(estrela.getAttribute('data-valor'));

            // 1. Atualiza o texto visual (o que o user vê)
            textoNota.innerText = classificacaoAtual;

            // 2. ATUALIZA O VALOR PARA O DJANGO (O mais importante!)
            // Isto faz com que o request.POST['nota'] leve o número certo
            if (inputNotaEscondido) {
                inputNotaEscondido.value = classificacaoAtual;
            }

            preencherEstrelas(classificacaoAtual);
        });
    });
});

$(document).ready(function() {
    // Verifica se o campo do realizador existe na página atual antes de ativar o Select2
    if ($('#id_realizador').length) {

        // Ativa o Select2 para o Realizador
        $('#id_realizador').select2({
            tags: true,
            placeholder: "Seleciona da lista ou escreve um novo...",
            allowClear: true
        });

        // Ativa o Select2 para o Género
        $('#id_genero').select2({
            tags: true,
            placeholder: "Seleciona da lista ou escreve um novo...",
            allowClear: true
        });

        // Ativa o Select2 para os Atores
        $('#id_atores').select2({
            tags: true,
            placeholder: "Seleciona ou escreve novos atores separando por vírgulas...",
            tokenSeparators: [',']
        });

    }
});