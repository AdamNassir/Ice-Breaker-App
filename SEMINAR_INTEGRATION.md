# Mode Séminaire LogicLever — AI or Human

Ce déploiement d'IceBreaker est compatible avec la régie Organizer de LogicLever Mercato. Les anciennes fonctions restent disponibles (création manuelle de salle avec mot de passe, QR pour usage autonome, équipes, votes, résultats, question manager local).

- `GET /api/integration/capabilities` signale la compatibilité avec les decks par salle et le passage de la régie.
- `POST /api/rooms` avec le `PRESENTER_PASSWORD` peut inclure `deck` : un tableau de questions validé avec le même schéma que `questions.json`. Chaque salle en conserve une copie autonome, et l'API renvoie `deck_hash` pour confirmer le deck réellement utilisé.
- L'URL de régie reçue de l'app séminaire est `/presenter?room=XXXXXX&seminar=1#host_token=<jeton>`; le navigateur lit le jeton une fois et retire le fragment. Dans ce mode seulement, aucun second QR ne s'affiche.
- Les joueurs arrivent directement dans la salle via `/?room=XXXXXX&return_to=<URL-du-seminaire>` et peuvent utiliser **Retour au Mercato** depuis le jeu. Le reste du jeu est inchangé.

## Déploiement

Déployez **ce ZIP IceBreaker complet** dans le projet Vercel correspondant (Git ou Vercel CLI), en conservant `DATABASE_URL` et `PRESENTER_PASSWORD` dans les variables d'environnement Vercel. Vérifiez `https://votre-deploiement.vercel.app/api/integration/capabilities`.

Ensuite, dans l'application séminaire mise à jour, ouvrez **Organiser → IceBreaker** et configurez cette URL et le mot de passe. Le jeu anciennement déployé ne reconnaît pas les nouveaux appels; déployez cette version avant de créer des salles depuis Organizer.

Les modifications de questions **texte** faites dans Organizer sont transmises dans le corps de création de salle, sans autre déploiement. Les nouveaux médias d’Organizer sont publiés automatiquement dans Vercel Blob (configuration unique dans Organizer). Consultez `MEDIAS_SEMINAIRE_VERCEL_BLOB.md`.

L'installation ne nécessite aucune modification du modèle de données Supabase pour cette intégration. Les salons déjà créés ne reçoivent pas automatiquement le nouveau deck. Pour une nouvelle série, créez une nouvelle salle dans Organizer.
