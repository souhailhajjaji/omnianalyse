"""
Static Code Analyzer — Extracts testable elements from source code.

Parses HTML, Angular, CSS, and JavaScript/TypeScript source code to identify:
- UI elements (forms, inputs, buttons, links)
- User interactions (click handlers, form submissions, navigation)
- Validations (required fields, patterns, error messages)
- Routes and navigation paths
- API calls and endpoints
- Conditional UI states (loading, error, success)

This produces a structured summary that enriches the AI prompt for
better test scenario generation.
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class UIElement:
    """Represents a detected UI element."""
    element_type: str          # input, button, link, form, select, textarea, etc.
    identifier: str            # id, name, class, or selector
    attributes: Dict[str, str] = field(default_factory=dict)
    context: str = ""          # surrounding context info


@dataclass
class UserInteraction:
    """Represents a detected user interaction."""
    interaction_type: str      # click, submit, input, change, navigate, hover
    target: str                # element description
    handler: str = ""          # handler function name if found
    context: str = ""


@dataclass
class Validation:
    """Represents a detected validation rule."""
    field: str
    rule: str                  # required, minlength, maxlength, pattern, email, etc.
    error_message: str = ""


@dataclass
class APICall:
    """Represents a detected API call."""
    method: str                # GET, POST, PUT, DELETE
    url: str
    context: str = ""


@dataclass
class ConditionalState:
    """Represents a conditional UI state."""
    condition: str             # loading, error, success, authenticated, etc.
    description: str = ""


@dataclass
class CodeAnalysisResult:
    """Full result of static code analysis."""
    ui_elements: List[UIElement] = field(default_factory=list)
    interactions: List[UserInteraction] = field(default_factory=list)
    validations: List[Validation] = field(default_factory=list)
    api_calls: List[APICall] = field(default_factory=list)
    conditional_states: List[ConditionalState] = field(default_factory=list)
    routes: List[Dict[str, str]] = field(default_factory=list)
    detected_features: List[str] = field(default_factory=list)


def analyze_source_code(content: str) -> CodeAnalysisResult:
    """
    Main entry point — analyzes source code and returns structured results.
    Supports HTML, Angular templates, CSS, JavaScript, TypeScript.
    """
    result = CodeAnalysisResult()

    _extract_ui_elements(content, result)
    _extract_interactions(content, result)
    _extract_validations(content, result)
    _extract_api_calls(content, result)
    _extract_conditional_states(content, result)
    _extract_routes(content, result)
    _detect_features(content, result)

    return result


def _extract_ui_elements(content: str, result: CodeAnalysisResult):
    """Extract form elements, buttons, links, etc."""

    # Input fields (HTML + Angular)
    input_patterns = [
        re.compile(r'<input\s+([^>]*?)/?>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<textarea\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<select\s+([^>]*?)>', re.IGNORECASE | re.DOTALL),
    ]

    for pattern in input_patterns:
        for match in pattern.finditer(content):
            attrs_str = match.group(1)
            elem_type = 'input'
            if 'textarea' in match.group(0).lower():
                elem_type = 'textarea'
            elif 'select' in match.group(0).lower():
                elem_type = 'select'

            attrs = _parse_attributes(attrs_str)
            identifier = attrs.get('id', attrs.get('name', attrs.get('formControlName',
                         attrs.get('placeholder', attrs.get('type', 'unknown')))))

            result.ui_elements.append(UIElement(
                element_type=elem_type,
                identifier=identifier,
                attributes=attrs
            ))

    # Buttons
    button_pattern = re.compile(
        r'<button\s+([^>]*?)>(.*?)</button>',
        re.IGNORECASE | re.DOTALL
    )
    for match in button_pattern.finditer(content):
        attrs = _parse_attributes(match.group(1))
        text = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        identifier = attrs.get('id', attrs.get('type', text or 'button'))

        result.ui_elements.append(UIElement(
            element_type='button',
            identifier=identifier,
            attributes=attrs,
            context=text
        ))

    # Links
    link_pattern = re.compile(
        r'<a\s+([^>]*?)>(.*?)</a>',
        re.IGNORECASE | re.DOTALL
    )
    for match in link_pattern.finditer(content):
        attrs = _parse_attributes(match.group(1))
        text = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        href = attrs.get('href', attrs.get('routerLink', attrs.get('routerlink', '#')))

        result.ui_elements.append(UIElement(
            element_type='link',
            identifier=text or href,
            attributes=attrs,
            context=f"navigates to {href}"
        ))

    # Forms
    form_pattern = re.compile(
        r'<form\s+([^>]*?)>',
        re.IGNORECASE | re.DOTALL
    )
    for match in form_pattern.finditer(content):
        attrs = _parse_attributes(match.group(1))
        identifier = attrs.get('id', attrs.get('name', attrs.get('formGroup', 'form')))
        result.ui_elements.append(UIElement(
            element_type='form',
            identifier=identifier,
            attributes=attrs
        ))

    # Images
    img_pattern = re.compile(r'<img\s+([^>]*?)/?>', re.IGNORECASE | re.DOTALL)
    for match in img_pattern.finditer(content):
        attrs = _parse_attributes(match.group(1))
        alt = attrs.get('alt', attrs.get('src', 'image'))
        result.ui_elements.append(UIElement(
            element_type='image',
            identifier=alt,
            attributes=attrs
        ))

    # File inputs specifically
    file_input_pattern = re.compile(r'type=["\']file["\']', re.IGNORECASE)
    if file_input_pattern.search(content):
        accept_match = re.search(r'accept=["\']([^"\']+)["\']', content, re.IGNORECASE)
        accept = accept_match.group(1) if accept_match else '*'
        result.detected_features.append(f"File upload (accepts: {accept})")


def _extract_interactions(content: str, result: CodeAnalysisResult):
    """Extract click handlers, event bindings, form submissions, etc."""

    # Angular event bindings: (click), (submit), (change), (input), (keyup), etc.
    angular_events = re.compile(
        r'\((\w+)\)\s*=\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )
    for match in angular_events.finditer(content):
        event_type = match.group(1)
        handler = match.group(2)
        result.interactions.append(UserInteraction(
            interaction_type=event_type,
            target=handler,
            handler=handler
        ))

    # onclick, onsubmit, etc (vanilla JS)
    vanilla_events = re.compile(
        r'on(\w+)\s*=\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )
    for match in vanilla_events.finditer(content):
        event_type = match.group(1).lower()
        handler = match.group(2)
        result.interactions.append(UserInteraction(
            interaction_type=event_type,
            target=handler,
            handler=handler
        ))

    # addEventListener
    addEventListener_pattern = re.compile(
        r"\.addEventListener\s*\(\s*['\"](\w+)['\"]",
        re.IGNORECASE
    )
    for match in addEventListener_pattern.finditer(content):
        result.interactions.append(UserInteraction(
            interaction_type=match.group(1),
            target='DOM element',
            handler='addEventListener callback'
        ))

    # Router navigation
    router_nav = re.compile(
        r'(?:router\.navigate|routerLink|router-link)\s*[\(=]\s*["\'\[]([^"\')\]]+)',
        re.IGNORECASE
    )
    for match in router_nav.finditer(content):
        result.interactions.append(UserInteraction(
            interaction_type='navigate',
            target=match.group(1)
        ))


def _extract_validations(content: str, result: CodeAnalysisResult):
    """Extract form validations (HTML5, Angular, custom)."""

    # HTML5 required attribute
    required_pattern = re.compile(
        r'<(?:input|textarea|select)\s+[^>]*?(?:required|required\s*=\s*["\'](?:true|required)["\'])[^>]*?>',
        re.IGNORECASE | re.DOTALL
    )
    for match in required_pattern.finditer(content):
        attrs = _parse_attributes(match.group(0))
        field_name = attrs.get('name', attrs.get('id', attrs.get('placeholder', 'field')))
        result.validations.append(Validation(
            field=field_name,
            rule='required'
        ))

    # minlength / maxlength
    for attr_name in ['minlength', 'maxlength', 'min', 'max']:
        pattern = re.compile(
            rf'{attr_name}\s*=\s*["\'](\d+)["\']',
            re.IGNORECASE
        )
        for match in pattern.finditer(content):
            result.validations.append(Validation(
                field='input',
                rule=f'{attr_name}={match.group(1)}'
            ))

    # pattern attribute
    pattern_attr = re.compile(
        r'pattern\s*=\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )
    for match in pattern_attr.finditer(content):
        result.validations.append(Validation(
            field='input',
            rule=f'pattern={match.group(1)}'
        ))

    # type=email, type=number, type=url, type=password
    type_validations = re.compile(
        r'type\s*=\s*["\'](\w+)["\']',
        re.IGNORECASE
    )
    for match in type_validations.finditer(content):
        input_type = match.group(1).lower()
        if input_type in ['email', 'number', 'url', 'tel', 'password']:
            result.validations.append(Validation(
                field='input',
                rule=f'type={input_type}'
            ))

    # Angular Validators
    angular_validators = re.compile(
        r'Validators\.(\w+)(?:\(([^)]*)\))?',
        re.IGNORECASE
    )
    for match in angular_validators.finditer(content):
        validator = match.group(1)
        param = match.group(2) or ''
        rule = f'{validator}({param})' if param else validator
        result.validations.append(Validation(
            field='form control',
            rule=rule
        ))

    # accept attribute for file inputs
    accept_pattern = re.compile(
        r'accept\s*=\s*["\']([^"\']+)["\']',
        re.IGNORECASE
    )
    for match in accept_pattern.finditer(content):
        result.validations.append(Validation(
            field='file input',
            rule=f'accept={match.group(1)}'
        ))


def _extract_api_calls(content: str, result: CodeAnalysisResult):
    """Extract fetch, HttpClient, axios, XMLHttpRequest calls."""

    # fetch() calls
    fetch_pattern = re.compile(
        r"fetch\s*\(\s*['\"`]([^'\"`]+)['\"`]\s*(?:,\s*\{[^}]*?method\s*:\s*['\"](\w+)['\"])?",
        re.IGNORECASE | re.DOTALL
    )
    for match in fetch_pattern.finditer(content):
        url = match.group(1)
        method = (match.group(2) or 'GET').upper()
        result.api_calls.append(APICall(method=method, url=url))

    # Angular HttpClient
    http_methods = re.compile(
        r'(?:this\.http|httpClient)\s*\.\s*(get|post|put|delete|patch)\s*(?:<[^>]*>)?\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        re.IGNORECASE
    )
    for match in http_methods.finditer(content):
        result.api_calls.append(APICall(
            method=match.group(1).upper(),
            url=match.group(2)
        ))

    # axios calls
    axios_pattern = re.compile(
        r'axios\s*\.\s*(get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        re.IGNORECASE
    )
    for match in axios_pattern.finditer(content):
        result.api_calls.append(APICall(
            method=match.group(1).upper(),
            url=match.group(2)
        ))


def _extract_conditional_states(content: str, result: CodeAnalysisResult):
    """Extract conditional rendering (loading, error, success states)."""

    # Angular @if blocks and *ngIf
    angular_if_patterns = [
        re.compile(r'@if\s*\(([^)]+)\)', re.IGNORECASE),
        re.compile(r'\*ngIf\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE),
    ]

    for pattern in angular_if_patterns:
        for match in pattern.finditer(content):
            condition = match.group(1).strip()

            # Categorize the condition
            condition_lower = condition.lower()
            if any(kw in condition_lower for kw in ['loading', 'isloading', 'spinner']):
                state_type = 'loading'
            elif any(kw in condition_lower for kw in ['error', 'err', 'failed']):
                state_type = 'error'
            elif any(kw in condition_lower for kw in ['success', 'result', 'data']):
                state_type = 'success/results'
            elif any(kw in condition_lower for kw in ['auth', 'logged', 'token', 'user']):
                state_type = 'authentication'
            else:
                state_type = 'conditional'

            result.conditional_states.append(ConditionalState(
                condition=state_type,
                description=condition
            ))

    # Ternary conditions in templates
    ternary_pattern = re.compile(r'\{\{\s*([^}]+?)\s*\?\s*([^:}]+?)\s*:\s*([^}]+?)\s*\}\}')
    for match in ternary_pattern.finditer(content):
        result.conditional_states.append(ConditionalState(
            condition='ternary',
            description=f"{match.group(1).strip()} ? {match.group(2).strip()} : {match.group(3).strip()}"
        ))


def _extract_routes(content: str, result: CodeAnalysisResult):
    """Extract route definitions."""

    # Angular routes
    route_pattern = re.compile(
        r"\{\s*path\s*:\s*['\"]([^'\"]*)['\"]",
        re.IGNORECASE
    )
    for match in route_pattern.finditer(content):
        path = match.group(1)
        result.routes.append({'path': path or '/'})

    # redirectTo
    redirect_pattern = re.compile(
        r"redirectTo\s*:\s*['\"]([^'\"]+)['\"]",
        re.IGNORECASE
    )
    for match in redirect_pattern.finditer(content):
        result.routes.append({'redirect': match.group(1)})


def _detect_features(content: str, result: CodeAnalysisResult):
    """Detect high-level features based on code patterns."""

    feature_indicators = {
        'Authentication / Login': [r'login', r'password', r'auth', r'token', r'jwt', r'credentials'],
        'File Upload': [r'type=["\']file["\']', r'upload', r'UploadFile', r'multipart'],
        'Form Validation': [r'required', r'Validators', r'pattern=', r'minlength'],
        'Data Table / List': [r'@for\s', r'\*ngFor', r'\.map\(', r'forEach'],
        'Error Handling': [r'catch\s*\(', r'\.error', r'error\(\)', r'HTTPException'],
        'Loading State': [r'loading', r'spinner', r'isLoading'],
        'Navigation / Routing': [r'router', r'Routes', r'navigate', r'routerLink'],
        'API Integration': [r'fetch\(', r'HttpClient', r'axios', r'http\.'],
        'Responsive Design': [r'@media', r'max-width', r'min-width'],
        'Drag and Drop': [r'drag', r'drop', r'dragover', r'draggable'],
        'Modal / Dialog': [r'modal', r'dialog', r'popup', r'overlay'],
        'Search / Filter': [r'search', r'filter', r'query'],
        'Pagination': [r'pagination', r'page\s*=', r'pageSize', r'offset'],
        'Download / Export': [r'download', r'export', r'Blob', r'createObjectURL'],
    }

    for feature, patterns in feature_indicators.items():
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                if feature not in result.detected_features:
                    result.detected_features.append(feature)
                break


def _parse_attributes(attrs_str: str) -> Dict[str, str]:
    """Parse HTML attributes from a string."""
    attrs = {}
    # Match key="value", key='value', [key]="value", (event)="handler", key (boolean)
    attr_pattern = re.compile(
        r'[\[\(]?(\w[\w\-.]*)[\]\)]?\s*=\s*["\']([^"\']*)["\']'
    )
    for match in attr_pattern.finditer(attrs_str):
        attrs[match.group(1)] = match.group(2)

    # Boolean attributes (e.g. "hidden", "required", "disabled")
    bool_pattern = re.compile(r'\b(hidden|required|disabled|readonly|autofocus)\b', re.IGNORECASE)
    for match in bool_pattern.finditer(attrs_str):
        attrs[match.group(1).lower()] = 'true'

    return attrs


def analysis_to_prompt_context(analysis: CodeAnalysisResult) -> str:
    """
    Convert the analysis result into a structured text summary
    to enrich the AI prompt.
    """
    sections = []

    if analysis.detected_features:
        sections.append("## Detected Features")
        for feat in analysis.detected_features:
            sections.append(f"- {feat}")

    if analysis.ui_elements:
        sections.append("\n## UI Elements Found")
        for elem in analysis.ui_elements:
            attrs_info = ""
            if elem.attributes:
                key_attrs = {k: v for k, v in elem.attributes.items()
                             if k in ('type', 'placeholder', 'id', 'name', 'class', 'accept', 'required')}
                if key_attrs:
                    attrs_info = f" [{', '.join(f'{k}={v}' for k, v in key_attrs.items())}]"
            ctx = f" — {elem.context}" if elem.context else ""
            sections.append(f"- **{elem.element_type}**: `{elem.identifier}`{attrs_info}{ctx}")

    if analysis.interactions:
        sections.append("\n## User Interactions")
        for inter in analysis.interactions:
            ctx = f" — {inter.context}" if inter.context else ""
            sections.append(f"- **{inter.interaction_type}** → `{inter.target}`{ctx}")

    if analysis.validations:
        sections.append("\n## Validation Rules")
        for val in analysis.validations:
            err = f" (error: {val.error_message})" if val.error_message else ""
            sections.append(f"- **{val.field}**: `{val.rule}`{err}")

    if analysis.api_calls:
        sections.append("\n## API Calls")
        for api in analysis.api_calls:
            sections.append(f"- `{api.method} {api.url}`")

    if analysis.conditional_states:
        sections.append("\n## Conditional UI States")
        for state in analysis.conditional_states:
            sections.append(f"- **{state.condition}**: `{state.description}`")

    if analysis.routes:
        sections.append("\n## Routes")
        for route in analysis.routes:
            if 'path' in route:
                sections.append(f"- Path: `{route['path']}`")
            if 'redirect' in route:
                sections.append(f"- Redirect → `{route['redirect']}`")

    return "\n".join(sections)
