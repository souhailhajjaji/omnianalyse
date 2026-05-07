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
**Afin de** accéder à mes données personnelles et aux fonctionnalités de l'application

## Critères d'acceptation

- L'utilisateur peut saisir son nom d'utilisateur et son mot de passe
- L'application valide les identifiants et bloque l'accès en cas d'erreur
- L'application redirige vers le Dashboard en cas de succès
- L'application différencie les rôles systèmes et restreint l'accès aux modules selon le profil connecté

## Notes techniques

L'application utilisera un système de gestion d'identité pour valider les identifiants et gérer les sessions.

## Definition of Done

La fonctionnalité d'authentification est implémentée et testée avec succès.

---

id: STORY-002
title: Réinitialisation de mot de passe
status: todo
priority: medium
scope: backend
estimate: S
depends_on: [STORY-001]

## User story

**En tant que** utilisateur
**Je veux** réinitialiser mon mot de passe
**Afin de** accéder à nouveau à l'application

## Critères d'acceptation

- L'utilisateur peut cliquer sur le lien "Forgot your password?" pour initier la procédure de réinitialisation
- L'application envoie un email de réinitialisation avec un lien de réinitialisation
- L'utilisateur peut saisir un nouveau mot de passe et valider la réinitialisation

## Notes techniques

L'application utilisera un système de gestion d'emails pour envoyer les emails de réinitialisation.

## Definition of Done

La fonctionnalité de réinitialisation de mot de passe est implémentée et testée avec succès.

---

id: STORY-003
title: Gestion des utilisateurs
status: todo
priority: high
scope: backend
estimate: L
depends_on: [STORY-001]

## User story

**En tant que** administrateur
**Je veux** gérer les utilisateurs de l'application
**Afin de** accéder à leurs données personnelles et gérer leurs droits d'accès

## Critères d'acceptation

- L'administrateur peut rechercher des utilisateurs par nom d'utilisateur, rôle, nom d'employé ou statut
- L'application affiche les résultats sous forme de tableau paginé avec options de tri croissant/décroissant par colonne
- L'administrateur peut ajouter un nouvel utilisateur via le bouton vert + Add
- L'administrateur peut modifier ou supprimer un utilisateur existant via les icônes ✏️ (édition) et 🗑️ (suppression)

## Notes techniques

L'application utilisera un système de gestion de base de données pour stocker les données des utilisateurs.

## Definition of Done

La fonctionnalité de gestion des utilisateurs est implémentée et testée avec succès.

---

id: STORY-004
title: Tableau de bord
status: todo
priority: high
scope: frontend
estimate: XL
depends_on: [STORY-001]

## User story

**En tant que** utilisateur
**Je veux** accéder au tableau de bord de l'application
**Afin de** visualiser mes données personnelles et les fonctionnalités de l'application

## Critères d'acceptation

- Le tableau de bord affiche un widget Time at Work indiquant le statut actuel (Punched In/Out), l'heure de pointage et un graphique hebdomadaire des heures travaillées
- Le tableau de bord affiche un widget My Actions listant les tâches en attente nécessitant une action utilisateur
- Le tableau de bord propose un raccourci Quick Launch pour accéder rapidement aux fonctionnalités les plus utilisées
- Le tableau de bord affiche un flux Buzz Latest Posts regroupant les publications ou annonces récentes

## Notes techniques

L'application utilisera un framework de développement web pour implémenter la fonctionnalité du tableau de bord.

## Definition of Done

La fonctionnalité du tableau de bord est implémentée et testée avec succès.

---

id: STORY-005
title: Gestion des employés
status: todo
priority: high
scope: backend
estimate: L
depends_on: [STORY-001]

## User story

**En tant que** administrateur
**Je veux** gérer les employés de l'application
**Afin de** accéder à leurs données personnelles et gérer leurs droits d'accès

## Critères d'acceptation

