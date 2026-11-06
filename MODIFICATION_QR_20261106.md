# IceBreaker — QR sur la page Présentateur (06/11/2026)

Dans le lobby du présentateur, le code de salle **et** le QR code pointant vers le lien public d'accès à cette salle sont visibles en mode normal et en mode séminaire (`?seminar=1`).

Le QR ne contient jamais le jeton privé de l'animateur : il encode uniquement le `join_url` de la salle. Les droits de la salle, le jeu et la procédure de participation sont inchangés.

Cette archive contient le code de l'IceBreaker et ses ressources, mais **pas** votre `.env`, la base locale `game.sqlite3`, l'environnement Python `.venv`, les historiques `.git` ou les dossiers d'agent. Restaurez vos propres variables d'environnement lors du déploiement.

Les tests n'ont pas été exécutés, conformément à la demande.
