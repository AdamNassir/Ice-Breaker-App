# IceBreaker — classement final des équipes

Cette version conserve les fonctions du Global Deck Manager, l'upload d'images d'explication, les vidéos réservées au présentateur et les durées locales de questions.

## Fin de la partie

- Le décompte réel provient du jeu de questions utilisé pour **cette salle** : de 1 à 200 manches.
- Après la révélation de la dernière réponse, le présentateur clique **Show final results**. Cela laisse le temps de commenter la dernière réponse avant la projection du classement.
- Le résultat final s'affiche à la fois sur l'écran du présentateur et sur les téléphones des participants dès la synchronisation suivante.
- Le classement affiche toutes les équipes avec leur score cumulé et leur rang. Le podium montre les trois premiers rangs, puis les autres équipes suivent dans la liste. Les ex-aequo partagent leur rang (exemple : 1, 1, 3).
- Les téléphones affichent un classement compact sur une seule colonne à petite largeur. Le classement reste stable lors des rafraîchissements.
- La mention « Final team ranking » apparait lorsqu'au moins une équipe est créée avant le début. Sans équipe, IceBreaker reste compatible avec le classement individuel.

## Vérifications

- Tests du serveur sur des parties réelles de 1, 2, 6, 17 et 200 manches avec quatre équipes, votes et calcul des points, ex-aequo, fin de partie, résultats identiques pour le présentateur et les joueurs.
- Tests de rendu dans Chromium sur le classement final du présentateur et sur téléphone (320 px) pour 1, 6 et 200 manches.
- Tests de régression ciblés du jeu, des équipes, du deck global et des médias.

Aucune migration SQL n'est nécessaire. Déployer l'application complète sur Vercel et conserver la configuration Supabase/Blob existante.
