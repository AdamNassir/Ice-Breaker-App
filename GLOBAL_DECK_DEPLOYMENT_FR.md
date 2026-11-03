# IceBreaker — gestionnaire global des questions (édition Vercel + Mercato)

## Ce qui change

- L'éditeur **indépendant** est accessible à `https://VOTRE-ICEBREAKER.vercel.app/deck-manager`, **même quand Mercato est arrêté**.
- L'éditeur est protégé par un **mot de passe d'administration du deck distinct** du mot de passe présentateur. Les questions, y compris les réponses et les notes privées, sont conservées dans **Supabase PostgreSQL**, jamais dans des fichiers statiques accessibles publiquement.
- Les **images, logos, audios et vidéos** ajoutés depuis l'éditeur global sont téléversés directement par l'API serveur vers votre magasin **Vercel Blob public**. Le jeton n'est jamais envoyé dans le navigateur.
- L'éditeur intégré à **Mercato** accède au **même deck**. À l'ouverture, lors d'une actualisation ou environ toutes les 30 secondes si aucune modification locale n'est en cours, il récupère les modifications faites dans l'éditeur global.
- Les articles **News Article** peuvent maintenant personnaliser la publication, le logo, l'édition, la navigation, la rubrique, le fil d'Ariane, le titre, le chapô, l'auteur, la date, le texte, la photo, les mots-clés, la barre latérale, les emplacements publicitaires et jusqu'à trois articles secondaires. Le bouton **Use existing Bitcoin article as template** reprend l'article Bitcoin fourni dans le projet.
- Les **salles déjà ouvertes** conservent leur propre copie du questionnaire. Seules les nouvelles salles récupèrent le deck courant.

## Installation impérative dans cet ordre

1. **Sauvegarder vos données existantes** : le dossier `secrets/`, `private/`, les fichiers `.env`, ainsi que vos bases de données. Les ZIP corrigés excluent volontairement les secrets et les données de session. Ne remplacez pas vos secrets par des dossiers vides.
2. Dans le **SQL Editor Supabase**, avec un rôle qui peut créer des tables dans le schéma `icebreaker`, exécuter **`supabase_deck_migration.sql`** provenant du ZIP IceBreaker. Ne pas réexécuter tout `supabase.sql` sur une instance existante. Cette migration ne modifie pas les salles déjà enregistrées.
3. Déployer le **ZIP IceBreaker complet** sur le projet Vercel existant. Maintenir `DATABASE_URL` et `PRESENTER_PASSWORD`. Relier à ce projet votre magasin **Vercel Blob public**, avec la variable d'environnement `BLOB_READ_WRITE_TOKEN`. Ajouter une nouvelle variable serveur **`shared deck access`** (mot de passe long et unique, différent du mot de passe présentateur). **Redéployer** l'application après l'ajout des variables.
4. Contrôler `https://VOTRE-ICEBREAKER.vercel.app/api/integration/capabilities` : la réponse doit inclure `"shared_deck": true`.
5. Mettre à jour les **fichiers de code Mercato** avec le ZIP Mercato complet, **sans écraser vos secrets ni vos données persistantes**. Reconstruire/recréer le conteneur Mercato depuis son dossier :
   ```sh
   docker compose build --no-cache mercato
   docker compose up -d --no-deps --force-recreate mercato testing
   ```
6. Dans **Organizer → IceBreaker**, conserver l'URL Vercel, le mot de passe présentateur et le jeton Blob ; ajouter **le même `shared deck access`** dans le nouveau champ *Mot de passe du deck global Vercel*, puis enregistrer. **Cette première connexion importe automatiquement le deck Mercato déjà sauvegardé**, avec ses médias privés publiés sur Blob si nécessaire, à condition que le deck Vercel n'ait pas encore été initialisé.
7. Ouvrir `https://VOTRE-ICEBREAKER.vercel.app/deck-manager`, saisir `shared deck access`, éditer puis enregistrer. Dans Mercato, ouvrir/recharger l'éditeur des questions et vérifier que les changements apparaissent. Créer une **nouvelle salle** pour tester les nouvelles questions.

**Très important :** si vous avez déjà enregistré une version du deck avec le gestionnaire global **avant** de connecter Mercato, celle-ci est considérée comme la version de référence. Dans ce cas, exportez le deck Mercato local si vous souhaitez récupérer d'anciennes questions, puis importez-le dans l'éditeur global. Les modifications concurrentes sont protégées par un numéro de révision : une ancienne page ne peut pas écraser silencieusement un deck plus récent.

## Limites et précautions

- **4 Mo maximum par média** pour un upload depuis l'éditeur global Vercel (limite de taille des requêtes des Functions). Utilisez Mercato pour des médias de 4 à 25 Mo ; il les transfère directement du conteneur Docker vers Vercel Blob, sans passer par le corps d'une Function Vercel. Vous pouvez aussi optimiser les médias en amont.
- Vercel Blob **public** : toute personne possédant une URL peut ouvrir le fichier. Ne pas y transférer de données confidentielles. Les **réponses** restent dans la base non publique et sont transmises seulement à la révélation en jeu.
- Ne mettez **jamais** `shared deck access`, `PRESENTER_PASSWORD`, `BLOB_READ_WRITE_TOKEN` ou `DATABASE_URL` dans le code JavaScript du navigateur, dans Git ou dans le ZIP partagé.
- Les images importées sous forme de fichiers privés dans Mercato sont promues vers Blob lors de la synchronisation ; les médias originaux inclus dans les fichiers statiques du projet restent sur Vercel.
- Si Mercato ne peut plus joindre l'API globale, il affiche une erreur au lieu de substituer silencieusement un ancien deck lors de la création d'une nouvelle salle. Le formulaire de configuration reste accessible pour corriger URL, mot de passe ou migration SQL.
- Le projet contient également un **question_manager.py local historique**, distinct. Pour l'édition partagée en production, utilisez `/deck-manager` ou **Organizer → IceBreaker** plutôt que le gestionnaire local hérité.

## Vérification du fonctionnement sans Mercato

1. Arrêter temporairement Mercato.
2. Ouvrir `https://VOTRE-ICEBREAKER.vercel.app/deck-manager` et s'authentifier.
3. Modifier un titre, enregistrer le deck, fermer et rouvrir la page : la modification doit persister grâce à Supabase.
4. Rallumer Mercato : l'éditeur Organizer retrouve ce même deck. Les nouvelles salles utilisent la dernière version, les salles existantes restent inchangées.

## Dépannage

- **« Shared deck table missing »** : exécuter `supabase_deck_migration.sql` et vérifier les privilèges de `icebreaker_app`.
- **401** : vérifier que les deux applications utilisent exactement le même `shared deck access` ; sans confondre ce secret avec `PRESENTER_PASSWORD`.
- **502 sur un média** : vérifier la liaison Blob au **projet Vercel IceBreaker** ainsi que le jeton dans Mercato.
- **409** : un autre utilisateur/onglet a sauvegardé un deck plus récent. Exporter votre brouillon, recharger puis fusionner.
- **Ancienne salle** : recommencer une salle ; le deck de la salle ouverte est volontairement immuable.
