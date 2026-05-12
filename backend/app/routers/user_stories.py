from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from app.core.groq_service import generate_user_stories_from_code
from app.core.code_analyzer import analyze_source_code, analysis_to_prompt_context
import glob
import os
import re

router = APIRouter()


def _enforce_minimum_user_stories(user_stories: list, min_count: int = 60, max_count: int = 70) -> list:
    """
    Ensure the output contains at least min_count user stories.
    If not enough, add additional stories based on detected features.
    """
    existing_count = len(user_stories)
    
    if existing_count >= min_count:
        return user_stories[:max_count]
    
    feature_templates = [
        ("utilisateur", "modifier mon profil", "Mettre à jour mes informations personnelles"),
        ("utilisateur", "consulter l'historique", "Voir mes actions passées"),
        ("utilisateur", "exporter mes données", "Télécharger mes informations"),
        ("utilisateur", "importer des données", "Charger mes informations depuis un fichier"),
        ("utilisateur", "recevoir des notifications", "Être notifié des événements importants"),
        ("utilisateur", "gérer mes préférences", "Personnaliser mon expérience"),
        ("administrateur", "générer des rapports", "Créer des rapports analytiques"),
        ("administrateur", "configurer les paramètres", "Personnaliser l'application"),
        ("administrateur", "surveiller l'activité", "Voir les statistiques d'utilisation"),
        ("administrateur", "gérer les accès", "Contrôler les permissions"),
    ]
    
    idx = existing_count
    for role, feature, benefit in feature_templates:
        if idx >= max_count:
            break
        idx += 1
        user_stories.append({
            "story_number": idx,
            "title": f"{role} - {feature}",
            "role": role,
            "feature": feature,
            "benefit": benefit,
            "status": "todo",
            "priority": "medium",
            "scope": [],
            "estimate": "S",
            "depends_on": [],
            "acceptance_criteria": [
                "[ ] La fonctionnalité est accessible",
                "[ ] Le comportement est conforme aux attentes",
                "[ ] Les erreurs sont gérées"
            ],
            "technical_notes": "",
            "definition_of_done": ""
        })
    
    for i, story in enumerate(user_stories):
        story['story_number'] = i + 1
    
    return user_stories


