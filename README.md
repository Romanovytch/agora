# RAGnaR

[🇫🇷 Français](README.fr.md) | [🇬🇧 English](README.md)

**RAGnaR** is a document ingestion pipeline for Retrieval Augmented Generation (RAG). It ships a command line interface (CLI) to:

- Configure **what to ingest** (sources, paths, filters)
- Control **how to chunk** docs (target / overlap / max tokens)
- **Embed** chunks via an OpenAI-compatible embeddings endpoint
- **Store** vectors + payload in **Qdrant**

RAGnaR is designed for **technical documentation** and handles code blocks well. It is particularly suited for internal-specifics coding practices and documentations.

Pair it with [CanaR](https://github.com/Romanovytch/canar), a Streamlit chat UI that queries Qdrant to deliver effective RAG answers with citations.

## Features

- 🧩 **Config-driven sources** via `sources.yaml`
- ✂️ **Code-aware chunker** for Markdown/Quarto (no splitting fenced code)
- 🔤 OpenAI-compatible **remote embeddings** (e.g., vLLM)
- 📦 **Qdrant** vector store (cosine)
- 🧭 Rich payload: breadcrumbs, chapter/section, token counts, URLs
- ✅ **Validation** for configs with helpful errors

## Requirements

- **Python** ≥ 3.10
- A running **Qdrant** instance
- A running **embeddings** endpoint (OpenAI-compatible), e.g vLLM serving `bge-multilingual-gemma2`

## Install 

```
# optional but recommended: use a virtualenv
python -m venv .venv
source .venv/bin/activate

# from repo root
pip install -U pip
pip install -e .
```
This installs the CLI binaries: `ragnar-config` and `ragnar-ingest`.


## Environment variables

You can pass credentials/URLs either via **CLI flags**, **environment variables**, or a **.env file**.

Example `.env`:

```
# Embeddings
EMBED_API_BASE="https://my-embeddings-model-url/v1"
EMBED_API_KEY="api-key"
EMBED_MODEL="model-name"

# Qdrand env vars
QDRANT_API_KEY="api-key"
QDRANT_URL="http://qdrant:6333"
```

> The ingest CLI will use CLI args first, then env vars, and can also load a `.env` file via `--dotenv-file`.


## Data compatibility

Stable today:

- Markdown: `*.md`
- RM arkdown: `*.rmd`
- Quarto: `*.qmd` (include books)

> *We plan to support HTML files for the 1.0 release via dedicated HTML source/chunker*

Have your docs available locally (e.g., clone next to the repo):

```shell
cd ..
git clone https://github.com/InseeFrLab/utilitR.git
``` 

## Configure sources (`sources.yaml`)

Create a starter file:

```bash
ragnar-config init
```

This command will create a pre-configured `sources.yaml`. Edit the `sources:` section and add a source. For Markdown/Quarto use `kind: markdown_repo`.

### Fields

* `kind` **(required)**: must be `markdown_repo` for `.md` , `.rmd` or `.qmd` documents.
* `repo_path` **(required)**: path to the folder with your docs (absolute or relative to this YAML file)
* `base_url` **(required)**: public docs base URL used to build citation links
* `repo_url_template` *(optional)*: template for repo links, e.g. https://github.com/org/repo/blob/{commit}/{path}
* `default_lang` *(optional)*: if the main language of your documents is different than default *english*
* `exclude_dirs`, `include_globs` *(optional)*

Example of config for the project [utilitR](https://book.utilitr.org/) :

```yaml
version: 1

defaults:
  include_globs: ["**/*.md", "**/*.qmd", "**/*.Rmd"]
  exclude_dirs: [".git", "_book", "docs", ".quarto", "renv", ".github", "node_modules", "build", "dist", "site"]
  default_lang: "en"
  follow_symlinks: false

sources:
  utilitr:
    kind: markdown_repo
    repo_path: "../utilitR"
    base_url: "https://book.utilitr.org/"
    repo_url_template: "https://github.com/InseeFrLab/utilitR/blob/{commit}/{path}"
    default_lang: "fr"
    exclude_dirs: [".git", "_book", "docs", ".quarto", "renv", ".github"]
```

Validate your config YAML at any time:

```
ragnar-config validate --file config/sources.yaml
```


## Usage

Once your config validates, ingest one source into Qdrant:

```
# using .env, single source in YAML:
ragnar-ingest \
  --sources-config-path config/sources.yaml \
  --collection utilitr_v1 \
  --dotenv-file config/.env
```

You can also pass everything explicitly:

```
ragnar-ingest \
  --sources-config-path config/sources.yaml \
  --source utilitr \
  --collection utilitr_v1 \
  --embed-api-base https://my-embeddings.example.com/v1 \
  --embed-model BAAI/bge-multilingual-gemma2 \
  --qdrant-url http://localhost:6333 \
  --drop-collection
```

### CLI help (abridged)

```
usage: ragnar-ingest [-h]
                     [--sources-config-path PATH]
                     [--source NAME]
                     --collection NAME
                     [--dotenv-file PATH]
                     [--embed-api-base URL] [--embed-model ID] [--embed-api-key KEY]
                     [--qdrant-url URL] [--qdrant-api-key KEY]
                     [--insecure]
                     [--target-tokens N] [--overlap-tokens N] [--max-tokens N]
                     [--batch-size N] [--drop-collection]

Ingest one source from sources.yaml into Qdrant.

If a required value is missing, the CLI will suggest:
- passing a CLI flag,
- setting an env var,
- or supplying a .env file via --dotenv-file.
```

Defaults:

* `--target-tokens` = `800`
* `--max-tokens` = `1200`
* `--overlap-tokens` = `120`
* `--batch-size` = `64`

## Roadmap

- HTML site ingestion (e.g., pkgdown) via an html_site source + HtmlChunker
- Basic ingest quality checks (CLI `ragnar-analyze` to warn user about potential chunking issues with given parameters)
- Optional metrics logging (MLflow)
- Multi-source orchestration in a single run
- Implement BM25 / Hybrid methods and a router

## Contributing

Issues and PRs welcome! Please open an issue to discuss large changes before submitting a PR. (A full CONTRIBUTING.md is coming soon.)

## License

TBD (to be confirmed by maintainers).
@ Insee