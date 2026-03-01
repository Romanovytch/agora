[🇫🇷 Français](README.fr.md) | [🇬🇧 English](README.md)

# AgoRa

**AgoRa** est une pipeline d’ingestion documentaire pour la **Retrieval-Augmented Generation (RAG)**.

Elle fournit des outils en ligne de commande pour :

- 🧩 Configurer **quoi ingérer** (sources, chemins, filtres)
- ✂️ Contrôler **comment découper** les documents (cible / chevauchement / max tokens)
- 🔤 **Vectoriser (embeddings)** les chunks via un **endpoint compatible OpenAI**
- 📦 **Stocker** les vecteurs + le payload dans **Qdrant**

À associer avec **[CanaR](https://github.com/Romanovytch/canar)** :duck: , une interface qui permet de créer des chatbots qui interrogent Qdrant pour fournir des réponses basées sur les documents en citant les sources.

AgoRa est conçue pour être exécutée en **CLI** afin que l’ingestion puisse être automatisée : par exemple, déclencher un job d’ingestion lorsqu’un repo/site change (pipeline CI, cron, Job Kubernetes) pour **remplacer** ou **insérer dans** une collection Qdrant.

> :construction: AgoRa est actuellement en 0.x et ne prend en charge que les fichiers Markdown *(la plupart des “books” en ligne sont en réalité du Markdown)*.
> En attendant la prise en charge du PDF/HTML/DOCX en 1.0, nous recommandons de convertir les documents en Markdown (par exemple avec un convertisseur en ligne ou via une IA générative) avant ingestion.

---

## Écosystème (AgoRa + CanaR)

- **AgoRa** : ingestion (sources → chunking → embeddings → payload Qdrant)
- **CanaR** : UI de chat + assistants + retrieval + citations + historique de conversation

Si tu cherches par où commencer (guide d'installation, workflow de contribution, templates), commence plutôt par le dépôt de **CanaR** qui est le point d'entrée officiel de l'écosystème AgoRa-CanaR :
- Repo : https://github.com/Romanovytch/canar/README.fr.md
- Contribution : https://github.com/Romanovytch/canar/blob/main/CONTRIBUTING.fr.md

Le dépôt de CanaR fournit aussi un **docker compose** pour déployer rapidement l'instance Qdrant requise pour AgoRa.

> :warning: Il n'est pas indispensable d'utiliser AgoRa avec CanaR (ni l'inverse). Les deux peuvent être compatibles avec d'autres produits si vous avez déjà un outil d'ingestion ou une UI chatbot à votre disposition.

---

## Contrat de payload d’ingestion

AgoRa écrit des points dans Qdrant avec un **schéma de payload stable**, consommé par CanaR.

**Ce contrat est une surface de compatibilité centrale.** Toute modification des clés du payload doit être considérée comme une rupture (*breaking change*) et doit être coordonnée avec CanaR.

Le payload contient (au minimum) :

- `source` (identifiant de la source, par ex. nom du document)
- `doc_id` (identifiant stable du document)
- `path` (chemin relatif dans le dépôt / la source)
- `url` (URL de citation si pertinent, construite à partir de `base_url` + ancres/breadcrumbs si possible)
- `breadcrumbs` (hiérarchie chapitre/section)
- `content` (texte du chunk)
- `token_count` (ou équivalent, selon le tokenizer)
- `chunk_id`, `chunk_index` (stables à l'intérieur d'un document)
- optionnel : `repo_url` (lien vers le fichier à un commit donné), métadonnées de langue, etc.

> Le schéma exact devrait vivre prochainement dans un fichier dédié (par ex. `docs/payload-contract.md`) et être couvert par des golden tests.

---

## Fonctionnalités

- Sources **pilotées par configuration** via `sources.yaml`
- **Chunker intelligent**
- **Embeddings** distants compatibles OpenAI (ex : endpoint API, vLLM)
- Base vectorielle **Qdrant**
- Payload riche : breadcrumbs, chapitre/section, comptage de tokens, URLs
- **Validation** des configs avec des erreurs explicites

## Prérequis

- **Python ≥ 3.10**
- Une instance **Qdrant** en fonctionnement
- Un endpoint **embeddings** compatible OpenAI, ex. OpenAI `text-embedding-3-large/small`, `bge-multilingual-gemma2` servi via vLLM, etc.

---

## Démarrage rapide (local)

### Makefile (optionnel mais recommandé)

Un `Makefile` minimal est disponible (aligné avec CanaR) :

```text
Targets:
  make venv          - Créer un venv (.venv)
  make install       - Installer AgoRa (editable) + outils dev
  make test          - Lancer les tests (pytest)
  make lint          - Lancer ruff lint (check)
  make format        - Auto-formater avec ruff
  make format-check  - Vérifier le formatage avec ruff
  make ci            - Lancer lint + format-check + tests
```

### 1) Installation

```shell
# optionnel mais recommandé : utiliser un virtualenv
python -m venv .venv
source .venv/bin/activate

# depuis la racine du repo
pip install -U pip
pip install -e .
```
ou `make venv` & `make install`

Cela installe les binaires : `agora-config` et `agora-ingest`.

> Attention à bien charger l'environnement virtuel pour utiliser les binaires via `source .venv/bin/activate` puisqu'ils sont installés dans cet environnement.

### 2) Configurer les variables d’environnement

Il est possible de fournir les identifiants/URLs via **flags CLI**, **variables d’environnement**, ou via un fichier **`.env`**.

Exemple de `.env` :
```dotenv
# Embeddings
EMBED_API_BASE=https://my-embeddings-model-url/v1
EMBED_API_KEY=api-key
EMBED_MODEL=model-name

# Qdrant
QDRANT_API_KEY=api-key
QDRANT_URL=http://qdrant:6333
```
> La CLI d’ingestion utilise d’abord les args CLI, puis les variables d’env, et peut aussi charger un fichier `.env` via `--dotenv-path` (absolu ou relatif).

---

## Compatibilité des données

Stable aujourd’hui :
- Markdown : `*.md`
- R Markdown : `*.Rmd`
- Quarto : `*.qmd` (y compris les Quarto books)

À venir (roadmap) :
- Ingestion HTML (fichiers locaux ou scrap via un URL)
- Ingestion PDF / DOCX / XLSX

Pour qu'AgoRa trouve les documents, il faut avoir les docs en local (sauf scrap via un URL), exemple :
```shell
cd ..
git clone https://github.com/InseeFrLab/utilitR.git
```

---

## Configurer les sources (`sources.yaml`)

Créer un fichier de départ :
```shell
agora-config init
```

Cette commande crée un `sources.yaml` pré-configuré. Pour ajouter une source, modifiez la section `sources:` et renseignez les champs listés ci-dessous.
> Pour des dépôts Markdown/Quarto, utiliser `kind: markdown_repo`.

### Champs d'une source

- `kind` **(requis)** : `markdown_repo` pour les documents `.md`, `.Rmd` ou `.qmd`
- `repo_path` **(requis)** : chemin vers le dossier contenant les docs (absolu ou relatif à ce YAML)
- `base_url` **(requis)** : URL publique de base utilisée pour construire les liens de citation
- `repo_url_template` *(optionnel)* : template pour les liens repo, ex. `https://github.com/org/repo/blob/{commit}/{path}`
- `default_lang` *(optionnel)* : langue principale si différente de l'anglais par défaut
- `exclude_dirs`, `include_globs` *(optionnel)*

Exemple de config pour [utilitR](https://book.utilitr.org/) :
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

Pour valider le contenu du `source.yaml` à tout moment :
```shell
agora-config validate --file config/sources.yaml
```

---

## Utilisation

Une fois la config validée, pour ingérer une source dans Qdrant :
```shell
# avec .env, une source unique dans le YAML :
agora-ingest --sources-config-path config/sources.yaml --collection utilitr_v1 --dotenv-path config/.env
```
> On suppose ici que l'utilisateur a créé un dossier config/ dans lequel il a placé le `sources.yaml` édité et le `.env` édité.

AgoRa permets aussi de tout passer explicitement par arguments :
```shell
agora-ingest \
  --sources-config-path config/sources.yaml \
  --source utilitr \
  --collection utilitr_v1 \
  --embed-api-base https://my-embeddings.example.com/v1 \
  --embed-api-key sk-**** \
  --embed-model BAAI/bge-multilingual-gemma2 \
  --qdrant-url http://localhost:6333 \
  --qdrant-api-key ""\
  --drop-collection
```

## Aide CLI (extrait)
```
usage: agora-ingest [-h]
                    [--sources-config-path PATH]
                    [--source NAME]
                    --collection NAME
                    [--dotenv-path PATH]
                    [--embed-api-base URL] [--embed-model ID] [--embed-api-key KEY]
                    [--qdrant-url URL] [--qdrant-api-key KEY]
                    [--insecure]
                    [--target-tokens N] [--overlap-tokens N] [--max-tokens N]
                    [--batch-size N] [--drop-collection]

Ingest one source from sources.yaml into Qdrant.

If a required value is missing, the CLI will suggest:
- passing a CLI flag,
- setting an env var,
- or supplying a .env file via --dotenv-path.
```

Valeurs par défaut :
- `--target-tokens` = `800`
- `--max-tokens` = `1200`
- `--overlap-tokens` = `120`
- `--batch-size` = `64`

---

## Contribuer

Ce dépôt fait partie de l'écosystème `AgoRa + CanaR`.
- Pour les règles globales de contribution, consultez le guide contributeur ici : https://github.com/Romanovytch/canar/blob/main/CONTRIBUTING.fr.md
- Les tickets et PR spécifiques à l'ingestion (sources, chunkers, parseurs, contrat payload) sont les bienvenues ici.

## Licence

TBD (à confirmer par les mainteneurs)
