"""
Groq LLM Service — Generates functional test scenarios from source code.

Uses a structured prompt enriched by static code analysis to produce
high-quality BDD test scenarios in JSON format that can be directly
parsed and validated by the BDD parser.
"""

from groq import AsyncGroq
from app.core.config import settings
from app.core.code_analyzer import analyze_source_code, analysis_to_prompt_context
import httpx

client = AsyncGroq(
    api_key=settings.GROQ_API_KEY,
    http_client=httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0))
)


SYSTEM_PROMPT = """Tu es un expert QA qui génère des scénarios de test BDD en français.

RÈGLES:
- Format: Étant donné que / Quand / Alors (3 lignes max par scénario)
- Chaque test de validation DOIT avoir le message d'erreur entre guillemets
- Sois précis: utilise les vrais noms de variables, endpoints du code
- Pas de "And" seul - supprime-le si inutile
- Maximum 15 scénarios"""


async def generate_scenarios_from_code(source_code: str) -> str:
    """
    Generate test scenarios from source code using AI.
    
    Pipeline:
    1. Static analysis extracts testable elements
    2. Analysis enriches the AI prompt
    3. AI generates structured BDD scenarios
    4. Output is in parseable Gherkin format
    """
    # Step 1: Static code analysis
    analysis = analyze_source_code(source_code)
    context = analysis_to_prompt_context(analysis)

    # Step 2: Build enriched prompt
    prompt = _build_prompt(source_code, context, analysis)

    # Step 3: Call LLM
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0.2,
        max_tokens=4000
    )

    return chat_completion.choices[0].message.content


def _build_prompt(source_code: str, context: str, analysis) -> str:
    """Build an enriched prompt with static analysis results."""

    complexity_score = (
        len(analysis.ui_elements) +
        len(analysis.interactions) * 2 +
        len(analysis.validations) * 2 +
        len(analysis.api_calls) * 3 +
        len(analysis.conditional_states)
    )

    if complexity_score > 30:
        min_scenarios = 12
        max_scenarios = 20
    elif complexity_score > 15:
        min_scenarios = 8
        max_scenarios = 15
    elif complexity_score > 5:
        min_scenarios = 5
        max_scenarios = 10
    else:
        min_scenarios = 3
        max_scenarios = 6

    suggestions = _generate_test_suggestions(analysis)
    features = analysis.detected_features
    test_types = _generate_test_types_from_features(analysis)

    prompt = f"""Analyse ce code et génère {min_scenarios}-{max_scenarios} scénarios BDD en français.

## Fonctionnalités: {', '.join(features[:5]) if features else 'À détecter'}

## Tests prioritaires:
{test_types[:300]}

## Extraits du code:
```
{source_code[:800]}
```

---

FORMAT OBLIGATOIRE (chaque scénario sur 3 lignes, PAS de numérotation):
## Scénario: 1 - [Titre du test]
Étant donné que [précondition]
Quand [action]
Alors [résultat]

## Scénario: 2 - [Titre suivant]
...
"""

    return prompt


