# IceBreaker — ZIP de 6 questions à importer

Cette version conserve le gestionnaire global `/deck-manager`, l'import ZIP et les minuteries locales par question.

1. Déployer l'application mise à jour sur le projet Vercel **IceBreaker** existant.
2. Vérifier que `BLOB_READ_WRITE_TOKEN` et la base partagée sont configurés côté Vercel.
3. Ouvrir `/deck-manager` > Deck tools > **Import ZIP + media**.
4. Choisir `IceBreaker_Questions_6_Courtes_Import_Global.zip`, puis **Remplacer** si les six questions doivent constituer tout le deck.
5. Vérifier la prévisualisation de chaque média et ouvrir une **nouvelle salle** pour utiliser le deck actualisé.

**IMPORTANT :** le ZIP de questions comporte une vraie image incorporée (maquette Jira HD), un lien YouTube, et quatre références vers des photos originales hébergées chez leurs éditeurs. Les originaux de ces quatre photos ne sont pas inclus dans le ZIP. Le serveur essaie de les télécharger, puis de les stocker sur Vercel Blob. Si un éditeur bloque le téléchargement, l'import s'arrête et le deck enregistré reste inchangé. Pour le rendre totalement autonome, il faut obtenir les quatre photographies et les placer sous leurs noms `assets/...` dans ce même ZIP (droits à respecter), sans modifier le manifeste.

**Image Excel :** la photo de la scène panoramique Microsoft, non un portrait du gagnant. La source utilisée est la photo panoramique choisie dans le manifeste (`excel_arena_microsoft_2025`).

**Contenu :** chaque question comporte seulement un titre, une introduction courte, la réponse AI/HUMAN, une explication brève et une source. Les champs « Discussion » et « Lien technique » sont volontairement vides. La vidéo est diffusée avant le compte à rebours ; le choix des minuteries locales se fait dans le gestionnaire.
