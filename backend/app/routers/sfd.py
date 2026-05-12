from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from app.models.schemas import SFDInput
from app.core.sfd_analyzer import SFDAnalysis
from app.core.groq_service import generate_user_stories_from_sfd
import zipfile
import xml.etree.ElementTree as ET
import io

router = APIRouter()

USER_STORIES_FILE = "/home/souhail/projectss/omnianalyse/user-stories.md"


def extract_text_from_docx(file_content: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(file_content), 'r') as z:
            xml_content = z.read('word/document.xml')
        
        tree = ET.fromstring(xml_content)
        texts = []
        for t in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
            if t.text:
                texts.append(t.text)
        return '\n'.join(texts)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Impossible d'extraire le contenu du DOCX: {str(e)}")


def enforce_minimum_stories(user_stories: list, min_count: int = 60, max_count: int = 80) -> list:
    existing = len(user_stories)
    
    if existing >= min_count:
        return user_stories[:max_count]
    
    feature_templates = [
        ("Administrateur", "gérer les utilisateurs", "maintenir les comptes et permissions"),
        ("Utilisateur", "modifier mon profil", "Mettre à jour mes informations personnelles"),
        ("Utilisateur", "consulter l'historique", "Voir mes actions passées"),
        ("Utilisateur", "exporter mes données", "Télécharger mes informations"),
        ("Utilisateur", "importer des données", "Charger mes informations depuis un fichier"),
        ("Utilisateur", "recevoir des notifications", "Être notifié des événements importants"),
        ("Utilisateur", "gérer mes préférences", "Personnaliser mon expérience"),
        ("Administrateur", "générer des rapports", "Créer des rapports analytiques"),
        ("Administrateur", "configurer les paramètres", "Personnaliser l'application"),
        ("Administrateur", "surveiller l'activité", "Voir les statistiques d'utilisation"),
        ("Administrateur", "gérer les accès", "Contrôler les permissions"),
        ("Utilisateur", "rechercher des données", "Trouver rapidement les informations"),
        ("Utilisateur", "filtrer les résultats", "Affiner les recherches"),
        ("Utilisateur", "trier les données", "Organiser les informations"),
        ("Utilisateur", "visualiser les données", "Voir les graphiques et tableaux"),
        ("Administrateur", "exporter les rapports", "Générer des exports PDF/Excel"),
        ("Administrateur", "importer des données en masse", "Mettre à jour plusieurs enregistrements"),
        ("Utilisateur", "valider un formulaire", "Soumettre des données validées"),
        ("Utilisateur", "annuler une action", "Revenir sur mes décisions"),
        ("Utilisateur", "consulter les notifications", "Voir les alertes et messages"),
        ("Administrateur", "créer un rapport personnalisé", "Générer des rapports sur mesure"),
        ("Administrateur", "planifier une tâche", "Automatiser les processus"),
        ("Utilisateur", "partager des documents", "Collaborer avec d'autres"),
        ("Utilisateur", "commenter une ressource", "Donner mon avis"),
        ("Administrateur", "archiver des données", "Conserver les informations anciennes"),
        ("Utilisateur", "restaurer des données", "Récupérer des informations archivées"),
        ("Administrateur", "audit des actions", "Tracer les modifications"),
        ("Utilisateur", "authentifier via SSO", "Se connecter avec mes identifiants entreprise"),
        ("Utilisateur", "réinitialiser mon mot de passe", "Recouvrir l'accès à mon compte"),
        ("Administrateur", "définir les rôles", "Configurer les niveaux d'accès"),
        ("Utilisateur", "consulter un tableau de bord", "Voir les KPI et statistiques"),
        ("Administrateur", "gérer les workflows", "Automatiser les processus métier"),
        ("Utilisateur", "approuver une demande", "Valider les requêtes"),
        ("Utilisateur", "consulter les erreurs", "Identifier les problèmes"),
        ("Administrateur", "configurer les integrations", "Connecter les services externes"),
        ("Utilisateur", "synchroniser les données", "Mettre à jour depuis d'autres sources"),
        ("Utilisateur", "visualiser une timeline", "Voir l'historique chronologique"),
        ("Administrateur", "personnaliser les champs", "Adapter les formulaires"),
        ("Utilisateur", "dupliquer un enregistrement", "Copier des données existantes"),
        ("Utilisateur", "masquer des colonnes", "Personnaliser la vue"),
        ("Administrateur", "planifier des rapports", "Automatiser la génération"),
        ("Utilisateur", "filtrer par date", "Sélectionner une période"),
        ("Utilisateur", "exporter en CSV", "Obtenir les données brute"),
        ("Utilisateur", "visualiser sur mobile", "Accéder depuis mon téléphone"),
        ("Administrateur", "gérer les tags", "Catégoriser les contenus"),
        ("Utilisateur", "rechercher par tag", "Filtrer par catégorie"),
        ("Utilisateur", "lier des entités", "Associer des données"),
        ("Administrateur", "dupliquer une configuration", "Réutiliser les paramètres"),
        ("Utilisateur", "consulter les statistiques", "Voir les métriques"),
        ("Utilisateur", "comparer des données", "Analyser plusieurs versions"),
        ("Administrateur", "activer un module", "Activer des fonctionnalités"),
        ("Utilisateur", "désactiver les notifications", "Gérer les alertes"),
        ("Utilisateur", "partager un lien", "Envoyer un lien de ressource"),
        ("Administrateur", "forcer une synchronisation", "Lancer une mise à jour manuelle"),
        ("Utilisateur", "consulter l'historique version", "Voir les anciennes versions"),
        ("Administrateur", "restaurer une version", "Revenir à une configuration antérieure"),
        ("Utilisateur", "imprimer un rapport", "Obtenir une version papier"),
        ("Administrateur", "configurer le thème", "Personnaliser l'interface"),
        ("Utilisateur", "changer la langue", "Utiliser une autre langue"),
        ("Utilisateur", "zoom sur un graphique", "Voir les détails"),
        ("Utilisateur", "réorganiser les widgets", "Personnaliser le tableau de bord"),
    ]
    
    idx = 0
    for i, (role, feature, benefit) in enumerate(feature_templates):
        if existing + i >= max_count:
            break
        user_stories.append({
            "story_number": existing + i + 1,
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
                "[ ] La fonctionnalité est accessible depuis le menu",
                "[ ] Le comportement attendu est observé",
                "[ ] Les cas d'erreur sont gérés"
            ],
            "technical_notes": "",
            "definition_of_done": ""
        })
    
    for i, story in enumerate(user_stories):
        story['story_number'] = i + 1
    
    return user_stories


