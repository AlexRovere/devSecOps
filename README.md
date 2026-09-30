# DevSecOps — pipeline CI de sécurité

[![CI Complète](https://github.com/AlexRovere/devsecops-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/AlexRovere/devsecops-pipeline/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://alexrovere.github.io/devsecops-pipeline/)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=AlexRovere_devSecOps&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=AlexRovere_devSecOps)

Pipeline GitHub Actions qui enchaîne lint, analyse de dépendances, analyse statique, scan d'images Docker et publication de la documentation, appliqué à une petite application Task Manager (FastAPI + front statique). Projet réalisé dans le cadre du module DevSecOps de la formation ENI.

> [!WARNING]
> L'API contient **des vulnérabilités volontaires** : c'est la matière que la chaîne de sécurité doit détecter.
> Elle ne doit pas être déployée telle quelle. Voir [Vulnérabilités volontaires](#vulnérabilités-volontaires).

## Le pipeline

`ci.yml` se déclenche à chaque push et pull request sur `master`, et orchestre des workflows réutilisables :

```
01 lint ──┐
02 Snyk ──┼──► 04 Docker ──► 05 Docs ──► 06 Completed
03 Sonar ─┘
```

| Étape | Outil | Rôle |
| --- | --- | --- |
| `01-lint.yml` | [pre-commit](https://pre-commit.com) | Espaces en fin de ligne, fins de fichier, YAML valide, fichiers trop volumineux |
| `02-snyk.yml` | [Snyk](https://snyk.io) | Dépendances vulnérables (`monitor`) et analyse du code (`code test`, sortie SARIF) |
| `03-sonarqube.yml` | [SonarQube Cloud](https://sonarcloud.io) | Qualité et sécurité du code (bugs, code smells, hotspots) |
| `04-docker.yml` | [Hadolint](https://github.com/hadolint/hadolint), [Trivy](https://trivy.dev) | Lint des Dockerfiles, build des images back et front, scan des CVE |
| `05-docs.yml` | [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) | Publication de la doc sur GitHub Pages |
| `06-completed.yml` | — | Notification de fin de pipeline |

Le Quality Gate SonarCloud est volontairement en échec : l'application contient des failles non corrigées. Les scans remontent les problèmes sans bloquer le pipeline (`continue-on-error`, `exit-code: 0`), pour pouvoir observer les résultats sur une application volontairement vulnérable.

Autour du pipeline :

- **Commits conventionnels et versioning** avec [Commitizen](https://commitizen-tools.github.io/commitizen/) (`cz.yaml`, `CHANGELOG.md` généré)
- **Hooks pre-commit** en local, identiques à ceux exécutés en CI
- **Image de base épinglée par digest** dans le Dockerfile du backend

Secrets GitHub nécessaires : `SNYK_TOKEN`, `SONAR_TOKEN`, `SONAR_HOST_URL`.

## Vulnérabilités volontaires

L'application sert de cible : les failles ci-dessous sont là pour être détectées par les outils du pipeline.

| Faille | Emplacement |
| --- | --- |
| Injection SQL (requête construite par f-string) | `GET /tasks/search` |
| Désérialisation YAML non sûre (`yaml.full_load`) | `POST /import` |
| Fuite des variables d'environnement | `GET /debug` |
| Clé d'API codée en dur | `API_KEY` dans `app/main.py` |
| CORS ouvert à toutes les origines avec credentials | `app/main.py` |
| Dépendances obsolètes et vulnérables (`jinja2==2.10.1`, `PyYAML==5.3.1`) | `src/backend/requirements.txt` |

## L'application

- **Backend** : FastAPI, SQLAlchemy, SQLite — CRUD de tâches (`/tasks`), recherche, import YAML, `/health`
- **Frontend** : HTML / CSS / JS sans framework, servi par Nginx

### Lancer avec Docker

```bash
docker compose up -d
```

- Front : <http://localhost:8080>
- API : <http://localhost:8000> (documentation interactive sur `/docs`)

### Lancer en local

```bash
# Backend
cd src/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Frontend (dans un autre terminal)
cd src/frontend
python3 -m http.server 5173
```

### Exemples d'appels

```bash
# Créer une tâche
curl -s -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Écrire tests API","description":"Ajouter des assertions sur /tasks"}' | jq

# Lister les tâches
curl -s http://127.0.0.1:8000/tasks | jq

# Mettre à jour une tâche
curl -s -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"DONE"}' | jq

# Supprimer une tâche
curl -i -X DELETE http://127.0.0.1:8000/tasks/1
```

## Structure

```
.github/workflows/   # ci.yml + workflows réutilisables 01 à 06
src/backend/         # API FastAPI + Dockerfile
src/frontend/        # Front statique + Dockerfile Nginx
docs/, mkdocs.yml    # Documentation publiée sur GitHub Pages
.pre-commit-config.yaml, cz.yaml, sonar-project.properties
```
