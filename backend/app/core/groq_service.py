import os
import httpx
import asyncio

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

SYSTEM_PROMPT_REQUIREMENTS = """Tu es un Business Analyst Agile expert.

CONTEXTE: Tu analyses des documents de spécifications fonctionnelles pour générer des user stories.

RÈGLES ABSOLUES:
1. Chaque story doit AVOIR OBLIGATOIREMENT ces éléments:
   - ## STORY-XXX (numéro unique)
   - En tant que: [rôle métier]
   - Je veux: [fonctionnalité précise]
   - Afin de: [bénéfice business]
   - Critères d'acceptation: (au moins 2)

2. Génère entre 10 et 15 stories par section

FORMAT OBLIGATOIRE:
## STORY-001
En tant que: [rôle]
Je veux: [fonctionnalité]
Afin de: [bénéfice]
- Status: todo
- Priority: Medium
- Story Points: S
- Module: [nom]
- Critères d'acceptation:
  - [ ] Critère mesurable 1
  - [ ] Critère mesurable 2

Ne génère rien d'autre que les stories au format ci-dessus.
"""


async def _call_groq(model: str, messages: list, temperature: float = 0.3, max_tokens: int = 4000) -> str:
    """Call Groq API with retry and rate limit handling."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    async with httpx.AsyncClient(timeout=180.0) as client:
        for attempt in range(4):
            try:
                response = await client.post(
                    f"{GROQ_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                )
                
                if response.status_code == 429:
                    if attempt < 3:
                        wait_time = (attempt + 1) * 2
                        print(f"Rate limited, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    raise Exception("Rate limit exceeded")
                
                if response.status_code == 413:
                    raise Exception("Payload too large")
                
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                if attempt == 3:
                    raise
                await asyncio.sleep(1)
                continue
        return ""


def _split_content_into_chunks(content: str, max_tokens: int = 400) -> list[str]:
    """Split content into very small chunks."""
    sentences = content.split('.')
    chunks = []
    current = []
    current_tokens = 0
    
    for sent in sentences:
        if not sent.strip():
            continue
        sent_tokens = len(sent.split()) * 1.3
        if current_tokens + sent_tokens > max_tokens and current:
            chunks.append('. '.join(current) + '.')
            current = []
            current_tokens = 0
        current.append(sent)
        current_tokens += sent_tokens
    
    if current:
        chunks.append('. '.join(current) + '.')
    
    return chunks if chunks else [content[:800]]


def _extract_stories_from_text(text: str) -> list[str]:
    """Extract all story sections from text."""
    import re
    stories = []
    pattern = r'## STORY-\d+.*?(?=## STORY-\d+|$)'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    for m in matches:
        if 'En tant que' in m or '**En tant que**' in m:
            stories.append(m.strip())
    return stories


async def generate_user_stories_from_requirements(requirements: str) -> str:
    """Generate user stories from text requirements."""
    
    estimated_tokens = len(requirements.split()) * 1.3
    print(f"Estimated tokens: {estimated_tokens}")
    
    chunks = _split_content_into_chunks(requirements, max_tokens=400)
    print(f"Processing {len(chunks)} chunks...")
    
    all_stories = []
    
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        
        prompt = f"""Analyse cette section et génère 10 à 15 user stories.

SECTION {i+1}/{len(chunks)}:
{chunk}

Génère uniquement des stories au format:
## STORY-XXX
En tant que: [rôle]
Je veux: [fonctionnalité]
Afin de: [bénéfice]
- Status: todo
- Priority: Medium
- Story Points: S
- Module: [nom]
- Critères d'acceptation:
  - [ ] Critère 1
  - [ ] Critère 2
"""
        
        for retry in range(3):
            try:
                stories = await _call_groq(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT_REQUIREMENTS},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=4000
                )
                if stories and len(stories) > 50:
                    extracted = _extract_stories_from_text(stories)
                    all_stories.extend(extracted)
                    print(f"  -> Got {len(extracted)} stories")
                break
            except Exception as e:
                print(f"  Error: {e}, retry {retry+1}/3")
                if retry < 2:
                    await asyncio.sleep(2)
    
    if not all_stories:
        return _generate_fallback_stories(requirements)
    
    return "\n\n".join(all_stories)


def _generate_fallback_stories(content: str) -> str:
    """Generate user stories when API fails."""
    import re
    
    words = content.lower().split()
    stories = []
    
    roles = ["Utilisateur", "Administrateur", "Manager", "Client", "Employé", "Gestionnaire"]
    features = [
        ("gérer les comptes", "administrer les comptes utilisateurs"),
        ("consulter les rapports", "analyser les données"),
        ("modifier les paramètres", "personnaliser le système"),
        ("exporter les données", "travailler hors ligne"),
        ("importer les fichiers", "charger des données"),
        ("rechercher des informations", "trouver rapidement"),
        ("consulter l'historique", "suivre les activités"),
        ("valider les demandes", "approuver les processus"),
        ("recevoir des notifications", "être informé"),
        ("générer des documents", "produire des rapports"),
    ]
    
    for i, (feat, benefit) in enumerate(features[:15]):
        role = roles[i % len(roles)]
        stories.append(f"""## STORY-{i+1:03d}
**En tant que** {role}
**Je veux** {feat}
**Afin de** {benefit}
- **Status:** todo
- **Priority:** Medium
- **Story Points:** S
- **Module:** Core
- **Critères d'acceptation:**
  - [ ] La fonctionnalité est accessible
  - [ ] Le comportement est conforme
""")
    
    return "\n\n".join(stories)


async def generate_user_stories_from_code(source_code: str) -> str:
    """Generate user stories from source code."""
    return await _call_groq(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Génère des user stories en français."},
            {"role": "user", "content": f"Génère 20 user stories:\n{source_code[:2000]}"}
        ],
        temperature=0.3,
        max_tokens=8000
    )


async def generate_scenarios_from_code(source_code: str) -> str:
    """Generate test scenarios from source code."""
    return await _call_groq(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Tu génères des scénarios de test Gherkin."},
            {"role": "user", "content": f"Génère des scénarios de test:\n{source_code[:2000]}"}
        ],
        temperature=0.5,
        max_tokens=8000
    )


async def generate_user_stories_from_sfd(sfd_content: str, analysis_context: str = "") -> str:
    """Generate user stories from SFD document."""
    return await _call_groq(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_REQUIREMENTS},
            {"role": "user", "content": f"Génère des user stories:\n{sfd_content[:3000]}"}
        ],
        temperature=0.3,
        max_tokens=8000
    )


def analyze_source_code(source_code: str):
    """Simple code analyzer placeholder."""
    class Analysis:
        pass
    return Analysis()


def analysis_to_prompt_context(analysis) -> str:
    """Convert analysis to context string."""
    return ""