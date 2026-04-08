import os

# Configuração: ficheiros ou pastas a ignorar (para o dump não ficar gigante)
IGNORAR_PASTAS = {'.git', '.idea', '__pycache__', 'venv', 'static_cdn', 'media'}
IGNORAR_EXTENSOES = {'.pyc', '.exe', '.sqlite3', '.png', '.jpg', '.zip'}


def gerar_resumo():
    output_file = "projeto_completo.txt"

    with open(output_file, "w", encoding="utf-8") as f_out:
        for root, dirs, files in os.walk("."):
            # Filtrar pastas ignoradas
            dirs[:] = [d for d in dirs if d not in IGNORAR_PASTAS]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in IGNORAR_EXTENSOES:
                    continue

                caminho_completo = os.path.join(root, file)
                f_out.write(f"\n{'=' * 50}\n")
                f_out.write(f"FICHEIRO: {caminho_completo}\n")
                f_out.write(f"{'=' * 50}\n\n")

                try:
                    with open(caminho_completo, "r", encoding="utf-8") as f_in:
                        f_out.write(f_in.read())
                except Exception as e:
                    f_out.write(f"Erro ao ler ficheiro: {e}")

                f_out.write("\n\n")

    print(f"Resumo gerado com sucesso em: {output_file}")


if __name__ == "__main__":
    gerar_resumo()