import re
import json
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Step:
    keyword: str
    text: str
    line_number: int


@dataclass
class ScenarioAnalysis:
    title: str
    scenario_number: int
    steps: List[Step] = field(default_factory=list)
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    expected_error_message: str = ""


def parse_json_tests(markdown_content: str) -> List[Dict[str, Any]]:
    # First: extract JSON block from code fences
    code_block_pattern = re.compile(r'```(?:json)?\s*\n(.*?)```', re.DOTALL | re.IGNORECASE)
    matches = code_block_pattern.findall(markdown_content)
    
    for match in matches:
        match = match.strip()
        if match.startswith('{') or match.startswith('['):
            try:
                data = json.loads(match)
            except json.JSONDecodeError:
                continue
            
            result = parse_json_tests_data(data)
            if result:
                return result
    
    # Second: find raw JSON with "tests" key
    if '"tests"' in markdown_content:
        start = markdown_content.find('"tests"')
        bracket_start = markdown_content.find('[', start)
        
        count = 0
        json_str = ""
        for i, char in enumerate(markdown_content[bracket_start:]):
            json_str += char
            if char == '[':
                count += 1
            elif char == ']':
                count -= 1
            if count == 0:
                break
        
        try:
            tests_array = json.loads(json_str)
            data = {"tests": tests_array}
        except json.JSONDecodeError:
            pass
        else:
            result = parse_json_tests_data(data)
            if result:
                return result
    
    return []


def parse_json_tests_data(data):
    if 'tests' in data and isinstance(data['tests'], list):
        scenarios = []
        for idx, test in enumerate(data['tests'], 1):
            steps = []
            if 'steps' in test and isinstance(test['steps'], list):
                for step_data in test['steps']:
                    action = step_data.get('action', '')
                    expected = step_data.get('expected', '')
                    selector = step_data.get('selector', '')
                    
                    if action in ['navigate', 'go_to', 'open']:
                        keyword = 'Given'
                        text = f"I navigate to {step_data.get('url', '')}"
                    elif action == 'exists':
                        if expected:
                            keyword = 'Then'
                            text = f"the element '{selector}' should exist"
                        else:
                            keyword = 'Then'
                            text = f"the element '{selector}' should not exist"
                    elif action == 'click':
                        keyword = 'When'
                        text = f"I click on '{selector}'"
                    elif action == 'fill':
                        keyword = 'And'
                        text = f"I fill '{selector}' with '{step_data.get('value', '')}'"
                    elif action == 'wait':
                        keyword = 'When'
                        text = f"I wait for {step_data.get('timeout', 5000)}ms"
                    else:
                        keyword = 'Then'
                        text = f"I perform action '{action}'"
                    
                    steps.append(Step(
                        keyword=keyword,
                        text=text,
                        line_number=idx
                    ))
            
            test_id = test.get('id', f'TEST-{idx:03d}')
            test_name = test.get('name', f'Test {idx}')
            test_type = test.get('type', 'functional')
            
            scenario = ScenarioAnalysis(
                title=f"{test_id}: {test_name} ({test_type})",
                scenario_number=idx
            )
            scenario.steps = steps
            
            if not steps:
                scenario.is_valid = False
                scenario.errors.append("Aucune étape trouvée")
            else:
                analyze_scenario(scenario, None, None)
            
            scenarios.append(scenario)
        
        if scenarios:
            return [scenario_to_dict(s) for s in scenarios]
    
    return []


