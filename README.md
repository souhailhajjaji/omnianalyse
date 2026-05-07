# OmniAnalyse

Générateur de User Stories et Scénarios BDD alimenté par IA.

## Fonctionnalités

- **Génération de User Stories** - Génère des user stories au format agile à partir de fichiers maquette
- **Télécharger des fichiers maquette** - Support multi-formats (.md, .txt, .pdf, .doc, .docx)
- ** Génération de scénarios BDD** - Crée des scénarios de test en français (Gherkin)
- **Analyse statique de code** - Extrait automatiquement les éléments testables du code source

## Stack Technique

- **Backend**: FastAPI (Python)
- **Frontend**: Angular 21
- **IA**: Groq API (Llama 3.1 8B)

## Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Configurez les variables d'environnement:

```bash
cp backend/.env.example backend/.env
# Éditez .env avec vos clés API
```

Lancez le backend:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Frontend

```bash
cd frontend/omnianalyse-frontend
npm install
npm start
```

Accédez à `http://localhost:4200`

## Utilisation

1. Téléchargez un fichier maquette (exigences fonctionnelles)
2. Cliquez sur "Générer User Stories"
3. Consultez les user stories générées
4. Téléchargez le résultat en Markdown

## Structure du Projet

```
omnianalyse/
├── backend/
│   └── app/
│       ├── core/
│       │   ├── groq_service.py     # Service IA
│       │   ├── bdd_parser.py      # Parseur BDD
│       │   └── code_analyzer.py  # Analyse statique
│       └── routers/
│           └── user_stories_requirements.py
└── frontend/
    └── omnianalyse-frontend/
        └── src/app/components/dashboard/
```

## API Endpoints

| Méthode | Endpoint | Description |
|--------|----------|-------------|
| POST | `/requirements/generate-from-requirements` | Génère user stories depuis des exigences |

## License

MIT