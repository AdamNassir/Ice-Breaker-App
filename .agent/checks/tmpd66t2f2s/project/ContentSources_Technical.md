# Technical deck: provenance, difficulty and presenter notes

**Answer key — keep outside `static/`.** This file is for the presenter, not the phone interface.

The deck contains ten independent AI/HUMAN decisions: two commits, five code excerpts, two electronics images and one incident note. Five originals are AI-generated and five are historical human material. Do not announce the balance or imply that similarly themed samples must have opposite labels.

The five difficulty levels describe increasing reading demands, engineering depth and deliberate imitation. They are editorial choices, not measured detection probabilities. A photo can fool a hardware expert earlier than a concurrency snippet fools a generalist. Rehearse with a few colleagues; adjust the timers or move a whole dictionary in `Content.py` if your audience finds a particular round unusually easy.

## Design inspiration

These projects informed the format, not the answer key or borrowed samples:

- **Human or Not?** (AI21 research, 2023): a brief anonymous interaction followed by a binary origin judgment. We borrow the time pressure and imitation premise, using fixed technical artifacts instead of live chat. Paper: https://arxiv.org/abs/2305.20010 .
- **Which Face Is Real?** (University of Washington): human and generated images from documented collections, with subject-matched comparison. We use independently voted electronics images with similar workshop subject matter. Methods: https://www.whichfaceisreal.com/methods.html .
- **Real or Not Quiz** (Microsoft research): a mixed collection of camera and generated images. We borrow variety and short decisions, while revealing provenance and the engineering discussion after every round. Research: https://www.microsoft.com/en-us/research/publication/how-good-are-humans-at-detecting-ai-generated-images-learnings-from-an-experiment/ .

The difficult AI examples imitate specific, competent engineering work rather than generic prose or deliberately broken code. Roughness, correctness, jargon and humor are not reliable authorship rules. For code/text rounds, classify the original authorship of the shown artifact; a model could later reproduce a human original from training. For images, classify camera capture versus image generation. Routine resizing and compression preserve that origin.

## The progression (contains answers)

| Round | Level | Topic / format | Origin | Timer | Reveal discussion |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 — Warm-up | Unicode casefold/NFC commit | AI | 30s | Named edge cases can be generated; normalization and folding are different operations. |
| 2 | 1 — Warm-up | CPython rejection sampling | HUMAN | 30s | A real implementation trades some efficiency for simplicity; modulo introduces bias in general. |
| 3 | 2 — Inspection | Hand-assembled electronics photo | HUMAN | 35s | An odd solder joint is not evidence of image generation. |
| 4 | 2 — Inspection | Generated prototype photo | AI | 35s | Ordinary workshop imperfections can be requested in a prompt. |
| 5 | 3 — Subtle behavior | Async cancellation commit | HUMAN | 40s | Exception inheritance changes cancellation control flow. |
| 6 | 3 — Subtle behavior | PostgreSQL job claiming | AI | 45s | Atomic claiming is different from exactly-once external effects. |
| 7 | 4 — Concurrency | C++ SPSC acquire/release handoff | AI | 55s | Correct memory ordering does not establish human authorship or lock-free progress. |
| 8 | 4 — Concurrency | Go mutex waiter wake-up | HUMAN | 55s | CAS and a packed state coordinate wake ownership; terse bit arithmetic has a purpose. |
| 9 | 5 — Expert | Redis reversed-bit scan cursor | HUMAN | 60s | An unfamiliar production algorithm can look invented; duplicates are allowed. |
| 10 | 5 — Expert | Stale-writer/fencing incident | AI | 60s | A convincing operational timeline can be fictional; fencing needs destination enforcement. |

Voting timers total **445 seconds (7 minutes 25 seconds)**. Allow roughly 12–18 minutes including joins, reveals and discussion. The presenter still starts each timer and advances manually. Per-round `seconds` override the room's initial timer slider. Remove those keys to use one uniform room timer instead.

## Human originals and transformations

### Round 2 — CPython