def _generate_test_types_from_features(analysis) -> str:
    """Generate test types based on detected features."""
    features = analysis.detected_features
    test_types = []

    auth_keywords = ['auth', 'login', 'password', 'token', 'jwt', 'credentials']
    if any(any(kw in f.lower() for kw in auth_keywords) for f in features):
        test_types.extend([
            "**Authentification** - Tests de connexion avec identifiants valides/invalides",
            "**Sécurité** - Accès aux routes protégées sans authentification",
            "**Validation** - Formulaire avec champs vides, format email invalide",
        ])

    file_keywords = ['file', 'upload', 'download', 'export']
    if any(any(kw in f.lower() for kw in file_keywords) for f in features):
        test_types.extend([
            "**Upload** - Fichier valide, fichier invalide, sans fichier",
            "**Download** - Export des données, génération de fichier",
        ])

    form_keywords = ['form', 'validation', 'required']
    if any(any(kw in f.lower() for kw in form_keywords) for f in features) or analysis.validations:
        test_types.append("**Validation de formulaire** - Champs requis, format, limites")

    table_keywords = ['table', 'list', 'data', 'pagination']
    if any(any(kw in f.lower() for kw in table_keywords) for f in features):
        test_types.extend([
            "**Affichage des données** - Tableau, liste, pagination",
            "**Filtrage** - Recherche, tri, filtres",
        ])

    search_keywords = ['search', 'filter', 'query']
    if any(any(kw in f.lower() for kw in search_keywords) for f in features):
        test_types.append("**Recherche/filtre** - Résultats avec/sans filtres")

    modal_keywords = ['modal', 'dialog', 'popup']
    if any(any(kw in f.lower() for kw in modal_keywords) for f in features):
        test_types.append("**Modales** - Ouverture, fermeture, validation")

    nav_keywords = ['routing', 'navigation', 'router']
    if any(any(kw in f.lower() for kw in nav_keywords) for f in features) or analysis.routes:
        test_types.append("**Navigation** - Routes, redirections,deep linking")

    if analysis.conditional_states:
        loading = any(s.condition == 'loading' for s in analysis.conditional_states)
        error = any(s.condition == 'error' for s in analysis.conditional_states)
        if loading:
            test_types.append("**Loading** - Affichage spinner pendant le chargement")
        if error:
            test_types.append("**Gestion d'erreurs** - Messages d'erreur, affichage")

    if analysis.api_calls:
        test_types.append(f"**API** - Tests des {len(analysis.api_calls)} appels API détectés")

    if not test_types:
        test_types = [
            "**Tests généraux** - Interaction avec les éléments UI détectés",
            "**Validation** - Vérification des comportements",
        ]

    return "\n".join(f"- {t}" for t in test_types)


def _generate_test_suggestions(analysis) -> str:
    """Generate specific test suggestions based on the static analysis."""
    suggestions = []

    # File upload suggestions
    if any('upload' in f.lower() or 'file' in f.lower() for f in analysis.detected_features):
        suggestions.extend([
            "- Upload d'un fichier valide → vérifier le traitement réussi",
            "- Upload d'un fichier avec mauvaise extension → vérifier le message d'erreur",
            "- Upload sans fichier → vérifier le comportement",
            "- Upload d'un fichier vide → vérifier la gestion",
        ])

    # Form/validation suggestions
    if analysis.validations:
        suggestions.extend([
            "- Soumission du formulaire avec toutes les données valides",
            "- Soumission avec champs vides (tester chaque champ required)",
            "- Saisie de données aux limites (minlength, maxlength)",
            "- Saisie de données avec format invalide (email, pattern)",
        ])

    # API call suggestions
    for api in analysis.api_calls:
        suggestions.append(f"- Appel API {api.method} {api.url} → tester succès et erreur")

    # Conditional state suggestions
    for state in analysis.conditional_states:
        if state.condition == 'loading':
            suggestions.append("- Vérifier que le spinner/loading s'affiche pendant le traitement")
        elif state.condition == 'error':
            suggestions.append("- Vérifier l'affichage du message d'erreur quand le serveur échoue")
        elif state.condition == 'success/results':
            suggestions.append("- Vérifier l'affichage des résultats après un traitement réussi")

    # Navigation suggestions
    if analysis.routes:
        for route in analysis.routes:
            if 'path' in route:
                suggestions.append(f"- Navigation vers la route '{route['path']}' → vérifier le rendu")

    # Authentication suggestions
    if any('auth' in f.lower() or 'login' in f.lower() for f in analysis.detected_features):
        suggestions.extend([
            "- Connexion avec identifiants valides → vérifier la redirection",
            "- Connexion avec identifiants invalides → vérifier le message d'erreur",
            "- Tentative d'accès sans authentification → vérifier la protection",
        ])

    # Interaction suggestions
    for inter in analysis.interactions:
        if inter.interaction_type == 'click':
            suggestions.append(f"- Clic sur l'élément '{inter.target}' → vérifier le comportement")

    # Download/export suggestions
    if any('download' in f.lower() or 'export' in f.lower() for f in analysis.detected_features):
        suggestions.append("- Téléchargement/export des résultats → vérifier le fichier généré")

    # Responsive suggestions
    if any('responsive' in f.lower() for f in analysis.detected_features):
        suggestions.extend([
            "- Affichage sur mobile (viewport ≤ 640px) → vérifier l'adaptation",
            "- Affichage sur desktop → vérifier le layout complet",
        ])

    if not suggestions:
        suggestions.append("- Tests basiques de rendu et d'interaction pour chaque élément UI")

    return "\n".join(suggestions)


