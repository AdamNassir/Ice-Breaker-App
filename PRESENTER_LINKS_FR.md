# Liens privés du présentateur IceBreaker (Mercato)

Le lien obtenu dans **Mercato → Organizer → IceBreaker → Copier le lien privé du présentateur** ouvre directement la salle existante sur **un autre ordinateur ou dans un navigateur neuf**, sans demander le mot de passe de création de salle. Le bouton **Ouvrir la régie** conserve le même comportement.

Le lien contient `/presenter?room=XXXXXX&seminar=1#host_token=...`. **Conservez tout le lien, y compris `#host_token=...`.** Ce fragment reste visible dans la barre d'adresse lors de la navigation et du rafraîchissement. Il n'est pas transmis aux serveurs lors des requêtes HTTP.

Le jeton est une clé d'administration de **cette salle uniquement** : toute personne qui obtient le lien peut démarrer les manches et gérer le jeu. Ne le publiez pas et ne le partagez pas dans le QR des participants. Un lien ne comportant que `?room=XXXXXX` est insuffisant : sur un nouveau navigateur il ne doit **pas** ouvrir la régie. Utilisez alors le bouton Copier dans Organizer.

La création de salle exige toujours le mot de passe configuré sur Vercel ; **ouvrir une salle déjà créée avec le lien privé n'exige pas ce mot de passe**. Les jetons des salles cessent de fonctionner quand la salle expire sur Vercel.

## Déploiement

Redéployez le ZIP **IceBreaker** sur Vercel et mettez à jour le ZIP **Mercato** en conservant les secrets et volumes ; lancez ensuite `DEMARRER-SEMINAIRE.cmd`. Les salles déjà créées utilisent leurs jetons existants, aucun changement de base ni re-création de salle n'est nécessaire.
