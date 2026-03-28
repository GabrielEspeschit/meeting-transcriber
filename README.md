# meeting-summary

CLI para gerar sumarios estruturados de transcricoes de reunioes usando a API do Claude.

A CLI tool to generate structured meeting summaries from transcription files using the Claude API.

---

## Portugues

### O que faz

Recebe um arquivo `.txt` com a transcricao de uma reuniao e gera um sumario `.md` estruturado contendo:

- **Objetivo e Contexto** — topicos discutidos na reuniao
- **Ideias-Chave** — com atribuicao de quem contribuiu
- **Indefinicoes e Pontos a Discutir** — pontos sem consenso, com responsavel e stakeholder
- **Acoes e Proximos Passos** — checklist de tarefas com responsaveis

### Requisitos

- Python >= 3.9
- [uv](https://github.com/astral-sh/uv) (recomendado para gestao de ambiente)
- Chave de API da Anthropic

### Instalacao

```bash
git clone https://github.com/GabrielEspeschit/meeting-transcriber.git
cd meeting-transcriber
uv venv
uv pip install -e .
cp .env.example .env
# Edite o .env e preencha sua ANTHROPIC_API_KEY
```

### Uso

```bash
meeting-summary reuniao.txt
```

O sumario sera salvo como `YYYY-MM-DD_slug-da-reuniao.md` no diretorio configurado.

### Opcoes

| Flag | Descricao | Default |
|------|-----------|---------|
| `--output-dir` | Diretorio de saida | `OUTPUT_DIR` do `.env` |
| `--model` | Modelo do Claude | `claude-sonnet-4-20250514` |
| `--language` | Idioma (`pt-br`, `en`) | `pt-br` |
| `--max-tokens` | Maximo de tokens na resposta | `4096` |

A precedencia de configuracao e: flag CLI > variavel `.env` > valor default.

### Exemplo de saida

```markdown
# 2026-03-28 - Planejamento Q2

**Participantes:** Ana, Bruno, Carla

## Objetivo e Contexto
- Definir prioridades do Q2
- Revisar resultados do Q1

## Ideias-Chave
- **Focar em retencao** — contribuicao de Ana e Bruno

## Indefinicoes e Pontos a Discutir
- **Budget de marketing** — Responsavel: Carla | Stakeholder: Ana

## Acoes e Proximos Passos
- [ ] Enviar proposta de OKRs (Bruno)
```

---

## English

### What it does

Takes a `.txt` meeting transcription file and generates a structured `.md` summary containing:

- **Objective and Context** — topics discussed in the meeting
- **Key Ideas** — with attribution to contributors
- **Open Questions and Points to Discuss** — unresolved points with owner and stakeholder
- **Action Items and Next Steps** — task checklist with owners

### Requirements

- Python >= 3.9
- [uv](https://github.com/astral-sh/uv) (recommended for environment management)
- Anthropic API key

### Installation

```bash
git clone https://github.com/GabrielEspeschit/meeting-transcriber.git
cd meeting-transcriber
uv venv
uv pip install -e .
cp .env.example .env
# Edit .env and fill in your ANTHROPIC_API_KEY
```

### Usage

```bash
meeting-summary meeting.txt
```

The summary will be saved as `YYYY-MM-DD_meeting-slug.md` in the configured output directory.

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--output-dir` | Output directory | `OUTPUT_DIR` from `.env` |
| `--model` | Claude model | `claude-sonnet-4-20250514` |
| `--language` | Language (`pt-br`, `en`) | `pt-br` |
| `--max-tokens` | Max tokens in response | `4096` |

Configuration precedence: CLI flag > `.env` variable > hardcoded default.

### Output example

```markdown
# 2026-03-28 - Q2 Planning

**Participants:** Ana, Bruno, Carla

## Objective and Context
- Define Q2 priorities
- Review Q1 results

## Key Ideas
- **Focus on retention** — contribution by Ana and Bruno

## Open Questions and Points to Discuss
- **Marketing budget** — Owner: Carla | Stakeholder: Ana

## Action Items and Next Steps
- [ ] Send OKR proposal (Bruno)
```

---

## Project Structure

```
meeting-transcriber/
  pyproject.toml          # Project metadata and dependencies
  .env.example            # Configuration template
  meeting_summary/
    __init__.py
    cli.py                # Entry point, argparse, validation
    summarizer.py         # Anthropic API wrapper
    prompt.py             # System prompts (pt-br and en)
  tests/fixtures/         # Sample transcription files for testing
```
