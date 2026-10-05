# Layout references — active deck

These are interface references, not sources for the fictional question writing. Truth Social is not used by the active deck.

| Question | Reference | Local implementation |
| --- | --- | --- |
| LinkedIn Post by a Manager | Presenter-supplied `image.png`: LinkedIn post by Kate Nazarova. No original post URL was supplied. The reference is included as `layout_sources/linkedin-reference.png`. | `build_question_images.py` → `linkedin()` → `sample18.png`. Post-only white card, identity block, Follow control, reaction row and four action columns. Fictional writing; identities blurred. |
| Macron Post About AI in Hospitals | Presenter-supplied `image(1).png`: X dark-mode post view. Included as `layout_sources/x-reference.png`. The separate `image(3).png` supplies the actual Macron profile picture. | `build_question_images.py` → `tweet(..., macron=True)` → `sample27.png`. Dark post view, original French quiz writing, readable Macron identity and supplied photo. |
| Teams Conversation With an Internship Manager | [Microsoft Support: Explore the new chat and channels experience](https://support.microsoft.com/en-us/teams/teams-channels/explore-the-new-chat-and-channels-experience-in-microsoft-teams), Combined view screenshot. | `build_question_images.py` → `teams()` → `sample19.png`. Combined Chat view, attachment-only conversation, Adam’s blurred sender name with a right-aligned blue document message, and the anonymized manager’s left-aligned grey reply; original French messages. The official screenshot shows the list/sidebar, not an entire conversation window. |
| Both French news articles | [Le Parisien article page, February 5, 2026](https://www.leparisien.fr/economie/le-bitcoin-passe-sous-la-barre-des-70-000-dollars-pour-la-premiere-fois-depuis-lelection-de-donald-trump-05-02-2026-FT7ITOQKI5DETKSOQUDIZPQNRA.php); [AREA 17’s full-page 2018–2019 design reference](https://area17.com/clients/le-parisien); [Le Parisien logo SVG](https://commons.wikimedia.org/wiki/File:Le_Parisien_logo.svg). | `static/newsarticle.js` + `static/newsarticle.css`, shared with manager preview. Full native page: official vector masthead logo, French navigation/local strip, headline/chapo/byline, article column, sidebar, related stories and footer. Article writing is original French fiction; neighbouring cards now use actual recent news photographs and paraphrased titles, detailed below. `static/branding/publication.svg` preserves the actual logo bytes. No article screenshot is used. |
| SQL Query for Employee Data | [PostgreSQL tutorial, section 2.7: Aggregate Functions](https://www.postgresql.org/docs/current/tutorial-agg.html). | `build_question_images.py` → `code_card()` → `sample23.png`. Commented two-CTE query with four tables and FILTER pivot-style columns. Clause indentation and monospace presentation follow the tutorial and [WITH Queries](https://www.postgresql.org/docs/current/queries-with.html). Original AI rewrite, not copied source code. |

## Copying and verification scope

The French article page is a full HTML/CSS reconstruction, rather than a cropped header or article screenshot. The logo asset is copied unchanged from [its source SVG](https://upload.wikimedia.org/wikipedia/commons/2/27/Le_Parisien_logo.svg), credited to Le Parisien on Commons. It is not a generated or redrawn logo. The former New York Post screenshot asset is removed and no longer referenced.

The official article supplies the page structure, French navigation and headline/chapo/byline ordering. AREA 17, the site’s designer, supplies a whole-page visual reference dated 2018–2019. This is explicitly a dated reference, not proof of the current site's precise CSS. The direct official HTML download was unavailable; the accessible primary-source page and designer imagery were inspected. The implementation recreates the complete shell but does not copy the publisher’s live DOM, proprietary fonts, tracking, advertisements or subscription functionality. Apparent navigation/account/share controls are decorative spans and do not send players away from voting. The two central stories are fictional. Neighbouring card titles paraphrase actual recent stories; only their photographs are copied. The requested mock bylines borrow verified journalist names and decorative dates; neither journalist authored these fictional stories. No invented engagement counts are shown.

The page is independently scrollable and responds to its embedded width; the timer and voting controls stay active. Scroll position persists through polling and reveal, then resets for a new article. The manager previews the same page. Public question text is rendered with textContent; private provenance stays out of live payloads.

LinkedIn, X and Teams use the unchanged references above. None of the native page/card reconstructions, including Le Parisien, has been proven pixel-identical. Article typography uses available system fonts; the publisher’s licensed fonts are not bundled. Native Chromium could not launch, so visual screenshot comparison is unavailable here. The exact-copy requirement remains open for viewport-matched browser comparison; do not describe this release as proven pixel-identical. No Truth Social layout is used by the active deck.

## Recent neighbouring article photographs — checked October 5, 2026

The following original JPEGs are bundled unchanged and rendered with CSS object-fit: cover in the sidebar and related-story cards. They are editorial source photographs, not generated illustrations or the subject of the AI/HUMAN vote. The central article text remains fiction.

| File | Source story/date | Observed credit |
| --- | --- | --- |
| `static/news/housing.jpg` | [Le Parisien Étudiant: APL increase](https://www.leparisien.fr/etudiant/vie-etudiante/logement-etudiant/logement-les-apl-augmentent-qui-peut-en-beneficier-et-comment-R3KYOHWRHJE6POB3WCDMMXWDTA.php), October 5, 2026 | LP / Stéphanie Forestier |
| `static/news/ai.jpg` | [Le Parisien: three OpenAI researchers dismissed](https://www.leparisien.fr/high-tech/ils-partageaient-leurs-inquietudes-sur-les-dangers-de-lia-trois-chercheurs-renvoyes-dopenai-qui-les-accuse-de-fuites-02-10-2026-P7VZOH3X7VEZHJ6CTFT3KY6G6A.php), October 2, 2026 | REUTERS / Carlos Barria, file photo |
| `static/news/football.jpg` | [Le Parisien: Zidane before France-Belgique](https://www.leparisien.fr/sports/football/equipe-de-france/france-belgique-je-suis-un-peu-frustre-parce-que-ca-va-sarreter-regrette-zinedine-zidane-04-10-2026-U7TGT27JZZB3XFFONQXO3NMIHM.php), October 4, 2026 | AFP / Franck Fife |

Original image URLs:

- housing: https://cloudfront-eu-central-1.images.arcpublishing.com/leparisien/5VBDC4GODVE4PJEJK2WVVLNL64.jpg
- ai: https://cloudfront-eu-central-1.images.arcpublishing.com/leparisien/5RUIJZZU3ZG5RDTCDVGX7BQUM4.jpg
- football: https://cloudfront-eu-central-1.images.arcpublishing.com/leparisien/CNDBUAFX45GOJFMTFA25BXDGDQ.jpg

Byline name references: [Sébastien Lernould](https://www.leparisien.fr/auteur/sebastien-lernould/) and [Dominique Sévérac](https://www.leparisien.fr/auteur/dominique-severac/). Names are used only in the requested fictional quiz presentation; the private provenance expressly states that they did not author either story. Static local photographs work without remote hotlinking; no additional cookies, trackers or external embeds are introduced.
