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
        model="llama-3.1-70b-versatile",
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
        model="llama-3.1-70b-versatile",
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


SYSTEM_PROMPT_REQUIREMENTS = """Tu es un expert en gestion de projet agile. Génère DES user stories COMPLÈTES avec VRAIS critères.

Format STRICT:
---
id: STORY-XXX
title: [titre]
**En tant que** [rôle précis]
**Je veux** [fonctionnalité]
**Afin de** [bénéfice]
Critères: [ ] critère réel 1, [ ] critère réel 2, [ ] critère réel 3
---

RÈGLES:
1. 70 fonctionnalités = 70 user stories MINIMUM
2. Chaque critère doit être-SPÉCIFIQUE (pas "Critère à définir")
3. Utilise les critères DU FICHIER d'exigences
4. 12 modules à couvrir ABSOLUMENT"""

async def generate_user_stories_from_requirements(requirements: str) -> str:
    """Generate user stories from text requirements."""
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
        model="llama-3.1-70b-versatile",
        temperature=0.3,
        max_tokens=10000
    )
    
    return chat_completion.choices[0].message.content


def _build_requirements_prompt(requirements: str) -> str:
    """Build prompt - force TOUTES les 70 fonctionnalités."""
    
    prompt = f"""Fichier exigence: {requirements}

---
OBLIGATOIRE: 70 fonctionnalités = 70 user stories AVEC CRITÈRES RÉELS

=== AUTH (1-4) ===
1. Connexion username/password
2. Lien forgot password + réinitialisation email
3. Rôles Admin/ESS + restriction modules
4. Modifier mot deasse via menu profil

=== DASHBOARD (5-8) ===
5. Widget Time at Work (Punched In/Out)
6. Widget My Actions (tâches attente)
7. Quick Launch
8. Buzz Latest Posts

=== ADMIN USERS (9-13) ===
9. Recherche Username/User Role/Employee Name/Status
10. Tableau paginé + tri colonne
11. + Add utilisateur
12. ✏️ Edit / 🗑️ Delete
13. Reset filtres, Enabled/Disabled

=== PIM (14-17) ===
14. Recherche Employee Name/Id/Status/Supervisor/Job/Sub Unit
15. Filtre Current Employees Only
16. Configuration champs
17. Reports employés

=== NAVIGATION (18-21) ===
18. Menu latéral (Admin/PIM/Leave/Time...)
19. Barre recherche globale
20. Masquer menu ‹
21. Bouton Upgrade

=== TIME (22-26) ===
22. Employee Name * Required
23. Timesheets Pending Action
24. Dates période
25. Attendance
26. Project Info

=== RECRUITMENT (27-34) ===
27. Recherche Job Title/Vacancy/Hiring Manager/Status
28. Mots-clés virgules
29. Filtre Date From/To
30. + Add candidat
31. Liste Vacancy/Candidate/Manager/Date/Status
32. Statuts (Initiated, Shortlisted)
33. 👁️ View
34. ⬇️ Download CV

=== MY INFO (35-43) ===
35. Personal Details (Nom/ID/Nationalité/Genre)
36. Date picker
37. Menu (Contact/Emergency/Dependents/Job/Salary)
38. Custom Fields
39. Save Custom Fields
40. Attachments + Add
41. Métadonnées (Name/Size/Type/Date)
42. Edit Attachment
43. Delete Attachment

=== PERFORMANCE (44-50) ===
44. Filtres Employee/Job/Sub Unit/Status/Date
45. Include Current Only
46. Review Period/Due Date/Status
47. Configure
48. Manage Reviews
49. My Trackers
50. Employee Trackers

=== DIRECTORY (51-54) ===
51. Recherche Name/Title/Location
52. Cartes visuels
53. Records Found

=== CLAIM (55-63) ===
55. Filtres Employee/Reference/Event/Status/Date
56. Multi-devises
57. Statut Initiated/Submitted
58. Assign Claim
59. Submit Claim
60. My Claims
61. Employee Claims
62. View Details

=== BUZZ (64-70) ===
64. What's on your mind?
65. Post
66. Share Photos
67. Share Video
68. Like/Comment/Share
69. Tri Most Recent/Liked
70. Upcoming Anniversaries

---
CRITÈRES OBLIGATOIRES pour chaque story:
- [ ] Utilise les critères du FICHIER d'exigences
- [ ] Pas de "Critère à définir"
- [ ] 70 user stories MINIMUM
---
"""
    
    return prompt