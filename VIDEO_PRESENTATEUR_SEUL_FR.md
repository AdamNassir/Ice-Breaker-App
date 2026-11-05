# Lecture vidéo uniquement sur le présentateur

- Pendant une question vidéo, seul le présentateur charge la vidéo (locale ou YouTube).
- Sur les téléphones, l'API des participants n'envoie plus `media`, `media_url`, `media_start`, `media_end` pour la question vidéo. L'écran n'ajoute aucun lecteur, bouton de lecture ou pause vidéo.
- La vidéo est diffusée sur l'écran présentateur. Le vote commence lorsque le lecteur annonce sa fin au serveur.
- L'autoplay peut être bloqué par le navigateur ; seul le présentateur a le bouton Play / Resume. Il existe un contrôle de secours « Start voting » si nécessaire.
- Les images normales restent visibles sur les téléphones ; seul le format « video » est affecté.
- Le serveur doit être redéployé sur Vercel pour que ces garanties s'appliquent.

## Vidéo Microsoft Surface 2025
Vidéo officielle (chaîne Microsoft Surface) : https://www.youtube.com/watch?v=9SWEA2y2DjQ
Article Microsoft expliquant la production hybride : https://microsoft.design/articles/we-made-an-ad-with-generative-ai/

Le fichier MP4 n'est pas inclus dans ce ZIP, et YouTube ne fournit pas ici un fichier à importer dans Vercel Blob. Pour remplacer le lien YouTube par un fichier, demandez un MP4 réutilisable à Microsoft / un détenteur des droits et téléversez-le dans le gestionnaire de médias IceBreaker.
