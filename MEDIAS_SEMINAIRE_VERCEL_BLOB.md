# IceBreaker — lecture des médias LogicLever publiés sur Vercel Blob

Le jeu valide à présent les URLs immuables de Vercel Blob dans `media` et `reveal_media` des decks transmis par la régie Organizer. Les URLs sont limitées à HTTPS, aux domaines `*.public.blob.vercel-storage.com`, aux chemins `/icebreaker/images/`, `/icebreaker/audio/`, `/icebreaker/videos/` et aux extensions autorisées pour le média correspondant.

Le jeu n'a **pas** besoin de connaître `BLOB_READ_WRITE_TOKEN` : les médias sont publiés par le serveur LogicLever, qui garde le jeton côté serveur. Le jeu lit les fichiers publics directement dans le navigateur des joueurs. Les fichiers déjà distribués dans `static/` fonctionnent toujours comme auparavant.

Pour activer le flux, déployez une fois cette version du jeu sur Vercel, créez un magasin Blob **public**, puis configurez son token dans **Organiser → IceBreaker** de l'application LogicLever mise à jour. Aucun nouveau déploiement n'est nécessaire lorsque l'organisateur ajoute des images ou modifie les questions.

Il n'y a aucun endpoint d'upload anonyme sur IceBreaker. Les salles existantes continuent à utiliser le deck enregistré lors de leur création ; pour refléter les dernières questions, créez une nouvelle salle.
