import argparse
import os
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from .folders import UNCLASSIFIED_EN, UNCLASSIFIED_PT_BR, discover_folders
from .summarizer import summarize

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
        "transcription_files",
        nargs="+",
        help="Um ou mais arquivos .txt de transcrição",
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

    folders = discover_folders(output_path)
    unclassified = UNCLASSIFIED_PT_BR if language != "en" else UNCLASSIFIED_EN
    if folders:
        print(f"Pastas encontradas: {', '.join(f.name for f in folders)}")

    errors = []
    input_paths = [Path(f) for f in args.transcription_files]

    for input_path in input_paths:
        try:
            if not input_path.exists():
                raise FileNotFoundError(f"arquivo não encontrado: {input_path}")
            if input_path.suffix != ".txt":
                raise ValueError(f"esperado .txt, recebido: {input_path.suffix}")

            transcription = input_path.read_text(encoding="utf-8")
            if not transcription.strip():
                raise ValueError("arquivo de transcrição está vazio")

            print(f"Processando: {input_path.name}")

            result = summarize(
                transcription=transcription,
                model=model,
                language=language,
                max_tokens=max_tokens,
                folders=folders if folders else None,
            )

            if folders:
                raw_folder = result.get("meeting_folder") or ""
                valid_names = {f.name for f in folders}
                folder_name = raw_folder if raw_folder in valid_names else unclassified
                dest_dir = output_path / folder_name
            else:
                dest_dir = output_path

            dest_dir.mkdir(parents=True, exist_ok=True)

            today = date.today().isoformat()
            slug = result["title_slug"] or input_path.stem
            output_file = dest_dir / f"{today}_{slug}.md"

            output_file.write_text(result["markdown"], encoding="utf-8")
            print(f"Sumário salvo em: {output_file}")

        except Exception as e:
            errors.append(input_path.name)
            print(f"ERRO [{input_path.name}]: {e}", file=sys.stderr)

    if errors:
        print(
            f"\n{len(errors)} arquivo(s) falharam: {', '.join(errors)}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
