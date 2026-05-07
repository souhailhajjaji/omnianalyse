import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface Step {
  keyword: string;
  text: string;
  line_number: number;
}

interface Scenario {
  title: string;
  scenario_number: number;
  is_valid: boolean;
  steps: Step[];
  errors: string[];
  warnings: string[];
  expected_error_message: string;
}

interface UserStory {
  story_number: number;
  title?: string;
  role?: string;
  feature?: string;
  benefit?: string;
  status?: string;
  priority?: string;
  scope?: string[];
  estimate?: string;
  depends_on?: string[];
  acceptance_criteria?: string[];
  technical_notes?: string;
  definition_of_done?: string;
  source_feature?: string;
}

interface AnalysisMeta {
  features: string[];
  ui_elements_count: number;
  interactions_count: number;
  validations_count: number;
  api_calls_count: number;
}

interface AnalysisResult {
  scenarios: Scenario[];
  status: string;
  total: number;
  analysis?: AnalysisMeta;
  message?: string;
  ai_raw?: string;
  files_count?: number;
}

interface UserStoryResult {
  user_stories: ParsedUserStory[];
  status: string;
  total: number;
  analysis?: AnalysisMeta;
  message?: string;
  ai_raw?: string;
  files_count?: number;
}

interface ParsedUserStory {
  id: string;
  title: string;
  status: string;
  priority: string;
  scope: string[];
  estimate: string;
  depends_on: string[];
  role: string;
  feature: string;
  benefit: string;
  acceptance_criteria: string[];
  story_number?: number;
  technical_notes?: string;
  definition_of_done?: string;
}

function translateKeyword(keyword: string): string {
  const map: Record<string, string> = {
    'Given': 'Étant donné que',
    'When': 'Quand',
    'Then': 'Alors',
    'And': 'Et',
    'But': 'Mais'
  };
  return map[keyword] || keyword;
}

