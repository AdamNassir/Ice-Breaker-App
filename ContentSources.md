# English fun deck: private answer key and credits

Rebuilt October 4, 2026. Ten rounds: five AI and five HUMAN; four images, two texts, two voices and two videos. All prompts, questions and reveals are in English. These are known-origin examples, not detector verdicts. The previous technical deck's sources remain in `ContentSources_Technical.md`; older credits remain in `ContentSources_Legacy.md`.

## Explain the rule before play

AI means the writing, image, voice or footage was generated. HUMAN means people wrote, painted, photographed or recorded it. A human-made joke, staged photo or double exposure still counts as HUMAN. For audio, judge the **voice**, independently of the script. For video, judge the **footage**: a robot filmed by people can be HUMAN content. This definition is about production, not whether a depicted event is plausible.

Each reveal gives a source and a quick discussion question. Strangeness is a decoy: human originals can be ridiculous, and generated originals can look ordinary. There is no claim of a measured difficulty curve.

## Rounds and provenance

| # | Title | Origin | Evidence and changes |
| --- | --- | --- | --- |
| 1 | My AI agent deleted the roadmap | AI | Original AI-written professional-network satire created for this game on October 4, 2026. Fictional founder; no real person's post, quotation, screenshot or endorsement. |
| 2 | The football upgrade nobody asked for | HUMAN | German Federal Archives photograph, August 1931; motorbike football. `sample15.jpg`: current Commons crop, re-encoded as JPEG without generative editing. |
| 3 | The voice behind the demo | AI | Official Alloy synthesized voice example embedded in OpenAI's text-to-speech guide. Approximately seven seconds, linked from its original WAV host. No local copy distributed. |
| 4 | Perfectly normal office lighting | HUMAN | Dickenson V. Alley's Tesla laboratory photograph, December 1899. Historical double exposure; resized/re-encoded, no generative editing. `sample16.jpg`. |
| 5 | A network with feathers | HUMAN | David Waitzman's RFC 1149, April 1, 1990. Two exact sentences from Frame Format, separated by a visible omission marker; 21 quoted words. No translation. |
| 6 | An unexpected guest at the coronation | AI | Original generated imperial ceremony with an Inspector Gadget cameo, October 4, 2026. Historical pastiche, not an altered museum original. `sample13.jpg`. |
| 7 | The family IT department | HUMAN | Grace Hopper's authentic English lecture voice, August 19, 1982. She jokes about a parent applying to his children for computer time. `sample17.mp3`, excerpt described below. |
| 8 | The new hire seems qualified | AI | Original generated fictional 1960s mainframe team photograph with a cat in a tie, October 4, 2026. `sample14.jpg`. |
| 9 | The robots have better moves than us | HUMAN | Boston Dynamics' official camera footage of real dancing robots, December 29, 2020. YouTube embed, 00:00–00:18. Footage is the object of classification. |
| 10 | The astronaut took the scenic route | AI | Official Runway Gen-3 Alpha demo, June 17, 2024. Its source explicitly identifies the page's videos as generated. Linked MP4, 00:00–00:10; original watermark retained. |

### Historical photos: credit and licenses

**Motorcycle football — sample15.jpg.** Credit: Bundesarchiv, Bild 102-12210 / CC-BY-SA 3.0 Germany. Photographer not recorded. Date: August 1931. The current Commons upload has a small crop documented in its file history; the app copy is re-encoded as JPEG. This derivative remains under the same license.

