from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from app.core.bdd_parser import parse_bdd_scenarios
from app.core.groq_service import generate_scenarios_from_code, generate_user_stories_from_code
from app.core.code_analyzer import analyze_source_code, analysis_to_prompt_context
import glob
import os

router = APIRouter()


@router.get("/")
def get_scenarios():
    return {"message": "Use POST /upload to analyze .md files"}


@router.post("/analyze-text")
def analyze_text(content: dict):
    """Parse existing BDD scenarios from markdown content."""
    markdown_content = content.get("content", "")
    
    if not markdown_content:
        return JSONResponse(
            status_code=400,
            content={"error": "No content provided"}
        )
    
    try:
        result = parse_bdd_scenarios(markdown_content)
        return {"scenarios": result, "status": "success", "total": len(result)}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/generate")
async def generate_from_source(content: dict):
    """
    Generate test scenarios from source code using AI + static analysis.
    
    Pipeline:
    1. Static code analysis extracts UI elements, interactions, validations
    2. Analysis enriches the AI prompt for targeted scenario generation
    3. AI generates Gherkin BDD scenarios
    4. BDD parser validates and structures the output
    5. Returns validated, structured scenarios
    """
    source_code = content.get("content", "")
    
    if not source_code:
        return JSONResponse(
            status_code=400,
            content={"error": "No content provided"}
        )
    
    try:
        # Step 1: Static analysis (always succeeds)
        analysis = analyze_source_code(source_code)
        analysis_summary = analysis_to_prompt_context(analysis)
        
        # Step 2: AI generation
        try:
            ai_output = await generate_scenarios_from_code(source_code)
        except Exception as ai_error:
            # If AI fails, fallback to static-only analysis
            return _fallback_static_response(analysis, str(ai_error))
        
        # Step 3: Parse and validate the AI output through BDD parser
        scenarios = parse_bdd_scenarios(ai_output)
        
        # Step 4: If parser found no scenarios, try returning raw AI output info
        if not scenarios:
            return {
                "scenarios": [],
                "status": "success",
                "total": 0,
                "ai_raw": ai_output,
                "analysis": {
                    "features": analysis.detected_features,
                    "ui_elements_count": len(analysis.ui_elements),
                    "interactions_count": len(analysis.interactions),
                    "validations_count": len(analysis.validations),
                    "api_calls_count": len(analysis.api_calls),
                },
                "message": "L'IA a généré du contenu mais le parser n'a pas pu extraire de scénarios structurés. Le contenu brut est fourni."
            }
        
        return {
            "scenarios": scenarios,
            "status": "success",
            "total": len(scenarios),
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


@router.post("/analyze-static")
def analyze_static(content: dict):
    """
    Static analysis only — no AI. Returns detected elements from source code.
    Useful for quick analysis or when AI service is unavailable.
    """
    source_code = content.get("content", "")
    
    if not source_code:
        return JSONResponse(
            status_code=400,
            content={"error": "No content provided"}
        )
    
    try:
        analysis = analyze_source_code(source_code)
        
        return {
            "status": "success",
            "analysis": {
                "features": analysis.detected_features,
                "ui_elements": [
                    {
                        "type": e.element_type,
                        "identifier": e.identifier,
                        "context": e.context,
                    }
                    for e in analysis.ui_elements
                ],
                "interactions": [
                    {
                        "type": i.interaction_type,
                        "target": i.target,
                        "handler": i.handler,
                    }
                    for i in analysis.interactions
                ],
                "validations": [
                    {
                        "field": v.field,
                        "rule": v.rule,
                    }
                    for v in analysis.validations
                ],
                "api_calls": [
                    {
                        "method": a.method,
                        "url": a.url,
                    }
                    for a in analysis.api_calls
                ],
                "conditional_states": [
                    {
                        "condition": s.condition,
                        "description": s.description,
                    }
                    for s in analysis.conditional_states
                ],
                "routes": analysis.routes,
            },
            "summary": analysis_to_prompt_context(analysis),
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.md'):
        return JSONResponse(
            status_code=400,
            content={"error": "Only .md files are supported"}
        )
    
    content = await file.read()
    content_str = content.decode('utf-8')
    
    try:
        result = parse_bdd_scenarios(content_str)
        return {
            "scenarios": result, 
            "filename": file.filename, 
            "status": "success",
            "total": len(result)
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


def _fallback_static_response(analysis, error_message: str):
    """
    Fallback response when AI is unavailable.
    Generates specific scenarios from static analysis based on detected features.
    """
    from app.core.bdd_parser import ScenarioAnalysis, Step, scenario_to_dict

    scenarios = []
    scenario_num = 0
    added_auth = False
    added_form = False
    added_login = False

    auth_keywords = ['auth', 'login', 'password', 'token', 'jwt']
    form_keywords = ['form', 'validation', 'required']

    for feature in analysis.detected_features:
        feature_lower = feature.lower()

        if any(kw in feature_lower for kw in auth_keywords) and not added_auth:
            scenario_num += 1
            scenario = ScenarioAnalysis(
                title=f"{scenario_num} - Connexion avec identifiants valides",
                scenario_number=scenario_num
            )
            scenario.steps = [
                Step(keyword="Given", text="l'utilisateur est sur la page de connexion", line_number=1),
                Step(keyword="When", text="il saisit un login et mot de passe valides et clique sur 'Se connecter'", line_number=2),
                Step(keyword="Then", text="il est redirigé vers le dashboard", line_number=3),
            ]
            scenario.warnings.append("Scénario généré par analyse statique (IA indisponible) - à affiner manuellement")
            scenarios.append(scenario_to_dict(scenario))

            scenario_num += 1
            scenario = ScenarioAnalysis(
                title=f"{scenario_num} - Connexion avec identifiants invalides",
                scenario_number=scenario_num
            )
            scenario.steps = [
                Step(keyword="Given", text="l'utilisateur est sur la page de connexion", line_number=1),
                Step(keyword="When", text="il saisit un login ou mot de passe incorrect et clique sur 'Se connecter'", line_number=2),
                Step(keyword="Then", text="un message d'erreur est affiché", line_number=3),
            ]
            scenario.warnings.append("Scénario généré par analyse statique (IA indisponible) - à affiner manuellement")
            scenarios.append(scenario_to_dict(scenario))

            scenario_num += 1
            scenario = ScenarioAnalysis(
                title=f"{scenario_num} - Accès au dashboard sans authentification",
                scenario_number=scenario_num
            )
            scenario.steps = [
                Step(keyword="Given", text="l'utilisateur n'est pas connecté", line_number=1),
                Step(keyword="When", text="il essaie d'accéder directement au dashboard", line_number=2),
                Step(keyword="Then", text="il est redirigé vers la page de connexion", line_number=3),
            ]
            scenario.warnings.append("Scénario généré par analyse statique (IA indisponible) - à affiner manuellement")
            scenarios.append(scenario_to_dict(scenario))
            added_auth = True

        if any(kw in feature_lower for kw in form_keywords) and not added_form:
            scenario_num += 1
            scenario = ScenarioAnalysis(
                title=f"{scenario_num} - Soumission du formulaire avec champs vides",
                scenario_number=scenario_num
            )
            scenario.steps = [
                Step(keyword="Given", text="le formulaire est affiché", line_number=1),
                Step(keyword="When", text="l'utilisateur clique sur 'Soumettre' sans remplir les champs obligatoires", line_number=2),
                Step(keyword="Then", text="les messages d'erreur pour les champs requis sont affichés", line_number=3),
            ]
            scenario.warnings.append("Scénario généré par analyse statique (IA indisponible) - à affiner manuellement")
            scenarios.append(scenario_to_dict(scenario))
            added_form = True

    for elem in analysis.ui_elements:
        if elem.element_type == 'input' and elem.identifier in ['username', 'email', 'password', 'login']:
            if not added_login:
                scenario_num += 1
                scenario = ScenarioAnalysis(
                    title=f"{scenario_num} - Validation du champ {elem.identifier}",
                    scenario_number=scenario_num
                )
                scenario.steps = [
                    Step(keyword="Given", text="le formulaire de connexion est affiché", line_number=1),
                    Step(keyword="When", text=f"le champ '{elem.identifier}' est laissé vide et le formulaire est soumis", line_number=2),
                    Step(keyword="Then", text=f"le message d'erreur \"Le champ {elem.identifier} est obligatoire\" est affiché", line_number=3),
                ]
                scenario.expected_error_message = f"Le champ {elem.identifier} est obligatoire"
                scenario.warnings.append("Scénario généré par analyse statique (IA indisponible) - à affiner manuellement")
                scenarios.append(scenario_to_dict(scenario))
                added_login = True
            break

    for api in analysis.api_calls:
        if '/login' in api.url or '/auth' in api.url:
            scenario_num += 1
            scenario = ScenarioAnalysis(
                title=f"{scenario_num} - Appel API {api.method} {api.url}",
                scenario_number=scenario_num
            )
            scenario.steps = [
                Step(keyword="Given", text="l'utilisateur saisit des identifiants", line_number=1),
                Step(keyword="When", text=f"une requête {api.method} est envoyée à '{api.url}'", line_number=2),
                Step(keyword="Then", text="la réponse contient un token d'authentification", line_number=3),
            ]
            scenario.warnings.append("Scénario généré par analyse statique (IA indisponible) - à affiner manuellement")
            scenarios.append(scenario_to_dict(scenario))

    for state in analysis.conditional_states:
        if state.condition == 'loading':
            scenario_num += 1
            scenario = ScenarioAnalysis(
                title=f"{scenario_num} - Affichage du chargement pendant la soumission",
                scenario_number=scenario_num
            )
            scenario.steps = [
                Step(keyword="Given", text="l'utilisateur est sur la page de connexion", line_number=1),
                Step(keyword="When", text="il clique sur 'Se connecter' et la requête est en cours", line_number=2),
                Step(keyword="Then", text="un indicateur de chargement (spinner) est affiché", line_number=3),
            ]
            scenario.warnings.append("Scénario généré par analyse statique (IA indisponible) - à affiner manuellement")
            scenarios.append(scenario_to_dict(scenario))

    if not scenarios:
        for feature in analysis.detected_features:
            scenario_num += 1
            scenario = ScenarioAnalysis(
                title=f"{scenario_num} - Test de la fonctionnalité: {feature}",
                scenario_number=scenario_num
            )
            scenario.steps = [
                Step(keyword="Given", text=f"la fonctionnalité '{feature}' est disponible", line_number=1),
                Step(keyword="When", text="l'utilisateur interagit avec cette fonctionnalité", line_number=2),
                Step(keyword="Then", text="le comportement attendu est observé", line_number=3),
            ]
            scenario.warnings.append("Scénario généré par analyse statique (IA indisponible) - à affiner manuellement")
            scenarios.append(scenario_to_dict(scenario))

    return {
        "scenarios": scenarios,
        "status": "partial",
        "total": len(scenarios),
        "ai_error": error_message,
        "message": f"L'IA n'est pas disponible ({error_message}). {len(scenarios)} scénarios générés par analyse statique.",
        "analysis": {
            "features": analysis.detected_features,
            "ui_elements_count": len(analysis.ui_elements),
            "interactions_count": len(analysis.interactions),
            "validations_count": len(analysis.validations),
            "api_calls_count": len(analysis.api_calls),
        }
    }


@router.post("/generate-from-path")
async def generate_from_path(body: dict):
    """
    Generate test scenarios from a local project path.
    
    Reads all source files from the given path and generates BDD tests.
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
        # Only frontend files - exclude backend and other noise
        extensions = ['.ts', '.tsx', '.vue', '.jsx', '.js']
        
        # Directories to exclude
        exclude_dirs = {'node_modules', 'dist', 'build', '.git', 'coverage', '.angular', 'vendor', '__pycache__'}
        
        content = ""
        files_read = []
        
        for ext in extensions:
            pattern = os.path.join(project_path, "**", f"*{ext}")
            for file_path in glob.glob(pattern, recursive=True):
                if os.path.isfile(file_path):
                    # Skip excluded directories
                    if any(excl in file_path for excl in exclude_dirs):
                        continue
                    
                    try:
                        relative_path = os.path.relpath(file_path, project_path)
                        
                        # Prioritize files by importance (components/pages first)
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
        
        # Sort content by priority (higher priority first)
        lines = content.split('\n')
        content = '\n'.join(lines)
        
        if not content:
            return JSONResponse(
                status_code=400,
                content={"error": "Aucun fichier source trouvé dans ce chemin"}
            )
        
        # Increase limit to allow AI to work
        max_content_size = 15000
        if len(content) > max_content_size:
            # Keep the beginning (most important files) and add a summary of what was cut
            content = content[:max_content_size]
            content += f"\n\n... (et {len(files_read) - 10} autres fichiers analysés mais tronqués pour la limite de tokens)"
        
        print(f"📄 Content size: {len(content)} chars, {len(files_read)} files")
        
        analysis = analyze_source_code(content)
        analysis_summary = analysis_to_prompt_context(analysis)
        
        try:
            ai_output = await generate_scenarios_from_code(content)
        except Exception as ai_error:
            import traceback
            print(f"❌ AI Error: {ai_error}")
            print(f"Traceback: {traceback.format_exc()}")
            return _fallback_static_response(analysis, str(ai_error))
        
        scenarios = parse_bdd_scenarios(ai_output)
        
        if not scenarios:
            return {
                "scenarios": [],
                "status": "success",
                "total": 0,
                "ai_raw": ai_output,
                "ai_used": True,
                "files_count": len(files_read),
                "message": "L'IA a généré du contenu mais le parser n'a pas pu extraire de scénarios structurés."
            }
        
        return {
            "scenarios": scenarios,
            "status": "success",
            "total": len(scenarios),
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