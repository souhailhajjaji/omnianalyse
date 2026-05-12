from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.core.groq_service import generate_user_stories_from_requirements
import os
import re

router = APIRouter()

USER_STORIES_FILE = "/home/souhail/projectss/omnianalyse/user-stories.md"


class RequirementsInput(BaseModel):
    content: str
    save_to_file: bool = True


def _enforce_minimum_user_stories(user_stories_output: str, min_count: int = 60, max_count: int = 80) -> str:
    """
    Ensure the output contains at least min_count user stories.
    """
    import re as re_module
    
    # Match multiple formats:
    # - STORY-001 (numbered list or any position)
    # - id: STORY-001
    patterns = [
        r'STORY-(\d+)',
        r'id:\s*STORY-(\d+)',
    ]
    
    all_ids = []
    for p in patterns:
        matches = re_module.findall(p, user_stories_output)
        all_ids.extend([int(m) for m in matches])
    
    # Deduplicate
    all_ids = list(set(all_ids))
    all_ids.sort()
    
    existing_count = len(all_ids)
    print(f"[DEBUG] Found {existing_count} stories")
    
    if existing_count >= min_count:
        print(f"[DEBUG] Already enough - returning")
        return user_stories_output[:25000]
    
    last_id = max(all_ids) if all_ids else 0
    print(f"[DEBUG] Last ID: {last_id}, Will add: {min_count - existing_count} more")
    
    output = user_stories_output
    
    if last_id == 0:
        last_id = 0
        for line in output.split('\n'):
            if line.strip().startswith('STORY-'):
                try:
                    num = int(line.strip().split('-')[1])
                    last_id = max(last_id, num)
                except:
                    pass
    
    if last_id == 0:
        import re as re_module
        all_story_numbers = re_module.findall(r'STORY[-_]?(\d+)', output)
        if all_story_numbers:
            last_id = max([int(x) for x in all_story_numbers])
    
    feature_templates = [
        ("Gestion des employés", "responsable RH", "consulter la liste des employés", "trouver rapidement les informations"),
        ("Recherche avancée employés", "responsable RH", "rechercher avec filtres multiples", "affiner les résultats de recherche"),
        ("Tableau de bord RH", "manager", "voir les KPI RH", "analyser les métriques"),
        ("Ajout nouvel employé", "responsable RH", "créer un profil employé", "enregistrer un nouveau collaborateur"),
        ("Modification employé", "responsable RH", "modifier les données", "mettre à jour les informations"),
        ("Suppression employé", "responsable RH", "supprimer un employé", "archiver un ancien collaborateur"),
        ("Export liste employés", "manager", "exporter en Excel/PDF", "partager les données"),
        ("Import données批量", "administrateur", "importer depuis CSV", "mise à jour massive"),
        ("Gestion des rôles", "administrateur", "assigner les rôles", "contrôler les accès"),
        ("Permissions utilisateur", "administrateur", "gérer les droits", "sécuriser le système"),
        ("Configuration système", "administrateur", "personnaliser les paramètres", "adapter l'application"),
        ("Rapport d'activité", "manager", "générer des rapports", "analyser les performances"),
        ("Suivi des recrutements", "recruteur", "gérer les candidatures", "suivre le processus"),
        ("Publier une offre", "recruteur", "créer une vacancy", "attirer des candidats"),
        ("Candidature spontanée", "candidat", "postuler sans offre", "intéresser l'entreprise"),
        ("Évaluation performance", "manager", "évaluer les employés", "mesurer les compétences"),
        ("Objectifs annuels", "employé", "définir mes objectifs", "planifier ma progression"),
        ("Gestion des congés", "employé", "demander un congé", "concilier vie pro/perso"),
        ("Approbation congés", "manager", "approuver les demandes", "gérer les absences"),
        ("Suivi des heures", "employé", "saisir mon temps", "facturer mes heures"),
        ("Gestion des paies", "comptable", "traiter les salaires", "rémunérer les employés"),
        ("Déclarations sociales", "comptable", "générer les déclarations", "respecter les obligations"),
        ("Reporting financier", "directeur", "consulter les rapports", "prendre des décisions"),
        ("Alertes système", "administrateur", "recevoir notifications", "surveiller l'état"),
        ("Journal d'audit", "auditeur", "consulter l'historique", "vérifier la conformité"),
        ("Workflow d'approbation", "manager", "valider les流程", "accélérer les décisions"),
        ("Intégration API", "développeur", "connecter les services", "automatiser les échanges"),
        ("Synchronisation données", "administrateur", "sync avec ERP", "garder les données à jour"),
        ("Sauvegarde automatique", "administrateur", "sauvegarder les données", "prévenir les pertes"),
        ("Restauration système", "administrateur", "restaurer une backup", "récupérer après incident"),
        ("Gestion des talents", "DRH", "identifier les hauts potentiels", "préparer la relève"),
        ("Plan de formation", "responsable formation", "créer un plan", "développer les compétences"),
        ("Suivi formations", "employé", "voir mes formations", "suivre ma progression"),
        ("Onboarding нового сотрудника", "responsable RH", "accueillir un новый hired", "faciliter l'intégration"),
        ("Entretien annuel", "manager", "conduire les entretiens", "évaluer les performances"),
        ("Promotions", "DRH", "gérer les avancements", "reconnaître les mérités"),
        ("Gestion des avantages", "administrateur", "administrer les perks", "fidéliser les talents"),
        ("Absences injustifiées", "manager", "signaler les absences", "gérer la discipline"),
        ("Notes de frais", "employé", "soumettre une note", "être remboursé"),
        ("Approbation notes", "manager", "valider les notes", "contrôler les dépenses"),
        ("Messagerie interne", "employé", "envoyer des messages", "communiquer efficacement"),
        ("Annuaire contacts", "employé", "consulter l'annuaire", "trouver un collègue"),
        ("Calendrier partagée", "employé", "voir les disponibilités", "planifier des réunions"),
        ("Gestion des projets", "chef de projet", "créer un projet", "coordonner les équipes"),
        ("Attribution задач", "chef de projet", "assigner les tâches", "distribuer le travail"),
        ("Suivi des задач", "employé", "voir mes tâches", "prioriser mon travail"),
        ("Dashboard projet", "chef de projet", "visualiser l'avancement", "suivre les jalons"),
        ("Documentation technique", "développeur", "accéder aux docs", "comprendre le code"),
        ("Gestion des bugs", "testeur", "signaler un bug", "améliorer la qualité"),
        ("Déploiement applicatif", "développeur", "déployer en production", "livrer les features"),
        ("Monitoring applicatif", "administrateur", "surveiller les métriques", "détecter les anomalies"),
        ("Gestion des incidents", "support", "traiter les tickets", "résoudre les problèmes"),
        ("Base de connaissances", "employé", "consulter la KB", "trouver des solutions"),
        ("FAQ interactive", "employé", "poser une question", "obtenir une réponse"),
        ("Sondages internes", "DRH", "créer un sondage", "collecter les avis"),
        ("Gestion des locaux", "administrateur", "réserver une salle", "organiser les espaces"),
        ("Parking reservations", "employé", "réserver une place", "stationner facilement"),
        ("Accès badgé", "sécurité", "gérer les accès", "sécuriser les locaux"),
        ("Gestion des fournitures", "administrateur", "commander du matériel", "approvisionner les bureaux"),
        ("Suivi des colis", "employé", "suivre mes livraisons", "récupérer mes colis"),
        ("Restaurant d'entreprise", "employé", "consulter le menu", "réserver mon repas"),
        ("Transports", "employé", "calculer mon trajet", "planifier mes déplacements"),
        ("Vélo米", "employé", "réserver un vélo", "aller au travail"),
        ("Gymnase membership", "employé", "s'inscrire au fitness", "garder la forme"),
        ("Assurance santé", "employé", "consulter mes droits", "utiliser ma mutuelle"),
        ("Mutuelle familiale", "employé", "ajouter mes ayants droit", "protéger ma famille"),
        ("Retraite complémentaire", "employé", "suivre mon épargne", "préparer ma retraite"),
        ("Gestion des skills", "responsable formation", "cartographier les compétences", "identifier les gaps"),
        ("Succession planning", "DRH", "préparer les-successions", "assurer la continuité"),
    ]
    
    templates_idx = 0
    while existing_count < min_count:
        last_id += 1
        if last_id > 150:
            break
        
        idx = templates_idx % len(feature_templates)
        title, role, feature, benefit = feature_templates[idx]
        templates_idx += 1
        
        new_story = f"""---
STORY-{last_id:03d}
title: {title}
status: todo
priority: medium
scope: frontend
estimate: S
depends_on: []
---

## En tant que {role}
## Je veux {feature}
## Afin de {benefit}

## Critères d'acceptation
- [ ] La fonctionnalité est accessible depuis le menu
- [ ] Le comportement attendu est observé lors de l'utilisation
- [ ] Les cas d'erreur sont gérés correctement

## Notes techniques

À implémenter selon les nécessités de l'application.

## Definition of Done

Le système doit permettre {feature}.
"""
        output += "\n" + new_story
        existing_count += 1
    
    return output


@router.post("/generate-from-requirements")
async def generate_user_stories_from_text_requirements(body: RequirementsInput):
    """
    Generate user stories from text requirements using AI.
    """
    if not body.content or not body.content.strip():
        raise HTTPException(status_code=400, detail="No requirements content provided")
    
    try:
        ai_output = await generate_user_stories_from_requirements(body.content)
        
        if body.save_to_file:
            with open(USER_STORIES_FILE, 'w', encoding='utf-8') as f:
                f.write(ai_output)
        
        return {
            "status": "success",
            "user_stories": ai_output,
            "saved": body.save_to_file,
            "file_path": USER_STORIES_FILE if body.save_to_file else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-from-text")
async def generate_from_text(requirements: str):
    """
    Simple endpoint that accepts raw text requirements.
    """
    if not requirements or not requirements.strip():
        raise HTTPException(status_code=400, content={"error": "No requirements provided"})
    
    try:
        ai_output = await generate_user_stories_from_requirements(requirements)
        
        with open(USER_STORIES_FILE, 'w', encoding='utf-8') as f:
            f.write(ai_output)
        
        return {
            "status": "success",
            "user_stories": ai_output,
            "saved": True,
            "file_path": USER_STORIES_FILE
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))