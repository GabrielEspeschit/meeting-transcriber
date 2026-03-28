import argparse
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_OUTPUT_DIR = (
    "/Users/gabrielespeschit/Library/CloudStorage/OneDrive-Personal/"
    "Documentos/08 - Anotações/gabriel.esp/02. Transcrição de Reuniões"
)
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_LANGUAGE = "pt-br"
DEFAULT_MAX_TOKENS = 4096


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Gera um sumário estruturado a partir de uma transcrição de reunião."
    )
    parser.add_argument(
        "transcription_file",
        help="Caminho para o arquivo .txt de transcrição",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Diretório de saída (default: variável OUTPUT_DIR do .env)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Modelo do Claude (default: variável CLAUDE_MODEL do .env)",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Idioma do sumário: pt-br, en (default: variável LANGUAGE do .env)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Máximo de tokens na resposta (default: variável MAX_TOKENS do .env)",
    )

    args = parser.parse_args()

    # Precedência: flag CLI > .env > default
    output_dir = args.output_dir or os.environ.get("OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
    model = args.model or os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL)
    language = args.language or os.environ.get("LANGUAGE", DEFAULT_LANGUAGE)
    max_tokens = args.max_tokens or int(os.environ.get("MAX_TOKENS", DEFAULT_MAX_TOKENS))

    # Validações
    input_path = Path(args.transcription_file)
    if not input_path.exists():
        print(f"Erro: arquivo não encontrado: {input_path}", file=sys.stderr)
        sys.exit(1)
    if not input_path.suffix == ".txt":
        print(f"Erro: esperado arquivo .txt, recebido: {input_path.suffix}", file=sys.stderr)
        sys.exit(1)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "Erro: ANTHROPIC_API_KEY não está definida.\n"
            "Configure no arquivo .env ou exporte no shell.",
            file=sys.stderr,
        )
        sys.exit(1)

    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"Erro: diretório de saída não encontrado: {output_path}", file=sys.stderr)
        sys.exit(1)

    # Ler transcrição
    transcription = input_path.read_text(encoding="utf-8")
    if not transcription.strip():
        print("Erro: arquivo de transcrição está vazio.", file=sys.stderr)
        sys.exit(1)

    # Gerar sumário
    print(f"Processando: {input_path.name}")
    print(f"Modelo: {model}")
    print(f"Idioma: {language}")

    try:
        from .summarizer import summarize

        result = summarize(
            transcription=transcription,
            model=model,
            language=language,
            max_tokens=max_tokens,
        )
    except Exception as e:
        print(f"Erro ao chamar a API: {e}", file=sys.stderr)
        sys.exit(1)

    # Determinar nome do arquivo de saída
    today = date.today().isoformat()
    slug = result["title_slug"] or input_path.stem
    output_filename = f"{today}_{slug}.md"
    output_file = output_path / output_filename

    # Salvar
    output_file.write_text(result["markdown"], encoding="utf-8")
    print(f"Sumário salvo em: {output_file}")


if __name__ == "__main__":
    main()
