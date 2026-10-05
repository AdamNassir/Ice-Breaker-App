# Question deck: private answer key and credits

Updated October 5, 2026. Ten rounds: **seven AI and three HUMAN**, eight images and two text articles. No audio/video rounds. The app interface, titles and short introductions are English; the Macron post and Teams messages are French. Origins come from documented production, not a detector.

Players judge the writing in social posts and only the **manager’s reply** in Teams. For photographs/paintings, judge image production. An authentic double exposure still counts as HUMAN. A plausible invented news story counts as AI because the agent wrote it, not merely because the story is false.

Every round shows its title, short introduction and content. Answer notes, origins, credits and highlight coordinates are withheld from live payloads. Reveals show AI or HUMAN; configured real photographs also show their subject, date and source. Posts have no extra reveal commentary. Inspector Gadget gets a red circle only at reveal.

## Current ten rounds

| Round | Subject | Origin | Provenance |
| --- | --- | --- | --- |
| 1 | LinkedIn roadmap satire | AI | Original AI-written fictional post; unchanged writing and image `sample18.png`. |
| 2 | Michael Jordan airborne | HUMAN | Steve Lipofsky / Basketballphoto.com, 1987–88 NBA season; original high-quality Commons JPEG `sample24.jpg`. |
| 3 | Employee-data SQL | AI | Original rewritten aggregate query, formatting reference: official PostgreSQL tutorial. `sample23.png` unchanged. |
| 4 | Tesla in his laboratory | HUMAN | Dickenson V. Alley, December 1899; historical double exposure, `sample16.jpg`. |
| 5 | Bitcoin dashboard incident | AI | Newly authored fictional English article. No genuine exchange notice or market event claimed. |
| 6 | Napoleon with Inspector Gadget | AI | Original generated imperial painting, `sample13.jpg`; unchanged painting and reveal circle. |
| 7 | Macron paperwork post | AI | Newly authored French parody, reconstructed X layout, visible name/handle and real unblurred portrait. `sample25.png`. Not a genuine post. |
| 8 | Ballon d’Or delivery tracker | AI | Newly authored fictional English sports article. No genuine leaked result, organiser quote or award winner claimed. |
| 9 | French internship handover on Teams | AI | Classify the manager’s reply only. Both messages and PDF attachment are fictional; simplified document-search request, mismatched aircraft-operations reply. `sample19.png`. |
| 10 | Moth logbook | HUMAN | U.S. Navy photograph of the Harvard Mark II logbook, September 9, 1947, `sample20.jpg`. |

## Authentic sports photograph — sample24.jpg

**Michael Jordan performing a tongue-out slam dunk.** Photographer: Steve Lipofsky / Basketballphoto.com. The source describes the Chicago Bulls, 1987–88, and dates it to the 1987 NBA season; it does not supply a precise match day. The reveal uses the season, not an invented day.

