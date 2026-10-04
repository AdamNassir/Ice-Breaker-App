"""Ten English starter questions: eight images and two texts.

questions.json takes priority over this fallback. The presenter-selected timer
applies to every round; legacy seconds fields are ignored by the game.
For social screenshots, judge the post or reply text. HUMAN includes deliberate
human-made camera tricks. Sources and classifications: ContentSources.md.
"""

ROUNDS = [{'title': 'My AI agent deleted the roadmap',
  'kind': 'image',
  'seconds': 25,
  'context': 'Judge the writing in the post.',
  'answer': 'AI',
  'explanation': 'The post is an original AI-written satire. The interface is a fictional '
                 'reconstruction, not a real LinkedIn account.',
  'discussion': '',
  'source': 'Original AI-written fictional LinkedIn-style post. Layout drawn in Python with '
            'Pillow; all names and avatars are fictional and blurred. No real account or public '
            'figure is depicted.',
  'media': '/static/images/sample18.png',
  'alt': 'A professional-network post with a blurred profile picture and identity.',
  'image_fit': 'contain'},
 {'title': 'The football upgrade nobody asked for',
  'kind': 'image',
  'seconds': 25,
  'context': 'Inspect the players and their equipment. Judge the image origin.',
  'media': '/static/images/sample15.jpg',
  'alt': 'A historical black-and-white photograph of people playing football while riding '
         'motorcycles.',
  'image_fit': 'contain',
  'answer': 'HUMAN',
  'explanation': 'Motorcycle football was real. This photograph is preserved by the German Federal '
                 'Archives and dated August 1931. Strange inventions existed long before image '
                 'generators.',
  'discussion': '',
  'source': 'Bundesarchiv, Bild 102-12210 / CC-BY-SA 3.0 Germany. Photographer unrecorded; August '
            '1931. Commons version cropped in 2024; app copy re-encoded as JPEG without generative '
            'edits. License: https://creativecommons.org/licenses/by-sa/3.0/de/deed.en',
  'source_url': 'https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_102-12210,_Fussballspiel_mit_dem_Motorrad.jpg'},
 {'title': 'A very scientific pop-culture observation',
  'kind': 'image',
  'media': '/static/images/sample21.png',
  'image_fit': 'contain',
  'alt': 'A short social-network post with the profile picture, name and handle pixelated.',
  'seconds': 25,
  'answer': 'HUMAN',
  'context': 'Judge the writing in the post.',
  'explanation': 'Unchanged wording of a genuine Donald Trump Truth Social post from May 16, 2025. '
                 'The interface is reconstructed and coarsely pixelated. HUMAN refers to the '
                 'original writing, not the truth of the claim.',
  'source': 'Donald J. Trump, Truth Social, May 16, 2025, post 114517718765768352. Exact complete '
            'wording (15 words), preserved in The American Presidency Project: '
            'https://www.presidency.ucsb.edu/documents/truth-social-posts-may-16-2025 . '
            'Reconstructed native interface; drawn placeholder avatar and coarsely pixelated '
            'name/handle. No fabricated date or engagement counts.',
  'source_url': 'https://truthsocial.com/@realDonaldTrump/posts/114517718765768352',
  'discussion': ''},
 {'title': 'Perfectly normal office lighting',
  'kind': 'image',
  'seconds': 25,
  'context': 'A person reads beside an electrical experiment. Judge whether AI created this image.',
  'media': '/static/images/sample16.jpg',
  'alt': 'A seated person reading near large electrical equipment and bright arcs in a historical '
         'photograph.',
  'image_fit': 'contain',
  'answer': 'HUMAN',
  'explanation': 'The famous Tesla laboratory publicity photograph dates to December 1899. It is a '
                 'human-made double exposure: the electrical arcs and Tesla were photographed '
                 'separately. HUMAN does not mean the scene happened exactly as pictured.',
  'discussion': '',
  'source': 'Dickenson V. Alley, Tesla laboratory photograph, December 1899; Commons '
            'public-domain-US record. Historical double exposure, resized/re-encoded for this app; '
            'no generative edits.',
  'source_url': 'https://commons.wikimedia.org/wiki/File:Tesla_colorado.jpg'},
 {'title': 'The protocol committee got creative',
  'kind': 'text',
  'seconds': 25,
  'context': 'Excerpts from four networking specifications. Judge the original writing.',
  'body': 'The bandwidth is limited to the leg length. A typical MTU is 256 milligrams. Some '
          'datagram padding may be needed.\n'
          '\n'
          '[...]\n'
          '\n'
          'The carriers may sleep while enqueued.\n'
          '[...]\n'
          'Packets MAY be marked for deletion using RED paint while enqueued.\n'
          '\n'
          '[...]\n'
          '\n'
          'There is evidence that some carriers have a propensity to eat other carriers and then '
          'carry the eaten payloads.\n'
          '\n'
          '[...]\n'
          '\n'
          "No options were given for decaffeinated coffee. What's the point?\n"
          '[...]\n'
          'The resulting entity body MAY be short and stout.',
  'answer': 'HUMAN',
  'explanation': 'These are unchanged excerpts from four human-written April Fools RFCs: 1149, '
                 '2549, 6214 and 2324. Marked omissions separate excerpts; their absurdity is '
                 'intentional.',
  'discussion': '',
  'source': 'RFC 1149 (D. Waitzman, 1990), 2549 (D. Waitzman, 1999), 6214 (B. Carpenter and R. '
            'Hinden, 2011), and 2324 (L. Masinter, 1998). All published April 1. Exact English '
            'excerpts, at most 25 words per RFC, with marked omissions. Individual URLs and '
            'excerpt mapping in ContentSources.md.',
  'source_url': 'https://www.rfc-editor.org/rfc/rfc1149.html'},
 {'title': 'An unexpected guest at the coronation',
  'kind': 'image',
  'seconds': 25,
  'context': 'Inspect the guests in this imperial painting. Then choose AI or HUMAN.',
  'media': '/static/images/sample13.jpg',
  'alt': 'An imperial ceremony painting with ornate robes and a grey-coated guest among the crowd.',
  'image_fit': 'contain',
  'answer': 'AI',
  'explanation': 'This is an original AI-generated historical pastiche. Inspector Gadget has '
                 'slipped into the crowd, complete with a mechanical arm. It is not an authentic '
                 'Napoleon painting, and no museum record is claimed.',
  'discussion': '',
  'source': 'OpenAI built-in image generation, October 4, 2026. Original fictional imperial '
            'ceremony; Inspector Gadget cameo. Resized/re-encoded; full prompt in '
            'ContentSources.md.'},
 {'title': 'The firewall procurement plan',
  'kind': 'image',
  'media': '/static/images/sample22.png',
  'image_fit': 'contain',
  'alt': 'A social-network post with the profile picture, name and handle pixelated.',
  'seconds': 25,
  'answer': 'AI',
  'context': 'Judge the writing in the post.',
  'explanation': 'AI wrote this original parody about a giant firewall and CAPS LOCK security. It '
                 'imitates a bombastic social-media style, but it is not a real Trump statement. '
                 'Both the post and interface were created for the game.',
  'source': 'Original AI-written fictional tweet-style satire, October 4, 2026. No real person '
            'said or posted these words. Native Python/Pillow interface reconstruction, coarsely '
            'pixelated drawn placeholder avatar and author fields; no fabricated date or '
            'engagement counts.',
  'discussion': ''},
 {'title': 'The printer has been promoted',
  'kind': 'text',
  'seconds': 25,
  'context': 'Judge the writing.',
  'body': 'At 09:14, the office printer was elected primary database server after reporting the '
          'best uptime in the building.\n'
          '\n'
          'The migration initially went well. Every transaction was acknowledged, stapled and '
          'placed in the output tray. Unfortunately, our backup strategy depended on someone '
          'remembering to buy paper.\n'
          '\n'
          'At 10:02, a jam caused the entire finance department to become read-only. The on-call '
          'engineer resolved the incident by opening Tray 2 and gently reassuring the printer.\n'
          '\n'
          'Action items: purchase toner, add a second printer for redundancy, and stop describing '
          'the shredder as our data-retention policy.',
  'answer': 'AI',
  'explanation': 'Original AI-written comic incident report. It turns ordinary printer problems '
                 'into a database outage; it is not a real company postmortem.',
  'discussion': '',
  'source': 'Original AI-written English tech satire created for this game, October 4, 2026. No '
            'external quotation or real incident claimed.'},
 {'title': 'The quarterly technical validation',
  'kind': 'image',
  'media': '/static/images/sample19.png',
  'image_fit': 'contain',
  'alt': 'A work chat with blurred identities, a PDF attachment, a visible document preview, and a '
         'reply.',
  'context': 'Judge the second message in the conversation.',
  'answer': 'AI',
  'explanation': 'AI wrote the off-topic validation: a company-wide automated purchasing platform '
                 'and international rollout are absent from the simple manual coffee-rota '
                 'document. The people, messages, document and interface are fictional.',
  'source': 'Original AI-written fictional Teams reply and coffee-rota PDF. Native editable UI '
            "reconstruction based on Microsoft Support's current combined Chat view, accessed "
            'October 4, 2026: '
            'https://support.microsoft.com/en-us/teams/teams-channels/explore-the-new-chat-and-channels-experience-in-microsoft-teams '
            '. No real account, employee or PDF; drawn profiles and names blurred.',
  'discussion': '',
  'seconds': 25},
 {'title': 'A bug report with physical evidence',
  'kind': 'image',
  'media': '/static/images/sample20.jpg',
  'image_fit': 'contain',
  'alt': 'A handwritten engineering logbook page with an insect taped beside an entry.',
  'context': 'Judge the photograph.',
  'answer': 'HUMAN',
  'explanation': 'A moth was recorded in the Harvard Mark II logbook on September 9, 1947. This is '
                 'a human-made photograph of the actual logbook, not generated imagery. The '
                 'engineering term bug already existed.',
  'source': 'U.S. Navy / Naval Surface Warfare Center, Dahlgren, photograph of the Harvard Mark II '
            'logbook. Public-domain U.S. federal government image, resized and re-encoded without '
            'generative edits. Correct logbook date September 9, 1947; some legacy photo metadata '
            'incorrectly says 1945.',
  'source_url': 'https://commons.wikimedia.org/wiki/File:First_Computer_Bug,_1947.jpg',
  'discussion': '',
  'seconds': 25}]