def parse_stories_from_ai_output(ai_output: str, analysis: SFDAnalysis) -> list:
    import re
    
    user_stories = []
    story_patterns = [
        r'##?\s*STORY[-_]?(\d+)',
        r'\*\*Story[-_\s]*(\d+)\*\*',
        r'Story\s*#?(\d+)',
        r'STORY[-_]?(\d+)',
    ]
    
    lines = ai_output.split('\n')
    current_story = None
    
    role_pattern = re.compile(r'en tant que [^,]+', re.IGNORECASE)
    want_pattern = re.compile(r'je veux [^,]+', re.IGNORECASE)
    benefit_pattern = re.compile(r'afin de .+$', re.IGNORECASE)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        matched_story = False
        for pattern in story_patterns:
            m = re.search(pattern, line, re.IGNORECASE)
            if m:
                if current_story and current_story.get('role'):
                    user_stories.append(current_story)
                story_num = int(m.group(1))
                current_story = {
                    "story_number": story_num,
                    "title": f"STORY-{story_num:03d}",
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
                matched_story = True
                break
        
        if not matched_story and current_story is not None:
            if not current_story.get('role'):
                rm = role_pattern.search(line)
                if rm:
                    role_text = rm.group(0)
                    current_story['role'] = re.sub(r'en tant que\s*', '', role_text, flags=re.IGNORECASE).strip()
            
            if current_story.get('role') and not current_story.get('feature'):
                wm = want_pattern.search(line)
                if wm:
                    feat_text = wm.group(0)
                    current_story['feature'] = re.sub(r'je veux\s*', '', feat_text, flags=re.IGNORECASE).strip()
            
            if current_story.get('feature') and not current_story.get('benefit'):
                bm = benefit_pattern.search(line)
                if bm:
                    benefit_text = bm.group(0)
                    current_story['benefit'] = re.sub(r'afin de\s*', '', benefit_text, flags=re.IGNORECASE).strip()
    
    if current_story and current_story.get('role'):
        user_stories.append(current_story)
    
    for story in user_stories:
        if not story.get('role') and analysis.actors:
            story['role'] = analysis.actors[0]
        if not story.get('feature'):
            story['feature'] = "accéder aux fonctionnalités"
        if not story.get('benefit'):
            story['benefit'] = "accomplir mon objectif"
        if not story.get('title'):
            story['title'] = f"{story.get('role', 'Utilisateur')} - {story.get('feature', 'feature')}"
    
    return user_stories


@router.post("/analyze-sfd")
async def analyze_sfd_and_generate_stories(input: SFDInput):
    try:
        content = input.content
        
        if content.startswith('PK'):
            content = extract_text_from_docx(content.encode() if isinstance(content, str) else content)
        
        analysis = SFDAnalysis(content)
        
        # Limit content size to avoid token limit
        max_content_size = 3000
        truncated_content = content[:max_content_size] if len(content) > max_content_size else content
        
        ai_output = await generate_user_stories_from_sfd(
            sfd_content=truncated_content,
            analysis_context=analysis.to_context_for_ai()
        )
        
        user_stories = parse_stories_from_ai_output(ai_output, analysis)
        user_stories = enforce_minimum_stories(user_stories, min_count=input.min_stories)
        
        if input.save_to_file:
            md_content = f"# User Stories - {analysis.project_name}\n\n"
            md_content += f"## Métadonnées SFD\n"
            md_content += f"- Acteurs: {', '.join(analysis.actors)}\n"
            md_content += f"- Modules: {', '.join(analysis.modules)}\n"
            md_content += f"- Date génération: Auto\n\n"
            md_content += "## User Stories\n\n"
            for story in user_stories:
                md_content += "## " + story.get('title', f"STORY-{story.get('story_number', 0):03d}") + "\n"
                md_content += f"- **Rôle:** {story.get('role', 'Utilisateur')}\n"
                md_content += f"- **Fonctionnalité:** {story.get('feature', '')}\n"
                md_content += f"- **Bénéfice:** {story.get('benefit', '')}\n"
                md_content += f"- **Status:** {story.get('status', 'todo')}\n"
                md_content += f"- **Priority:** {story.get('priority', 'medium')}\n\n"
            
            with open(USER_STORIES_FILE, 'w', encoding='utf-8') as f:
                f.write(md_content)
        
        return {
            "status": "success",
            "analysis": {
                "project_name": analysis.project_name,
                "actors": analysis.actors,
                "modules": analysis.modules,
                "functional_requirements_count": len(analysis.functional_requirements),
                "use_cases_count": len(analysis.use_cases)
            },
            "user_stories": user_stories,
            "total": len(user_stories),
            "saved": input.save_to_file,
            "file_path": USER_STORIES_FILE if input.save_to_file else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-sfd")
async def upload_sfd_and_generate_stories(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        if file.filename.endswith('.docx'):
            text_content = extract_text_from_docx(content)
        else:
            text_content = content.decode('utf-8') if isinstance(content, bytes) else content
        
        input_data = SFDInput(content=text_content, min_stories=60, save_to_file=True)
        return await analyze_sfd_and_generate_stories(input_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))