def parse_bdd_scenarios(markdown_content: str) -> List[Dict[str, Any]]:
    json_result = parse_json_tests(markdown_content)
    if json_result:
        return json_result
    
    lines = markdown_content.split('\n')
    scenarios: List[ScenarioAnalysis] = []
    current_scenario: ScenarioAnalysis | None = None
    scenario_number = 0
    found_scenario = False

    step_keyword_pattern = re.compile(
        r'^\s*[-*]?\s*(Étant\s+donné(?:\s+que)?|Etant\s+donné(?:\s+que)?|Quand|Alors|Et|Mais|Given|When|Then|And|But)\s+(.+?)\s*$',
        re.IGNORECASE
    )

    scenario_patterns = [
        (re.compile(r'^\s*##\s*(?:Scénario|Scenario)\s*[:.]\s*(\d+)[\s\-]*(.+?)\s*$', re.IGNORECASE), 2),
        (re.compile(r'^\s*\*+\s*(?:Test\s+(?:Scenario|Sénario)|Scénario|Scenario)\s*[:\-]?\s*(\d+:?.+?)\s*\*+$', re.IGNORECASE), 1),
        (re.compile(r'^\s*#+\s*#*\s*(?:Test\s+(?:Scenario|Sénario)|Scénario|Scenario)\s*[:\-]?\s*(.+)', re.IGNORECASE), 1),
        (re.compile(r'^\s*\*+\s*(?:Test\s+(?:Scenario|Sénario)|Scénario|Scenario)\s*[:\-]?\s*(\d+)', re.IGNORECASE), 1),
    ]

    error_message_pattern = re.compile(
        r'["\']?([^"\']+)["\']?\s*$',
        re.IGNORECASE
    )

    empty_field_pattern = re.compile(
        r'(?:laisse|leave|laisses?|empty|vide)\s+(?:les?|the)?\s+(?:champs?|fields?)',
        re.IGNORECASE
    )

    for i, line in enumerate(lines):
        matched_scenario = None
        matched_pattern_name = None
        for pattern, group_idx in scenario_patterns:
            match = pattern.match(line)
            if match:
                matched_scenario = match.group(group_idx).strip()
                matched_pattern_name = pattern.pattern
                break
        
        if matched_scenario:
            if current_scenario and current_scenario.steps:
                analyze_scenario(current_scenario, empty_field_pattern, error_message_pattern)
                scenarios.append(current_scenario)

            scenario_number += 1
            title = matched_scenario if matched_scenario else f"Scénario {scenario_number}"
            current_scenario = ScenarioAnalysis(
                title=title,
                scenario_number=scenario_number
            )
            continue

        if current_scenario:
            step_match = step_keyword_pattern.match(line)
            if step_match:
                raw_keyword = step_match.group(1)
                keyword_map = {
                    'Étant donné que': 'Given', 'Etant donné que': 'Given',
                    'Étant donné': 'Given', 'Etant donné': 'Given',
                    'Étant': 'Given', 'Etant': 'Given',
                    'Quand': 'When',
                    'Alors': 'Then',
                    'Et': 'And',
                    'Mais': 'But',
                    'given': 'Given', 'when': 'When', 'then': 'Then', 'and': 'And', 'but': 'But',
                }
                keyword = keyword_map.get(raw_keyword, raw_keyword).capitalize()
                text = step_match.group(2).strip()
                current_scenario.steps.append(Step(
                    keyword=keyword,
                    text=text,
                    line_number=i + 1
                ))

                if keyword.lower() == 'then':
                    potential_msg = None

                    # Skip if this is a success scenario (no error message)
                    success_keywords = ['succès', 'succes', 'bienvenue', 'redirigé', 'redirige', 'succès', 'successful']
                    if any(kw in text.lower() for kw in success_keywords):
                        current_scenario.expected_error_message = ""
                    else:
                        # Pattern 1: avec le message "xxx"
                        match = re.search(r'avec (?:le )?message ["\']([^"\']+)["\']', text, re.IGNORECASE)
                        if match:
                            potential_msg = match.group(1).strip()

                        # Pattern 2: affiche un message d'erreur "xxx"
                        if not potential_msg:
                            match = re.search(r'affiche (?:un )?message d\'?erreurs? ["\']([^"\']+)["\']', text, re.IGNORECASE)
                            if match:
                                potential_msg = match.group(1).strip()

                        # Pattern 3: le message "xxx" est affiché
                        if not potential_msg:
                            match = re.search(r'le message ["\']([^"\']+)["\']', text, re.IGNORECASE)
                            if match:
                                potential_msg = match.group(1).strip()

                        # Pattern 4: "xxx" (any quoted text that looks like an error)
                        if not potential_msg:
                            match = re.search(r'["\']([^"\']{10,80})["\']', text)
                            if match:
                                potential_msg = match.group(1).strip()

                        if potential_msg and len(potential_msg) > 3:
                            current_scenario.expected_error_message = potential_msg

    if current_scenario and current_scenario.steps:
        analyze_scenario(current_scenario, empty_field_pattern, error_message_pattern)
        scenarios.append(current_scenario)

    return [scenario_to_dict(s) for s in scenarios]


def analyze_scenario(scenario: ScenarioAnalysis, empty_field_pattern, error_message_pattern):
    if not scenario.steps:
        scenario.is_valid = False
        scenario.errors.append("Aucun étape trouvée dans ce scénario")
        return

    keywords = [step.keyword.lower() for step in scenario.steps]

    has_given = any(k == 'given' for k in keywords)
    has_when = any(k == 'when' for k in keywords)
    has_then = any(k == 'then' for k in keywords)

    if not has_given:
        scenario.warnings.append("Il manque une étape 'Given' (précondition)")
    if not has_when:
        scenario.warnings.append("Il manque une étape 'When' (action)")
    if not has_then:
        scenario.errors.append("Il manque une étape 'Then' (résultat attendu)")
        scenario.is_valid = False

    prev_keyword = None
    for step in scenario.steps:
        keyword = step.keyword.lower()
        if keyword == 'and' or keyword == 'but':
            if prev_keyword is None:
                scenario.errors.append(f"Ligne {step.line_number}: 'And' ne peut pas être la première étape")
            elif prev_keyword in ['then', 'given', 'when']:
                scenario.warnings.append(f"Ligne {step.line_number}: 'And' devrait suivre un autre 'And'")

        if empty_field_pattern and empty_field_pattern.search(step.text):
            scenario.warnings.append(f"Ligne {step.line_number}: Test de champs vides détecté - vérifier le message d'erreur attendu")

        prev_keyword = keyword

    if has_then and not scenario.expected_error_message:
        for step in scenario.steps:
            if step.keyword.lower() == 'then':
                if 'error' in step.text.lower() or 'erreur' in step.text.lower() or 'message' in step.text.lower():
                    if error_message_pattern:
                        scenario.warnings.append(f"Ligne {step.line_number}: Message d'erreur attendu non trouvé (format attendu: \"message entre guillemets\")")


def scenario_to_dict(scenario: ScenarioAnalysis) -> Dict[str, Any]:
    return {
        "title": scenario.title,
        "scenario_number": scenario.scenario_number,
        "is_valid": scenario.is_valid,
        "steps": [
            {
                "keyword": step.keyword,
                "text": step.text,
                "line_number": step.line_number
            }
            for step in scenario.steps
        ],
        "errors": scenario.errors,
        "warnings": scenario.warnings,
        "expected_error_message": scenario.expected_error_message
    }