# Keep backward compatibility
async def analyze_markdown(content: str) -> str:
    """Legacy function — redirects to the new pipeline."""
    return await generate_scenarios_from_code(content)


SYSTEM_PROMPT_USER_STORIES = """Tu es un expert en gestion de projet agile qui génère des user stories à partir de code source.

RÈGLES:
- Format: "En tant que [rôle], je veux [fonctionnalité], afin de [bénéfice]"
- Chaque user story doit avoir 3 critères d'acceptation
- Sois précis: utilise les vrais noms de fonctionnalités du code
- Maximum 15 user stories par projet
- Un rôle par user story"""

async def generate_user_stories_from_code(source_code: str) -> str:
    """
    Generate user stories from source code using AI.
    
    Pipeline:
    1. Static analysis extracts testable elements
    2. Analysis enriches the AI prompt
    3. AI generates user stories in Agile format
    """
    analysis = analyze_source_code(source_code)
    context = analysis_to_prompt_context(analysis)
    
    prompt = _build_user_stories_prompt(source_code, context, analysis)
    
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_USER_STORIES
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=3000
    )
    
    return chat_completion.choices[0].message.content


def _build_user_stories_prompt(source_code: str, context: str, analysis) -> str:
    """Build prompt for user stories generation."""
    features = analysis.detected_features
    
    prompt = f"""Analyse ce code source et génère des user stories au format agile complet.

## Fonctionnalités détectées: {', '.join(features[:5]) if features else 'À détecter'}

## Extraits du code:
```
{source_code[:800]}
```

---

FORMAT OBLIGATOIRE (chaque user story doit être complète avec ces 3 éléments):

En tant que [rôle], je veux [fonctionnalité]
Afin de [bénéfice]
Critères: [ ] 1, [ ] 2, [ ] 3

Exemple:
En tant que utilisateur, je veux me connecter avec mon email et mot de passe
Afin de accéder à mon espace personnel
Critères: [ ] Le formulaire de connexion s'affiche, [ ] Les identifiants sont validés, [ ] L'utilisateur est redirigé vers le dashboard

---
"""
    
    return prompt


SYSTEM_PROMPT_REQUIREMENTS = """Tu es un expert en gestion de projet agile qui génère des user stories à partir d'exigences fonctionnelles.

RÈGLES OBLIGATOIRES - Format REQUIRED pour chaque user story:
---
id: STORY-XXX
title: [titre]
**En tant que** [rôle]
**Je veux** [fonctionnalité]
**Afin de** [bénéfice]
Critères: [ ] 1, [ ] 2, [ ] 3
---

RÈGLES CRITIQUES:
1. TOUS LES MODULES (12): Auth, Dashboard, Admin, PIM, Navigation, Time, Recruitment, My Info, Performance, Directory, Claim, Buzz
2. Chaque fonctionnalité ci-dessous = 1 user story
3. Rôles: Admin (gestion), Employé (consult/modif), Candidat (candidature), Manager (evaluation)
4. Minimum: 20 user stories"""

async def generate_user_stories_from_requirements(requirements: str) -> str:
    """
    Generate user stories from text requirements using AI.
    """
    prompt = _build_requirements_prompt(requirements)
    
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT_REQUIREMENTS
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0.4,
        max_tokens=8000
    )
    
    return chat_completion.choices[0].message.content


