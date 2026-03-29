import re

import anthropic

from .prompt import build_user_message, get_system_prompt


def summarize(
    transcription: str,
    model: str = "claude-sonnet-4-20250514",
    language: str = "pt-br",
    max_tokens: int = 4096,
    folders: list = None,
) -> dict:
    """Envia a transcrição para o Claude e retorna o sumário estruturado.

    Returns:
        dict com "title_slug" (str), "meeting_folder" (str | None) e "markdown" (str)
    """
    client = anthropic.Anthropic()

    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0,
        system=get_system_prompt(language, folders),
        messages=[
            {"role": "user", "content": build_user_message(transcription, folders)},
        ],
    )

    response_text = message.content[0].text
    return _parse_response(response_text)


def _parse_response(response_text: str) -> dict:
    """Extrai o slug, pasta e o markdown da resposta do Claude."""
    lines = response_text.strip().split("\n")

    title_slug = None
    meeting_folder = None
    markdown_start = 0

    for i, line in enumerate(lines):
        match = re.match(r"^MEETING_SLUG:\s*(.+)$", line.strip())
        if match:
            title_slug = match.group(1).strip()
            markdown_start = i + 1
            break

    for i in range(markdown_start, len(lines)):
        match = re.match(r"^MEETING_FOLDER:\s*(.+)$", lines[i].strip())
        if match:
            meeting_folder = match.group(1).strip()
            markdown_start = i + 1
            break
        elif lines[i].strip():
            break

    # Remove linhas vazias entre os metadados e o início do markdown
    while markdown_start < len(lines) and not lines[markdown_start].strip():
        markdown_start += 1

    markdown = "\n".join(lines[markdown_start:]).strip()

    return {
        "title_slug": title_slug,
        "meeting_folder": meeting_folder,
        "markdown": markdown,
    }