@router.post("/generate-from-path")
async def generate_user_stories_from_path(body: dict):
    """
    Generate user stories from a local project path using AI.
    
    Returns user stories in Agile format:
    "En tant que [rôle], je veux [fonctionnalité], afin de [bénéfice]"
    """
    project_path = body.get("path", "")
    
    if not project_path:
        return JSONResponse(
            status_code=400,
            content={"error": "No path provided"}
        )
    
    if not os.path.isdir(project_path):
        return JSONResponse(
            status_code=400,
            content={"error": f"Le chemin '{project_path}' n'existe pas ou n'est pas un dossier"}
        )
    
    try:
        extensions = ['.ts', '.tsx', '.vue', '.jsx', '.js']
        exclude_dirs = {'node_modules', 'dist', 'build', '.git', 'coverage', '.angular', 'vendor', '__pycache__'}
        
        content = ""
        files_read = []
        
        for ext in extensions:
            pattern = os.path.join(project_path, "**", f"*{ext}")
            for file_path in glob.glob(pattern, recursive=True):
                if os.path.isfile(file_path):
                    if any(excl in file_path for excl in exclude_dirs):
                        continue
                    
                    try:
                        relative_path = os.path.relpath(file_path, project_path)
                        
                        priority = 0
                        if 'component' in relative_path.lower() or 'page' in relative_path.lower() or 'app/' in relative_path.lower():
                            priority = 2
                        elif 'lib/' in relative_path.lower() or 'utils' in relative_path.lower() or 'service' in relative_path.lower():
                            priority = 1
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            file_content = f.read()
                            if file_content.strip():
                                content += f"\n\n=== [{priority}] {relative_path} ===\n"
                                content += file_content
                                files_read.append(relative_path)
                    except Exception:
                        pass
        
        lines = content.split('\n')
        content = '\n'.join(lines)
        
        if not content:
            return JSONResponse(
                status_code=400,
                content={"error": "Aucun fichier source trouvé dans ce chemin"}
            )
        
        max_content_size = 50000
        if len(content) > max_content_size:
            content = content[:max_content_size]
            content += f"\n\n... (et d'autres fichiers analysés mais tronqués pour la limite de tokens)"
        
        print(f"📄 User Stories - Content size: {len(content)} chars, {len(files_read)} files")
        
        analysis = analyze_source_code(content)
        
        try:
            ai_output = await generate_user_stories_from_code(content)
        except Exception as ai_error:
            import traceback
            print(f"❌ AI Error: {ai_error}")
            return _fallback_user_stories_response(analysis, str(ai_error))
        
        user_stories = _parse_user_stories(ai_output, analysis.detected_features)
        
        user_stories = _enforce_minimum_user_stories(user_stories, min_count=60, max_count=70)
        
        if not user_stories:
            return {
                "user_stories": [],
                "status": "success",
                "total": 0,
                "ai_raw": ai_output,
                "ai_used": True,
                "files_count": len(files_read),
                "message": "L'IA a généré du contenu mais le parsing n'a pas pu extraire de user stories structurées."
            }
        
        return {
            "user_stories": user_stories,
            "status": "success",
            "total": len(user_stories),
            "ai_used": True,
            "files_count": len(files_read),
            "analysis": {
                "features": analysis.detected_features,
                "ui_elements_count": len(analysis.ui_elements),
                "interactions_count": len(analysis.interactions),
                "validations_count": len(analysis.validations),
                "api_calls_count": len(analysis.api_calls),
            }
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


def _generate_acceptance_criteria(feature: str) -> list:
    """Generate specific acceptance criteria based on the feature type."""
    feature_lower = feature.lower()
    
    criteria_map = {
        'authentifi': [
            "[ ] Le formulaire de connexion est affiché avec les champs username et password",
            "[ ] Les identifiants sont validés et un token JWT est retourné en cas de succès",
            "[ ] L'utilisateur est redirigé vers le dashboard après une connexion réussie"
        ],
        'erreurs': [
            "[ ] Un message d'erreur clair est affiché en cas d'échec",
            "[ ] L'erreur est logged pour le debugging",
            "[ ] L'utilisateur peut réessayer après une erreur"
        ],
        'chargement': [
            "[ ] Un indicateur de chargement (spinner) est affiché pendant le traitement",
            "[ ] Les interactions sont désactivées pendant le chargement",
            "[ ] Le contenu est affiché une fois le chargement terminé"
        ],
        'validation': [
            "[ ] Les champs obligatoires sont validés avant la soumission",
            "[ ] Les messages d'erreur sont affichés pour les champs invalides",
            "[ ] Le formulaire ne peut pas être soumis tant que les validations échouent"
        ],
        'navigation': [
            "[ ] Les liens de navigation fonctionnent correctement",
            "[ ] L'utilisateur est redirigé vers la bonne page",
            "[ ] L'historique de navigation est préservé"
        ],
        'formulaire': [
            "[ ] Tous les champs du formulaire sont accessibles",
            "[ ] Les données sont validées avant soumission",
            "[ ] Un message de confirmation est affiché après soumission"
        ],
        'recherch': [
            "[ ] La barre de recherche est visible et accessible",
            "[ ] Les résultats sont filtrés en temps réel",
            "[ ] Un message 'Aucun résultat' est affiché si pas de résultats"
        ],
        'télécharger': [
            "[ ] Le bouton de téléchargement est accessible",
            "[ ] Le fichier est généré au bon format",
            "[ ] Le téléchargement se termine sans erreur"
        ],
        'télévers': [
            "[ ] L'utilisateur peut sélectionner un fichier",
            "[ ] Le fichier est.uploadé et traité correctement",
            "[ ] Un message de confirmation est affiché après.upload"
        ],
        'modale': [
            "[ ] La modale s'ouvre lors du clic sur le bouton",
            "[ ] La modale peut être fermée avec le bouton X ou en cliquant à l'extérieur",
            "[ ] Le contenu de la modale est correctement affiché"
        ],
        'pagination': [
            "[ ] Les éléments sont paginés correctement",
            "[ ] Les boutons Suivant/Précédent fonctionnent",
            "[ ] Le nombre de pages est affiché"
        ],
        'table': [
            "[ ] Les données sont affichées dans un tableau",
            "[ ] Le tableau est triable par colonne",
            "[ ] Le tableau gère les données vides"
        ],
        'consulter': [
            "[ ] Les données sont affichées dans un tableau",
            "[ ] Le tableau est triable par colonne",
            "[ ] Le tableau gère les données vides"
        ],
        'liste': [
            "[ ] Les données sont affichées dans un tableau ou liste",
            "[ ] Les éléments sont accessibles et navigables",
            "[ ] La liste gère les données vides correctement"
        ],
        'responsive': [
            "[ ] L'interface s'adapte aux écrans mobiles (< 640px)",
            "[ ] L'interface s'adapte aux écrans tablette (640px - 1024px)",
            "[ ] L'interface s'affiche correctement sur desktop (> 1024px)"
        ],
        'drag': [
            "[ ] L'utilisateur peut glisser-déposer des éléments",
            "[ ] La zone de drop est visualisée lors du drag",
            "[ ] L'élément droppé est traité correctement"
        ],
        'connexion': [
            "[ ] Le formulaire de connexion est affiché avec les champs username et password",
            "[ ] Les identifiants sont validés et un token JWT est retourné en cas de succès",
            "[ ] L'utilisateur est redirigé vers le dashboard après une connexion réussie"
        ],
    }
    
    for key, criteria in criteria_map.items():
        if key in feature_lower:
            return criteria
    
    return [
        "[ ] La fonctionnalité est accessible depuis l'interface utilisateur",
        "[ ] Le comportement attendu est observé lors de l'utilisation",
        "[ ] Les cas d'erreur sont gérés correctement"
    ]


def _parse_user_stories(ai_output: str, detected_features: list = None) -> list:
    """Parse user stories from AI output."""
    if detected_features is None:
        detected_features = []
    
    user_stories = []
    lines = ai_output.split('\n')
    
    current_story = {}
    story_number = 0
    
    role_pattern = re.compile(r"En tant que (.+?)(?:,|\n)", re.IGNORECASE)
    want_pattern = re.compile(r"je veux (.+?)(?:,|\n| afin)", re.IGNORECASE)
    benefit_pattern = re.compile(r"afin de (.+?)$", re.IGNORECASE)
    
    role_key_pattern = re.compile(r"r[ôo]le:\s*(.+?)(?:\||\n|$)", re.IGNORECASE)
    feature_key_pattern = re.compile(r"fonctionnalit[éè]:\s*(.+?)(?:\||\n|$)", re.IGNORECASE)
    benefit_key_pattern = re.compile(r"benefit:\s*(.+?)(?:\||\n|$)", re.IGNORECASE)
    story_num_pattern = re.compile(r"\*\*?story-?(\d+)\*\*?", re.IGNORECASE)
    
    feature_keywords_map = {
        'Authentication / Login': ('utilisateur', 's\'authentifier', 'accéder à mon compte de manière sécurisée'),
        'Form Validation': ('utilisateur', 'soumettre un formulaire', 'enregistrer mes informations avec validation'),
        'Error Handling': ('utilisateur', 'gérer les erreurs', 'recevoir des informations claires en cas de problème'),
        'Loading State': ('utilisateur', 'voir l\'état de chargement', 'savoir que l\'application est en cours de traitement'),
        'Navigation / Routing': ('utilisateur', 'naviguer entre les pages', 'accéder aux différentes fonctionnalités'),
        'API Integration': ('utilisateur', 'interagir avec les données', 'accéder aux fonctionnalités du serveur'),
        'Search / Filter': ('utilisateur', 'rechercher et filtrer', 'trouver rapidement les informations recherchées'),
        'Download / Export': ('utilisateur', 'télécharger des données', 'travailler hors ligne ou partager des informations'),
        'File Upload': ('utilisateur', 'téléverser un fichier', 'partager des documents avec l\'application'),
        'Data Table / List': ('utilisateur', 'consulter une liste de données', 'visualiser et parcourir les informations'),
        'Responsive Design': ('utilisateur', 'utiliser sur mobile', 'accéder aux fonctionnalités depuis tout appareil'),
        'Drag and Drop': ('utilisateur', 'glisser-déposer des éléments', 'manipuler des éléments de manière intuitive'),
        'Modal / Dialog': ('utilisateur', 'ouvrir une modale', 'voir des détails supplémentaires'),
        'Pagination': ('utilisateur', 'paginer les résultats', 'parcourir de grandes quantités de données'),
    }
    
    used_features = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        role_match = role_pattern.search(line)
        if role_match:
            if current_story and 'role' in current_story:
                user_stories.append(current_story)
            story_number += 1
            current_story = {
                "story_number": story_number,
                "role": role_match.group(1).strip(),
                "feature": "",
                "benefit": "",
                "status": "todo",
                "priority": "medium",
                "scope": [],
                "estimate": "S",
                "depends_on": [],
                "acceptance_criteria": [],
                "technical_notes": "",
                "definition_of_done": ""
            }
            continue
        
        want_match = want_pattern.search(line)
        if want_match and current_story:
            current_story["feature"] = want_match.group(1).strip()
            continue
        
        benefit_match = benefit_pattern.search(line)
        if benefit_match and current_story:
            current_story["benefit"] = benefit_match.group(1).strip()
            if not current_story.get("title"):
                current_story["title"] = f"{current_story.get('role', 'User')} - {current_story.get('feature', 'feature')}"
            continue
        
        story_num_match = story_num_pattern.search(line)
        if story_num_match:
            story_number = int(story_num_match.group(1))
            current_story = {
                "story_number": story_number,
                "role": "",
                "feature": "",
                "benefit": "",
                "status": "todo",
                "priority": "medium",
                "scope": [],
                "estimate": "S",
                "depends_on": [],
                "acceptance_criteria": [],
                "technical_notes": "",
                "definition_of_done": ""
            }
            continue
        
        role_key_match = role_key_pattern.search(line)
        if role_key_match and current_story:
            current_story["role"] = role_key_match.group(1).strip()
            continue
        
        feature_key_match = feature_key_pattern.search(line)
        if feature_key_match and current_story:
            current_story["feature"] = feature_key_match.group(1).strip()
            continue
        
        benefit_key_match = benefit_key_pattern.search(line)
        if benefit_key_match and current_story:
            current_story["benefit"] = benefit_key_match.group(1).strip()
            if not current_story.get("title") and current_story.get("role") and current_story.get("feature"):
                current_story["title"] = f"{current_story.get('role', 'User')} - {current_story.get('feature', 'feature')}"
            user_stories.append(current_story)
            current_story = {}
            continue
        
        if current_story and current_story.get('benefit'):
            user_stories.append(current_story)
            current_story = {}
    
    if current_story and 'role' in current_story:
        user_stories.append(current_story)
    
    if not user_stories:
        story_number = 0
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('```'):
                if 'tant que' in line.lower() or 'en tant' in line.lower():
                    story_number += 1
                    user_stories.append({
                        "story_number": story_number,
                        "role": "",
                        "feature": "",
                        "benefit": "",
                        "title": f"STORY-{story_number:03d}",
                        "status": "todo",
                        "priority": "medium",
                        "scope": [],
                        "estimate": "S",
                        "depends_on": [],
                        "acceptance_criteria": [],
                        "technical_notes": "",
                        "definition_of_done": ""
                    })
                elif story_number > 0:
                    if user_stories:
                        last = user_stories[-1]
                        if not last.get('role'):
                            last['role'] = line
                        elif not last.get('feature'):
                            last['feature'] = line
    
    if detected_features:
        unique_features = list(set(detected_features))
        feature_counts = {}
        for story in user_stories:
            feature = story.get('feature', '').lower()
            for uf in unique_features:
                if uf.lower() in feature or feature in uf.lower():
                    feature_counts[uf] = feature_counts.get(uf, 0) + 1
                    break
        
        pass  # Removing the artificial max_stories trimming
    
    used_features = []
    
    for idx, story in enumerate(user_stories):
        story_number = story.get('story_number', idx+1)
        
        role = story.get('role', 'utilisateur')
        feature = story.get('feature', '')
        
        if role == 'développeur':
            role = 'utilisateur'
        
        feature_clean = feature.replace("'", "").replace('"', '').split(' ')[0:3]
        feature_title = ' '.join(feature_clean).capitalize()
        
        story['title'] = f"{role} - {feature_title}"
        story['role'] = role
        
        benefit = story.get('benefit', '')
        feature = story.get('feature', '')
        role = story.get('role', 'utilisateur')
        
        if feature == benefit or not feature or 'accomplir' in feature.lower() or feature in ['', 'faire quelque chose', 'utiliser une fonctionnalité']:
            benefit_lower = (benefit + ' ' + feature).lower()
            
            if 'erreur' in benefit_lower or 'échec' in benefit_lower:
                feature = "gérer les erreurs"
                benefit = "recevoir des informations claires en cas de problème"
            elif 'connexion' in benefit_lower or 'authent' in benefit_lower or 'login' in benefit_lower:
                feature = "s'authentifier"
                benefit = "accéder à mon compte de manière sécurisée"
            elif 'navigation' in benefit_lower or 'route' in benefit_lower or 'page' in benefit_lower:
                feature = "naviguer entre les pages"
                benefit = "accéder aux différentes fonctionnalités de l'application"
            elif 'chargement' in benefit_lower or 'loading' in benefit_lower or 'spinner' in benefit_lower:
                feature = "voir l\'état de chargement"
                benefit = "savoir que l\'application est en cours de traitement"
            elif 'télécharge' in benefit_lower or 'export' in benefit_lower:
                feature = "télécharger des données"
                benefit = "travailler hors ligne ou partager des informations"
            elif 'formulaire' in benefit_lower or 'validation' in benefit_lower or 'soumettre' in benefit_lower:
                feature = "soumettre un formulaire"
                benefit = "enregistrer mes informations avec validation"
            elif 'recherche' in benefit_lower or 'filter' in benefit_lower or 'filtr' in benefit_lower:
                feature = "rechercher et filtrer"
                benefit = "trouver rapidement les informations recherchées"
            elif 'table' in benefit_lower or 'liste' in benefit_lower or 'données' in benefit_lower:
                feature = "consulter une liste de données"
                benefit = "visualiser et parcourir les informations"
            elif 'modale' in benefit_lower or 'popup' in benefit_lower or 'dialog' in benefit_lower:
                feature = "ouvrir une fenêtre modale"
                benefit = "voir des détails supplémentaires"
            elif 'upload' in benefit_lower or 'télévers' in benefit_lower or 'fichier' in benefit_lower:
                feature = "téléverser un fichier"
                benefit = "partager des documents avec l'application"
            elif 'pagination' in benefit_lower or 'page' in benefit_lower:
                feature = "paginer les résultats"
                benefit = "parcourir grandes quantités de données"
            elif 'responsive' in benefit_lower or 'mobile' in benefit_lower:
                feature = "utiliser l'application sur mobile"
                benefit = "accéder aux fonctionnalités depuis n'importe quel appareil"
            else:
                feature = "accomplir une tâche"
                benefit = "réaliser mon objectif efficacement"
            
            story['feature'] = feature
            story['benefit'] = benefit
        
        if not story.get('role') or story['role'] == 'utilisateur':
            role_lower = (role + ' ' + story.get('feature', '')).lower()
            if 'admin' in role_lower or 'gestion' in role_lower:
                story['role'] = 'administrateur'
            elif 'développeur' in role_lower or 'dev' in role_lower:
                story['role'] = 'développeur'
            else:
                story['role'] = 'utilisateur'
        
        role = story.get('role', 'utilisateur')
        feature = story.get('feature', '')
        
        if feature or story.get('title', '').startswith('STORY-'):
            feature_clean = feature.replace("'", "").replace('"', '')[:30] if feature else 'tâche'
            story['title'] = f"{role} - {feature_clean}"
        
        if detected_features and ('accomplir' in feature.lower() or 'tâche' in feature.lower() or not feature):
            for detected_feat in detected_features:
                if detected_feat in feature_keywords_map and detected_feat not in used_features:
                    new_role, new_feature, new_benefit = feature_keywords_map[detected_feat]
                    story['role'] = new_role
                    story['feature'] = new_feature
                    story['benefit'] = new_benefit
                    story['title'] = f"{new_role} - {new_feature}"
                    used_features.append(detected_feat)
                    break
        
        if not story.get('status'):
            story['status'] = 'todo'
        if not story.get('priority'):
            story['priority'] = 'medium'
        if not story.get('scope'):
            story['scope'] = []
        if not story.get('estimate'):
            story['estimate'] = 'S'
        if not story.get('depends_on'):
            story['depends_on'] = []
        criteria = story.get('acceptance_criteria', [])
        
        is_generic = False
        if not criteria:
            is_generic = True
        elif isinstance(criteria, list):
            for c in criteria:
                c_str = str(c) if c else ""
                if 'Critère' in c_str or not c_str.strip():
                    is_generic = True
                    break
        
        if is_generic:
            story['acceptance_criteria'] = _generate_acceptance_criteria(story.get('feature', ''))
        if not story.get('technical_notes'):
            story['technical_notes'] = ''
        if not story.get('definition_of_done'):
            story['definition_of_done'] = ''
    
    if detected_features:
        unique_detected = list(set(detected_features))
        
        feature_to_keyword = {
            'Authentication / Login': ['authentifi', 'connexion', 'login', 'password'],
            'File Upload': ['télévers', 'upload', 'fichier'],
            'Form Validation': ['formulaire', 'validation', 'soumettre'],
            'Error Handling': ['erreur', 'échec'],
            'Loading State': ['chargement', 'loading', 'spinner'],
            'Navigation / Routing': ['naviguer', 'page', 'route'],
            'API Integration': ['interagir', 'données', 'api'],
            'Search / Filter': ['recherch', 'filter', 'filtr'],
            'Download / Export': ['télécharger', 'download', 'export'],
            'Data Table / List': ['table', 'liste', 'données', 'consulter', 'afficher'],
            'Responsive Design': ['responsive', 'mobile', 'écran'],
            'Drag and Drop': ['drag', 'glisser', 'drop'],
            'Modal / Dialog': ['modale', 'dialog', 'popup'],
            'Pagination': ['pagination', 'page'],
        }
        
        seen_features = set()
        clean_stories = []
        
        for story in user_stories:
            feature = story.get('feature', '').lower()
            feature_key = story.get('feature', '')
            
            matched_detected = None
            for detected, keywords in feature_to_keyword.items():
                if detected in unique_detected:
                    for kw in keywords:
                        if kw in feature:
                            matched_detected = detected
                            break
                if matched_detected:
                    break
            
            if matched_detected:
                if matched_detected not in seen_features:
                    seen_features.add(matched_detected)
                    clean_stories.append(story)
            elif feature and feature not in ['accomplir une tâche', '']:
                clean_stories.append(story)
        
        needed = max(len(unique_detected), len(clean_stories))
        while len(clean_stories) < needed:
            for detected in unique_detected:
                if detected not in seen_features and detected in feature_keywords_map:
                    role, feat, benefit = feature_keywords_map[detected]
                    clean_stories.append({
                        "story_number": len(clean_stories) + 1,
                        "title": f"{role} - {feat}",
                        "role": role,
                        "feature": feat,
                        "benefit": benefit,
                        "status": "todo",
                        "priority": "medium",
                        "scope": [],
                        "estimate": "S",
                        "depends_on": [],
                        "acceptance_criteria": _generate_acceptance_criteria(feat),
                        "technical_notes": "",
                        "definition_of_done": ""
                    })
                    seen_features.add(detected)
                    break
        
        user_stories = clean_stories
        
        feature_content_seen = set()
        final_stories = []
        for story in user_stories:
            feat = story.get('feature', '').lower()
            if feat not in feature_content_seen:
                feature_content_seen.add(feat)
                final_stories.append(story)
        
        user_stories = final_stories
        
        for i, story in enumerate(user_stories):
            story['story_number'] = i + 1
            story['title'] = f"{story.get('role', 'utilisateur')} - {story.get('feature', '')}"
    
    return user_stories


def _fallback_user_stories_response(analysis, error_message: str):
    """Fallback response when AI is unavailable."""
    user_stories = []
    story_num = 0
    
    feature_to_role = {
        'Authentication / Login': ('utilisateur', 'me connecter', 'accéder à mon compte de manière sécurisée'),
        'File Upload': ('utilisateur', 'téléverser un fichier', 'partager des documents avec l\'application'),
        'Form Validation': ('utilisateur', 'soumettre un formulaire', 'enregistrer mes informations avec validation'),
        'Data Table / List': ('utilisateur', 'consulter une liste de données', 'visualiser et parcourir les informations'),
        'Search / Filter': ('utilisateur', 'rechercher et filtrer des données', 'trouver rapidement ce que je cherche'),
        'Navigation / Routing': ('utilisateur', 'naviguer entre les pages', 'accéder aux différentes fonctionnalités'),
        'Modal / Dialog': ('utilisateur', 'ouvrir une fenêtre modale', 'voir des détails supplémentaires'),
        'Download / Export': ('utilisateur', 'télécharger des données', 'travailler hors ligne ou partager des informations'),
        'Error Handling': ('utilisateur', 'gérer les erreurs', 'recevoir des informations claires en cas de problème'),
        'Loading State': ('utilisateur', 'voir l\'état de chargement', 'savoir que l\'application est en cours de traitement'),
        'API Integration': ('utilisateur', 'interagir avec les données', 'accéder aux fonctionnalités du serveur'),
        'Responsive Design': ('utilisateur', 'utiliser l\'application sur mobile', 'accéder aux fonctionnalités depuis n\'importe quel appareil'),
        'Drag and Drop': ('utilisateur', 'glisser-déposer des éléments', 'manipuler des éléments de manière intuitive'),
        'Pagination': ('utilisateur', 'paginer les résultats', 'parcourir de grandes quantités de données'),
    }
    
    for feature in analysis.detected_features:
        if feature in feature_to_role:
            role, want, benefit = feature_to_role[feature]
            story_num += 1
            user_stories.append({
                "story_number": story_num,
                "title": f"{role} - {want}",
                "role": role,
                "feature": want,
                "benefit": benefit,
                "status": "todo",
                "priority": "medium",
                "scope": [],
                "estimate": "S",
                "depends_on": [],
                "acceptance_criteria": _generate_acceptance_criteria(want),
                "technical_notes": "",
                "definition_of_done": "",
                "source_feature": feature
            })
    
    if not user_stories:
        for feature in analysis.detected_features:
            story_num += 1
            feature_clean = feature.split('/')[0].strip()
            user_stories.append({
                "story_number": story_num,
                "title": f"utilisateur - {feature_clean}",
                "role": "utilisateur",
                "feature": f"utiliser la fonctionnalité {feature_clean}",
                "benefit": "accomplir mon objectif efficacement",
                "status": "todo",
                "priority": "medium",
                "scope": [],
                "estimate": "S",
                "depends_on": [],
                "acceptance_criteria": _generate_acceptance_criteria(feature_clean),
                "technical_notes": "",
                "definition_of_done": "",
                "source_feature": feature
            })
    
    return {
        "user_stories": user_stories,
        "status": "partial",
        "total": len(user_stories),
        "ai_error": error_message,
        "message": f"L'IA n'est pas disponible ({error_message}). {len(user_stories)} user stories générées par analyse statique.",
        "analysis": {
            "features": analysis.detected_features,
            "ui_elements_count": len(analysis.ui_elements),
            "interactions_count": len(analysis.interactions),
            "validations_count": len(analysis.validations),
            "api_calls_count": len(analysis.api_calls),
        }
    }