@Component({
  selector: 'app-dashboard',
  imports: [FormsModule],
  template: `
    <div class="page">
      <div class="gradient-bg"></div>
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>
      
      <div class="brand-logo">
        <img src="https://medtech.ma/wp-content/uploads/2025/01/Omnishore-1.png" alt="Omnishore" />
      </div>
      
      <div class="card">
        <div class="header">
          <div class="logo-wrapper">
            <div class="logo">
              <span class="logo-icon">◇</span>
              <span class="logo-text">OmniAnalyse</span>
            </div>
          </div>
          <p class="subtitle">Générateur de User Stories</p>
        </div>

<div class="content">
          <div class="path-section">
              <div class="requirements-wrapper">
                <div class="requirements-header">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:20px;height:20px">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                    <polyline points="10 9 9 9 8 9"/>
                  </svg>
                  <span class="requirements-label">Télécharger les fichiers maquette</span>
                </div>
                <div class="file-upload-section">
                  <label class="file-upload-btn">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                    <span>Télécharger maquette</span>
                    <input type="file" (change)="onMaquetteSelected($event)" accept=".md,.txt,.pdf,.doc,.docx" multiple style="display:none">
                  </label>
                  @if (maquetteFiles().length > 0) {
                    <div class="maquette-files-list">
                      @for (file of maquetteFiles(); track file.name) {
                        <div class="maquette-file-item">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                          </svg>
                          <span>{{ file.name }}</span>
                          <button class="remove-file-btn" (click)="removeMaquetteFile(file.name)">×</button>
                        </div>
                      }
                    </div>
                  }
                </div>
              </div>
              @if (maquetteFiles().length > 0) {
                <div class="buttons-row">
                  <button class="run-btn run-btn-us" [disabled]="loading()" (click)="generateFromMaquette()">
                    <svg viewBox="0 0 24 24" fill="currentColor" style="width:16px;height:16px">
                      <polygon points="5 3 19 12 5 21 5 3"/>
                    </svg>
                    Générer User Stories
                  </button>
                </div>
              }
            </div>
          
          @if (error()) {
            <div class="error">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {{ error() }}
            </div>
          }
          
          @if (loading()) {
            <div class="loading">
              <div class="spinner"></div>
              <span>Génération des tests en cours...</span>
            </div>
          }
          
          @if (results()) {
            <div class="results">
              <div class="results-header">
                <h3>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 11l3 3L22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                  Résultats de l'analyse
                  <span class="badge">{{ results()!.total }} scénario(s)</span>
                  @if (results()!.status === 'partial') {
                    <span class="badge badge-warning">⚡ Statique</span>
                  }
                </h3>
                <button class="download-btn" (click)="downloadAsMarkdown()">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  Télécharger .md
</button>
              </div>

              @if (results()!.message) {
                <div class="info-message">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;flex-shrink:0">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="16" x2="12" y2="12"/>
                    <line x1="12" y1="8" x2="12.01" y2="8"/>
                  </svg>
                  {{ results()!.message }}
                </div>
              }

              @for (scenario of results()!.scenarios; track scenario.scenario_number; let idx = $index) {
                <div class="scenario-card" [class.invalid]="!scenario.is_valid">
                  <div class="scenario-header" (click)="toggleScenario(scenario.scenario_number)">
                    <div class="scenario-info">
                      <span 
                        class="status-badge"
                        [class.valid]="scenario.is_valid"
                        [class.invalid]="!scenario.is_valid"
                      >
                        {{ scenario.is_valid ? '✓ Valide' : '✗ Invalide' }}
                      </span>
                      <span class="scenario-number">#{{ scenario.scenario_number }}</span>
                      <span class="scenario-title">{{ scenario.title }}</span>
                    </div>
                    <svg class="chevron" [class.expanded]="expandedScenario() === scenario.scenario_number" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M19 9l-7 7-7-7"/>
                    </svg>
                  </div>
                  
                  @if (expandedScenario() === scenario.scenario_number) {
                    <div class="scenario-body">
                      <div class="steps">
                        @for (step of scenario.steps; track $index) {
                          <div class="step" [class]="step.keyword.toLowerCase()">
                            <span class="step-keyword">{{ translateKeyword(step.keyword) }}</span>
                            <span class="step-text">{{ step.text }}</span>
                          </div>
                        }
                      </div>
                      
                      @if (scenario.expected_error_message) {
                        <div class="expected-error">
                          <span class="error-label">Erreur attendue:</span>
                          <span class="error-message">"{{ scenario.expected_error_message }}"</span>
                        </div>
                      }
                      
                      @if (scenario.errors.length > 0) {
                        <div class="errors">
                          @for (err of scenario.errors; track err) {
                            <div class="error-item">
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <line x1="15" y1="9" x2="9" y2="15"/>
                                <line x1="9" y1="9" x2="15" y2="15"/>
                              </svg>
                              {{ err }}
                            </div>
                          }
                        </div>
                      }
                      
                      @if (scenario.warnings.length > 0) {
                        <div class="warnings">
                          @for (warn of scenario.warnings; track warn) {
                            <div class="warning-item">
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.342-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                              </svg>
                              {{ warn }}
                            </div>
                          }
                        </div>
                      }
                    </div>
                  }
                </div>
              }
            </div>
          }
        </div>

        @if (userStoryResults()) {
          <div class="results">
            <div class="results-header">
              <h3>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 11l3 3L22 4"/>
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                </svg>
                User Stories
                <span class="badge">{{ userStoryResults()!.total }} story(ies)</span>
              </h3>
              <div class="display-mode-toggle">
                <button 
                  class="mode-toggle-btn" 
                  [class.active]="displayMode() === 'cards'"
                  (click)="setDisplayMode('cards')"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px">
                    <rect x="3" y="3" width="7" height="7"/>
                    <rect x="14" y="3" width="7" height="7"/>
                    <rect x="3" y="14" width="7" height="7"/>
                    <rect x="14" y="14" width="7" height="7"/>
                  </svg>
                  Cartes
                </button>
                <button 
                  class="mode-toggle-btn" 
                  [class.active]="displayMode() === 'markdown'"
                  (click)="setDisplayMode('markdown')"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                  Markdown
                </button>
              </div>
            </div>

            @if (userStoryResults()!.message) {
              <div class="info-message">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;flex-shrink:0">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="16" x2="12" y2="12"/>
                  <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
                {{ userStoryResults()!.message }}
              </div>
            }

            @if (displayMode() === 'cards') {
              <div class="cards-view">
                @for (story of userStoryResults()!.user_stories; track $index) {
                  <div class="user-story-card">
                    <div class="user-story-number">{{ story.id }}</div>
                    <div class="user-story-content">
                      <div class="user-story-header">
                        <span class="us-status" [class]="story.status || 'todo'">{{ story.status || 'todo' }}</span>
                        <span class="us-priority">{{ story.priority || 'medium' }}</span>
                        <span class="us-estimate">{{ story.estimate || 'S' }}</span>
                      </div>
                      <div class="user-story-fields">
                        <div class="user-story-field">
                          <span class="us-label">En tant que</span>
                          <span class="us-value">{{ story.role || '[Rôle à définir]' }}</span>
                        </div>
                        <div class="user-story-field">
                          <span class="us-label">Je veux</span>
                          <span class="us-value">{{ story.feature || '[Fonctionnalité à définir]' }}</span>
                        </div>
                        <div class="user-story-field">
                          <span class="us-label">Afin de</span>
                          <span class="us-value">{{ story.benefit || '[Bénéfice à définir]' }}</span>
                        </div>
                      </div>
                      @if (story.acceptance_criteria?.length) {
                        <div class="user-story-acceptance">
                          <span class="us-label">Critères:</span>
                          <ul>
                            @for (critere of story.acceptance_criteria; track critere) {
                              <li>{{ critere }}</li>
                            }
                          </ul>
                        </div>
                      }
                    </div>
                  </div>
                }
              </div>
            }

            @if (displayMode() === 'markdown') {
              <div class="markdown-view">
                <pre class="markdown-content">{{ userStoryResults()!.ai_raw }}</pre>
                <button class="copy-btn" (click)="copyMarkdown()">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                  Copier
                </button>
              </div>
            }

            <div class="download-actions">
              <button class="download-btn" (click)="downloadUserStoriesAsMarkdown()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Télécharger .md
              </button>
            </div>
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :host {
      --bg-deep: #050510;
      --bg-card: rgba(15, 15, 30, 0.7);
      --primary: #7c3aed;
      --primary-light: #a78bfa;
      --primary-glow: rgba(124, 58, 237, 0.5);
      --accent: #06b6d4;
      --accent-glow: rgba(6, 182, 212, 0.3);
      --text: #f1f5f9;
      --text-dim: #94a3b8;
      --text-muted: #64748b;
      --border: rgba(148, 163, 184, 0.1);
      --border-light: rgba(148, 163, 184, 0.15);
      --glass: rgba(255, 255, 255, 0.025);
      --glass-border: rgba(255, 255, 255, 0.06);
      --error: #f43f5e;
      --error-bg: rgba(244, 63, 94, 0.1);
      --success: #22c55e;
      --warning: #f59e0b;
      --warning-bg: rgba(245, 158, 11, 0.1);
    }

    .page {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg-deep);
      position: relative;
      overflow: hidden;
      padding: 20px;
    }

    .brand-logo {
      position: fixed;
      top: 24px;
      right: 32px;
      z-index: 100;
      animation: fadeInDown 0.6s ease forwards;
    }

    .brand-logo img {
      height: 50px;
      width: auto;
      object-fit: contain;
      filter: brightness(0) invert(1);
      opacity: 0.85;
      transition: all 0.3s ease;
    }

    .brand-logo img:hover {
      opacity: 1;
      transform: scale(1.05);
    }

    @keyframes fadeInDown {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .gradient-bg {
      position: fixed;
      inset: 0;
      background: 
        radial-gradient(ellipse 100% 80% at 50% -30%, rgba(124, 58, 237, 0.2) 0%, transparent 50%),
        radial-gradient(ellipse 80% 60% at 80% 100%, rgba(6, 182, 212, 0.15) 0%, transparent 40%),
        radial-gradient(ellipse 60% 50% at 10% 90%, rgba(124, 58, 237, 0.1) 0%, transparent 40%);
      animation: gradientShift 15s ease infinite;
    }

    @keyframes gradientShift {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.7; }
    }

    .orb {
      position: fixed;
      border-radius: 50%;
      filter: blur(100px);
      animation: orbFloat 25s ease-in-out infinite;
    }

    .orb-1 {
      width: 500px;
      height: 500px;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      top: -150px;
      left: -150px;
      opacity: 0.4;
    }

    .orb-2 {
      width: 400px;
      height: 400px;
      background: linear-gradient(135deg, var(--accent), var(--primary));
      bottom: -100px;
      right: -100px;
      opacity: 0.35;
      animation-delay: -10s;
    }

    .orb-3 {
      width: 300px;
      height: 300px;
      background: linear-gradient(135deg, var(--primary-light), var(--accent));
      top: 40%;
      left: 60%;
      opacity: 0.25;
      animation-delay: -20s;
    }

    @keyframes orbFloat {
      0%, 100% { transform: translate(0, 0) scale(1) rotate(0deg); }
      25% { transform: translate(40px, -40px) scale(1.1) rotate(5deg); }
      50% { transform: translate(-30px, 30px) scale(0.95) rotate(-3deg); }
      75% { transform: translate(20px, 20px) scale(1.05) rotate(2deg); }
    }

    .glow {
      position: fixed;
      border-radius: 50%;
      animation: glowPulse 8s ease-in-out infinite;
    }

    .glow-1 {
      width: 600px;
      height: 600px;
      background: radial-gradient(circle, rgba(124, 58, 237, 0.15) 0%, transparent 70%);
      top: 20%;
      left: 50%;
      transform: translateX(-50%);
    }

    .glow-2 {
      width: 400px;
      height: 400px;
      background: radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 70%);
      bottom: 10%;
      right: 20%;
      animation-delay: -4s;
    }

    @keyframes glowPulse {
      0%, 100% { opacity: 0.5; transform: translateX(-50%) scale(1); }
      50% { opacity: 0.8; transform: translateX(-50%) scale(1.1); }
    }

    .card {
      position: relative;
      width: 100%;
      max-width: 720px;
      background: var(--glass);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--glass-border);
      border-radius: 28px;
      padding: 48px;
      box-shadow: 
        0 0 0 1px rgba(255, 255, 255, 0.03),
        0 20px 50px rgba(0, 0, 0, 0.4),
        0 0 100px rgba(124, 58, 237, 0.1);
      animation: cardEnter 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    @keyframes cardEnter {
      to { opacity: 1; transform: translateY(0); }
    }

    .header {
      text-align: center;
      margin-bottom: 40px;
    }

    .logo-wrapper {
      display: inline-block;
      animation: logoFloat 6s ease-in-out infinite;
    }

    @keyframes logoFloat {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-5px); }
    }

    .logo {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 14px;
    }

    .logo-icon {
      font-size: 2.2rem;
      color: var(--primary-light);
      animation: logoPulse 3s ease-in-out infinite;
      text-shadow: 0 0 20px var(--primary-glow);
    }

    @keyframes logoPulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.8; transform: scale(1.1); }
    }

    .logo-text {
      font-family: 'Outfit', sans-serif;
      font-size: 1.8rem;
      font-weight: 700;
      color: var(--text);
      letter-spacing: -0.5px;
      background: linear-gradient(135deg, var(--text) 0%, var(--text-dim) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .subtitle {
      font-family: 'Outfit', sans-serif;
      font-size: 0.8rem;
      font-weight: 500;
      color: var(--text-muted);
      letter-spacing: 3px;
      text-transform: uppercase;
      margin: 8px 0 0 0;
    }

    .content {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .error {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 14px 18px;
      background: var(--error-bg);
      border: 1px solid rgba(244, 63, 94, 0.2);
      border-radius: 12px;
      color: var(--error);
      font-family: 'Outfit', sans-serif;
      font-size: 0.9rem;
      font-weight: 500;
      animation: errorShake 0.5s ease;
    }

    .error svg {
      width: 18px;
      height: 18px;
      flex-shrink: 0;
    }

    @keyframes errorShake {
      0%, 100% { transform: translateX(0); }
      20%, 60% { transform: translateX(-5px); }
      40%, 80% { transform: translateX(5px); }
    }

    .loading {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      padding: 24px;
      color: var(--text-dim);
      font-family: 'Outfit', sans-serif;
    }

    .spinner {
      width: 24px;
      height: 24px;
      border: 2px solid var(--border);
      border-top-color: var(--primary);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .results {
      display: flex;
      flex-direction: column;
      gap: 16px;
      animation: fadeIn 0.5s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .results-header h3 {
      display: flex;
      align-items: center;
      gap: 10px;
      font-family: 'Outfit', sans-serif;
      font-size: 1rem;
      font-weight: 600;
      color: var(--text);
      margin: 0;
    }

    .results-header h3 svg {
      width: 18px;
      height: 18px;
      color: var(--accent);
    }

    .badge {
      font-size: 0.75rem;
      font-weight: 500;
      padding: 4px 10px;
      background: rgba(124, 58, 237, 0.2);
      color: var(--primary-light);
      border-radius: 20px;
    }

    .download-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: var(--accent);
      color: white;
      border: none;
      border-radius: 8px;
      font-family: 'Outfit', sans-serif;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .download-btn:hover {
      background: var(--primary-light);
      transform: translateY(-1px);
    }

    .download-btn svg {
      width: 16px;
      height: 16px;
    }

    .scenario-card {
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      transition: all 0.3s ease;
    }

    .scenario-card:hover {
      border-color: var(--border-light);
    }

    .scenario-card.invalid {
      border-color: rgba(244, 63, 94, 0.3);
    }

    .scenario-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 20px;
      cursor: pointer;
      transition: background 0.2s ease;
    }

    .scenario-header:hover {
      background: rgba(255, 255, 255, 0.02);
    }

    .scenario-info {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .status-badge {
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 20px;
    }

    .status-badge.valid {
      background: rgba(34, 197, 94, 0.15);
      color: var(--success);
    }

    .status-badge.invalid {
      background: rgba(244, 63, 94, 0.15);
      color: var(--error);
    }

    .scenario-number {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .scenario-title {
      font-family: 'Outfit', sans-serif;
      font-size: 0.95rem;
      font-weight: 500;
      color: var(--text);
    }

    .chevron {
      width: 20px;
      height: 20px;
      color: var(--text-muted);
      transition: transform 0.3s ease;
    }

    .chevron.expanded {
      transform: rotate(180deg);
    }

    .scenario-body {
      padding: 0 20px 20px 20px;
      border-top: 1px solid var(--border);
      animation: slideDown 0.3s ease;
    }

    @keyframes slideDown {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .steps {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-top: 16px;
    }

    .step {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 12px 16px;
      background: rgba(0, 0, 0, 0.3);
      border-radius: 10px;
      border-left: 3px solid;
    }

    .step.given {
      border-left-color: #3b82f6;
    }

    .step.when {
      border-left-color: #f59e0b;
    }

    .step.then {
      border-left-color: #22c55e;
    }

    .step.and {
      border-left-color: #a855f7;
    }

    .step-keyword {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;
      min-width: 50px;
      text-align: center;
    }

    .step.given .step-keyword {
      background: rgba(59, 130, 246, 0.15);
      color: #3b82f6;
    }

    .step.when .step-keyword {
      background: rgba(245, 158, 11, 0.15);
      color: #f59e0b;
    }

    .step.then .step-keyword {
      background: rgba(34, 197, 94, 0.15);
      color: #22c55e;
    }

    .step.and .step-keyword {
      background: rgba(168, 85, 247, 0.15);
      color: #a855f7;
    }

    .step-text {
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      color: var(--text-dim);
      line-height: 1.5;
    }

    .expected-error {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 16px;
      padding: 12px 16px;
      background: rgba(245, 158, 11, 0.1);
      border: 1px solid rgba(245, 158, 11, 0.2);
      border-radius: 10px;
    }

    .error-label {
      font-family: 'Outfit', sans-serif;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--warning);
    }

    .error-message {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      color: var(--warning);
    }

    .errors, .warnings {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-top: 16px;
    }

    .error-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      background: var(--error-bg);
      border-radius: 8px;
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      color: var(--error);
    }

    .error-item svg {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }

    .warning-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 14px;
      background: var(--warning-bg);
      border-radius: 8px;
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      color: var(--warning);
    }

    .warning-item svg {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }

    @media (max-width: 640px) {
      .card {
        padding: 32px 24px;
      }

      .logo-text {
        font-size: 1.5rem;
      }

      .upload-zone {
        padding: 36px 24px;
      }

      .orb-1 { width: 300px; height: 300px; }
      .orb-2 { width: 250px; height: 250px; }
      .orb-3 { display: none; }
    }

    .mode-toggle {
      display: flex;
      gap: 8px;
      padding: 4px;
      background: rgba(0, 0, 0, 0.3);
      border-radius: 14px;
      border: 1px solid var(--border);
    }

    .mode-btn {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 12px 16px;
      background: transparent;
      border: none;
      border-radius: 10px;
      color: var(--text-muted);
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .mode-btn:hover {
      color: var(--text-dim);
      background: rgba(255, 255, 255, 0.03);
    }

    .mode-btn.active {
      background: linear-gradient(135deg, rgba(124, 58, 237, 0.25), rgba(6, 182, 212, 0.15));
      color: var(--text);
      box-shadow: 0 0 20px rgba(124, 58, 237, 0.15);
      border: 1px solid rgba(124, 58, 237, 0.3);
    }

    .user-story-card {
      display: flex;
      gap: 16px;
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px 20px;
      margin-bottom: 12px;
      transition: all 0.3s ease;
    }

    .user-story-card:hover {
      border-color: var(--border-light);
    }

    .user-story-number {
      background: linear-gradient(135deg, #10b981, #059669);
      color: white;
      font-weight: 600;
      font-size: 0.85rem;
      padding: 8px 12px;
      border-radius: 8px;
      height: fit-content;
    }

    .user-story-header {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
    }

    .us-status {
      font-size: 0.7rem;
      padding: 2px 8px;
      border-radius: 4px;
      text-transform: uppercase;
    }

    .us-status.todo {
      background: rgba(245, 158, 11, 0.2);
      color: #f59e0b;
    }

    .us-status.in-progress {
      background: rgba(59, 130, 246, 0.2);
      color: #3b82f6;
    }

    .us-status.done {
      background: rgba(34, 197, 94, 0.2);
      color: #22c55e;
    }

    .us-priority, .us-estimate {
      font-size: 0.7rem;
      padding: 2px 8px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-dim);
    }

    .user-story-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .user-story-fields {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .user-story-field {
      display: flex;
      align-items: flex-start;
      gap: 8px;
    }

    .us-label {
      font-weight: 600;
      color: var(--accent);
      min-width: 80px;
      font-size: 0.9rem;
    }

    .us-value {
      color: var(--text);
    }

    .user-story-acceptance {
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid var(--border);
    }

    .user-story-acceptance ul {
      margin: 4px 0 0 0;
      padding-left: 20px;
    }

    .user-story-acceptance li {
      color: var(--text-dim);
      font-size: 0.85rem;
      margin-bottom: 2px;
    }

    .user-story-raw {
      font-style: italic;
      color: var(--text-dim);
      margin-top: 4px;
    }

    .path-section {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .requirements-wrapper {
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 16px;
      background: rgba(0, 0, 0, 0.3);
      border: 2px dashed var(--border);
      border-radius: 16px;
      transition: all 0.3s ease;
    }

    .requirements-wrapper:focus-within {
      border-color: var(--primary);
      background: rgba(124, 58, 237, 0.05);
    }

    .requirements-header {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .requirements-header svg {
      color: var(--text-muted);
      flex-shrink: 0;
    }

    .requirements-label {
      font-family: 'Outfit', sans-serif;
      font-size: 0.9rem;
      font-weight: 500;
      color: var(--text-dim);
    }

    .requirements-input {
      width: 100%;
      min-height: 180px;
      padding: 14px;
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--border);
      border-radius: 12px;
      color: var(--text);
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      line-height: 1.6;
      resize: vertical;
      outline: none;
      transition: border-color 0.2s ease;
    }

    .requirements-input:focus {
      border-color: var(--primary);
    }

    .requirements-input::placeholder {
      color: var(--text-muted);
      opacity: 0.7;
    }

    .info-message {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 14px 18px;
      background: rgba(6, 182, 212, 0.08);
      border: 1px solid rgba(6, 182, 212, 0.2);
      border-radius: 12px;
      color: var(--accent);
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      font-weight: 400;
      line-height: 1.5;
    }

    .badge-warning {
      background: rgba(245, 158, 11, 0.2) !important;
      color: var(--warning) !important;
    }

    .download-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      background: rgba(124, 58, 237, 0.15);
      border: 1px solid rgba(124, 58, 237, 0.3);
      border-radius: 10px;
      color: var(--primary-light);
      font-family: 'Outfit', sans-serif;
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      white-space: nowrap;
    }

    .download-btn:hover {
      background: rgba(124, 58, 237, 0.25);
      transform: translateY(-1px);
    }

    .download-btn svg {
      width: 16px;
      height: 16px;
    }

    .display-mode-toggle {
      display: flex;
      gap: 4px;
      padding: 4px;
      background: rgba(0, 0, 0, 0.3);
      border-radius: 10px;
      border: 1px solid var(--border);
    }

    .mode-toggle-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      background: transparent;
      border: none;
      border-radius: 8px;
      color: var(--text-muted);
      font-family: 'Outfit', sans-serif;
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .mode-toggle-btn:hover {
      color: var(--text-dim);
    }

    .mode-toggle-btn.active {
      background: linear-gradient(135deg, rgba(124, 58, 237, 0.25), rgba(6, 182, 212, 0.15));
      color: var(--text);
      box-shadow: 0 0 15px rgba(124, 58, 237, 0.15);
    }

    .cards-view {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-top: 16px;
    }

    .markdown-view {
      position: relative;
      margin-top: 16px;
    }

    .markdown-content {
      padding: 20px;
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--border);
      border-radius: 12px;
      color: var(--text-dim);
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
      max-height: 500px;
      overflow-y: auto;
    }

    .copy-btn {
      position: absolute;
      top: 8px;
      right: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      background: rgba(124, 58, 237, 0.2);
      border: 1px solid rgba(124, 58, 237, 0.3);
      border-radius: 8px;
      color: var(--primary-light);
      font-family: 'Outfit', sans-serif;
      font-size: 0.8rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .copy-btn:hover {
      background: rgba(124, 58, 237, 0.3);
    }

    .download-actions {
      display: flex;
      gap: 12px;
      margin-top: 16px;
    }

    .file-upload-section {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 16px;
    }

    .file-upload-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 16px;
      background: rgba(124, 58, 237, 0.15);
      border: 1px dashed rgba(124, 58, 237, 0.4);
      border-radius: 10px;
      color: var(--primary-light);
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .file-upload-btn:hover {
      background: rgba(124, 58, 237, 0.25);
      border-style: solid;
    }

    .maquette-files-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .maquette-file-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text-dim);
      font-size: 0.8rem;
    }

    .maquette-file-item svg {
      color: var(--accent);
      flex-shrink: 0;
    }

    .maquette-file-item span {
      flex: 1;
    }

    .remove-file-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 20px;
      height: 20px;
      background: rgba(244, 63, 94, 0.2);
      border: none;
      border-radius: 50%;
      color: var(--error);
      font-size: 14px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .remove-file-btn:hover {
      background: rgba(244, 63, 94, 0.4);
    }

    .buttons-row {
      display: flex;
      gap: 12px;
      margin-top: 16px;
    }

    .run-btn-bdd {
      background: linear-gradient(135deg, #7c3aed, #06b6d4);
    }

    .run-btn-us {
      background: linear-gradient(135deg, #10b981, #059669);
    }

    .run-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 14px 28px;
      margin-top: 16px;
      background: linear-gradient(135deg, #7c3aed, #06b6d4);
      border: none;
      border-radius: 12px;
      color: white;
      font-family: 'Outfit', sans-serif;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
    }

    .run-btn:hover:not([disabled]) {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(124, 58, 237, 0.4);
    }

    .run-btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    @media (max-width: 640px) {
      .meta-grid { grid-template-columns: repeat(2, 1fr); }
      .mode-btn { font-size: 0.75rem; padding: 10px 12px; }
    }
  `]
})
export class DashboardComponent {
  selectedFile = signal('');
  loading = signal(false);
  error = signal('');
  results = signal<AnalysisResult | null>(null);
  userStoryResults = signal<UserStoryResult | null>(null);
  expandedScenario = signal<number | null>(null);
  currentFile = signal<File | null>(null);
  inputMode = signal<'text'>('text');
  displayMode = signal<'cards' | 'markdown'>('cards');
  maquetteFiles = signal<File[]>([]);
  maquetteContent = signal('');