- L'administrateur peut rechercher un employé par nom d'employé, ID d'employé, statut d'emploi, nom de superviseur, titre de poste ou sous-unité
- L'application propose un filtre Include: Current Employees Only pour restreindre la liste aux employés actifs
- L'application affiche les résultats sous forme de liste/tableau avec pagination et tri
- L'administrateur peut ajouter un nouvel employé via le bouton + Add

## Notes techniques

L'application utilisera un système de gestion de base de données pour stocker les données des employés.

## Definition of Done

La fonctionnalité de gestion des employés est implémentée et testée avec succès.

---

id: STORY-006
title: Menu latéral
status: todo
priority: medium
scope: frontend
estimate: M
depends_on: [STORY-001]

## User story

**En tant que** utilisateur
**Je veux** accéder au menu latéral de l'application
**Afin de** naviguer facilement dans les fonctionnalités de l'application

## Critères d'acceptation

- Le menu latéral est fixe et regroupe les modules : Admin, PIM, Leave, Time, Recruitment, My Info, Performance, Directory, Maintenance, Claim, Dashboard
- Le menu latéral est accessible via un bouton fléché ‹

## Notes techniques

L'application utilisera un framework de développement web pour implémenter la fonctionnalité du menu latéral.

## Definition of Done

La fonctionnalité du menu latéral est implémentée et testée avec succès.

---

id: STORY-007
title: Gestion des rôles
status: todo
priority: high
scope: backend
estimate: L
depends_on: [STORY-001]

## User story

**En tant que** administrateur
**Je veux** gérer les rôles de l'application
**Afin de** accéder à leurs données personnelles et gérer leurs droits d'accès

## Critères d'acceptation

- L'administrateur peut créer, modifier ou supprimer des rôles
- L'application affecte les rôles aux utilisateurs en fonction de leurs droits d'accès

## Notes techniques

L'application utilisera un système de gestion de base de données pour stocker les données des rôles.

## Definition of Done

La fonctionnalité de gestion des rôles est implémentée et testée avec succès.

---

id: STORY-008
title: Gestion des permissions
status: todo
priority: high
scope: backend
estimate: L
depends_on: [STORY-001]

## User story

**En tant que** administrateur
**Je veux** gérer les permissions de l'application
**Afin de** accéder à leurs données personnelles et gérer leurs droits d'accès

## Critères d'acceptation

- L'administrateur peut créer, modifier ou supprimer des permissions
- L'application affecte les permissions aux utilisateurs en fonction de leurs droits d'accès

## Notes techniques

L'application utilisera un système de gestion de base de données pour stocker les données des permissions.

## Definition of Done

La fonctionnalité de gestion des permissions est implémentée et testée avec succès.

---

id: STORY-009
title: Gestion des rapports
status: todo
priority: medium
scope: backend
estimate: M
depends_on: [STORY-001]

## User story

**En tant que** administrateur
**Je veux** générer des rapports sur les données de l'application
**Afin de** obtenir des informations précises sur les données de l'application

## Critères d'acceptation

- L'administrateur peut générer des rapports sur les données de l'application
- Les rapports sont accessibles via un onglet Reports

## Notes techniques

L'application utilisera un système de gestion de base de données pour stocker les données des rapports.

## Definition of Done

La fonctionnalité de gestion des rapports est implémentée et testée avec succès.

---

id: STORY-010
title: Gestion des notifications
status: todo
priority: medium
scope: backend
estimate: M
depends_on: [STORY-001]

## User story

**En tant que** utilisateur
**Je veux** recevoir des notifications sur les événements de l'application
**Afin de** être informé des changements dans l'application

## Critères d'acceptation

- L'utilisateur peut recevoir des notifications sur les événements de l'application
- Les notifications sont accessibles via un onglet Notifications

## Notes techniques

L'application utilisera un système de gestion de base de données pour stocker les données des notifications.

## Definition of Done

La fonctionnalité de gestion des notifications est implémentée et testée avec succès.