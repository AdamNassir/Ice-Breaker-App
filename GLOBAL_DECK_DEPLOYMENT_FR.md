# Déploiement du gestionnaire global IceBreaker + import ZIP

## 1. Mettre à jour le projet Vercel IceBreaker

- Déployez cette version de **Ice_Breaker_Game_App** sur le projet Vercel **IceBreaker** existant.
- Conservez `DATABASE_URL`, `PRESENTER_PASSWORD` et `PUBLIC_BASE_URL` existants.
- Votre stockage **Vercel Blob public** doit être relié au projet IceBreaker. La variable serveur `BLOB_READ_WRITE_TOKEN` doit être disponible **sur ce projet**, et non seulement dans les secrets Mercato.
- Si ce n'est pas déjà fait, exécutez `supabase_deck_migration.sql` dans l'éditeur SQL du bon projet Supabase.
- Aucun `DECK_ADMIN_PASSWORD` n'est demandé dans cette version. Il n'y a pas de mur de connexion spécifique pour `/deck-manager` : **quiconque accède à cet éditeur public peut modifier le deck**. Si cela n'est pas souhaité, configurez la protection d'accès au niveau Vercel.

## 2. Importer le lot de six questions

1. Ouvrez `https://VOTRE-ICEBREAKER.vercel.app/deck-manager`.
2. Dans **Deck tools**, cliquez sur **Download draft** pour sauvegarder le deck actuel.
3. Cliquez sur **Import ZIP + media** et sélectionnez `IceBreaker_6_Questions_OneClick_Bundle.zip`.
4. Confirmez le remplacement du deck actuel si vous souhaitez **six questions au total**. Choisissez plutôt « append » pour ajouter ces questions à l'existant.
5. Confirmez que vous disposez des droits nécessaires pour présenter les photographies.
6. IceBreaker vérifie la structure, récupère les images depuis des sources publiques épinglées, modifie la capture Jira authentique et publie ces fichiers sur Vercel Blob. Une fois toutes les étapes terminées, il enregistre le deck dans Supabase.
7. Prévisualisez chacune des six questions, surtout la publicité vidéo pour repérer les indices qui pourraient révéler l'IA.
8. Créez une **nouvelle salle** : une salle déjà créée garde une copie du deck au moment de sa création.

**Important** : le ZIP de six questions n'embarque pas les photographies tierces protégées. Les originaux sont téléchargés lors de l'import depuis les éditeurs/créateurs. Si une source bloque le téléchargement ou a changé, l'import **échoue sans remplacer le deck** : obtenez l'original avec les autorisations nécessaires et placez-le dans le ZIP au chemin `assets/...` indiqué dans `manifest.json` avant de recommencer. L'import préfère les images embarquées aux téléchargements distants.

Le plan large de l'Excel World Championship 2025 remplace le portrait de champion. La photo du flamant provient du fichier original du site Miles Astray et est affichée en mode `contain`, sans recadrage.

## 3. Format pour les prochains ZIP

- À la racine : `manifest.json`, `questions.json`.
- Sous `assets/` : fichiers `.jpg`, `.jpeg`, `.png`, `.webp` facultatifs (max. 4 Mo pour le ZIP compressé entier).
- `manifest.json` contient `{"format":"icebreaker-deck-bundle","version":1,"media":{"assets/monimage.jpg":{}}}` pour une image embarquée.
- `questions.json` contient `{"schema_version":1,"rounds":[{"title":"...","kind":"image","answer":"HUMAN","media":"assets/monimage.jpg", ...}]}`.
- Pour une vidéo YouTube, mettez `kind:"video"`, `media:""`, et `media_url:"https://www.youtube.com/watch?v=..."` : la vidéo reste sur YouTube et n'est pas recopiée dans Blob.
- L'import vérifie les champs, le nombre de questions, la présence et la validité des médias, et le numéro de révision. Il remplace les `assets/...` par les URL publiques de Blob à l'enregistrement.
- La requête ZIP est limitée à **4 Mo** par Vercel ; les fichiers multimédias volumineux doivent être compressés ou déposés séparément.
- Une erreur ne publie **aucun deck incomplet**, mais des fichiers Blob déjà transférés peuvent rester orphelins si la sauvegarde finale échoue.

## 4. Mercato

Mercato lit et enregistre le même deck Supabase via l'URL IceBreaker configurée dans **Organiser → IceBreaker**. Nul besoin de redéployer Mercato après avoir modifié le deck sur Vercel. Les salles créées après la sauvegarde utilisent les nouvelles questions.

Si Mercato est ouvert au moment de l'import, utilisez **Recharger les questions sauvegardées** dans son éditeur. Les modifications non enregistrées doivent être exportées ou abandonnées pour éviter un conflit de version.

## 5. Sécurité, droit d'auteur et sauvegarde

- Le deck public est modifiable sans authentification spécifique, conformément à la configuration demandée. En production, protégez l'URL / le projet au niveau de l'hébergeur si nécessaire.
- Conservez une copie JSON des questions avant tout remplacement.
- Les liens d'images et les mentions d'attribution ne constituent pas une autorisation de rediffusion. Demandez la permission aux ayants droit pour utiliser les médias pendant le séminaire et a fortiori pour un déploiement public.
- Les réponses du jeu, anciennes salles et données du séminaire ne sont pas effacées par un import ZIP.
