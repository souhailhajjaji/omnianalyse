import re


class SFDAnalysis:
    def __init__(self, content: str):
        self.content = content
        self.project_name = self._extract_project_name()
        self.actors = self._extract_actors()
        self.modules = self._extract_modules()
        self.functional_requirements = self._extract_functional_requirements()
        self.use_cases = self._extract_use_cases()
        self.system_overview = self._extract_system_overview()
        self.non_functional = self._extract_non_functional()
        
    def _extract_project_name(self) -> str:
        patterns = [
            r'(?:Project Name|<Project Name>)\s*([^\n<]+)',
            r'#\s*(.+)',
            r'Titre[:\s]*(.+)',
        ]
        for p in patterns:
            m = re.search(p, self.content, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
                if name and name not in ['<Project Name>', '']:
                    return name
        return "Projet SFD"
    
    def _extract_actors(self) -> list:
        actors = []
        patterns = [
            r'User/Role\s*[:\s]*([^\n]+)',
            r'(\d+\.\d+\.?\d*)\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
        ]
        
        actor_keywords = ['Admin', 'Manager', 'User', 'Client', 'Employee', 'Administrateur', 'Utilisateur', 'Client', 'Gestionnaire', 'Operateur', 'Operateur']
        for line in self.content.split('\n'):
            for kw in actor_keywords:
                if kw.lower() in line.lower() and line.strip():
                    match = re.search(r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)', line)
                    if match:
                        actor = match.group(1).strip()
                        if actor not in actors and len(actor) > 2:
                            actors.append(actor)
        
        default_actors = ['Administrateur', 'Utilisateur', 'Gestionnaire', 'Invité']
        for a in default_actors:
            if a not in actors:
                actors.append(a)
        return actors[:10]
    
    def _extract_modules(self) -> list:
        modules = []
        section_pattern = r'(?:^|\n)\s*(\d+\.\d+)\s+([A-Z][^<\n]{5,50})'
        matches = re.findall(section_pattern, self.content, re.MULTILINE)
        
        for num, name in matches:
            name = name.strip()
            if name and len(name) > 3:
                modules.append(name)
        
        if not modules:
            keywords = ['Authentication', 'Utilisateur', 'Gestion', 'Administration', 'Rapport', 'Configuration', 'Notification', 'Import', 'Export', 'Recherche']
            for kw in keywords:
                if kw.lower() in self.content.lower():
                    modules.append(f"Module {kw}")
        
        return modules[:20]
    
    def _extract_functional_requirements(self) -> list:
        requirements = []
        
        spec_pattern = r'(?:Spec ID|Sp[eé]cification)\s*[:\s]*([^\n]+)'
        specs = re.findall(spec_pattern, self.content, re.IGNORECASE)
        for s in specs:
            if s.strip():
                requirements.append(s.strip())
        
        desc_pattern = r'(?:Description|Sp[eé]cification)\s*[:\s]*([^\n]{20,200})'
        descs = re.findall(desc_pattern, self.content, re.IGNORECASE)
        for d in descs:
            if d.strip():
                requirements.append(d.strip())
        
        return requirements
    
    def _extract_use_cases(self) -> list:
        use_cases = []
        uc_pattern = r'UC[-_]?\d+\s*[^\n]*'
        matches = re.findall(uc_pattern, self.content, re.IGNORECASE)
        for m in matches:
            use_cases.append(m.strip())
        return use_cases
    
    def _extract_system_overview(self) -> str:
        patterns = [
            r'System/Solution Overview\s*[<>\n]*([^\n]{50,500})',
            r'Project Scope\s*[<>\n]*([^\n]{50,500})',
            r'Description\s*[:\s]*([^\n]{50,500})',
        ]
        for p in patterns:
            m = re.search(p, self.content, re.IGNORECASE | re.MULTILINE)
            if m:
                return m.group(1).strip()
        return ""
    
    def _extract_non_functional(self) -> list:
        nfr = []
        nfr_keywords = ['Performance', 'Security', 'Scalability', 'Reliability', 'Availability', 'Maintainability', 'Audit', 'Backup', 'Response time']
        for kw in nfr_keywords:
            if kw.lower() in self.content.lower():
                nfr.append(kw)
        return nfr
    
    def to_context_for_ai(self) -> str:
        return f"""PROJET: {self.project_name}

ACTEURS IDENTIFIÉS: {', '.join(self.actors)}

MODULES IDENTIFIÉS: {', '.join(self.modules)}

EXIGENCES FONCTIONNELLES:
{chr(10).join(self.functional_requirements[:20]) if self.functional_requirements else 'À analyser depuis le document'}

CAS D'UTILISATION IDENTIFIÉS: {', '.join(self.use_cases) if self.use_cases else 'Aucun'}

VUE D'ENSEMBLE DU SYSTÈME: {self.system_overview}

EXIGENCES NON FONCTIONNELLES: {', '.join(self.non_functional) if self.non_functional else 'Standard'}"""