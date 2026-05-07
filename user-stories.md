---

id: STORY-001
title: Authentification
status: todo
priority: high
scope: backend
estimate: M
depends_on: []

## User story

**En tant que** utilisateur
**Je veux** me connecter à l'application
**Afin de** accéder aux fonctionnalités

## Critères d'acceptation

- [ ] L'utilisateur peut saisir son nom d'utilisateur et son mot de passe
- [ ] L'application valide les identifiants et bloque l'accès en cas d'erreur
- [ ] L'application redirige vers le Dashboard en cas de succès

## Notes techniques

_(optionnel)_

## Definition of Done

_(optionnel — hérite de la DoD globale si omis)_

---

id: STORY-002
title: Gestion de session
status: todo
priority: high
scope: backend
estimate: M
depends_on: [STORY-001]

## User story

**En tant que** utilisateur
**Je veux** être connecté à l'application
**Afin de** accéder aux fonctionnalités

## Critères d'acceptation

- [ ] L'application différencie les rôles systèmes (ex: Admin, ESS)
- [ ] L'application restreint l'accès aux modules selon le profil connecté
- [ ] L'utilisateur peut modifier son mot de passe ou se déconnecter via le menu profil

## Notes techniques

_(optionnel)_

## Definition of Done

_(optionnel — hérite de la DoD globale si omis)_

---

id: STORY-003
title: Widget Time at Work
status: todo
priority: medium
scope: frontend
estimate: S
depends_on: [STORY-002]

## User story

**En tant que** utilisateur
**Je veux** voir mon statut de travail
**Afin de** savoir si je suis connecté ou non

## Critères d'acceptation

- [ ] Le widget affiche le statut actuel (Punched In/Out)
- [ ] Le widget affiche l'heure de pointage
- [ ] Le widget affiche un graphique hebdomadaire des heures travaillées

## Notes techniques

_(optionnel)_

## Definition of Done

_(optionnel — hérite de la DoD globale si omis)_

---

id: STORY-004
title: Gestion des utilisateurs
status: todo
priority: high
scope: backend
estimate: L
depends_on: []

## User story

**En tant que** administrateur
**Je veux** gérer les utilisateurs
**Afin de** contrôler l'accès à l'application

## Critères d'acceptation

- [ ] L'administrateur peut rechercher des utilisateurs par Username, User Role, Employee Name ou Status
- [ ] L'application affiche les résultats sous forme de tableau paginé avec options de tri croissant/décroissant par colonne
- [ ] L'administrateur peut ajouter un nouvel utilisateur via le bouton vert + Add

## Notes techniques

_(optionnel)_

## Definition of Done

_(optionnel — hérite de la DoD globale si omis)_

---

id: STORY-005
title: Gestion des employés
status: todo
priority: high
scope: backend
estimate: L
depends_on: []

## User story

**En tant que** administrateur
**Je veux** gérer les employés
**Afin de** contrôler les données employés

## Critères d'acceptation

- [ ] L'administrateur peut rechercher un employé par Employee Name, Employee Id, Employment Status, Supervisor Name, Job Title ou Sub Unit
- [ ] L'application propose un filtre Include: Current Employees Only pour restreindre la liste aux employés actifs
- [ ] L'administrateur peut ajouter un nouvel employé via le bouton + Add

## Notes techniques

_(optionnel)_

## Definition of Done

_(optionnel — hérite de la DoD globale si omis)_

---

id: STORY-006
title: Menu latéral fixe
status: todo
priority: medium
scope: frontend
estimate: S
depends_on: [STORY-002]

## User story

**En tant que** utilisateur
**Je veux** accéder aux fonctionnalités
**Afin de** utiliser l'application

## Critères d'acceptation

- [ ] Le menu latéral fixe regroupe les modules : Admin, PIM, Leave, Time, Recruitment, My Info, Performance, Directory, Maintenance, Claim, Dashboard
- [ ] Le menu est accessible via un bouton fléché ‹

## Notes techniques

_(optionnel)_

## Definition of Done

_(optionnel — hérite de la DoD globale si omis)_

---

id: STORY-007
title: Raccourci Quick Launch
status: todo
priority: low
scope: frontend
estimate: XS
depends_on: [STORY-002]

## User story

**En tant que** utilisateur
**Je veux** accéder rapidement aux fonctionnalités
**Afin de** utiliser l'application

## Critères d'acceptation

- [ ] Le raccourci Quick Launch propose un accès rapide aux fonctionnalités les plus utilisées

## Notes techniques

_(optionnel)_

## Definition of Done

_(optionnel — hérite de la DoD globale si omis)_

---

id: STORY-008
title: Flux Buzz Latest Posts
status: todo
priority: medium
scope: frontend
estimate: S
depends_on: [STORY-002]

## User story

**En tant que** utilisateur
**Je veux** voir les publications ou annonces récentes
**Afin de** rester informé

## Critères d'acceptation

- [ ] Le flux Buzz Latest Posts regroupe les publications ou annonces récentes
- [ ] Le flux est accessible via un widget sur le Dashboard

## Notes techniques

_(optionnel)_

## Definition of Done

_(optionnel — hérite de la DoD globale si omis)_

---

id: STORY-009
title: Gestion des rapports
status: todo
priority: high
scope: backend
estimate: L
depends_on: [STORY-005]

## User story

**En tant que** administrateur
**Je veux** générer des rapports sur les données employés
**Afin de** prendre des décisions éclairées

## Critères d'acceptation

- [ ] L'administrateur peut générer des rapports sur les données employés via l'onglet Reports
- [ ] Les rapports sont accessibles via un bouton sur le Dashboard

## Notes techniques

_(optionnel)_

## Definition of Done

_(optionnel — hérite de la DoD globale si omis)_