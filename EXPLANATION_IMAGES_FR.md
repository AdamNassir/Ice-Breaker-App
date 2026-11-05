# Image dans l’explication d’une question

- Dans `/deck-manager`, ouvrir une question > « Answer notes and source » > « Upload explanation image ».
- Enregistrer le deck après l’envoi. L’image est enregistrée dans Vercel Blob.
- L’image et l’explication ne sont envoyées aux participants qu’à la révélation de la réponse. Aucune image explicative n’est chargée pendant le vote.
- Dans Mercato > Organiser > IceBreaker, les mêmes champs sont disponibles. Le média privé est publié dans Blob au moment de la sauvegarde.
- Dans un ZIP d’import, on peut déclarer `"explanation_image":"assets/explanation.png"` dans une question et `"assets/explanation.png":{}` dans `manifest.json`, puis inclure le fichier `assets/explanation.png`. La validation et le remplacement se font avec les autres médias.
- Ne pas confondre avec `reveal_media` : ce dernier remplace la photo de l’énoncé d’une question de type image, alors que `explanation_image` fonctionne avec tous les formats.