  setInputMode(m: 'text') {
    this.inputMode.set(m);
    this.results.set(null);
    this.error.set('');
    this.selectedFile.set('');
    this.currentFile.set(null);
    this.maquetteFiles.set([]);
    this.maquetteContent.set('');
  }

  setDisplayMode(m: 'cards' | 'markdown') {
    this.displayMode.set(m);
  }

  onMaquetteSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      const newFiles = Array.from(input.files);
      const currentFiles = this.maquetteFiles();
      const updatedFiles = [...currentFiles, ...newFiles];
      this.maquetteFiles.set(updatedFiles);
      this.loadMaquetteContent();
    }
  }

  removeMaquetteFile(name: string) {
    const currentFiles = this.maquetteFiles().filter(f => f.name !== name);
    this.maquetteFiles.set(currentFiles);
    this.loadMaquetteContent();
  }

  async loadMaquetteContent() {
    const files = this.maquetteFiles();
    if (files.length === 0) {
      this.maquetteContent.set('');
      return;
    }

    let content = '';
    for (const file of files) {
      try {
        const fileContent = await file.text();
        content += `\n\n=== ${file.name} ===\n\n${fileContent}`;
      } catch (e) {
        console.error('Error reading file:', file.name, e);
      }
    }
    this.maquetteContent.set(content);
  }

  async generateFromMaquette() {
    const content = this.maquetteContent();
    if (!content) {
      this.error.set('Veuillez télécharger une maquette');
      return;
    }

    this.loading.set(true);
    this.error.set('');
    this.userStoryResults.set(null);

    try {
      const response = await fetch('http://localhost:8001/requirements/generate-from-requirements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content, save_to_file: true })
      });

      if (!response.ok) {
        const data = await response.json();
        this.error.set(data.detail || 'Erreur lors de la génération');
        return;
      }

      const data = await response.json();
      const parsedStories = this.parseMarkdownUserStories(data.user_stories);
      
      this.userStoryResults.set({
        user_stories: parsedStories,
        status: 'success',
        total: parsedStories.length,
        ai_raw: data.user_stories,
        message: 'User stories générées depuis les fichiers maquette'
      });
    } catch (e) {
      this.error.set('Erreur de connexion au serveur');
    } finally {
      this.loading.set(false);
    }
  }

  toggleDisplayMode() {
    this.displayMode.set(this.displayMode() === 'cards' ? 'markdown' : 'cards');
  }

  private parseMarkdownUserStories(markdown: string): ParsedUserStory[] {
    const stories: ParsedUserStory[] = [];

    // Split into blocks separated by --- lines
    const parts = markdown.split(/(?:^|\n)---+(?:\n|$)/);

    // Merge consecutive parts: a metadata block (with id:, title:) followed by
    // a content block (with En tant que, Je veux) belong to the same story.
    const mergedBlocks: string[] = [];
    let pendingMeta = '';

    for (const part of parts) {
      const trimmed = part.trim();
      if (!trimmed || trimmed.length < 5) continue;

      const hasId = /^id\s*:/im.test(trimmed);
      const hasStoryContent = /en tant que/i.test(trimmed) || /je veux/i.test(trimmed);

      if (hasId && !hasStoryContent) {
        // This is a metadata-only block, save it to merge with the next content block
        pendingMeta = trimmed;
      } else if (hasStoryContent) {
        // This is a content block — merge with pending metadata if any
        mergedBlocks.push(pendingMeta ? pendingMeta + '\n' + trimmed : trimmed);
        pendingMeta = '';
      } else if (hasId && hasStoryContent) {
        // Complete block with both metadata and content
        mergedBlocks.push(pendingMeta ? pendingMeta + '\n' + trimmed : trimmed);
        pendingMeta = '';
      }
      // Skip blocks that have neither id nor story content (noise)
    }

    // Parse each merged block into a story
    const usedIds = new Set<string>();
    let storyIndex = 0;

    for (const block of mergedBlocks) {
      const lines = block.split('\n');

      let id = '';
      let title = '';
      let status = 'todo';
      let priority = 'medium';
      let scope = '';
      let estimate = 'S';
      let role = '';
      let feature = '';
      let benefit = '';
      let acceptanceCriteria: string[] = [];

      for (const line of lines) {
        const l = line.trim();

        if (l.match(/^id\s*:/i) && !id) {
          id = l.replace(/^id\s*:\s*/i, '').trim();
        }
        if (l.match(/^title\s*:/i) && !title) {
          title = l.replace(/^title\s*:\s*/i, '').trim();
        }
        if (l.match(/^status\s*:/i)) {
          status = l.replace(/^status\s*:\s*/i, '').trim() || 'todo';
        }
        if (l.match(/^priority\s*:/i)) {
          priority = l.replace(/^priority\s*:\s*/i, '').trim() || 'medium';
        }
        if (l.match(/^scope\s*:/i)) {
          scope = l.replace(/^scope\s*:\s*/i, '').trim();
        }
        if (l.match(/^estimate\s*:/i)) {
          estimate = l.replace(/^estimate\s*:\s*/i, '').trim() || 'S';
        }

        // Extract user story fields (handle both **bold** and plain formats)
        const roleMatch = l.match(/(?:\*\*)?en tant que(?:\*\*)?\s+(.+)/i);
        if (roleMatch) {
          role = roleMatch[1].replace(/\*\*/g, '').replace(/,\s*$/, '').trim();
        }
        const featureMatch = l.match(/(?:\*\*)?je veux(?:\*\*)?\s+(.+)/i);
        if (featureMatch) {
          feature = featureMatch[1].replace(/\*\*/g, '').replace(/,\s*$/, '').trim();
        }
        const benefitMatch = l.match(/(?:\*\*)?afin de(?:\*\*)?\s+(.+)/i);
        if (benefitMatch) {
          benefit = benefitMatch[1].replace(/\*\*/g, '').replace(/,\s*$/, '').trim();
        }

        if (l.startsWith('- [') || l.startsWith('* [')) {
          acceptanceCriteria.push(l);
        }
      }

      // Skip stories that are clearly placeholders or empty
      const isPlaceholder = (
        (!role && !feature && !benefit) ||
        (feature === 'fonctionnalité' && benefit === 'bénéfice') ||
        (feature === '[fonctionnalité]' && benefit === '[bénéfice]')
      );
      if (isPlaceholder) continue;

      // Generate unique ID if missing or duplicate
      storyIndex++;
      if (!id) {
        id = `STORY-${String(storyIndex).padStart(3, '0')}`;
      }
      // Ensure unique IDs
      let uniqueId = id;
      let suffix = 1;
      while (usedIds.has(uniqueId)) {
        uniqueId = `${id}-${suffix}`;
        suffix++;
      }
      usedIds.add(uniqueId);

      if (!title) {
        title = `${role || 'utilisateur'} - ${(feature || 'fonctionnalité').substring(0, 40)}`;
      }

      stories.push({
        id: uniqueId,
        title: title,
        status: status,
        priority: priority,
        scope: scope ? [scope] : [],
        estimate: estimate,
        depends_on: [],
        role: role || 'utilisateur',
        feature: feature || '[Fonctionnalité à définir]',
        benefit: benefit || '[Bénéfice à définir]',
        acceptance_criteria: acceptanceCriteria.length > 0
          ? acceptanceCriteria
          : ['- [ ] Critère à définir']
      });
    }

    return stories;
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.[0]) {
      const file = input.files[0];
      this.selectedFile.set(file.name);
      this.currentFile.set(file);
    }
  }

  async runAnalysis() {
    const file = this.currentFile();
    if (!file) return;

    this.loading.set(true);
    this.error.set('');
    this.results.set(null);

    try {
      const content = await file.text();
      const endpoint = 'http://localhost:8001/scenarios/generate';
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      });

      if (!response.ok) {
        const data = await response.json();
        this.error.set(data.detail || 'Erreur lors de la génération');
        return;
      }

      const data = await response.json();
      this.results.set(data);
    } catch (e) {
      this.error.set('Erreur de connexion au serveur');
    } finally {
      this.loading.set(false);
    }
  }

  toggleScenario(num: number) {
    if (this.expandedScenario() === num) {
      this.expandedScenario.set(null);
    } else {
      this.expandedScenario.set(num);
    }
  }

  downloadAsMarkdown() {
    const results = this.results();
    if (!results) return;

    const md = this.generateMarkdown(results);
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analyse-resultats-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  downloadUserStoriesAsMarkdown() {
    const results = this.userStoryResults();
    if (!results) return;

    const md = results.ai_raw || this.generateUserStoriesMarkdown(results);
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `user-stories-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  copyMarkdown() {
    const results = this.userStoryResults();
    if (!results?.ai_raw) return;
    
    navigator.clipboard.writeText(results.ai_raw).then(() => {
      this.error.set('');
    }).catch(() => {
      this.error.set('Erreur lors de la copie');
    });
  }

  translateKeyword(keyword: string): string {
    const map: Record<string, string> = {
      'Given': 'Étant donné que',
      'When': 'Quand',
      'Then': 'Alors',
      'And': 'Et',
      'But': 'Mais'
    };
    return map[keyword] || keyword;
  }

  private generateMarkdown(results: AnalysisResult): string {
    const statusLabel = results.status === 'success' ? 'Succès' : results.status === 'partial' ? 'Partiel' : 'Erreur';
    const validCount = results.scenarios.filter(s => s.is_valid).length;
    const invalidCount = results.scenarios.length - validCount;

    let md = `# 📊 Rapport d'Analyse des Scénarios BDD\n\n`;
    md += `**Statut:** ${statusLabel}\n`;
    md += `**Total des scénarios:** ${results.total}\n`;
    md += `**Scénarios valides:** ${validCount}\n`;
    md += `**Scénarios invalides:** ${invalidCount}\n\n`;

    if (results.files_count) {
      md += `**Fichiers analysés:** ${results.files_count}\n\n`;
    }

    if (results.analysis) {
      md += `### Analyse Statique du Code\n\n`;
      if (results.analysis.features) {
        md += `**Fonctionnalités détectées:** ${results.analysis.features.join(', ')}\n`;
      }
      if (results.analysis.ui_elements_count) {
        md += `**Éléments UI:** ${results.analysis.ui_elements_count}\n`;
      }
      if (results.analysis.interactions_count) {
        md += `**Interactions:** ${results.analysis.interactions_count}\n`;
      }
      if (results.analysis.validations_count) {
        md += `**Validations:** ${results.analysis.validations_count}\n`;
      }
      if (results.analysis.api_calls_count) {
        md += `**Appels API:** ${results.analysis.api_calls_count}\n`;
      }
      md += `\n---\n\n`;
    }

    for (const scenario of results.scenarios) {
      md += `## 🔹 Scénario #${scenario.scenario_number}: ${scenario.title}\n\n`;
      md += `**${scenario.is_valid ? '✅ Valide' : '❌ Invalide'}**\n\n`;

      if (scenario.expected_error_message) {
        md += `📌 *Erreur attendue:* ${scenario.expected_error_message}\n\n`;
      }

      md += `#### 📝 Étapes du Test:\n`;
      for (const step of scenario.steps) {
        const keywordFr = step.keyword === 'Given' ? 'Étant donné que' :
                          step.keyword === 'When' ? 'Quand' :
                          step.keyword === 'Then' ? 'Alors' :
                          step.keyword === 'And' ? 'Et' : step.keyword;
        md += `- **${keywordFr}** ${step.text}\n`;
      }
      md += `\n`;

      if (scenario.errors.length > 0) {
        md += `#### 🚨 Erreurs Détectées:\n`;
        for (const err of scenario.errors) {
          md += `- ${err}\n`;
        }
        md += `\n`;
      }

      if (scenario.warnings.length > 0) {
        md += `#### ⚠️ Avertissements:\n`;
        for (const warn of scenario.warnings) {
          md += `- ${warn}\n`;
        }
        md += `\n`;
      }

      md += `---\n\n`;
    }

    if (results.message) {
      md += `### 📌 Note\n${results.message}\n`;
    }

    return md;
  }

  private generateUserStoriesMarkdown(results: UserStoryResult): string {
    let md = `# 📖 User Stories - Projet Analysé\n\n`;
    md += `**Total des user stories:** ${results.total}\n\n`;

    if (results.files_count) {
      md += `**Fichiers analysés:** ${results.files_count}\n\n`;
    }

    if (results.analysis) {
      md += `## Analyse du Code\n\n`;
      if (results.analysis.features) {
        md += `**Fonctionnalités détectées:** ${results.analysis.features.join(', ')}\n\n`;
      }
    }

    md += `---\n\n`;

    for (const story of results.user_stories) {
      const storyId = story.id || (story.story_number ? `STORY-${String(story.story_number).padStart(3, '0')}` : 'STORY-001');
      const role = story.role || '[Rôle à définir]';
      const feature = story.feature || '[Fonctionnalité à définir]';
      const benefit = story.benefit || '[Bénéfice à définir]';
      const status = story.status || 'todo';
      const priority = story.priority || 'medium';
      const scope = story.scope?.length ? story.scope.join(', ') : '';
      const estimate = story.estimate || 'S';
      const dependsOn = story.depends_on?.length ? story.depends_on.join(', ') : '';
      const acceptanceCriteria = story.acceptance_criteria?.length ? story.acceptance_criteria.join('\n') : '[ ] Critère 1\n[ ] Critère 2\n[ ] Critère 3';
      const techNotes = story.technical_notes || '';
      const dod = story.definition_of_done || '';

      md += `---
id: ${storyId}
title: ${role} - ${feature}
status: ${status}
priority: ${priority}
scope: ${scope ? `[${scope}]` : '[]'}
estimate: ${estimate}
depends_on: ${dependsOn ? `[${dependsOn}]` : '[]'}
---

## User story

**En tant que** ${role}
**Je veux** ${feature}
**Afin de** ${benefit}

## Critères d'acceptation

${acceptanceCriteria}

## Notes techniques

${techNotes || '_(optionnel)_'}

## Definition of Done

${dod || '_(optionnel — hérite de la DoD globale si omis)_'}

`;
      md += `---\n\n`;
    }

    if (results.message) {
      md += `## 📌 Note\n${results.message}\n`;
    }

    return md;
  }
}