def _build_requirements_prompt(requirements: str) -> str:
    """Build prompt for user stories from requirements."""
    
    prompt = f"""Fichier d'exigences COMPLET - génère MINIMUM 20 user stories pour TOUTES les fonctionnalités:

```
{requirements}
```

---
LISTE EXHAUSTIVE DES FONCTIONNALITÉS PAR MODULE (1 user story chacune MINIMUM):

=== AUTH (1-4) ===
- Connexion username/password
- Lien forgot password + réinitialisation
- Différenciation rôles Admin/ESS
- Modification mot de passe via menu profil

=== DASHBOARD (5-8) ===
- Widget Time at Work (Punched In/Out, heures travaillées)
- Widget My Actions (tâches en attente)
- Raccourci Quick Launch
- Widget Buzz Latest Posts

=== ADMIN USERS (9-13) ===
- Recherche par Username/User Role/Employee Name/Status
- Tableau paginé avec tri par colonne
- Ajout nouvel utilisateur (+ Add)
- Édition/suppression utilisateur (✏️/🗑️)
- Reset filtres, statut Enabled/Disabled

=== PIM (14-17) ===
- Recherche employé par Employee Name/Id/Status/Supervisor/Job Title/Sub Unit
- Filtre Current Employees Only
- Bouton Configuration (champs personnalisés)
- Onglet Reports (rapports employés)

=== NAVIGATION (18-21) ===
- Menu latéral Admin/PIM/Leave/Time/Recruitment/My Info/Performance/Directory/Maintenance/Claim
- Barre recherche globale
- Masquer menu (bouton ‹)
- Bouton Upgrade (version premium)

=== TIME (22-26) ===
- Sélection Employee Name (* Required)
- Timesheets Pending Action
- Période dates (début - fin)
- Sous-module Attendance
- Sous-module Project Info

=== RECRUITMENT (27-34) ===
- Recherche avancée (Job Title/Vacancy/Hiring Manager/Status/Candidate Name/Keywords/Date/Method)
- Recherche par mots-clés (virgules)
- Filtre date (From/To)
- Ajout candidat (+ Add)
- Liste candidats (Vacancy/Candidate/Hiring Manager/Date/Status)
- Statuts candidature (Initiated, Shortlisted)
- View candidat (👁️)
- Download CV candidat (⬇️)

=== MY INFO (35-43) ===
- Consultation Personal Details (Nom/ID/Permis/Nationalité/État civil/Date naissance/Genre)
- Format ID multiples (Employee Id, Other Id)
- Date picker (License Expiry, Date of Birth)
- Menu latéral (Contact Details/Emergency Contacts/Dependents/Immigration/Job/Salary/Report-to)
- Custom Fields (Blood Type)
- Save Custom Fields
- Attachments (ajout + Add)
- Métadonnées fichiers (Name/Description/Size/Type/Date/Added By)
- Edit/Delete/TéléchargerAttachment

=== PERFORMANCE (44-50) ===
- Filtres Employee Name/Job Title/Sub Unit/Review Status/From Date/To Date
- Filtre Include Current Employees Only
- Informations (Review Period/Due Date/Review Status)
- Onglet Configure
- Onglet Manage Reviews
- Onglet My Trackers
- Onglet Employee Trackers

=== DIRECTORY (51-54) ===
- Recherche Employee Name/Job Title/Location
- Cartes visuels employés
- Affichage "Records Found"

=== CLAIM (55-63) ===
- Filtres Employee Name/Reference Id/Event Name/Status/dates
- Multi-devises (INR, DZD, CAD)
- Cycle de vie réclamation (Initiated, Submitted)
- Bouton Assign Claim
- Onglet Submit Claim
- Onglet My Claims
- Onglet Employee Claims
- View Details

=== BUZZ (64-70) ===
- Création publication ("What's on your mind?")
- Bouton Post
- Share Photos
- Share Video
- Like/Comment/Share
- Tri Most Recent/Liked/Commented
- Widget Upcoming Anniversaries

---
Génère AU FORMAT REQUIRED - MINIMUM 20 user stories.
Chaque fonctionnalité ci-dessus = 1 user story.
---
"""
    
    return prompt