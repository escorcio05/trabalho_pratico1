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
    console.log("DOM pronto, a carregar Select2...");

    function ativarSelect2(seletor, placeholder) {
        if ($(seletor).length) {
            $(seletor).select2({
                tags: true,
                placeholder: placeholder,
                allowClear: true,
                width: '100%',
                tokenSeparators: [',', ';'] // Permite separar por vírgula ou ponto e vírgula
            });
            console.log("Select2 aplicado a: " + seletor);
        }
    }

    // IDs PADRÃO DO DJANGO:

    // 1. Realizador (Normalmente ForeignKey - Único)
    ativarSelect2('#id_realizador', "Seleciona ou escreve o realizador...");

    // 2. Géneros (Agora ManyToMany - Múltiplos)
    // Nota: O Django gera 'id_generos' se o campo se chamar 'generos' no plural
    ativarSelect2('#id_generos', "Seleciona ou escreve os géneros (ex: Ação, Drama)...");
    ativarSelect2('#id_genero', "Seleciona ou escreve o género..."); // Backup caso o nome no model seja singular

    // 3. Atores (ManyToMany - Múltiplos)
    ativarSelect2('#id_atores', "Escreve os atores separados por vírgulas...");
});