- [Source and high-quality file](https://commons.wikimedia.org/wiki/File:Jordan_by_Lipofsky_16577_(high_quality).jpg)
- [Original lower-resolution record](https://commons.wikimedia.org/wiki/File:Jordan_by_Lipofsky_16577.jpg)
- [CC BY-SA 3.0 Unported](https://creativecommons.org/licenses/by-sa/3.0/)

The bundled JPEG retains the downloaded source bytes, 1866 × 2340 pixels, SHA-1 `907435b3ef5832d0c284a9091c7da4bc77d4262f`, matching the source record. No crop, compositing or generative edit is applied. This is an authentic photograph, not a recreation of a sports image. The game shows its credit and source after the deadline.

## Other authentic photographs

**Tesla — sample16.jpg.** Dickenson V. Alley, December 1899, Colorado Springs laboratory. The [Commons record](https://commons.wikimedia.org/wiki/File:Tesla_colorado.jpg) identifies a historical double exposure and public-domain U.S. status. Tesla and the arcs were not captured together in one exposure. The bundled copy was resized/re-encoded, without generative additions.

**Moth logbook — sample20.jpg.** Courtesy Naval Surface Warfare Center, Dahlgren; U.S. Navy photograph. [Source and public-domain record](https://commons.wikimedia.org/wiki/File:First_Computer_Bug,_1947.jpg), [Smithsonian object](https://americanhistory.si.edu/collections/object/nmah_334663). The entry is September 9, 1947; older photo metadata sometimes says 1945. The word bug already existed. The bundled copy is 1500 × 1186, resized/re-encoded without generative editing.

## Macron parody and portrait — sample25.png

The French text is an **original AI-written fictional parody**, created October 5, 2026. It describes a supposedly simplified administrative form that still requires the twelve old forms. Emmanuel Macron did not supply or post these words. It is not a real screenshot, quote, policy announcement or accusation that he used AI.

The X-style interface is locally drawn by `build_question_images.py`. Name and `@EmmanuelMacron` are deliberately readable; no blur or pixelation is applied. The portrait is a real photograph, not a synthetic face. No invented timestamp or engagement totals are shown. Players classify **post writing**, not portrait origin.

Portrait credit: **Presidency of Bulgaria / President.bg**, December 4, 2017. [Source file](https://commons.wikimedia.org/wiki/File:Emmanuel_Macron_(04-12-2017).jpg), [CC BY 2.5 Bulgaria](https://creativecommons.org/licenses/by/2.5/bg/deed.en). The original 249 × 410 JPEG is bundled as `macron-profile-source.jpg`. The screenshot crops coordinates `(35, 24, 220, 209)` around the face, resizes to 80 × 80, and applies a circular mask. No face-generation or blur. The screenshot incorporates this attributed, licensed photograph alongside independently generated text.

## LinkedIn and French Teams reconstructions

Both are editable native interface reconstructions, not real account screenshots. LinkedIn writing/layout remain unchanged. Its invented identity/avatar stay blurred. The Teams layout follows [Microsoft’s combined Chat interface](https://support.microsoft.com/en-us/teams/teams-channels/explore-the-new-chat-and-channels-experience-in-microsoft-teams); no Microsoft screenshot pixels or actual employee messages are redistributed.

The French intern’s message describes a tool for questions over technical documents, useful passages, PDF reading, information organisation and testing. It asks the manager to validate `Bilan_Stage_Recherche_Documents.pdf`. The manager incorrectly interprets document search as monitoring aircraft, deciding repairs and switching propulsion. The messages use less technical vocabulary. Names/avatars remain anonymized, and the PDF is an attachment only; no document interior is displayed. The intro states: classify only the manager’s reply. This is fiction inspired by the supplied internship topics, not a record or claim about an actual colleague.

## Two plausible fictional news articles

Rounds 5 and 8 replace the former RFC excerpts and printer incident. Both are original English AI writing created October 5, 2026. They imitate short news reporting without impersonating an actual publication or adding fake source citations. All incidents and quoted snippets are invented. The Bitcoin story is not financial reporting; the Mbappé story is not an award result. Both reveal AI. No outside article is credited because neither is copied from one.

## SQL formatting reference — sample23.png

The original AI-written employee-data aggregate query uses the clause formatting of [PostgreSQL’s official tutorial: Aggregate Functions](https://www.postgresql.org/docs/current/tutorial-agg.html). Uppercase clauses, lowercase identifiers/functions, four-space clause indentation and a plain monospace block are preserved. It filters active employees, groups by department, keeps groups of at least five and sorts by average salary. The use case stays implied in table/column/filter names. The new neutral introduction asks who wrote the SQL, without narrating a separate scenario. The code image is unchanged and reveals AI only.

## Supplied logos and theme

The two original embedded PNGs from the user’s `Logos_To_Add.docx` are bundled unchanged: `static/branding/logiclever.png` (189 × 63) and `totalenergies.png` (400 × 225). No logo generation, tracing, recoloring or cropping. They appear in the player, presenter, standalone bonus and local manager; the presenter’s final ranking retains its placements-only layout.

The game’s blue `#1f2ade` is sampled from LogicLever. The UI red is `#e52330`. White/neutral backgrounds remain; gold/silver/bronze are reserved for medal/podium decoration. Original logo colors are preserved.

## Retained legacy media

Old assets remain available for older room snapshots/custom decks. They are not active questions. The motorcycle-football JPEG `sample15.jpg` credits **Bundesarchiv, Bild 102-12210 / CC-BY-SA 3.0 Germany**, August 1931; current Commons crop, JPEG re-encoding, no generative editing. [Source](https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_102-12210,_Fussballspiel_mit_dem_Motorrad.jpg), [license](https://creativecommons.org/licenses/by-sa/3.0/de/deed.en). Other retained camera/technical image credits are in `ContentSources_Legacy.md` and `ContentSources_Technical.md`.

`sample21.png` retains a reconstructed Trump Truth Social post dated May 16, 2025, [original](https://truthsocial.com/@realDonaldTrump/posts/114517718765768352), [archive](https://www.presidency.ucsb.edu/documents/truth-social-posts-may-16-2025). `sample22.png` retains the original AI-written English Trump-style firewall parody. Both identities were coarsely pixelated. Neither is used by this deck or rebuilt by the current default script. Removed RFC excerpts can still be added as custom HUMAN text with explicit source credits; their source-link feature remains supported.

### Legacy audio credit — not in the current deck

**Human voice.** Grace Hopper, *Future Possibilities: Data, Hardware, Software, and People*, delivered to the NSA on August 19, 1982 and publicly released in 2024. The Commons file identifies it as a public-domain U.S. government recording. The retained legacy file uses the original voice: **01:23:40.650–01:23:49.300** in the full Commons WebM (8.65 seconds). It is trimmed, downmixed to mono and encoded as 96 kbps MP3, with no synthetic speech or replacement words. Times refer to that full file, not separately uploaded parts.

- [Official NSA release](https://www.nsa.gov/helpful-links/nsa-foia/declassification-transparency-initiatives/historical-releases/view/article/3880193/capt-grace-hopper-on-future-possibilities-data-hardware-software-and-people-1982/)
- [Full recording, source and public-domain record](https://commons.wikimedia.org/wiki/File:Grace_Hopper_-_Future_Possibilities_-_Data,_Hardware,_Software,_and_People.webm)


## Generated images: full prompts

The remaining generated image was made with OpenAI's built-in image generation tool on October 4, 2026. No external CLI or paid API setup is required to play. The original PNG output was 1536 × 1024; the app uses a JPEG copy at that size, quality 91, without added generative edits. It is a fictional scene, not an authentic painting.

**sample13.jpg — Napoleon's unexpected guest**

> Use case: historical-scene. Asset type: one landscape image for an AI-or-HUMAN party quiz. Create an original oil painting evocative of a large early nineteenth-century French imperial ceremony: Napoleon in ornate coronation clothes, gathered clergy and aristocrats, rich crimson robes, elaborate gold architecture, huge painted canvas texture and aged varnish. Sneak Inspector Gadget into the middle-distance guests: recognizable grey trench coat, grey hat, long nose, one subtly extended mechanical arm, but render him in the same realistic oil-painted style. His figure should be findable on close inspection on a projector, about 8% of image height, not a giant cartoon foreground subject. Make the rest of the painting convincingly historical and spatially coherent. This is a humorous fictional scene, not a claim of an authentic painting. No captions, no logos, no watermark, no text. Landscape aspect ratio.


## Editing and installation

Use the local manager or edit questions.json and its Content.py fallback together. `build_question_images.py` rebuilds the LinkedIn, French Teams, SQL and French Macron cards. The source portrait is bundled, so no live download is needed to play or rebuild. Deploy both deck files, updated frontend files and all new assets; create a new room, since existing rooms retain their original deck snapshots. Exact files and checks are in UpdateGuide.md.