- Source: https://raw.githubusercontent.com/python/cpython/v3.5.0/Lib/random.py .
- Browsable source: https://github.com/python/cpython/blob/v3.5.0/Lib/random.py#L229-L233 .
- Exact five-line selection from `_randbelow`, lines 229–233; remove twelve leading spaces, preserving comments and remaining whitespace.
- License: PSF; retain `licenses/CPython-LICENSE.txt`.
- SHA-256 of fetched complete source: `a6ac95976f92ecf1da52433a78e2cbcca099c0e114d209de25949e0d30c41331`.

### Round 3 — camera image

- Photographer: **Jguarin**. File: *Circuit Board 2015.jpg*. The filename is not the capture date: the description gives **February 23, 2014**; Commons first upload is **August 26, 2016**.
- Original file page: https://commons.wikimedia.org/wiki/File:Circuit_Board_2015.jpg .
- Original bytes: https://upload.wikimedia.org/wikipedia/commons/9/91/Circuit_Board_2015.jpg .
- License: **CC BY-SA 4.0**, https://creativecommons.org/licenses/by-sa/4.0/ . The bundled resized derivative `static/images/sample11.jpg` remains under that license. Keep the author, original link, license and modification notice when redistributing this image.
- Transformation: resized from 2592×1944 to 1440×1080, JPEG quality 88, original metadata omitted. No generative edits or selective image changes.
- SHA-256 of downloaded original: `eebda37be58f9d8b5d8a32ddfbee59031699a84e5e36ba3f0cc5243108b53ea5`.

### Round 5 — CPython cancellation commit

- Author: **Yury Selivanov**, **May 27, 2019**.
- Commit: https://github.com/python/cpython/commit/431b540bf79f0982559b1b0e420b1b085f667bb7 .
- Retrieved patch/message: https://github.com/python/cpython/commit/431b540bf79f0982559b1b0e420b1b085f667bb7.patch .
- Transformation: omit the subject's `bpo-32528:` prefix and `(GH-13528)` suffix; retain the first two body paragraphs and omit the final paragraph. Remaining wording/capitalization/line breaks are preserved.
- License: CPython PSF license; retain `licenses/CPython-LICENSE.txt`.
- SHA-256 of downloaded complete patch: `984d3cde369e3dcc985fb88781c3bc626e082f4d8f7353745e600489ff3f6b59`.

### Round 8 — Go mutex

- Original: https://raw.githubusercontent.com/golang/go/go1.9/src/sync/mutex.go .
- Browsable source: https://github.com/golang/go/blob/go1.9/src/sync/mutex.go .
- Historical Go 1.9 (2017), `Mutex.Unlock` normal-mode wake-up loop. Selected statements from the no-waiter/flag check through `old = m.state`; preceding explanatory comment block, surrounding loop and three leading indentation tabs omitted. The displayed `// Grab the right to wake someone.` comment is original.
- License: BSD 3-Clause; retain `licenses/GO-LICENSE.txt`. No modern AI-edited repository head is substituted for the tagged source.
- SHA-256 of complete source: `a2622b7f9abf98138d14c957d6093ce517b02f3b8203ef007dedd2d564a9259e`.

### Round 9 — Redis cursor

- Original: https://raw.githubusercontent.com/redis/redis/3.2.13/src/dict.c .
- Browsable source: https://github.com/redis/redis/blob/3.2.13/src/dict.c .
- Historical Redis 3.2.13 (2019), contiguous selection in `dictScan`'s non-rehashing branch from `de = t0->table[v & m0];` through the second `v = rev(v);`. Eight leading spaces and surrounding control flow omitted; comments retained.
- Release date verified from the tagged release notes: March 18, 2019; https://raw.githubusercontent.com/redis/redis/3.2.13/00-RELEASENOTES .
- Algorithm credited in the source to **Pieter Noordhuis**.
- License of this historical release: BSD 3-Clause; retain `licenses/REDIS-LICENSE.txt`.
- SHA-256 of complete tagged source: `68c9f3e5e657e2b290af4bb7424d19b984d830b25c4c73735b070d7cb720f67a`.
- Technical reference: https://redis.io/docs/latest/commands/scan/ .

