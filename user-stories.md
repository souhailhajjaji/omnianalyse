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
**Je veux** m'authentifier via un champ Username et un champ Password
**Afin de** accéder au système

## Critères d'acceptation

- [ ] Le système valide les identifiants
- [ ] Le système bloque l'accès en cas d'erreur
- [ ] Le système redirige vers le Dashboard en cas de succès

## Notes techniques

Le système doit utiliser un protocole de sécurité pour protéger les identifiants.

## Definition of Done

Le système doit permettre à l'utilisateur de s'authentifier via un champ Username et un champ Password.

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
**Je veux** que le système gère la session
**Afin de** m'identifier comme utilisateur connecté

## Critères d'acceptation

- [ ] Le système différencie les rôles systèmes (ex: Admin, ESS)
- [ ] Le système restreint l'accès aux modules selon le profil connecté
- [ ] Le système permet à l'utilisateur de modifier son mot de passe ou de se déconnecter

## Notes techniques

Le système doit utiliser une session pour stocker les informations de l'utilisateur connecté.

## Definition of Done

Le système doit gérer la session de l'utilisateur connecté.

---

id: STORY-003
title: Tableau de bord
status: todo
priority: medium
scope: frontend
estimate: L
depends_on: [STORY-002]

## User story

**En tant que** utilisateur
**Je veux** afficher un tableau de bord
**Afin de** visualiser mes informations

## Critères d'acceptation

- [ ] Le système affiche un widget Time at Work
- [ ] Le système affiche un widget My Actions
- [ ] Le système propose un raccourci Quick Launch

## Notes techniques

Le système doit utiliser un framework de visualisation pour afficher les widgets.

## Definition of Done

Le système doit afficher un tableau de bord avec les widgets requis.

---

id: STORY-004
title: Recherche d'utilisateurs
status: todo
priority: medium
scope: backend
estimate: M
depends_on: [STORY-002]

## User story

**En tant que** administrateur
**Je veux** rechercher des utilisateurs
**Afin de** gérer les comptes

## Critères d'acceptation

- [ ] Le système permet de rechercher des utilisateurs par Username, User Role, Employee Name ou Status
- [ ] Le système affiche les résultats sous forme de tableau paginé
- [ ] Le système permet de trier les résultats

## Notes techniques

Le système doit utiliser une base de données pour stocker les informations des utilisateurs.

## Definition of Done

Le système doit permettre de rechercher des utilisateurs.

---

id: STORY-005
title: Gestion des utilisateurs
status: todo
priority: high
scope: backend
estimate: L
depends_on: [STORY-004]

## User story

**En tant que** administrateur
**Je veux** gérer les utilisateurs
**Afin de** gérer les comptes

## Critères d'acceptation

- [ ] Le système permet d'ajouter un nouvel utilisateur
- [ ] Le système permet de modifier ou supprimer un utilisateur existant
- [ ] Le système gère le statut des comptes (Enabled/Disabled)

## Notes techniques

Le système doit utiliser une base de données pour stocker les informations des utilisateurs.

## Definition of Done

Le système doit permettre de gérer les utilisateurs.

---

id: STORY-006
title: Gestion des employés
status: todo
priority: medium
scope: backend
estimate: M
depends_on: [STORY-002]

## User story

**En tant que** administrateur
**Je veux** gérer les employés
**Afin de** gérer les données employés

## Critères d'acceptation

- [ ] Le système permet de rechercher un employé par Employee Name, Employee Id, Employment Status, Supervisor Name, Job Title ou Sub Unit
- [ ] Le système propose un filtre Include: Current Employees Only
- [ ] Le système permet d'ajouter un nouvel employé

## Notes techniques

Le système doit utiliser une base de données pour stocker les informations des employés.

## Definition of Done

Le système doit permettre de gérer les employés.

---

id: STORY-007
title: Navigation & Structure globale
status: todo
priority: low
scope: frontend
estimate: S
depends_on: [STORY-003]

## User story

**En tant que** utilisateur
**Je veux** naviguer dans le système
**Afin de** accéder aux fonctionnalités

## Critères d'acceptation

- [ ] Le système propose un menu latéral fixe
- [ ] Le système regroupe les modules dans des catégories

## Notes techniques

Le système doit utiliser un framework de navigation pour afficher le menu.

## Definition of Done

Le système doit proposer un menu latéral fixe.

---

id: STORY-008
title: Réinitialisation de mot de passe
status: todo
priority: medium
scope: backend
estimate: M
depends_on: [STORY-001]

## User story

**En tant que** utilisateur
**Je veux** réinitialiser mon mot de passe
**Afin de** accéder au système

## Critères d'acceptation

- [ ] Le système propose un lien Forgot your password?
- [ ] Le système permet de réinitialiser le mot de passe

## Notes techniques

Le système doit utiliser un protocole de sécurité pour protéger les identifiants.

## Definition of Done

Le système doit permettre de réinitialiser le mot de passe.

---

id: STORY-009
title: Génération de rapports
status: todo
priority: low
scope: backend
estimate: S
depends_on: [STORY-006]

## User story

**En tant que** administrateur
**Je veux** générer des rapports
**Afin de** analyser les données employés

## Critères d'acceptation

- [ ] Le système permet de générer des rapports sur les données employés
- [ ] Le système propose des options de filtre pour les rapports

## Notes techniques

Le système doit utiliser une bibliothèque de génération de rapports pour créer les rapports.

## Definition of Done

Le système doit permettre de générer des rapports.

---

id: STORY-010
title: Configuration de PIM
status: todo
priority: medium
scope: backend
estimate: M
depends_on: [STORY-006]

## User story

**En tant que** administrateur
**Je veux** configurer PIM
**Afin de** personnaliser les champs affichés ou les règles de validation PIM

## Critères d'acceptation

- [ ] Le système propose un onglet Configuration pour PIM
- [ ] Le système permet de personnaliser les champs affichés ou les règles de validation PIM

## Notes techniques

Le système doit utiliser une base de données pour stocker les informations de configuration.

## Definition of Done

Le système doit permettre de configurer PIM.