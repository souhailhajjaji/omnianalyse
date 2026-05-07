---

### Authentification & Gestion de session

#### STORY-001
title: Authentification
status: todo
priority: high
scope: backend
estimate: M
depends_on: []

**En tant que** utilisateur
**Je veux** m'authentifier via un champ Username et un champ Password
**Afin de** accéder au système

Critères d'acceptation
- [ ] Le système valide les identifiants
- [ ] Le système bloque l'accès en cas d'erreur
- [ ] Le système redirige vers le Dashboard en cas de succès

#### STORY-002
title: Gestion de session
status: todo
priority: high
scope: backend
estimate: M
depends_on: [STORY-001]

**En tant que** utilisateur
**Je veux** modifier mon mot de passe ou me déconnecter
**Afin de** sécuriser mon compte

Critères d'acceptation
- [ ] Le système permet de modifier le mot de passe
- [ ] Le système permet de se déconnecter
- [ ] Le système supprime la session utilisateur

#### STORY-003
title: Authentification avancée
status: todo
priority: medium
scope: backend
estimate: L
depends_on: [STORY-001]

**En tant que** administrateur
**Je veux** différencier les rôles systèmes et restreindre l'accès aux modules
**Afin de** sécuriser l'accès au système

Critères d'acceptation
- [ ] Le système différencie les rôles systèmes
- [ ] Le système restreint l'accès aux modules selon le profil connecté

---

### Tableau de bord (Dashboard)

#### STORY-004
title: Affichage du widget Time at Work
status: todo
priority: high
scope: frontend
estimate: S
depends_on: []

**En tant que** utilisateur
**Je veux** afficher le statut actuel, l'heure de pointage et un graphique hebdomadaire des heures travaillées
**Afin de** suivre mes heures de travail

Critères d'acceptation
- [ ] Le système affiche le statut actuel
- [ ] Le système affiche l'heure de pointage
- [ ] Le système affiche un graphique hebdomadaire des heures travaillées

#### STORY-005
title: Affichage du widget My Actions
status: todo
priority: high
scope: frontend
estimate: S
depends_on: []

**En tant que** utilisateur
**Je veux** afficher les tâches en attente nécessitant une action utilisateur
**Afin de** suivre mes tâches

Critères d'acceptation
- [ ] Le système affiche les tâches en attente
- [ ] Le système affiche les détails des tâches

#### STORY-006
title: Affichage du widget Quick Launch
status: todo
priority: medium
scope: frontend
estimate: XS
depends_on: []

**En tant que** utilisateur
**Je veux** accéder rapidement aux fonctionnalités les plus utilisées
**Afin de** simplifier mon accès

Critères d'acceptation
- [ ] Le système propose un raccourci Quick Launch
- [ ] Le système redirige vers la fonctionnalité sélectionnée

---

### Administration → Gestion des utilisateurs

#### STORY-007
title: Recherche d'utilisateurs
status: todo
priority: high
scope: backend
estimate: M
depends_on: []

**En tant que** administrateur
**Je veux** rechercher des utilisateurs système par Username, User Role, Employee Name ou Status
**Afin de** trouver rapidement les informations nécessaires

Critères d'acceptation
- [ ] Le système permet de rechercher des utilisateurs
- [ ] Le système affiche les résultats sous forme de tableau paginé

#### STORY-008
title: Gestion des utilisateurs
status: todo
priority: high
scope: backend
estimate: M
depends_on: [STORY-007]

**En tant que** administrateur
**Je veux** ajouter, modifier ou supprimer un utilisateur existant
**Afin de** gérer les utilisateurs

Critères d'acceptation
- [ ] Le système permet d'ajouter un nouvel utilisateur
- [ ] Le système permet de modifier un utilisateur existant
- [ ] Le système permet de supprimer un utilisateur existant

#### STORY-009
title: Gestion des comptes
status: todo
priority: medium
scope: backend
estimate: L
depends_on: [STORY-008]

**En tant que** administrateur
**Je veux** gérer le statut des comptes (Enabled/Disabled) et empêcher la connexion des comptes désactivés
**Afin de** sécuriser l'accès au système

Critères d'acceptation
- [ ] Le système gère le statut des comptes
- [ ] Le système empêche la connexion des comptes désactivés

---

### PIM (Personal Information Management) → Gestion des employés

#### STORY-010
title: Recherche d'employés
status: todo
priority: high
scope: backend
estimate: M
depends_on: []

**En tant que** administrateur
**Je veux** rechercher un employé par Employee Name, Employee Id, Employment Status, Supervisor Name, Job Title ou Sub Unit
**Afin de** trouver rapidement les informations nécessaires

Critères d'acceptation
- [ ] Le système permet de rechercher des employés
- [ ] Le système affiche les résultats sous forme de liste/tableau

#### STORY-011
title: Gestion des employés
status: todo
priority: high
scope: backend
estimate: M
depends_on: [STORY-010]

**En tant que** administrateur
**Je veux** ajouter, modifier ou supprimer un employé existant
**Afin de** gérer les employés

Critères d'acceptation
- [ ] Le système permet d'ajouter un nouvel employé
- [ ] Le système permet de modifier un employé existant
- [ ] Le système permet de supprimer un employé existant

---

### Navigation & Structure globale

#### STORY-012
title: Affichage du menu latéral
status: todo
priority: high
scope: frontend
estimate: S
depends_on: []

**En tant que** utilisateur
**Je veux** afficher un menu latéral fixe regroupant les modules
**Afin de** naviguer facilement

Critères d'acceptation
- [ ] Le système affiche le menu latéral
- [ ] Le système regroupe les modules correctement