Source hashes identify the inspected bytes; they are not authorship detectors.

## AI originals

Rounds 1, 6, 7 and 10 were written by the AI assistant on October 2, 2026 for this request. They are original fictional examples rather than copied commits or reported incidents. No precise text-model version was exposed, so none is asserted.

Writing brief: produce concise engineering artifacts whose specificity and correctness invite a human guess; include Unicode canonical equivalence, PostgreSQL queue claiming, a correctly ordered SPSC handoff, and an incident timeline involving stale lease holders. Include explicit assumptions for code and avoid claiming that code style establishes origin. The exact delivered artifacts are the `body` strings in `Content.py`.

Technical references used to check reveal explanations (these did **not** author the AI samples):

- Python normalization: https://docs.python.org/3/library/unicodedata.html ; casefold: https://docs.python.org/3/library/stdtypes.html#str.casefold .
- PostgreSQL row locks/SKIP LOCKED: https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE ; UPDATE/RETURNING: https://www.postgresql.org/docs/current/sql-update.html .
- C++ acquire/release and data races: https://eel.is/c++draft/atomics.order ; https://eel.is/c++draft/intro.races .
- Fencing discussion: Martin Kleppmann's original explanation, https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html . The fictional incident is not a quotation or a claim about a real outage.

### Round 4 — exact image-generation prompt

Generated using the **built-in OpenAI image-generation tool**, October 2, 2026. A stable model-version identifier was not exposed. The output was resized to 1440×1080 and re-encoded at JPEG quality 88 as `static/images/sample12.jpg`. No human image was supplied to the tool as a reference or edit target.

```text
Use case: photorealistic-natural
Asset type: one technical image round in an AI-versus-human guessing game for engineers.
Primary request: a mundane handheld camera photograph of the solder side of a small hand-assembled electronics prototype on green perforated circuit board, resting on a stained, slightly creased sheet of off-white workshop paper.
Subject: plausible real-world point-to-point solder wiring, uneven but credible solder joints, thin tinned copper wires joining selected pads, minor flux residue, clipped leads, a few insulated jumper wires visible near an edge. The physical wiring should look like patient human bench work rather than a patterned machine design.
Composition/framing: landscape 4:3, close-up viewed obliquely from above, board fills most of the frame, slightly off-center, one edge gently out of focus; no people, no hands. Show small imperfections of framing and focus rather than dramatic composition.
Lighting/mood: ordinary indirect daylight and indoor workshop light, realistic mild shadows; modest camera dynamic range, subtle sensor noise, low-key everyday documentation photograph.
Constraints: no legible text, no labels identifying origin, no logos, no watermark, no artificial red/blue lighting, no futuristic hardware, no cinematic bokeh, no arrows or graphic overlays. Make a believable unglamorous electronics photograph with internally plausible geometry. This is an AI-produced fictional board; do not imitate a named person's particular photograph.
```

## Facilitation and editing

Read each neutral context aloud if the room needs it. After reveal, discuss the engineering point briefly and ask which clue influenced the vote. Ask for reasoning before opening the provenance link. Technical skill should make the debate better; it does not provide a dependable authorship test.

Edit complete dictionaries in `Content.py`. Keep `context` free of author names, repository names, dates, model names or origin hints. Keep provenance and technical explanations in the reveal-only fields. Neutral asset filenames prevent labels from leaking through the player URL. New rooms snapshot the deck, so create a fresh room after redeploying.

The original four imagery assets remain in `static/images/` as optional replacements: `sample03.jpg` and `sample10.jpg` are AI-generated; `sample04.jpg` and `sample09.jpg` are NASA camera photographs. They are not used by the revised default deck. Original credits: NASA/Buzz Aldrin AS11-40-5878 (1969), https://science.nasa.gov/resource/apollo-11-bootprint/ ; NASA/Apollo 17 AS17-148-22727 (1972), https://science.nasa.gov/resource/the-blue-marble/ .

Full provenance and generation prompts for the optional old assets are retained in `ContentSources_Legacy.md`. That file also records the retired text/code samples; it is a private archival answer key, not the current deck.
