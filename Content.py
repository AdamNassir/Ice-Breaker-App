"""Bundled starter deck. Run python question_manager.py to edit questions visually.

The manager saves questions.json; that file takes priority over these ROUNDS.
Advanced users can edit this fallback directly when questions.json is absent.

kind: commit | code | text | image | audio | video; answer: AI | HUMAN (server-only).
difficulty: 1..5, an editorial reading/deception level, not a measured detection rate.
context: neutral setup visible before voting; seconds: optional round timer (5..120).
technical_note and discussion: visible only after the answer is revealed.
source/source_url: actual origin. technical_source_url: explanatory reference only.
Human excerpts preserve source text except documented omissions/outer indentation.
AI means generated original content; camera photos count as HUMAN.
"""

ROUNDS = [
    {
        "title": "The key that would not match", "kind": "commit", "difficulty": 1, "seconds": 30,
        "context": "Commit message from a search-index change. Judge who wrote it, not whether you agree with the fix.",
        "body": 'fix(search): re-normalize keys after casefold\n\nU+01F0 casefolds to "j" + COMBINING CARON.\nThe folded result is not NFC, even if the input was.\n\nNormalize the folded key before writing it to the index.\nDisplay text stays untouched. NFC, not NFKC: compatibility\nfolding would merge distinctions we still expose in identifiers.',
        "answer": "AI",
        "explanation": "Generated for this game. The concrete Unicode edge case and the restrained scope were deliberately included to sound like a maintainer explaining a real patch.",
        "technical_note": "U+01F0 is LATIN SMALL LETTER J WITH CARON. Its casefolded form contains two code points and is not NFC; normalizing afterward recomposes it. NFC preserves canonical equivalence, while NFKC also collapses compatibility distinctions. This is a technically plausible commit, not an intentionally broken one.",
        "discussion": "Did the named edge case feel like evidence that the author had debugged a production incident?",
        "source": "AI assistant, original fictional commit written for this deck, October 2, 2026. No repository or incident is claimed.",
        "technical_source_url": "https://docs.python.org/3/library/unicodedata.html",
    },
    {
        "title": "A suspicious extra loop", "kind": "code", "difficulty": 1, "seconds": 30,
        "context": "Python excerpt. n is a positive integer; getrandbits(k) returns a uniformly sampled k-bit integer.",
        "body": "k = n.bit_length()  # don't use (n-1) here because n can be 1\nr = getrandbits(k)          # 0 <= r < 2**k\nwhile r >= n:\n    r = getrandbits(k)\nreturn r",
        "answer": "HUMAN",
        "explanation": "This is the original rejection-sampling branch of CPython 3.5.0's _randbelow, with only outer indentation removed. Its small inefficiency at powers of two is real historical code.",
        "technical_note": "Taking r % n would bias the output unless n divides 2**k. Rejecting values at least n keeps the accepted results uniform. When n is a power of two, n.bit_length() draws one extra bit, so half the candidates are rejected; that is a performance observation, not an authorship test.",
        "discussion": "Did you interpret the apparently unnecessary loop or defensive comment as an AI tell?",
        "source": "Python/CPython contributors, v3.5.0 (2015), Lib/random.py, lines 229–233. PSF license; surrounding setup omitted.",
        "source_url": "https://github.com/python/cpython/blob/v3.5.0/Lib/random.py#L229-L233",
    },
    {
        "title": "Bench inspection / A", "kind": "image", "difficulty": 2, "seconds": 35,
        "context": "Workshop image. Inspect solder joints, wire routes and board geometry. Choose the image's origin.",
        "media": "/static/images/sample11.jpg", "alt": "The solder side of an electronics prototype with wires and uneven solder joints on a work surface.",
        "image_fit": "contain", "image_position": "center", "answer": "HUMAN",
        "explanation": "Jguarin's camera photo, taken in 2014 and uploaded to Wikimedia Commons in 2016. It has been resized and JPEG-compressed for this app. The historical file record establishes the origin.",
        "technical_note": "Hand-built prototypes often have improvised wire routing, uneven joints and residue. Those are ordinary manufacturing details; an odd-looking joint is not sufficient evidence of generation. A single view also cannot prove the electrical continuity of every connection.",
        "discussion": "Which physical detail made you trust or doubt this board, and could that detail be deliberately synthesized?",
        "source": "Jguarin, Circuit Board 2015.jpg; photographed February 23, 2014, uploaded August 26, 2016. CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Resized/re-encoded; no generative edits. This derivative remains CC BY-SA 4.0.",
        "source_url": "https://commons.wikimedia.org/wiki/File:Circuit_Board_2015.jpg",
    },
    {
        "title": "Bench inspection / B", "kind": "image", "difficulty": 2, "seconds": 35,
        "context": "Workshop image. Inspect solder joints, wire routes and board geometry. Choose the image's origin.",
        "media": "/static/images/sample12.jpg", "alt": "The solder side of an electronics prototype with wires and uneven solder joints on a work surface.",
        "image_fit": "contain", "image_position": "center", "answer": "AI",
        "explanation": "Generated for this deck using the built-in image-generation tool. The prompt requested an ordinary hand-built prototype, imperfect joints and modest camera quality rather than a polished product photograph.",
        "technical_note": "Workshop mess, flux-like marks and uneven soldering can all be generated. You can inspect geometry, but neither visual plausibility nor an apparent wiring defect establishes who produced the image. No claim is made that this fictional board would work electrically.",
        "discussion": "Did the DIY appearance make this seem more human than a clean circuit-board render?",
        "source": "OpenAI built-in image generation, October 2, 2026. Original fictional prototype image; full prompt in ContentSources.md. Resized/re-encoded for this app.",
    },
    {
        "title": "The exception that escaped", "kind": "commit", "difficulty": 3, "seconds": 40,
        "context": "Commit excerpt about task cancellation. Repository, issue number and author are withheld until reveal.",
        "body": 'Make asyncio.CancelledError a BaseException.\n\nThis will address the common mistake many asyncio users make:\nan "except Exception" clause breaking Tasks cancellation.\n\nIn addition to this change, we stop inheriting asyncio.TimeoutError\nand asyncio.InvalidStateError from their concurrent.futures.*\ncounterparts.  There\'s no point for these exceptions to share the\ninheritance chain.',
        "answer": "HUMAN",
        "explanation": "Yury Selivanov's CPython commit from May 27, 2019. The subject's issue/PR identifiers and the final paragraph are omitted; the displayed wording is otherwise preserved.",
        "technical_note": "Making CancelledError a direct BaseException subclass means broad 'except Exception' handlers no longer swallow cancellation. This is a control-flow compatibility change, not merely tidying exception names. The commit's terse confidence belongs to a real maintainer.",
        "discussion": "Did the confident dismissal of shared inheritance seem like an AI oversimplification or a human judgment?",
        "source": "Yury Selivanov, CPython commit 431b540bf79f0982559b1b0e420b1b085f667bb7, May 27, 2019. PSF license. Selected commit-message excerpt.",
        "source_url": "https://github.com/python/cpython/commit/431b540bf79f0982559b1b0e420b1b085f667bb7",
    },
    {
        "title": "Claim first, work later", "kind": "code", "difficulty": 3, "seconds": 45,
        "context": "PostgreSQL. Each worker commits its claim before performing an external side effect. jobs.id is unique.",
        "body": "WITH picked AS (\n    SELECT id\n    FROM jobs\n    WHERE state = 'queued'\n    ORDER BY priority DESC, id\n    LIMIT 1\n    FOR UPDATE SKIP LOCKED\n)\nUPDATE jobs AS j\nSET state = 'running', attempts = j.attempts + 1\nFROM picked AS p\nWHERE j.id = p.id\nRETURNING j.id, j.payload;",
        "answer": "AI",
        "explanation": "Original AI-written SQL for this game. The concurrency mechanism is deliberate and plausible. Correctness under the stated assumptions is not evidence of human authorship.",
        "technical_note": "FOR UPDATE locks the selected job; SKIP LOCKED lets peers choose other unlocked jobs. Updating state in the same statement makes the claim durable on commit. This does not provide exactly-once external effects: crash recovery that requeues a job can repeat work unless the downstream operation is idempotent or deduplicated.",
        "discussion": "Does recognizing a legitimate queue pattern make you more willing to call the code human?",
        "source": "AI assistant, original fictional SQL written for this deck, October 2, 2026. The query is displayed, never executed by the game.",
        "technical_source_url": "https://www.postgresql.org/docs/current/sql-select.html#SQL-FOR-UPDATE-SHARE",
    },
    {
        "title": "One slot, two threads", "kind": "code", "difficulty": 4, "seconds": 55,
        "context": "C++11+. <atomic> is included. Exactly one producer calls put; one consumer calls take. The Slot outlives both threads.",
        "body": "struct Slot {\n    int payload;\n    std::atomic<bool> full{false};\n};\nvoid put(Slot& s, int v) {\n    while (s.full.load(std::memory_order_acquire)) {}\n    s.payload = v;\n    s.full.store(true, std::memory_order_release);\n}\nint take(Slot& s) {\n    while (!s.full.load(std::memory_order_acquire)) {}\n    int v = s.payload;\n    s.full.store(false, std::memory_order_release);\n    return v;\n}",
        "answer": "AI",
        "explanation": "AI wrote this compact handoff for the deck. It deliberately uses correct acquire/release ordering under the stated single-producer, single-consumer assumptions.",
        "technical_note": "The producer's release of true publishes payload to the consumer's matching acquire. The consumer's release of false orders its read before the producer reuses the slot. Both directions matter even though payload is not atomic. Busy waiting is not a lock-free progress guarantee; multiple producers or consumers would invalidate this protocol.",
        "discussion": "Would an explicit memory-order argument convince you the author was human? What changes if the loads become relaxed?",
        "source": "AI assistant, original C++ example written for this deck, October 2, 2026. Displayed only; not executed by the app.",
        "technical_source_url": "https://eel.is/c++draft/atomics.order",
    },
    {
        "title": "Permission to wake", "kind": "code", "difficulty": 4, "seconds": 55,
        "context": "Go excerpt from an unlock loop. State packs lock/wake/starvation flags and a shifted waiter count; old is the observed state.",
        "body": "if old>>mutexWaiterShift == 0 || old&(mutexLocked|mutexWoken|mutexStarving) != 0 {\n\treturn\n}\n// Grab the right to wake someone.\nnew = (old - 1<<mutexWaiterShift) | mutexWoken\nif atomic.CompareAndSwapInt32(&m.state, old, new) {\n\truntime_Semrelease(&m.sema, false)\n\treturn\n}\nold = m.state",
        "answer": "HUMAN",
        "explanation": "Original Go 1.9 sync.Mutex unlock code, published in 2017. The surrounding loop and its explanatory comment block are omitted; the selected statements are unchanged apart from outer indentation.",
        "technical_note": "The count check and flags avoid redundant wakes. The candidate state decrements a waiter and sets mutexWoken; CAS claims the right to wake without losing a concurrent state update. A failed CAS refreshes old for the surrounding loop. In Go, shifts have higher precedence than subtraction here, so 1<<mutexWaiterShift is the waiter-count unit.",
        "discussion": "Did the dense expression and informal comment look too rough to be generated, or too clever to be human?",
        "source": "The Go Authors, go1.9 (2017), src/sync/mutex.go, selected Mutex.Unlock slow-path statements. BSD 3-Clause license in licenses/GO-LICENSE.txt.",
        "source_url": "https://github.com/golang/go/blob/go1.9/src/sync/mutex.go",
    },
    {
        "title": "The cursor goes backwards", "kind": "code", "difficulty": 5, "seconds": 60,
        "context": "C excerpt. Hash-table size is a power of two; m0 = size - 1. rev() reverses all bits of an unsigned long.",
        "body": "de = t0->table[v & m0];\nwhile (de) {\n    fn(privdata, de);\n    de = de->next;\n}\n\n/* Set unmasked bits so incrementing the reversed cursor\n * operates on the masked bits */\nv |= ~m0;\n\n/* Increment the reverse cursor */\nv = rev(v);\nv++;\nv = rev(v);",
        "answer": "HUMAN",
        "explanation": "Original Redis 3.2.13 dictScan code from 2019. The unusual cursor transformation is a production algorithm, not a generated flourish. Only surrounding control flow and outer indentation are omitted.",
        "technical_note": "The implementation increments the cursor in reversed-bit order so iteration remains useful when a power-of-two table changes size between calls. SCAN is not a snapshot and can return duplicates; elements continuously present during a full iteration are covered. The curious bit operations solve a real resizing constraint.",
        "discussion": "Did unfamiliar low-level code make you guess AI? Can you explain why simply using v++ would be a different traversal?",
        "source": "Redis contributors, 3.2.13 (2019), src/dict.c, dictScan non-rehashing branch. Algorithm credited in source to Pieter Noordhuis. BSD 3-Clause license in licenses/REDIS-LICENSE.txt.",
        "source_url": "https://github.com/redis/redis/blob/3.2.13/src/dict.c",
        "technical_source_url": "https://redis.io/docs/latest/commands/scan/",
    },
    {
        "title": "The lock was valid", "kind": "text", "difficulty": 5, "seconds": 60,
        "context": "Excerpt from an incident channel discussing stale writes under a lease. Decide who wrote the note.",
        "body": "09:41:02  worker A gets lease 71, valid for 10s.\n09:41:03  A checks expiry, then pauses before sending its write.\n09:41:12  lease 71 expires. B acquires lease 72.\n09:41:13  B writes the new value.\n09:41:17  A resumes and overwrites B.\n\nThe lease service did exactly what we asked. The store\nnever knew that 71 was stale. Checking expiry twice just\nmoves the pause window.\n\nPatch: send the generation with every write. The store\natomically rejects tokens lower than the highest accepted\nfor that resource. Generations must survive failover; a\nrandom UUID is an owner ID, not an ordering relation.",
        "answer": "AI",
        "explanation": "A fictional incident note written by AI for this deck. The timestamps, restrained blame and failover caveat were chosen to resemble an experienced operator's explanation.",
        "technical_note": "An expired lease does not physically stop its former holder. A monotonic fencing token checked atomically by the destination can reject A's stale write after B's newer write. A unique random owner ID is useful for identifying an owner, but does not order generations. Equal-token retries and duplicate side effects need a separate idempotency policy.",
        "discussion": "Did the precise failure timeline and operational caveat feel like firsthand experience? What assumption does the proposed fix need from storage?",
        "source": "AI assistant, original fictional incident written for this deck, October 2, 2026. The scenario applies the established fencing-token pattern; it is not a reported outage or a quotation.",
        "technical_source_url": "https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html",
    },
]
