---

id: STORY-001
title: Authentification
status: todo
priority: high
scope: backend
estimate: M
depends_on: []
---

## User story

**En tant que** utilisateur
**Je veux** m'authentifier via un champ Username et un champ Password
**Afin de** accéder au système

## Critères d'acceptation

- [ ] Le système valide les identifiants
- [ ] Le système bloque l'accès en cas d'erreur
- [ ] Le système redirige vers le Dashboard en cas de succès
- [ ] Le système différencie les rôles systèmes (ex: Admin, ESS) et restreint l'accès aux modules selon le profil connecté

## Notes techniques

Le système doit utiliser une méthode de cryptage sécurisée pour stocker les mots de passe.

## Definition of Done

Le système permet l'authentification avec succès et redirige vers le Dashboard.

---

id: STORY-002
title: Réinitialisation de mot de passe
status: todo
priority: medium
scope: backend
estimate: S
depends_on: [STORY-001]
---

## User story

**En tant que** utilisateur
**Je veux** réinitialiser mon mot de passe
**Afin de** accéder au système avec un nouveau mot de passe

## Critères d'acceptation

- [ ] Le système propose un lien Forgot your password?
- [ ] Le système permet de réinitialiser le mot de passe via un lien envoyé par email
- [ ] Le système valide les identifiants et redirige vers le Dashboard en cas de succès

## Notes techniques

Le système doit utiliser une méthode de cryptage sécurisée pour stocker les mots de passe.

## Definition of Done

Le système permet la réinitialisation de mot de passe avec succès.

---

id: STORY-003
title: Modification du mot de passe
status: todo
priority: medium
scope: backend
estimate: S
depends_on: [STORY-001]
---

## User story

**En tant que** utilisateur
**Je veux** modifier mon mot de passe
**Afin de** accéder au système avec un nouveau mot de passe

## Critères d'acceptation

- [ ] Le système permet de modifier le mot de passe via le menu profil
- [ ] Le système valide les identifiants et redirige vers le Dashboard en cas de succès
- [ ] Le système bloque l'accès en cas d'erreur

## Notes techniques

Le système doit utiliser une méthode de cryptage sécurisée pour stocker les mots de passe.

## Definition of Done

Le système permet la modification de mot de passe avec succès.

---

id: STORY-004
title: Affichage du tableau de bord
status: todo
priority: high
scope: frontend
estimate: L
depends_on: [STORY-001]
---

## User story

**En tant que** utilisateur
**Je veux** afficher le tableau de bord
**Afin de** visualiser les informations importantes

## Critères d'acceptation

- [ ] Le système affiche un widget Time at Work indiquant le statut actuel (Punched In/Out), l'heure de pointage et un graphique hebdomadaire des heures travaillées
- [ ] Le système affiche un widget My Actions listant les tâches en attente nécessitant une action utilisateur
- [ ] Le système propose un raccourci Quick Launch pour accéder rapidement aux fonctionnalités les plus utilisées

## Notes techniques

Le système doit utiliser une bibliothèque de graphiques pour afficher les données.

## Definition of Done

Le système affiche le tableau de bord avec succès.

---

id: STORY-005
title: Recherche d'utilisateurs
status: todo
priority: medium
scope: backend
estimate: M
depends_on: [STORY-001]
---

## User story

**En tant que** administrateur
**Je veux** rechercher des utilisateurs système
**Afin de** gérer les comptes utilisateurs

## Critères d'acceptation

- [ ] Le système permet de rechercher des utilisateurs système par Username, User Role, Employee Name ou Status
- [ ] Le système affiche les résultats sous forme de tableau paginé avec options de tri croissant/décroissant par colonne
- [ ] Le système permet d'ajouter un nouvel utilisateur via le bouton vert + Add

## Notes techniques

Le système doit utiliser une méthode de pagination pour afficher les résultats.

## Definition of Done

Le système permet la recherche d'utilisateurs avec succès.

---

id: STORY-006
title: Gestion des employés
status: todo
priority: high
scope: backend
estimate: XL
depends_on: [STORY-001]
---

## User story

**En tant que** administrateur
**Je veux** gérer les employés
**Afin de** gérer les données employés

## Critères d'acceptation

- [ ] Le système permet de rechercher un employé par Employee Name, Employee Id, Employment Status, Supervisor Name, Job Title ou Sub Unit
- [ ] Le système propose un filtre Include: Current Employees Only pour restreindre la liste aux employés actifs
- [ ] Le système permet d'ajouter un nouvel employé via le bouton + Add

## Notes techniques

Le système doit utiliser une méthode de pagination pour afficher les résultats.

## Definition of Done

Le système permet la gestion des employés avec succès.

---

id: STORY-007
title: Navigation & Structure globale
status: todo
priority: high
scope: frontend
estimate: L
depends_on: [STORY-001]
---

## User story

**En tant que** utilisateur
**Je veux** naviguer dans le système
**Afin de** accéder aux fonctionnalités

## Critères d'acceptation

- [ ] Le système fournit un menu latéral fixe regroupant les modules : Admin, PIM, Leave, Time, Recruitment, My Info, Performance, Directory, Maintenance, Claim, Dashboard
- [ ] Le système permet de masquer/réduire la barre latérale via le bouton fléché ‹

## Notes techniques

Le système doit utiliser une bibliothèque de navigation pour afficher le menu.

## Definition of Done

Le système permet la navigation avec succès.

---

id: STORY-008
title: Gestion des rôles
status: todo
priority: medium
scope: backend
estimate: M
depends_on: [STORY-001]
---

## User story

**En tant que** administrateur
**Je veux** gérer les rôles
**Afin de** restreindre l'accès aux modules

## Critères d'acceptation

- [ ] Le système différencie les rôles systèmes (ex: Admin, ESS) et restreint l'accès aux modules selon le profil connecté
- [ ] Le système permet de modifier ou supprimer un rôle existant via les icônes ✏️ (édition) et 🗑️ (suppression)

## Notes techniques

Le système doit utiliser une méthode de gestion des rôles pour restreindre l'accès.

## Definition of Done

Le système permet la gestion des rôles avec succès.

---

id: STORY-009
title: Gestion des permissions
status: todo
priority: medium
scope: backend
estimate: M
depends_on: [STORY-001]
---

## User story

**En tant que** administrateur
**Je veux** gérer les permissions
**Afin de** restreindre l'accès aux fonctionnalités

## Critères d'acceptation

- [ ] Le système permet de modifier ou supprimer une permission existante via les icônes ✏️ (édition) et 🗑️ (suppression)
- [ ] Le système permet de créer une nouvelle permission via le bouton vert + Add

## Notes techniques

Le système doit utiliser une méthode de gestion des permissions pour restreindre l'accès.

## Definition of Done

Le système permet la gestion des permissions avec succès.

---

id: STORY-010
title: Gestion des rapports
status: todo
priority: low
scope: backend
estimate: S
depends_on: [STORY-006]
---

## User story

**En tant que** administrateur
**Je veux** générer des rapports sur les données employés
**Afin de** analyser les données

## Critères d'acceptation

- [ ] Le système permet de générer des rapports sur les données employés via l'onglet Reports
- [ ] Le système affiche les résultats sous forme de tableau ou de graphique

## Notes techniques

Le système doit utiliser une bibliothèque de rapports pour générer les rapports.

## Definition of Done

Le système permet la génération des rapports avec succès.