- [Archive image and file history](https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_102-12210,_Fussballspiel_mit_dem_Motorrad.jpg)
- [CC BY-SA 3.0 Germany, English deed](https://creativecommons.org/licenses/by-sa/3.0/de/deed.en)

**Tesla — sample16.jpg.** Credit: Dickenson V. Alley, December 1899, Tesla's Colorado Springs laboratory. The Commons record identifies this as a double exposure and public domain in the United States. The two exposures do not show Tesla sitting beside active arcs in one instant. The app copy is resized/re-encoded; no new characters or arcs were added.

- [Source, explanation and public-domain record](https://commons.wikimedia.org/wiki/File:Tesla_colorado.jpg)

### Voice sources

**AI voice.** The [official text-to-speech guide](https://developers.openai.com/api/docs/guides/text-to-speech) embeds the Alloy voice example at `https://cdn.openai.com/API/docs/audio/alloy.wav`. The game uses that original-host link. No local copy, API call, paid key or runtime speech generation occurs. Retrieved October 4, 2026. The recording is in English.

**Human voice.** Grace Hopper, *Future Possibilities: Data, Hardware, Software, and People*, delivered to the NSA on August 19, 1982 and publicly released in 2024. The Commons file identifies it as a public-domain U.S. government recording. The app excerpt uses the original voice: **01:23:40.650–01:23:49.300** in the full Commons WebM (8.65 seconds). It is trimmed, downmixed to mono and encoded as 96 kbps MP3, with no synthetic speech or replacement words. Times refer to that full file, not separately uploaded parts.

- [Official NSA release](https://www.nsa.gov/helpful-links/nsa-foia/declassification-transparency-initiatives/historical-releases/view/article/3880193/capt-grace-hopper-on-future-possibilities-data-hardware-software-and-people-1982/)
- [Full recording, source and public-domain record](https://commons.wikimedia.org/wiki/File:Grace_Hopper_-_Future_Possibilities_-_Data,_Hardware,_Software,_and_People.webm)

### Text and video sources

- [RFC 1149, original publication](https://www.rfc-editor.org/rfc/rfc1149.html). The app selects two short sentences with a marked omission; it does not rewrite them. The fictional founder's post is original AI-written content, not copied from LinkedIn. Style alone does not establish a real person's use of AI.
- [Boston Dynamics: Do You Love Me?](https://www.youtube.com/watch?v=fn3KWM1kuAw). Official upload; embed-only excerpt. No video or music is redistributed in the archive. AI/HUMAN refers to recorded versus generated footage, not whether the robots use machine learning.
- [Runway: Introducing Gen-3 Alpha](https://runway.com/research/introducing-gen-3-alpha). The page labels all its example videos as generated outputs. The selected file is `carousel-01/gen-3-alpha-output-002.mp4`, the astronaut running through a Rio de Janeiro alley. It remains on Runway's host; the archive contains only its playback URL.

## Generated images: full prompts

Both images were made with OpenAI's built-in image generation tool on October 4, 2026. No external CLI or paid API setup is required to play. Original PNG outputs were 1536 × 1024; the app uses JPEG copies at that size, quality 91, without added generative edits. The originals are fictional scenes. Do not describe either as a recovered historical photograph or authentic painting.

**sample13.jpg — Napoleon's unexpected guest**

> Use case: historical-scene. Asset type: one landscape image for an AI-or-HUMAN party quiz. Create an original oil painting evocative of a large early nineteenth-century French imperial ceremony: Napoleon in ornate coronation clothes, gathered clergy and aristocrats, rich crimson robes, elaborate gold architecture, huge painted canvas texture and aged varnish. Sneak Inspector Gadget into the middle-distance guests: recognizable grey trench coat, grey hat, long nose, one subtly extended mechanical arm, but render him in the same realistic oil-painted style. His figure should be findable on close inspection on a projector, about 8% of image height, not a giant cartoon foreground subject. Make the rest of the painting convincingly historical and spatially coherent. This is a humorous fictional scene, not a claim of an authentic painting. No captions, no logos, no watermark, no text. Landscape aspect ratio.

**sample14.jpg — The cat at the mainframe**

> Use case: photorealistic-natural. Asset type: one landscape image for an AI-or-HUMAN party quiz. Create a convincingly old 1960s black-and-white press photograph of a computer training room: six serious office workers in suits, big mainframe cabinets, neatly routed cables, paper tape reels, desk terminals. One deadpan tabby cat sits upright in a little chair at the central terminal with its forepaws naturally resting on the keyboard, wearing a very small dark tie, as though it belongs in the team photograph. The workers look studiously unimpressed. Candid archival photograph, subtle film grain, mild flash, ordinary messy room, imperfect framing. Make the absurdity funny yet the physical details plausible. One cat only. No readable signs, no invented gibberish lettering, no captions, no watermark. Landscape aspect ratio.

## Game inspiration and event notes

[Sightengine's AI or Not](https://www.sightengine.com/ai-or-not) uses a simple real/generated choice across images, voices and videos. [Realdle](https://www.realdle.com/) encourages comparing plausible real and generated images. This deck borrows the quick choice and visual surprise; it adds a presenter-controlled reveal, humorous sources and discussion. It does not copy those games' assets or code.

The four images and Hopper clip are bundled locally. **Three rounds need internet:** Alloy audio, the Boston Dynamics YouTube embed, and Runway's MP4. Online hosts can change links; YouTube can show branding, titles, ads or restrictions, and the Runway watermark can be a clue. Rehearse the entire deck on the event connection. Those clues are retained rather than hidden through unauthorized downloads or watermark removal. Replace a blocked round in the local manager before the event.

Start the round, then press Play: voting timers do not wait for media playback. Use the projector's audio for the room; phone playback is optional. The short excerpts leave time to vote. Keep this answer-key file outside `static/` and your source repository private if participants should not inspect it.
