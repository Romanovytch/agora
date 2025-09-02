# RAGnaR

[🇫🇷 Français](README.fr.md) | [🇬🇧 English](README.md)

**RAGnaR** est une pipeline d’ingestion de documents pour la **Génération augmentée par la recherche (RAG)**. Il embarque une CLI pour :

- Configurer **quels documents ingérer** (sources, chemins, filtres)
- Contrôler **comment découper** les documents (taille/chevauchement/maximum de tokens)
- **Encoder** les documents découpés via un modèle d'embeddings compatible OpenAI
- **Stocker** les vecteurs issus de l'embeddings et les méta-données dans **Qdrant**

RAGnaR a été conçu pour ingérer efficacement de la **documentation technique** et gère particulièrement bien les blocs de code. Il est efficace pour augmenter un LLM avec de la documentations interne sur les recommandations et bonnes pratiques de code.

Vous pouvez associer RagnaR à [CanaR](https://github.com/Romanovytch/canar), une interface de chat qui interroge Qdrant pour fournir des réponses adaptées avec citations des ressources utilisées.

## Fonctionnalités

- 🧩 **Documents renseignés par fichier de configuration** via `sources.yaml`
- ✂️ **Chunker (découpeur) sensible aux blocs de code** pour Markdown/Quarto (pas de découpe au milieu des blocs de code)
- 🔤 **Embeddings distants** compatibles avec les endpoints OpenAI (e.g., vLLM)
- 📦 **Qdrant** comme base vectorielle (cosine)
- 🧭 **Méta-données riches** : fil d’Ariane, chapitre/section, nombre de tokens, URLs
- ✅ **Validation** des configs avec erreurs explicites

## Prérequis

- **Python** ≥ 3.10
- Une instance **Qdrant**
- Un modèle d'**embeddings** (compatible OpenAI /v1)

## Installation

```
# optionnel mais recommandé : environnement virtuel
python -m venv .venv
source .venv/bin/activate

# depuis la racine du dépôt
pip install -U pip
pip install -e .
```
Cela installe les binaires : `ragnar-config` et `ragnar-ingest`.


## Variables d'environnement

Vous pouvez renseigner les variables de configuration (URLs de Qdrant et du modèle, clés API...) dans vos **variables d'environnement** ou les écrire dans un fichier `.env` ou les passer  directement via **l'invite de commande `ragnar-ingest`**.

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

> Le fichier `.env` peut être passé en argument de l'invite de commande via `--dotenv-file`.


## Compatibilité des données

Supporté à ce jour :

- Markdown: `*.md`
- R Markdown: `*.rmd`
- Quarto: `*.qmd` (inclus les livres quarto)

> *Nous prévoyons de supporter l'ingestion de fichiers HTML pour la 1.0 à travers un Chunker et un Loader dédiés.*

Vous devez avoir les documents en local (par exemple, en clonant le projet markdown à côté de RAGnaR):

```shell
cd ..
git clone https://github.com/InseeFrLab/utilitR.git
``` 

## Fichier de configuration (`sources.yaml`)

Initialisez un modèle de fichier de configuration :

```bash
ragnar-config init
```

Cette commande va créer un fichier `sources.yaml` pré-rempli. Éditez la partie `sources:` et ajoutez-y une source. Pour des documents Markdown/Quarto, utilisez `kind: markdown_repo`. 

### Champs de configuration

* `kind` **(requis)**: doit être `markdown_repo` pour les fichiers `.md` , `.rmd` ou `.qmd`.
* `repo_path` **(requis)**: chemin vers le dossier contenant les documents (absolu ou relatif à ce fichier YAML)
* `base_url` **(requis)**: URL pour reconstruire les liens publiques (permets de citer les sources)
* `repo_url_template` *(optionnel)*: template pour les liens du repo git, par exemple : https://github.com/org/repo/blob/{commit}/{path}
* `default_lang` *(optionnel)*: *en* par défaut, *fr* pour les documents français
* `exclude_dirs`, `include_globs` : dossiers à exclure de la lecture ; dossiers ou fichiers à inclure

Example de fichier de configuration `sources.yaml` pour l'ingestion d'[utilitR](https://book.utilitr.org/) :

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

Validez votre fichier de configuration avec `ragnar-config validate` :

```
ragnar-config validate --file config/sources.yaml
```


## Utilisation

Une fois la configuration validée, utilisez la CLI `ragnar-ingest` pour ingérer les documents dans Qdrant :

```
# using .env, single source in YAML:
ragnar-ingest \
  --sources-config-path config/sources.yaml \
  --collection utilitr_v1 \
  --dotenv-file config/.env
```

Vous pouvez aussi tout renseigner explicitement :

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

### CLI help (abrégé)

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

Par défaut :

* `--target-tokens` = `800`
* `--max-tokens` = `1200`
* `--overlap-tokens` = `120`
* `--batch-size` = `64`

## Roadmap

- Implémenter le BM25 / Hybride pour les documents marqués `technical` (techniques) pour améliorer la qualité de la recherche
- Ingestion de sites/fichiers HTML (par exemple la doc pkgdown) en ajoutant un HtmlChunker
- Tester la qualité du découpage avant l'ingestion avec une CLI dédiée `ragnar-analyze` qui avertie/conseille l'utilisateur pour changer la configuration du Chunker.
- Métriques sur les modèles d'embeddings / tokens / logs (MLflow)
- Support du multi-sources en un seul fichier `sources.yaml`

## Contribuer

Les issues et les PR sont les bienvenues ! Merci d'ouvrir une issue pour discuter des changements avant de soumettre une PR. (Un CONTRIBUTING.md complet arrive bientôt)


## License

TBD (to be confirmed by maintainers).
@ Insee